"""
SKILL 管理器

负责加载和管理 SKILL 内容。
SKILL 是 Markdown 文件，包含对大模型的指导说明，
会被注入到 system prompt 中，指导大模型行为。
"""

import os
import glob
from typing import Dict, List
from src.core.logger import get_logger


class SkillManager:
    """SKILL 管理器，负责加载和提供 SKILL 内容。"""

    def __init__(self, workplace: str):
        """
        初始化 SKILL 管理器。

        Args:
            workplace: 项目根目录路径
        """
        self.logger = get_logger('skill_manager')
        self.workplace = workplace
        self.skills: Dict[str, str] = {}

        # 定义 SKILL 文件路径
        self.builtin_skills_dir = os.path.join(workplace, "src", "skills", "builtin")
        self.user_skills_dir = os.path.join(workplace, "config", "skills")

        # 加载所有 SKILL
        self.load_all_skills()

    def load_all_skills(self) -> None:
        """加载所有系统 SKILL 和用户 SKILL。"""
        self.logger.info("Loading SKILL files...")

        # 清空现有技能
        self.skills = {}

        # 加载系统内置 SKILL
        builtin_count = self._load_skills_from_directory(self.builtin_skills_dir)
        self.logger.info(f"Loaded {builtin_count} builtin SKILL(s)")

        # 加载用户自定义 SKILL
        user_count = self._load_skills_from_directory(self.user_skills_dir)
        self.logger.info(f"Loaded {user_count} user SKILL(s)")

        total_count = builtin_count + user_count
        self.logger.info(f"Total {total_count} SKILL(s) loaded")

    def _load_skills_from_directory(self, directory: str) -> int:
        """
        从指定目录加载所有 SKILL。

        Args:
            directory: SKILL 目录路径

        Returns:
            加载的 SKILL 数量
        """
        count = 0

        if not os.path.exists(directory):
            self.logger.debug(f"SKILL directory not found: {directory}")
            return count

        # 查找所有 SKILL.md 文件
        skill_pattern = os.path.join(directory, "*/SKILL.md")
        skill_files = glob.glob(skill_pattern)

        for skill_file in skill_files:
            # 从文件路径提取 SKILL 名称
            skill_name = os.path.basename(os.path.dirname(skill_file))

            try:
                # 读取 SKILL 内容
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                if content:
                    self.skills[skill_name] = content
                    count += 1
                    self.logger.debug(f"Loaded SKILL: {skill_name}")
                else:
                    self.logger.warning(f"SKILL file is empty: {skill_file}")

            except Exception as e:
                self.logger.error(f"Failed to load SKILL {skill_name}: {str(e)}")

        return count

    def get_skills_content(self) -> str:
        """
        获取所有 SKILL 的内容拼接。

        Returns:
            所有 SKILL 的 Markdown 内容拼接字符串
        """
        if not self.skills:
            return ""

        content_parts = []

        for skill_name, skill_content in self.skills.items():
            content_parts.append(skill_content)
            content_parts.append("\n")

        return "\n".join(content_parts)

    def get_skill(self, skill_name: str) -> str:
        """
        获取指定 SKILL 的内容。

        Args:
            skill_name: SKILL 名称

        Returns:
            SKILL 内容，如果不存在则返回空字符串
        """
        return self.skills.get(skill_name, "")

    def get_all_skill_names(self) -> List[str]:
        """
        获取所有 SKILL 名称列表。

        Returns:
            SKILL 名称列表
        """
        return list(self.skills.keys())

    def has_skill(self, skill_name: str) -> bool:
        """
        检查是否存在指定 SKILL。

        Args:
            skill_name: SKILL 名称

        Returns:
            如果 SKILL 存在返回 True，否则返回 False
        """
        return skill_name in self.skills

    def reload_skills(self) -> None:
        """重新加载所有 SKILL。"""
        self.logger.info("Reloading SKILL files...")
        self.load_all_skills()
