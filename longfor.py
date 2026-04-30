import os
import requests
from dotenv import load_dotenv


load_dotenv()


def get_user_info(token: str) -> dict:
    """
    查询用户信息
    返回: {"growth": 积分, "level": 等级, "next_growth": 下一级所需积分}
    """
    url = "https://gw2c-hw-open.longfor.com/supera/member/api/bff/pages/v1_25_0/v1/user-info"
    headers = {
        "X-Gaia-Api-Key": "98717e7a-a039-46af-8143-be7558a089c0",
        "lmToken": token,
        "X-LF-Bucode": "C20400",
        "X-LF-Api-Version": "v1_25_0",
        "X-LF-Channel": "C2",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254162e) XWEB/18163",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        user_data = data.get("data", {})
        return {
            "growth": int(user_data.get("growthValue", 0)),
            "level": user_data.get("levelName", ""),
            "next_growth": int(user_data.get("nextLevelGrowthValue", 0)),
        }
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return {"growth": 0, "level": "", "next_growth": 0}


def longfor_sign_single(token: str, dxrisk_token: str, max_retry: int = 2):
    """
    执行单个token的龙湖天街每日签到
    
    Args:
        token: 用户token
        dxrisk_token: 风控token
        max_retry: 遇到验证码时的最大重试次数
    """
    url = "https://gw2c-hw-open.longfor.com/lmarketing-task-api-mvc-prod/openapi/task/v1/signature/clock"
    activity_no = "11111111111686241863606037740000"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://longzhu.longfor.com",
        "Referer": "https://longzhu.longfor.com/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS "
                      "18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.67(0x18004330) NetType/WIFI Language/en miniProgram/wx50282644351869da",
        "token": token,
        "X-LF-UserToken": token,
        "X-GAIA-API-KEY": "c06753f1-3e68-437d-b592-b94656ea5517",
        "X-LF-Bu-Code": "C20400",
        "X-LF-Channel": "C2",
        "X-LF-DXRisk-Source": "5",
        "X-LF-DXRisk-Token": dxrisk_token,
    }

    json_data = {
        "activity_no": activity_no
    }

    for attempt in range(max_retry):
        resp = requests.post(url, headers=headers, json=json_data, timeout=10)
        print(f"status: {resp.status_code}")
        print(f"body: {resp.text}")

        try:
            data = resp.json()
        except Exception:
            return False, "返回不是 JSON"

        # 签到成功
        if data.get("code") == "0000":
            reward_info = data.get("data", {}).get("reward_info", [])
            msg = f"【龙湖天街】签到成功: {reward_info or '无（可能当日已签到）'}"
            return True, msg
        
        # 检查是否需要验证码
        error_code = data.get("code")
        error_msg = data.get("message", "")
        
        # 可能触发验证码的错误码（根据实际情况调整）
        needs_captcha = (
            error_code == "8040012" or  # 网络故障，请稍后再试 (触发验证码)
            error_code == "8040016" or  # 也可能是这个
            "验证" in error_msg or
            "滑块" in error_msg or
            "人机" in error_msg
        )
        
        if needs_captcha:
            print(f"\n⚠️  检测到需要验证码，尝试自动处理... (尝试 {attempt + 1}/{max_retry})")
            
            try:
                # 导入验证码处理器
                from captcha_handler import CaptchaHandler
                
                handler = CaptchaHandler(token, dxrisk_token)
                captcha_token = handler.handle_captcha_if_needed()
                
                if captcha_token:
                    # 验证码通过，更新请求头
                    print(f"✓ 验证码处理成功，获得token: {captcha_token[:20]}...")
                    headers["X-LF-DXRisk-Captcha-Token"] = captcha_token
                    headers["X-LF-DXRisk-Source"] = "5"
                    
                    # 立即使用新token重新发送签到请求
                    print(f"\n📤 使用验证码token重新发送签到请求...")
                    resp = requests.post(url, headers=headers, json=json_data, timeout=10)
                    print(f"status: {resp.status_code}")
                    print(f"body: {resp.text}")
                    
                    try:
                        data = resp.json()
                        if data.get("code") == "0000":
                            reward_info = data.get("data", {}).get("reward_info", [])
                            msg = f"【龙湖天街】签到成功: {reward_info or '无（可能当日已签到）'}"
                            return True, msg
                        else:
                            # 即使有验证码token，签到仍然失败
                            print(f"✗ 使用验证码token签到仍失败: {data}")
                            if attempt < max_retry - 1:
                                print(f"  将在下一次循环中重试...")
                                continue
                            return False, f"【龙湖天街】签到失败（已通过验证码）: {data.get('message', data)}"
                    except Exception as e:
                        print(f"✗ 解析响应失败: {e}")
                        if attempt < max_retry - 1:
                            continue
                        return False, f"【龙湖天街】响应解析失败: {str(e)}"
                else:
                    print(f"✗ 验证码处理失败")
                    # 如果不是最后一次尝试，继续重试
                    if attempt < max_retry - 1:
                        print(f"  将在下一次循环中重试...")
                        continue
                    # 最后一次尝试失败，返回错误
                    return False, f"【龙湖天街】验证码处理失败，已重试{max_retry}次"
                    
            except ImportError:
                print("✗ 验证码处理模块未安装，请先实现 captcha_handler.py")
                return False, f"【龙湖天街】需要验证码，但自动处理失败: {data}"
            except Exception as e:
                print(f"✗ 验证码处理出错: {e}")
                # 如果不是最后一次尝试，继续重试
                if attempt < max_retry - 1:
                    print(f"  将在下一次循环中重试...")
                    continue
                # 最后一次尝试失败，返回错误
                return False, f"【龙湖天街】验证码处理异常: {str(e)}"
        
        # 其他错误（不需要验证码的情况），直接返回失败
        return False, f"【龙湖天街】签到失败: {data}"
    
    return False, f"【龙湖天街】签到失败，已重试{max_retry}次"


