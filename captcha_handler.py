"""
龙湖天街滑块验证码处理模块
"""
import requests
import time
import random
import hashlib
import os
import shutil
from datetime import datetime
from typing import Optional, Dict, Tuple
from image_recognition_v2 import find_gap_position, download_images
from trajectory_enhanced import generate_realistic_trajectory
from ac_encoder_full import generate_ac

# 是否保存验证码图片用于分析（通过环境变量控制）
SAVE_CAPTCHA_IMAGES = os.getenv('SAVE_CAPTCHA_IMAGES', 'false').lower() == 'true'
CAPTCHA_IMAGES_DIR = 'captcha_collection'


class CaptchaHandler:
    """验证码处理器"""
    
    def __init__(self, token: str, dxrisk_token: str):
        self.token = token
        self.dxrisk_token = dxrisk_token
        self.session = requests.Session()
        
        # 基础配置
        self.app_id = "d1a43734fc59aeae9f1562dbd70fdf54"  # 从你的抓包中获取
        self.api_base = "https://ly-ver.longhu.net/api"
        self.uv_check_url = "https://devops-prod.longfor.com/v2/api/uv/type"
    
    def _save_captcha_images(self, bg_path: str, slider_path: str, result: dict = None):
        """
        保存验证码图片用于后续分析
        
        Args:
            bg_path: 背景图路径（还原后的）
            slider_path: 滑块图路径
            result: 验证结果（包含 x, y 坐标等信息）
        """
        if not SAVE_CAPTCHA_IMAGES:
            return
        
        try:
            # 创建保存目录
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_dir = os.path.join(CAPTCHA_IMAGES_DIR, timestamp)
            os.makedirs(save_dir, exist_ok=True)
            
            # 复制背景图
            if os.path.exists(bg_path):
                shutil.copy(bg_path, os.path.join(save_dir, 'bg_restored.png'))
            
            # 复制滑块图
            if os.path.exists(slider_path):
                shutil.copy(slider_path, os.path.join(save_dir, 'slider.png'))
            
            # 保存识别结果信息
            if result:
                info_path = os.path.join(save_dir, 'info.txt')
                with open(info_path, 'w', encoding='utf-8') as f:
                    f.write(f"时间: {timestamp}\n")
                    f.write(f"X 坐标: {result.get('x', 'N/A')}\n")
                    f.write(f"Y 坐标: {result.get('y', 'N/A')}\n")
                    f.write(f"验证结果: {result.get('success', 'N/A')}\n")
                    f.write(f"错误信息: {result.get('msg', 'N/A')}\n")
            
            print(f"   📦 验证码图片已保存: {save_dir}")
        
        except Exception as e:
            print(f"   ⚠️  保存验证码图片失败: {e}")
        
    def _generate_aid(self) -> str:
        """生成aid (设备指纹)"""
        timestamp = int(time.time() * 1000)
        random_num = random.randint(10000000, 99999999)
        return f"dx-{timestamp}-{random_num}-1"
    
    def check_uv_type(self) -> Optional[str]:
        """
        检查需要什么类型的验证
        
        Returns:
            验证类型: "c" = captcha滑块验证, None = 不需要验证
        """
        try:
            params = {
                'appId': 'LdIPdF3earg'  # 从你的抓包中获取的appId
            }
            
            response = self.session.get(
                self.uv_check_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == '200':
                    uv_type = data.get('data')
                    print(f"✓ UV类型检查: {uv_type}")
                    return uv_type
                else:
                    print(f"✗ UV类型检查失败: {data}")
                    return None
            else:
                print(f"✗ UV类型检查HTTP错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ UV类型检查异常: {e}")
            return None
    
    def init_captcha(self) -> Optional[Dict]:
        """
        初始化验证码，获取challenge等参数
        
        Returns:
            验证码初始化数据，包含sid, challenge, 图片URL等
        """
        aid = self._generate_aid()
        
        # 生成challenge参数（根据JS代码，这是一个随机生成的标识）
        challenge = self._generate_challenge()
        
        params = {
            'w': 300,          # 宽度
            'h': 150,          # 高度  
            's': 50,           # 滑块尺寸
            'ak': self.app_id,
            'c': challenge,    # challenge参数
            'jsv': '1.3.41.372',
            'aid': aid,
            'wp': 1,           # webp支持
            'de': 0,
            'uid': '',
            'lf': 0,
            'tpc': '',
            '_r': random.random()
        }
        
        try:
            response = self.session.get(
                f"{self.api_base}/a",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 保存返回的参数
                if data.get('success') and data.get('result') == 1:
                    # p1和p2是相对路径，需要拼接完整URL
                    p1_path = data.get('p1', '')
                    p2_path = data.get('p2', '')
                    
                    captcha_data = {
                        'sid': data.get('sid'),
                        'challenge': challenge,  # 使用请求时的challenge
                        'bg_url': f"https://ly-ver.longhu.net{p1_path}",
                        'slider_url': f"https://ly-ver.longhu.net{p2_path}",
                        'aid': aid,
                        'ak': self.app_id,
                        'y': data.get('y', 0),  # 服务端返回的y坐标
                        'o': data.get('o', None)  # 切片顺序数组（用于还原背景图）
                    }
                    
                    print(f"✓ 验证码初始化成功")
                    print(f"  - SID: {captcha_data['sid']}")
                    print(f"  - Challenge: {captcha_data['challenge']}")
                    print(f"  - Y坐标: {captcha_data['y']}")
                    
                    return captcha_data
                else:
                    print(f"✗ 验证码初始化失败: {data}")
                    return None
                    
        except Exception as e:
            print(f"✗ 初始化验证码出错: {e}")
            return None
    
    def _generate_challenge(self) -> str:
        """
        生成challenge参数
        根据JS代码分析，这是一个随机字符串
        """
        # 生成类似 "696f23b1pMDxzP4CVdYjSMMZzplPiY3z5Yvs4Xy1" 的字符串
        import string
        chars = string.ascii_letters + string.digits
        random_part = ''.join(random.choices(chars, k=32))
        
        # 添加一个固定前缀（8位十六进制）
        prefix = format(random.randint(0, 0xFFFFFFFF), '08x')
        
        return f"{prefix}{random_part}"
    
    def solve_captcha(self, captcha_data: Dict) -> Optional[str]:
        """
        识别并通过验证码
        
        Args:
            captcha_data: 从init_captcha获取的数据
            
        Returns:
            验证成功的token
        """
        print("\n" + "="*50)
        print("开始处理滑块验证码")
        print("="*50)
        
        # 1. 下载图片
        print("1️⃣ 正在下载验证码图片...")
        try:
            bg_path, slider_path = download_images(
                captcha_data['bg_url'],
                captcha_data['slider_url']
            )
            print("   ✓ 图片下载成功")
        except Exception as e:
            print(f"   ✗ 图片下载失败: {e}")
            return None
        
        # 2. 还原背景图（如果有切片顺序）
        o_value = captcha_data.get('o')
        if o_value:
            print("2️⃣ 正在还原背景图...")
            try:
                from restore_correct import restore_image_correct
                from decode_o_string import decode_o_string
                
                # 解码 o 字符串为顺序数组
                if isinstance(o_value, str):
                    print(f"   - o 字符串: {o_value}")
                    slice_order = decode_o_string(o_value)
                    print(f"   - 解码为数组: {slice_order[:10]}... (前10个)")
                elif isinstance(o_value, list):
                    # 如果直接是数组（某些情况下）
                    slice_order = o_value
                else:
                    print(f"   ⚠️  未知的 o 类型: {type(o_value)}")
                    slice_order = []
                
                if slice_order and len(slice_order) > 0:
                    # 根据图片宽度自动计算切片宽度
                    from PIL import Image
                    img = Image.open(bg_path)
                    width = img.width
                    
                    # 通常是 12px 切片，但根据实际情况调整
                    slice_width = width // len(slice_order)
                    if slice_width == 0:
                        slice_width = 12  # 默认值
                    
                    print(f"   - 切片数量: {len(slice_order)}")
                    print(f"   - 切片宽度: {slice_width}px")
                    
                    # 还原图片
                    restored_path = restore_image_correct(
                        bg_path,
                        slice_order,
                        slice_width,
                        debug=False  # 不输出详细调试信息
                    )
                    
                    # 使用还原后的图片
                    bg_path = restored_path
                    print(f"   ✓ 背景图还原成功: {restored_path}")
                else:
                    print(f"   ⚠️  解码后的数组为空")
                
            except Exception as e:
                print(f"   ⚠️  背景图还原失败，使用原图: {e}")
                if DEBUG_MODE:
                    import traceback
                    traceback.print_exc()
                # 继续使用原图，不中断流程
        else:
            print("2️⃣ 跳过背景图还原（无切片顺序信息）")
        
        # 3. 识别缺口位置（只需要识别 x 坐标，y 由服务端提供）
        print("3️⃣ 正在识别缺口位置...")
        try:
            x, y_detected = find_gap_position(bg_path, slider_path)
            
            # 使用服务端返回的 y 坐标，而不是识别出的 y
            y = captcha_data.get('y', y_detected)
            
            print(f"   ✓ 识别成功: x={x}")
            print(f"   - 服务端y坐标: {captcha_data.get('y')}")
            print(f"   - 识别出的y: {y_detected}")
            print(f"   - 使用y坐标: {y}")
        except Exception as e:
            print(f"   ✗ 识别失败: {e}")
            return None
        
        # 4. 生成轨迹（使用增强版）
        print("4️⃣ 正在生成滑动轨迹...")
        try:
            trajectory = generate_realistic_trajectory(x)
            duration_ms = trajectory[-1][2] - trajectory[0][2]
            print(f"   ✓ 生成 {len(trajectory)} 个轨迹点")
            print(f"   ✓ 总时长: {duration_ms}ms")
        except Exception as e:
            print(f"   ✗ 轨迹生成失败: {e}")
            return None
        
        # 5. 编码ac参数
        print("5️⃣ 正在编码轨迹数据...")
        try:
            final_x = trajectory[-1][0]
            final_y = y + trajectory[-1][1]  # 服务端 y + 轨迹 y 偏移
            
            # 使用新的 AC 编码器
            ac = generate_ac(trajectory, final_x, final_y, sid=captcha_data['sid'])
            print(f"   ✓ AC参数长度: {len(ac)}")
            print(f"   ✓ AC前缀: {ac[:10]}")
        except Exception as e:
            print(f"   ✗ 编码失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # 6. 提交验证
        print("6️⃣ 正在提交验证...")
        try:
            
            print(f"   - 最终坐标: x={final_x}, y={final_y}")
            print(f"   - 轨迹点数: {len(trajectory)}")
            
            data = {
                'ac': ac,
                'ak': captcha_data['ak'],
                'c': captcha_data['challenge'],
                'uid': '',
                'jsv': '1.3.41.372',
                'sid': captcha_data['sid'],
                'aid': captcha_data['aid'],
                'x': final_x,
                'y': final_y
            }
            
            response = self.session.post(
                f"{self.api_base}/v1",
                data=data,
                timeout=10
            )
            
            result = response.json()
            print(f"   验证响应: {result}")
            
            # 保存验证码图片（如果启用）
            self._save_captcha_images(
                bg_path, 
                slider_path, 
                {
                    'x': final_x, 
                    'y': final_y, 
                    'success': result.get('success'),
                    'msg': result.get('msg')
                }
            )
            
            if result.get('success'):
                token = result.get('token')
                print(f"   ✓ 验证成功! Token: {token}")
                return token
            else:
                print(f"   ✗ 验证失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            print(f"   ✗ 提交验证出错: {e}")
            return None
    
    def handle_captcha_if_needed(self) -> Optional[str]:
        """
        完整的验证码处理流程
        当签到接口返回需要验证时调用 (错误码 8040012)
        
        Returns:
            验证码token，失败返回None
        """
        # 1. 检查验证类型
        print("\n" + "="*50)
        print("开始验证码处理流程")
        print("="*50)
        
        uv_type = self.check_uv_type()
        
        # 如果不是滑块验证，直接返回
        if uv_type != 'c':
            print(f"⚠️  当前验证类型: {uv_type} (非滑块验证)")
            return None
        
        print("✓ 确认需要滑块验证")
        
        # 2. 初始化验证码
        captcha_data = self.init_captcha()
        if not captcha_data:
            return None
        
        # 3. 识别并通过验证
        token = self.solve_captcha(captcha_data)
        
        return token


def test_captcha_handler():
    """测试验证码处理"""
    # 使用你的token进行测试
    handler = CaptchaHandler(
        token="your_longfor_token",
        dxrisk_token="your_dxrisk_token"
    )
    
    result = handler.handle_captcha_if_needed()
    print(f"\n最终结果: {result}")


if __name__ == "__main__":
    test_captcha_handler()
