#!/usr/bin/env python3
"""
验证码参数计算工具
用于本地测试：从还原好的背景图和滑块图计算 x, y, ac 参数
"""

import sys
import os
from image_recognition_v2 import find_gap_position
from trajectory import generate_trajectory, add_shake_at_end
from ac_encoder_full import generate_ac

def calculate_captcha_params(bg_image_path: str, slider_image_path: str, server_y: int = None, debug: bool = True):
    """
    计算验证码参数
    
    Args:
        bg_image_path: 还原后的背景图路径
        slider_image_path: 滑块图路径 (p2)
        server_y: 服务端返回的 y 坐标（如果有）
        debug: 是否显示详细信息
        
    Returns:
        dict: {'x': int, 'y': int, 'ac': str, 'trajectory': list}
    """
    if debug:
        print("="*60)
        print("🧮 验证码参数计算工具")
        print("="*60)
    
    # 1. 检查文件是否存在
    if not os.path.exists(bg_image_path):
        print(f"❌ 背景图不存在: {bg_image_path}")
        return None
    
    if not os.path.exists(slider_image_path):
        print(f"❌ 滑块图不存在: {slider_image_path}")
        return None
    
    if debug:
        print(f"📁 背景图: {bg_image_path}")
        print(f"📁 滑块图: {slider_image_path}")
    
    # 2. 识别缺口位置
    if debug:
        print(f"\n1️⃣ 正在识别缺口位置...")
    
    try:
        x_detected, y_detected = find_gap_position(bg_image_path, slider_image_path, debug=debug)
        
        # 使用服务端 y 或识别的 y
        if server_y is not None:
            y = server_y
            if debug:
                print(f"   ✓ 识别完成: x={x_detected}, y_detected={y_detected}")
                print(f"   - 使用服务端 y={y}")
        else:
            y = y_detected
            if debug:
                print(f"   ✓ 识别完成: x={x_detected}, y={y}")
        
        x = x_detected
        
    except Exception as e:
        print(f"   ❌ 识别失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 3. 生成轨迹
    if debug:
        print(f"\n2️⃣ 正在生成滑动轨迹...")
    
    try:
        trajectory = generate_trajectory(x)
        trajectory = add_shake_at_end(trajectory)
        
        if debug:
            print(f"   ✓ 生成 {len(trajectory)} 个轨迹点")
            print(f"   - 前5个点: {trajectory[:5]}")
            print(f"   - 后5个点: {trajectory[-5:]}")
        
    except Exception as e:
        print(f"   ❌ 轨迹生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 4. 计算最终坐标
    final_x = trajectory[-1][0]
    final_y = y + trajectory[-1][1]
    
    # 5. 编码 ac 参数
    if debug:
        print(f"\n3️⃣ 正在编码 ac 参数...")
    
    try:
        # 使用新的 AC 编码器
        ac = generate_ac(trajectory, final_x, final_y, sid="")
        
        if debug:
            print(f"   ✓ AC 参数长度: {len(ac)}")
            print(f"   - AC 前50字符: {ac[:50]}...")
        
    except Exception as e:
        print(f"   ❌ 编码失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    result = {
        'x': final_x,
        'y': final_y,
        'x_detected': x,
        'y_detected': y_detected,
        'y_server': server_y,
        'ac': ac,
        'trajectory': trajectory,
        'trajectory_count': len(trajectory)
    }
    
    # 6. 输出结果
    if debug:
        print(f"\n" + "="*60)
        print(f"✅ 计算完成!")
        print(f"="*60)
        print(f"\n📊 识别结果:")
        print(f"   - x 坐标（识别）: {x}")
        print(f"   - y 坐标（识别）: {y_detected}")
        if server_y is not None:
            print(f"   - y 坐标（服务端）: {server_y}")
            print(f"   - y 坐标（使用）: {y}")
        
        print(f"\n📊 最终参数:")
        print(f"   - x: {final_x}")
        print(f"   - y: {final_y}")
        print(f"   - ac: {ac[:100]}...")
        print(f"   - 轨迹点数: {len(trajectory)}")
        
        print(f"\n💡 提交验证时使用:")
        print(f"   data = {{")
        print(f"       'x': {final_x},")
        print(f"       'y': {final_y},")
        print(f"       'ac': '{ac[:50]}...',")
        print(f"       'sid': '<从 API 获取>',")
        print(f"       'ak': '<app_id>',")
        print(f"       'c': '<challenge>',")
        print(f"       'aid': '<aid>',")
        print(f"       'uid': '',")
        print(f"       'jsv': '1.3.41.372'")
        print(f"   }}")
        print(f"\n" + "="*60)
    
    return result

def interactive_mode():
    """交互式模式"""
    print("\n" + "="*60)
    print("🎨 交互式参数计算")
    print("="*60)
    
    # 1. 获取背景图路径
    print("\n请输入还原后的背景图路径:")
    print("  提示: 可以拖拽图片到终端")
    bg_path = input("背景图: ").strip().strip('"').strip("'")
    
    if not bg_path:
        print("❌ 未输入背景图路径")
        return
    
    # 2. 获取滑块图路径
    print("\n请输入滑块图路径 (p2):")
    slider_path = input("滑块图: ").strip().strip('"').strip("'")
    
    if not slider_path:
        print("❌ 未输入滑块图路径")
        return
    
    # 3. 是否有服务端 y 坐标
    print("\n是否有服务端返回的 y 坐标？(可选)")
    print("  如果有，请输入；如果没有，直接回车")
    server_y_str = input("y 坐标: ").strip()
    
    server_y = None
    if server_y_str:
        try:
            server_y = int(server_y_str)
        except:
            print("⚠️  无效的 y 值，将使用识别的 y")
    
    # 4. 执行计算
    result = calculate_captcha_params(bg_path, slider_path, server_y, debug=True)
    
    if result:
        # 5. 是否保存结果
        print("\n是否保存结果到文件？(y/n)")
        save = input("保存: ").strip().lower()
        
        if save == 'y':
            import json
            output_file = "captcha_params.json"
            with open(output_file, 'w') as f:
                # 简化 trajectory 输出
                save_data = {
                    'x': result['x'],
                    'y': result['y'],
                    'ac': result['ac'],
                    'x_detected': result['x_detected'],
                    'y_detected': result['y_detected'],
                    'y_server': result['y_server'],
                    'trajectory_count': result['trajectory_count']
                }
                json.dump(save_data, f, indent=2)
            print(f"✓ 已保存到: {output_file}")

def main():
    """主函数"""
    if len(sys.argv) == 1:
        # 无参数：交互式模式
        interactive_mode()
    
    elif len(sys.argv) == 3:
        # 两个参数：背景图 + 滑块图
        bg_path = sys.argv[1]
        slider_path = sys.argv[2]
        calculate_captcha_params(bg_path, slider_path, debug=True)
    
    elif len(sys.argv) == 4:
        # 三个参数：背景图 + 滑块图 + y坐标
        bg_path = sys.argv[1]
        slider_path = sys.argv[2]
        try:
            server_y = int(sys.argv[3])
        except:
            print("❌ 无效的 y 值")
            return
        calculate_captcha_params(bg_path, slider_path, server_y, debug=True)
    
    elif len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']:
        # 帮助信息
        print("""
╔════════════════════════════════════════════════════════════╗
║  🧮 验证码参数计算工具 - 使用说明                          ║
╚════════════════════════════════════════════════════════════╝

用法1：交互式模式（推荐）
────────────────────────────────────────────────────────────
  python3 calculate_captcha_params.py
  
  按照提示输入背景图和滑块图路径

用法2：命令行模式
────────────────────────────────────────────────────────────
  # 只有图片（自动识别 y）
  python3 calculate_captcha_params.py <背景图> <滑块图>
  
  # 指定服务端 y 坐标
  python3 calculate_captcha_params.py <背景图> <滑块图> <y坐标>
  
  示例：
    python3 calculate_captcha_params.py bg_restored.png slider.png
    python3 calculate_captcha_params.py bg_restored.png slider.png 80

用法3：Python 代码调用
────────────────────────────────────────────────────────────
  from calculate_captcha_params import calculate_captcha_params
  
  result = calculate_captcha_params('bg.png', 'slider.png', server_y=80)
  print(f"x={result['x']}, y={result['y']}, ac={result['ac']}")

完整流程：
────────────────────────────────────────────────────────────
1. 从 API 获取验证码信息（o 字符串、图片 URL、y 坐标等）
2. 下载背景图和滑块图
3. 使用 restore_local.py 还原背景图
4. 使用本工具计算 x, y, ac 参数
5. 提交验证到 /api/v1

输出说明：
────────────────────────────────────────────────────────────
- x: 最终 x 坐标（带轨迹）
- y: 最终 y 坐标（带轨迹）
- ac: Base64 编码的轨迹数据
- x_detected: 识别出的原始 x 坐标
- y_detected: 识别出的原始 y 坐标
- trajectory: 完整的轨迹点列表
        """)
    
    else:
        print("❌ 参数错误")
        print("使用 'python3 calculate_captcha_params.py --help' 查看帮助")

if __name__ == "__main__":
    main()
