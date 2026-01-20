#!/usr/bin/env python3
"""
解码顶象的 o 字符串为切片顺序数组
基于 Grd8 函数的逻辑
"""

def decode_o_string(o_string: str) -> list:
    """
    将 o 字符串（如 "dingxiang85b86927..."）转换为切片顺序数组
    
    算法逻辑：
    1. 遍历字符串的前32个字符
    2. 对每个字符取 ASCII 码
    3. 计算 charCode % 32
    4. 如果这个值已存在数组中，就递增 charCode 直到不重复
    5. 推入数组
    
    Args:
        o_string: API 返回的 o 字符串
        
    Returns:
        切片顺序数组（0-31的整数列表）
    """
    if not o_string:
        return []
    
    result = []
    
    for i in range(len(o_string)):
        # 只处理前32个字符
        if i == 32:
            break
        
        # 获取字符的 ASCII 码
        char_code = ord(o_string[i])
        
        # 计算 charCode % 32，如果重复就递增
        mod_value = char_code % 32
        while mod_value in result:
            char_code += 1
            mod_value = char_code % 32
        
        # 推入结果数组
        result.append(mod_value)
    
    return result

def test_decode():
    """测试解码函数"""
    # 测试用例1：顶象官网的 o 字符串
    test_cases = [
        "dingxiang85b86927da6c31ecee742bd20ee03743",
        "dingxiangabcdefg1234567890",
    ]
    
    for o_string in test_cases:
        print(f"输入字符串: {o_string}")
        result = decode_o_string(o_string)
        print(f"输出数组: {result}")
        print(f"数组长度: {len(result)}")
        print(f"数组范围: {min(result) if result else 0} ~ {max(result) if result else 0}")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 从命令行读取 o 字符串
        o_string = sys.argv[1]
        result = decode_o_string(o_string)
        print(f"解码结果: {result}")
    else:
        # 运行测试
        test_decode()
