"""
Todo 任务管理工具
用于在复杂任务中跟踪进度、管理状态、处理重复尝试
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from src.core.logger import get_logger

logger = get_logger('agent.tools.todo')


# Todo 数据存储文件
TODO_FILE = "todo_state.json"


class TodoManager:
    """任务管理器"""

    def __init__(self):
        self.tasks: List[Dict] = []
        self.current_index: int = 0
        self.max_retries: int = 3
        self.retry_counts: Dict[int, int] = {}
        self.load_state()

    def load_state(self):
        """从文件加载任务状态"""
        if os.path.exists(TODO_FILE):
            try:
                with open(TODO_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.current_index = data.get('current_index', 0)
                    self.retry_counts = data.get('retry_counts', {})
                logger.info(f"Loaded todo state: {len(self.tasks)} tasks")
            except Exception as e:
                logger.error(f"Failed to load todo state: {e}", exc_info=True)

    def save_state(self):
        """保存任务状态到文件"""
        self.tasks = [task for task in self.tasks if task.get('status') != 'deleted']
        try:
            with open(TODO_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'tasks': self.tasks,
                    'current_index': self.current_index,
                    'retry_counts': self.retry_counts
                }, f, ensure_ascii=False, indent=2)
            logger.debug("Todo state saved successfully")
        except Exception as e:
            logger.error(f"Failed to save todo state: {e}", exc_info=True)

    def create_tasks(self, items: List[Dict]) -> Dict:
        """
        创建任务列

        Args:
            items: 任务列表，每个任务包含 content, status, activeForm

        Returns:
            操作结果
        """
        try:
            # 验证输入格式
            for item in items:
                if 'content' not in item or 'status' not in item:
                    return {
                        "success": False,
                        "error": "每个任务必须包含 content 和 status 字段"
                    }
                if item['status'] not in ['pending', 'in_progress', 'completed']:
                    return {
                        "success": False,
                        "error": "status 必须是 pending, in_progress 或 completed"
                    }

            # 创建新任务
            new_tasks = []
            for i, item in enumerate(items):
                task = {
                    "id": len(self.tasks) + i + 1,
                    "content": item['content'],
                    "status": item['status'],
                    "activeForm": item.get('activeForm', ''),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                new_tasks.append(task)
                self.retry_counts[task['id']] = 0

            self.tasks.extend(new_tasks)
            self.current_index = 0
            self.save_state()

            return {
                "success": True,
                "message": f"成功创建 {len(new_tasks)} 个任务",
                "tasks": new_tasks,
                "summary": self._get_summary()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"创建任务失败: {str(e)}"
            }

    def list_tasks(self) -> Dict:
        """获取任务列表摘要"""
        try:
            summary = self._get_summary()
            return {
                "success": True,
                "tasks": self.tasks,
                "current_index": self.current_index,
                "summary": summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取任务列表失败: {str(e)}"
            }

    def get_next_task(self) -> Dict:
        """获取下一个待处理的任务"""
        try:
            # 查找下一个 pending 或 in_progress 状态的任务
            for i, task in enumerate(self.tasks):
                if task['status'] in ['pending', 'in_progress']:
                    # 检查依赖是否完成
                    if not self._has_unmet_dependencies(task):
                        self.current_index = i
                        task['updated_at'] = datetime.now().isoformat()
                        self.save_state()
                        return {
                            "success": True,
                            "task": task,
                            "message": f"找到下一个任务: {task['id']}"
                        }

            return {
                "success": False,
                "message": "没有找到待处理的任务",
                "all_completed": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取下一个任务失败: {str(e)}"
            }

    def update_task(self, task_id: int, **kwargs) -> Dict:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段（status, content, activeForm等）

        Returns:
            操作结果
        """
        try:
            # 查找任务
            task = None
            task_index = -1
            for i, t in enumerate(self.tasks):
                if t['id'] == task_id:
                    task = t
                    task_index = i
                    break

            if task is None:
                return {
                    "success": False,
                    "error": f"未找到任务 ID: {task_id}"
                }

            # 处理重复尝试
            old_status = task.get('status')
            new_status = kwargs.get('status')

            if new_status == 'in_progress' and old_status == 'in_progress':
                # 重新进入 in_progress，增加重试计数
                self.retry_counts[task_id] = self.retry_counts.get(task_id, 0) + 1
                if self.retry_counts[task_id] >= self.max_retries:
                    return {
                        "success": False,
                        "error": f"任务 {task_id} 已达到最大重试次数 ({self.max_retries})，请重新评估任务",
                        "max_retries_exceeded": True,
                        "task_id": task_id
                    }
            elif new_status == 'completed':
                # 任务完成，重置重试计数
                self.retry_counts[task_id] = 0

            # 更新任务字段
            for key, value in kwargs.items():
                if key in ['status', 'content', 'activeForm', 'addBlocks', 'addBlockedBy']:
                    task[key] = value

            task['updated_at'] = datetime.now().isoformat()
            self.save_state()

            # 获取进展信息
            progress = self._get_progress()

            return {
                "success": True,
                "message": f"任务 {task_id} 已更新",
                "task": task,
                "progress": progress,
                "summary": self._get_summary()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"更新任务失败: {str(e)}"
            }

    def delete_task(self, task_id: int) -> Dict:
        """删除任务"""
        try:
            task_found = False
            for task in self.tasks:
                if task['id'] == task_id:
                    task['status'] = 'deleted'
                    task_found = True
                    break

            if task_found:
                self.retry_counts.pop(task_id, None)
                self.save_state()
                return {
                    "success": True,
                    "message": f"任务 {task_id} 已删除"
                }
            else:
                return {
                    "success": False,
                    "error": f"未找到任务 ID: {task_id}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"删除任务失败: {str(e)}"
            }

    def clear_all(self) -> Dict:
        """清除所有任务"""
        try:
            self.tasks = []
            self.current_index = 0
            self.retry_counts = {}
            self.save_state()
            return {
                "success": True,
                "message": "所有任务已清除"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"清除任务失败: {str(e)}"
            }

    def reset_task_retry(self, task_id: int) -> Dict:
        """
        重置任务的重试计数

        Args:
            task_id: 任务ID

        Returns:
            操作结果
        """
        try:
            if task_id in self.retry_counts:
                self.retry_counts[task_id] = 0
                self.save_state()
                return {
                    "success": True,
                    "message": f"任务 {task_id} 的重试计数已重置"
                }
            else:
                return {
                    "success": False,
                    "error": f"任务 {task_id} 未找到重试记录"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"重置重试计数失败: {str(e)}"
            }

    def get_task_status(self, task_id: int) -> Dict:
        """
        获取任务详细状态

        Args:
            task_id: 任务ID

        Returns:
            任务详情
        """
        try:
            for task in self.tasks:
                if task['id'] == task_id:
                    return {
                        "success": True,
                        "task": task,
                        "retry_count": self.retry_counts.get(task_id, 0),
                        "max_retries": self.max_retries
                    }

            return {
                "success": False,
                "error": f"未找到任务 ID: {task_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"获取任务状态失败: {str(e)}"
            }

    def _get_summary(self) -> str:
        """获取任务列表摘要"""
        pending = sum(1 for t in self.tasks if t['status'] == 'pending')
        in_progress = sum(1 for t in self.tasks if t['status'] == 'in_progress')
        completed = sum(1 for t in self.tasks if t['status'] == 'completed')
        total = pending + in_progress + completed

        return f"任务进度: {completed}/{total} 完成, {in_progress} 进行中, {pending} 待处理"

    def _get_progress(self) -> Dict:
        """获取详细的进度信息"""
        pending = sum(1 for t in self.tasks if t['status'] == 'pending')
        in_progress = sum(1 for t in self.tasks if t['status'] == 'in_progress')
        completed = sum(1 for t in self.tasks if t['status'] == 'completed')
        total = pending + in_progress + completed

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "completed_percentage": round(completed / total) if total > 0 else 0
        }

    def _has_unmet_dependencies(self, task: Dict) -> bool:
        """检查任务是否有未完成的依赖"""
        blocked_by = task.get('addBlockedBy', [])
        if not blocked_by:
            return False

        for dep_id in blocked_by:
            for dep_task in self.tasks:
                if dep_task['id'] == dep_id and dep_task['status'] != 'completed':
                    return True
        return False


