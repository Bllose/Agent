"""
Agent 日志配置模块

提供统一的日志配置和获取器
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class AgentLogger:
    """Agent 日志管理器"""

    # 日志级别映射
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    # 日志颜色配置
    LOG_COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }
    RESET_COLOR = '\033[0m'

    def __init__(self):
        self._loggers: dict = {}
        self._initialized: bool = False
        self._log_dir: Optional[Path] = None

    def initialize(
        self,
        name: str = 'agent',
        level: str = 'INFO',
        log_dir: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        console_format: str = None,
        file_format: str = None
    ):
        """
        初始化日志系统

        Args:
            name: 日志器名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志文件目录
            enable_console: 是否启用控制台输出
            enable_file: 是否启用文件输出
            console_format: 控制台日志格式
            file_format: 文件日志格式
        """
        if self._initialized:
            return self._loggers.get(name, self._create_logger(name))

        # 设置日志目录
        if log_dir:
            self._log_dir = Path(log_dir)
        else:
            # 默认日志目录
            project_root = Path(__file__).parent.parent.parent
            self._log_dir = project_root / 'logs'

        # 确保日志目录存在
        if enable_file:
            self._log_dir.mkdir(parents=True, exist_ok=True)

        # 创建根日志器
        root_logger = logging.getLogger(name)
        root_logger.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))

        # 清除现有处理器
        root_logger.handlers.clear()

        # 控制台处理器
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))

            # 默认控制台格式
            if console_format is None:
                console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

            console_handler.setFormatter(
                ColoredFormatter(
                    fmt=console_format,
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
            root_logger.addHandler(console_handler)

        # 文件处理器
        if enable_file:
            log_file = self._log_dir / f'{name}_{datetime.now().strftime("%Y%m%d")}.log'
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))

            # 默认文件格式
            if file_format is None:
                file_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

            file_handler.setFormatter(
                logging.Formatter(
                    fmt=file_format,
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
            root_logger.addHandler(file_handler)

        self._loggers[name] = root_logger
        self._initialized = True

        # 初始化子模块日志器
        self._setup_child_loggers(name, level)

        return root_logger

    def _setup_child_loggers(self, parent_name: str, level: str):
        """设置子模块日志器"""
        child_modules = ['loop', 'tools', 'cli']
        for module in child_modules:
            logger = logging.getLogger(f'{parent_name}.{module}')
            logger.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))
            # 让子logger传播到父logger，不添加自己的handler
            logger.propagate = True

    def get_logger(self, name: str = 'agent') -> logging.Logger:
        """
        获取日志器

        Args:
            name: 日志器名称

        Returns:
            日志器实例
        """
        if name in self._loggers:
            return self._loggers[name]

        return self._create_logger(name)

    def _create_logger(self, name: str) -> logging.Logger:
        """创建新日志器"""
        logger = logging.getLogger(name)
        # 不添加handler，只让传播到父logger
        # 如果是子logger（包含点），设置为传播但不添加自己的handler
        if '.' in name:
            logger.propagate = True
            # 确保没有重复的handler
            if logger.handlers:
                logger.handlers.clear()
        else:
            # 根logger如果没有handler，添加一个基本的控制台处理器
            if not logger.handlers:
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(
                    ColoredFormatter(
                        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                    )
                )
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)

        self._loggers[name] = logger
        return logger

    def set_level(self, level: str, name: str = 'agent'):
        """
        设置日志级别

        Args:
            level: 日志级别
            name: 日志器名称
        """
        logger = self.get_logger(name)
        logger.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))
        for handler in logger.handlers:
            handler.setLevel(self.LOG_LEVELS.get(level.upper(), logging.INFO))


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.colors = {
            'DEBUG': '\033[36m',      # 青色
            'INFO': '\033[32m',       # 绿色
            'WARNING': '\033[33m',    # 黄色
            'ERROR': '\033[31m',      # 红色
            'CRITICAL': '\033[35m',   # 紫色
        }
        self.reset_color = '\033[0m'

    def format(self, record):
        """格式化日志记录"""
        levelname = record.levelname
        if levelname in self.colors:
            record.levelname = f"{self.colors[levelname]}{levelname}{self.reset_color}"
        return super().format(record)


# 全局日志管理器实例
_logger_manager = AgentLogger()


def get_logger(name: str = 'agent') -> logging.Logger:
    """
    获取日志器（便捷函数）

    Args:
        name: 日志器名称

    Returns:
        日志器实例
    """
    return _logger_manager.get_logger(name)


def initialize_logging(
    name: str = 'agent',
    level: str = 'INFO',
    log_dir: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """
    初始化日志系统（便捷函数）

    Args:
        name: 日志器名称
        level: 日志级别
        log_dir: 日志文件目录
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出

    Returns:
        日志器实例
    """
    return _logger_manager.initialize(
        name=name,
        level=level,
        log_dir=log_dir,
        enable_console=enable_console,
        enable_file=enable_file
    )


def set_log_level(level: str, name: str = 'agent'):
    """
    设置日志级别（便捷函数）

    Args:
        level: 日志级别
        name: 日志器名称
    """
    _logger_manager.set_level(level, name)


# 便捷的日志函数（使用默认日志器）
def debug(message: str, name: str = 'agent'):
    """输出 DEBUG 级别日志"""
    get_logger(name).debug(message)


def info(message: str, name: str = 'agent'):
    """输出 INFO 级别日志"""
    get_logger(name).info(message)


def warning(message: str, name: str = 'agent'):
    """输出 WARNING 级别日志"""
    get_logger(name).warning(message)


def error(message: str, name: str = 'agent', exc_info: bool = False):
    """输出 ERROR 级别日志"""
    get_logger(name).error(message, exc_info=exc_info)


def critical(message: str, name: str = 'agent', exc_info: bool = False):
    """输出 CRITICAL 级别日志"""
    get_logger(name).critical(message, exc_info=exc_info)
