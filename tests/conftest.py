"""
Pytest 配置文件
在测试开始前加载 .env 文件
"""
import os
import sys
import io

# 解决 Windows 终端编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 加载 .env 文件
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"[OK] 已加载 .env 文件: {dotenv_path}")
else:
    print(f"[WARN] .env 文件不存在: {dotenv_path}")


def pytest_configure(config):
    """Pytest 配置钩子"""
    # 可以在这里添加更多的测试配置
    pass
