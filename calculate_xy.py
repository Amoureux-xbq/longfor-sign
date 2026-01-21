#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙湖验证码 X/Y 坐标计算工具

用法:
    python calculate_xy.py <背景图路径> <滑块图路径> [方法]
    
参数:
    背景图路径: 背景图片的路径（需要先还原）
    滑块图路径: 滑块图片的路径
    方法: 识别方法 (可选，默认为 shape)
          - auto: 自动选择最佳方法
          - shape: 形状匹配（推荐）
          - contour: 轮廓检测
          - color: 颜色差异

示例:
    python calculate_xy.py bg.jpg slider.png
    python calculate_xy.py bg.jpg slider.png shape
    python calculate_xy.py bg.jpg slider.png auto
"""

import sys
import os
from image_recognition_v2 import find_gap_position


def print_usage():
    """打印使用说明"""
    print(__doc__)


def calculate_xy(bg_path: str, slider_path: str, method: str = "shape"):
    """
    计算滑块验证码的 x 和 y 坐标
    
    Args:
        bg_path: 背景图路径
        slider_path: 滑块图路径
        method: 识别方法 (auto/shape/contour/color)
    
    Returns:
        tuple: (x, y) 坐标
    """
    # 验证文件是否存在
    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"❌ 背景图不存在: {bg_path}")
    
    if not os.path.exists(slider_path):
        raise FileNotFoundError(f"❌ 滑块图不存在: {slider_path}")
    
    print("="*60)
    print("🔍 龙湖验证码坐标计算")
    print("="*60)
    print(f"📁 背景图: {bg_path}")
    print(f"📁 滑块图: {slider_path}")
    print(f"🔧 识别方法: {method}")
    print("="*60)
    
    # 调用图像识别
    x, y = find_gap_position(
        bg_image_path=bg_path,
        slider_image_path=slider_path,
        debug=True,
        method=method
    )
    
    print("="*60)
    print("✅ 计算完成")
    print("="*60)
    print(f"📊 结果:")
    print(f"   x = {x} (滑动距离)")
    print(f"   y = {y} (垂直位置)")
    print("="*60)
    
    return x, y


def main():
    """主函数"""
    # 检查参数
    if len(sys.argv) < 3:
        print("❌ 参数不足\n")
        print_usage()
        sys.exit(1)
    
    if sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    # 获取参数
    bg_path = sys.argv[1]
    slider_path = sys.argv[2]
    method = sys.argv[3] if len(sys.argv) > 3 else "shape"
    
    # 验证方法参数
    valid_methods = ["auto", "shape", "contour", "color"]
    if method not in valid_methods:
        print(f"❌ 无效的方法: {method}")
        print(f"   有效方法: {', '.join(valid_methods)}")
        sys.exit(1)
    
    try:
        # 计算坐标
        x, y = calculate_xy(bg_path, slider_path, method)
        
        # 输出到标准输出（方便脚本调用）
        print(f"\n📋 输出格式:")
        print(f"x={x}")
        print(f"y={y}")
        print(f"x,y={x},{y}")
        
    except Exception as e:
        print(f"\n❌ 计算失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