# 全局任务管理器实例
_manager = None


def get_manager() -> TodoManager:
    """获取任务管理器单例"""
    global _manager
    if _manager is None:
        _manager = TodoManager()
    return _manager


def todo_create(items: List[Dict]) -> Dict:
    """
    创建新的任务列表

    Args:
        items: 任务列表，每个任务包含:
            - content: 任务描述
            - status: 任务状态 (pending, in_progress, completed)
            - activeForm: 可选，进行时状态显示的文本
            - addBlocks: 可选，阻塞的任务ID列表
            - addBlockedBy: 可选，被阻塞的任务ID列表

    Returns:
        操作结果
    """
    return get_manager().create_tasks(items)


def todo_list() -> Dict:
    """获取任务列表"""
    return get_manager().list_tasks()


def todo_next() -> Dict:
    """获取下一个待处理的任务"""
    return get_manager().get_next_task()


def todo_update(task_id: int, **kwargs) -> Dict:
    """
    更新任务状态

    Args:
        task_id: 任务ID
        **kwargs: 要更新的字段

    Returns:
        操作结果
    """
    return get_manager().update_task(task_id, **kwargs)


def todo_delete(task_id: int) -> Dict:
    """删除任务"""
    return get_manager().delete_task(task_id)


def todo_clear() -> Dict:
    """清除所有任务"""
    return get_manager().clear_all()


def todo_reset_retry(task_id: int) -> Dict:
    """
    重置任务的重试计数

    Args:
        task_id: 任务ID

    Returns:
        操作结果
    """
    return get_manager().reset_task_retry(task_id)


def todo_status(task_id: int) -> Dict:
    """
    获取任务详细状态

    Args:
        task_id: 任务ID

    Returns:
        任务详情
    """
    return get_manager().get_task_status(task_id)
