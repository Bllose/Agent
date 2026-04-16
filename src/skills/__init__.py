"""
SKILL 系统模块

提供技能内容管理功能，用于指导 AI Agent 的行为。
SKILL 是 Markdown 文件，包含对大模型的指导说明。
"""

from src.skills.manager import SkillManager

__all__ = ['SkillManager']