def longfor_sign():
    """
    执行龙湖天街每日签到（支持多个token，换行分隔）
    """
    token_str = os.environ.get("LONGFOR_TOKEN", "").strip()
    dxrisk_token_str = os.environ.get("LONGFOR_DXRISK_TOKEN", "").strip()
    
    if not token_str:
        return False, "未配置 LONGFOR_TOKEN"
    
    # 按换行符分割token，过滤空行
    tokens = [t.strip() for t in token_str.split("\n") if t.strip()]
    dxrisk_tokens = [t.strip() for t in dxrisk_token_str.split("\n") if t.strip()] if dxrisk_token_str else []
    
    if not tokens:
        return False, "LONGFOR_TOKEN 为空"
    
    # 如果只有一个token，保持向后兼容
    if len(tokens) == 1:
        dxrisk_token = dxrisk_tokens[0] if dxrisk_tokens else ""
        success, msg = longfor_sign_single(tokens[0], dxrisk_token)
        user_info = get_user_info(tokens[0])
        return success, msg, 1 if success else 0, 1, user_info

    # 多个token的情况
    results = []
    success_count = 0
    total_count = len(tokens)
    total_growth = 0
    
    for i, token in enumerate(tokens):
        # 获取对应的dxrisk_token，如果没有足够的则使用第一个或空字符串
        dxrisk_token = dxrisk_tokens[i] if i < len(dxrisk_tokens) else (dxrisk_tokens[0] if dxrisk_tokens else "")

        print(f"\n处理第 {i+1}/{len(tokens)} 个账号...")
        success, msg = longfor_sign_single(token, dxrisk_token)
        user_info = get_user_info(token)
        results.append(f"账号{i+1}: {msg}\n等级: {user_info['level']}  积分: {user_info['growth']}  距下一级还需: {user_info['next_growth']}")

        if success:
            success_count += 1
    
    combined_msg = "\n".join(results)
    all_success = (success_count == total_count)
    return all_success, combined_msg, success_count, total_count


if __name__ == "__main__":
    ok, msg = longfor_sign()
    print(ok, msg)