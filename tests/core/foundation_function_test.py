"""
Agent 基础功能测试
使用 pytest 框架测试 Agent 能否正确响应命令并执行文件操作
"""
import os
import sys
import random
import string
import time
import pytest

# 解决 Windows 终端编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.core.agent import Agent
from src.tools.file import read_file

# 测试文件路径
TEST_FILE = os.path.join(os.getcwd(), "test_foundation_temp.txt")

# 测试内容
LINE1 = "这是第一行测试文字"
LINE2 = "这是第二行测试文字"


@pytest.fixture
def agent():
    """Agent 实例 fixture"""
    print("\n正在初始化Agent...")
    agent_instance = Agent()
    print("✓ Agent 初始化成功")
    yield agent_instance
    print("\nAgent 清理完成")


@pytest.fixture(autouse=True)
def cleanup_test_file():
    """自动清理测试文件 fixture"""
    yield
    if os.path.exists(TEST_FILE):
        try:
            os.remove(TEST_FILE)
            print("✓ 测试文件已清理")
        except Exception as e:
            print(f"✗ 清理失败: {e}")


def test_agent_create_file(agent):
    """
    测试1：让 Agent 创建并写入文件
    验证：
    1. 文件是否存在
    2. 文件内容是否完全匹配，没有多余字符
    """
    print("\n=== 测试1：Agent 创建文件 ===")

    prompt = f"""请在路径 {TEST_FILE} 创建一个新文件，并写入以下两行文字，每一行后面都要有一个换行符：
{LINE1}
{LINE2}

重要要求：
1. 第一行文字后面必须有换行符
2. 第二行文字后面也必须有换行符
3. 不要添加任何额外的空行或空格
4. 文件总内容应该只有这两行文字"""

    print(f"发送命令给Agent: {prompt[:50]}...")

    response = agent.process_message(prompt)
    print(f"Agent 响应: {response[:100]}...")

    # 验证文件是否存在
    assert os.path.exists(TEST_FILE), f"文件未创建: {TEST_FILE}"
    print("✓ 文件已创建")

    # 验证文件内容
    result = read_file(TEST_FILE)
    assert result.get('success'), f"读取文件失败: {result.get('error')}"

    content = result.get('content')
    expected_content = f"{LINE1}\n{LINE2}\n"

    # 精确匹配内容，不能有多余字符
    assert content == expected_content, (
        f"文件内容不正确\n"
        f"期望内容:\n{repr(expected_content)}\n"
        f"实际内容:\n{repr(content)}"
    )
    print("✓ 文件内容完全正确")
    print("✅ 测试1通过")


def test_agent_edit_file(agent):
    """
    测试2：让 Agent 修改文件
    验证：
    1. 随机编码已插入
    2. 插入位置正确（在两行之间）
    """
    print("\n=== 测试2：Agent 修改文件 ===")

    # 先创建测试文件
    initial_content = f"{LINE1}\n{LINE2}\n"
    from src.tools.file import write_file
    write_file(TEST_FILE, initial_content)

    random_code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    print(f"生成的随机编码: {random_code}")

    prompt = f"""请在文件 {TEST_FILE} 的两行文字中间插入随机编码 {random_code}。
具体来说，在第一行和第二行之间添加这个编码。"""

    print(f"发送命令给Agent: {prompt[:60]}...")

    response = agent.process_message(prompt)
    print(f"Agent 响应: {response[:100]}...")

    # 验证文件内容
    result = read_file(TEST_FILE)
    assert result.get('success'), f"读取文件失败: {result.get('error')}"

    content = result.get('content')

    # 期望内容：第一行、随机编码、第二行
    expected_content = f"{LINE1}\n{random_code}\n{LINE2}\n"

    # 精确匹配内容和位置
    assert content == expected_content, (
        f"随机编码插入位置或内容不正确\n"
        f"期望内容:\n{repr(expected_content)}\n"
        f"实际内容:\n{repr(content)}"
    )
    print("✓ 随机编码已正确插入到两行之间")
    print("✅ 测试2通过")


def test_agent_delete_file(agent):
    """
    测试3：让 Agent 删除文件
    验证：
    1. 文件是否已被删除
    """
    print("\n=== 测试3：Agent 删除文件 ===")

    # 先创建测试文件
    initial_content = f"{LINE1}\n{LINE2}\n"
    from src.tools.file import write_file
    write_file(TEST_FILE, initial_content)

    prompt = f"""请使用 bash 命令删除文件 {TEST_FILE}"""

    print(f"发送命令给Agent: {prompt}")

    response = agent.process_message(prompt)
    print(f"Agent 响应: {response[:100]}...")

    # 短暂等待，确保文件操作完成
    time.sleep(0.5)

    # 验证文件是否已删除
    assert not os.path.exists(TEST_FILE), f"文件仍然存在: {TEST_FILE}"
    print("✓ 文件已删除")
    print("✅ 测试3通过")
