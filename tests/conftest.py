"""
Pytest 配置文件
在测试开始前加载 .env 文件
"""
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 加载 .env 文件
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"✓ 已加载 .env 文件: {dotenv_path}")
else:
    print(f"✗ .env 文件不存在: {dotenv_path}")


def pytest_configure(config):
    """Pytest 配置钩子"""
    # 可以在这里添加更多的测试配置
    pass
