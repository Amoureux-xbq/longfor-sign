#!/usr/bin/env python3
"""
根据顶象算法逆向还原图片
基于发现的 JavaScript 还原逻辑
"""

from PIL import Image
import os
import json

def create_inverse_mapping(slice_order):
    """
    创建逆映射数组
    
    如果原数组是 [2, 5, 3, ...]，表示：
    - 位置 0 的切片来自位置 2
    - 位置 1 的切片来自位置 5
    - 位置 2 的切片来自位置 3
    
    逆映射就是反过来：
    - 位置 2 的切片现在在位置 0
    - 位置 5 的切片现在在位置 1
    - 位置 3 的切片现在在位置 2
    
    Args:
        slice_order: 打乱后的顺序数组
        
    Returns:
        逆映射数组
    """
    max_index = max(slice_order)
    inverse = [0] * (max_index + 1)
    
    for dest_index, src_index in enumerate(slice_order):
        inverse[src_index] = dest_index
    
    return inverse

def restore_image_correct(
    image_path: str,
    slice_order: list,
    slice_width: int = 12,
    debug: bool = True
):
    """
    使用正确的逆映射还原图片
    
    Args:
        image_path: 打乱的图片路径
        slice_order: API返回的切片顺序数组
        slice_width: 切片宽度（默认12px）
        debug: 是否输出调试信息
    """
    if debug:
        print("="*60)
        print("🔧 图片还原配置")
        print("="*60)
        print(f"📁 图片路径: {image_path}")
        print(f"📏 切片宽度: {slice_width}px")
        print(f"📦 切片数组: {slice_order[:10]}... (前10个)")
        print(f"📊 数组长度: {len(slice_order)}")
        print(f"📈 数组范围: 0-{max(slice_order)}")
    
    # 打开图片
    img = Image.open(image_path)
    width, height = img.size
    
    if debug:
        print(f"📐 图片尺寸: {width}×{height}")
    
    # 创建逆映射
    inverse_order = create_inverse_mapping(slice_order)
    
    if debug:
        print(f"\n🔄 逆映射数组: {inverse_order[:10]}... (前10个)")
        print(f"\n📝 映射关系示例:")
        for i in range(min(5, len(slice_order))):
            src = slice_order[i]
            dest = i
            print(f"   打乱: 位置 {dest} ← 位置 {src} (从 {src*slice_width}px)")
        
        print(f"\n📝 还原关系示例:")
        for i in range(min(5, len(inverse_order))):
            dest = inverse_order[i]
            src = i
            print(f"   还原: 位置 {src} → 位置 {dest} (到 {dest*slice_width}px)")
    
    # 创建新图片
    restored = Image.new('RGB', (width, height))
    
    # 计算主要还原区域
    main_width = len(inverse_order) * slice_width
    
    if debug:
        print(f"\n✂️ 还原区域: 0 到 {main_width}px")
    
    # 还原：对于原图的每个位置 i，找到它应该放在哪里（inverse[i]）
    for src_index in range(len(inverse_order)):
        dest_index = inverse_order[src_index]
        
        # 从打乱的图片中取切片
        src_x = src_index * slice_width
        src_box = (src_x, 0, src_x + slice_width, height)
        slice_img = img.crop(src_box)
        
        # 放到还原图片的正确位置
        dest_x = dest_index * slice_width
        restored.paste(slice_img, (dest_x, 0))
        
        if debug and src_index < 3:
            print(f"   切片 {src_index}: {src_x}px → {dest_x}px")
    
    # 处理剩余部分（如果有）
    if main_width < width:
        remaining_width = width - main_width
        if debug:
            print(f"\n📌 处理剩余部分: {main_width} 到 {width}px (宽{remaining_width}px)")
        
        # 直接复制剩余部分
        remaining_box = (main_width, 0, width, height)
        remaining_slice = img.crop(remaining_box)
        restored.paste(remaining_slice, (main_width, 0))
    
    # 保存
    base, ext = os.path.splitext(image_path)
    output_path = f"{base}_restored_correct{ext}"
    restored.save(output_path)
    
    if debug:
        print(f"\n💾 已保存: {output_path}")
        print("="*60)
    
    return output_path

def test_with_dingxiang_order():
    """使用顶象官网的顺序测试"""
    ORDER_32 = [
        2, 5, 3, 22, 21, 24, 18, 23, 25, 26, 6, 27, 20, 4, 19, 7, 
        8, 1, 9, 28, 29, 30, 31, 10, 0, 16, 11, 17, 12, 13, 14, 15
    ]
    
    print("🧪 使用顶象官网的32位顺序数组测试\n")
    
    try:
        output = restore_image_correct(
            "bg_temp.png",
            ORDER_32,
            slice_width=12,
            debug=True
        )
        print(f"\n✅ 测试完成！查看文件: {output}")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def restore_from_api_response(image_path: str, api_response: dict):
    """
    从 API 响应中提取顺序并还原
    
    Args:
        image_path: 图片路径
        api_response: /api/a 的响应数据
    """
    # 查找可能的字段
    possible_keys = ['order', 'o', 'seq', 'blocks', 'slice', 'serialize']
    
    slice_order = None
    for key in possible_keys:
        if key in api_response:
            slice_order = api_response[key]
            print(f"✓ 在字段 '{key}' 中找到顺序数组")
            break
    
    if not slice_order:
        print("❌ 未在 API 响应中找到顺序数组")
        print("可用字段:", list(api_response.keys()))
        return None
    
    # 还原图片
    return restore_image_correct(image_path, slice_order)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 从命令行传入顺序数组
        order_json = sys.argv[1]
        try:
            order = json.loads(order_json)
            restore_image_correct("bg_temp.png", order)
        except Exception as e:
            print(f"解析失败: {e}")
    else:
        # 使用顶象官网的测试数据
        test_with_dingxiang_order()
