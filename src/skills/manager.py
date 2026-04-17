"""
SKILL 管理器

负责（懒）加载和管理 SKILL 内容。
SKILL 是 Markdown 文件，包含对大模型的指导说明，
会被注入到 system prompt 中，指导大模型行为。
"""

import os
import glob
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from src.core.logger import get_logger


@dataclass
class SkillMetadata:
    """SKILL 元数据（懒加载用）"""
    name: str
    description: str
    file_path: str
    loaded: bool = False


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
        self.skills: Dict[str, str] = {}  # 完整技能内容缓存
        self.skill_metadata: Dict[str, SkillMetadata] = {}  # 技能元数据

        # 定义 SKILL 文件路径
        self.builtin_skills_dir = os.path.join(workplace, "src", "skills", "builtin")
        self.user_skills_dir = os.path.join(workplace, "config", "skills")

        # 加载所有 SKILL 元数据
        self.load_all_skills()

    def load_all_skills(self) -> None:
        """加载所有系统 SKILL 和用户 SKILL 的元数据（懒加载）。"""
        self.logger.info("Loading SKILL metadata...")

        # 清空现有技能
        self.skills = {}
        self.skill_metadata = {}

        # 加载系统内置 SKILL
        builtin_count = self._load_skills_from_directory(self.builtin_skills_dir)
        self.logger.info(f"Loaded {builtin_count} builtin SKILL(s) metadata")

        # 加载用户自定义 SKILL
        user_count = self._load_skills_from_directory(self.user_skills_dir)
        self.logger.info(f"Loaded {user_count} user SKILL(s) metadata")

        total_count = builtin_count + user_count
        self.logger.info(f"Total {total_count} SKILL(s) registered")

    def _load_skills_from_directory(self, directory: str) -> int:
        """
        从指定目录加载所有 SKILL 的元数据（懒加载）。

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
            try:
                # 解析 frontmatter 获取元数据
                name, description = self._parse_skill_metadata(skill_file)

                if name:
                    self.skill_metadata[name] = SkillMetadata(
                        name=name,
                        description=description,
                        file_path=skill_file,
                        loaded=False
                    )
                    count += 1
                    self.logger.debug(f"Registered SKILL: {name}")
                else:
                    self.logger.warning(f"SKILL file missing name in frontmatter: {skill_file}")

            except Exception as e:
                self.logger.error(f"Failed to load SKILL metadata from {skill_file}: {str(e)}")

        return count

    def _parse_skill_metadata(self, file_path: str) -> tuple[Optional[str], str]:
        """
        解析 SKILL 文件的 frontmatter 获取元数据。

        Args:
            file_path: SKILL 文件路径

        Returns:
            tuple: (name, description) 如果解析失败返回 (None, "")
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析 YAML frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter_text = frontmatter_match.group(1)

                # 提取 name
                name_match = re.search(r'name:\s*(.+)', frontmatter_text)
                name = name_match.group(1).strip().strip('"') if name_match else None

                # 提取 description
                desc_match = re.search(r'description:\s*(.+)', frontmatter_text)
                description = desc_match.group(1).strip().strip('"') if desc_match else ""

                return name, description

            return None, ""

        except Exception as e:
            self.logger.error(f"Failed to parse SKILL metadata from {file_path}: {str(e)}")
            return None, ""

    def _load_skill_content(self, skill_name: str) -> Optional[str]:
        """
        懒加载指定 SKILL 的完整内容。

        Args:
            skill_name: SKILL 名称

        Returns:
            SKILL 完整内容，如果加载失败返回 None
        """
        metadata = self.skill_metadata.get(skill_name)
        if not metadata:
            self.logger.warning(f"SKILL not found: {skill_name}")
            return None

        # 如果已经加载过，直接返回缓存
        if skill_name in self.skills:
            return self.skills[skill_name]

        try:
            with open(metadata.file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if content:
                self.skills[skill_name] = content
                metadata.loaded = True
                self.logger.debug(f"Loaded SKILL content: {skill_name}")
                return content
            else:
                self.logger.warning(f"SKILL file is empty: {metadata.file_path}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to load SKILL content {skill_name}: {str(e)}")
            return None

    def get_skills_content(self, skill_names: List[str] = None) -> str:
        """
        获取指定 SKILL 的内容拼接。

        Args:
            skill_names: 要加载的 SKILL 名称列表，如果为 None 则加载所有 SKILL

        Returns:
            指定 SKILL 的 Markdown 内容拼接字符串
        """
        if not self.skill_metadata:
            return ""

        # 如果没有指定 SKILL，默认加载所有 SKILL
        if skill_names is None:
            skill_names = list(self.skill_metadata.keys())

        content_parts = []

        for skill_name in skill_names:
            skill_content = self._load_skill_content(skill_name)
            if skill_content:
                content_parts.append(skill_content)
                content_parts.append("\n")

        return "\n".join(content_parts)

    def get_skill_metadata_list(self) -> List[dict]:
        """
        获取所有 SKILL 的元数据列表。

        Returns:
            SKILL 元数据列表
        """
        return [
            {
                'name': metadata.name,
                'description': metadata.description,
                'loaded': metadata.loaded
            }
            for metadata in self.skill_metadata.values()
        ]

    def get_skills_summary(self) -> str:
        """
        获取所有 SKILL 的摘要信息（仅包含名称和描述）。

        Returns:
            SKILL 摘要的 Markdown 格式字符串
        """
        if not self.skill_metadata:
            return ""

        lines = ["Available Skills:\n"]

        for metadata in self.skill_metadata.values():
            lines.append(f"## {metadata.name}")
            lines.append(metadata.description)
            lines.append("")

        return "\n".join(lines)

    def get_skill(self, skill_name: str) -> str:
        """
        获取指定 SKILL 的内容（懒加载）。

        Args:
            skill_name: SKILL 名称

        Returns:
            SKILL 内容，如果不存在则返回空字符串
        """
        content = self._load_skill_content(skill_name)
        return content if content else ""

    def get_all_skill_names(self) -> List[str]:
        """
        获取所有 SKILL 名称列表。

        Returns:
            SKILL 名称列表
        """
        return list(self.skill_metadata.keys())

    def has_skill(self, skill_name: str) -> bool:
        """
        检查是否存在指定 SKILL。

        Args:
            skill_name: SKILL 名称

        Returns:
            如果 SKILL 存在返回 True，否则返回 False
        """
        return skill_name in self.skill_metadata

    def reload_skills(self) -> None:
        """重新加载所有 SKILL 元数据。"""
        self.logger.info("Reloading SKILL files...")
        self.load_all_skills()
