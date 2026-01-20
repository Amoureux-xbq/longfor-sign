import os
import requests


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
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.67(0x18004330) NetType/WIFI Language/en miniProgram/wx50282644351869da",
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
        
        if needs_captcha and attempt < max_retry - 1:
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
                    
                    # 继续下一次尝试
                    continue
                else:
                    print(f"✗ 验证码处理失败")
                    
            except ImportError:
                print("✗ 验证码处理模块未安装，请先实现 captcha_handler.py")
                return False, f"【龙湖天街】需要验证码，但自动处理失败: {data}"
            except Exception as e:
                print(f"✗ 验证码处理出错: {e}")
        
        # 其他错误或最后一次尝试失败
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
        return success, msg, 1 if success else 0, 1
    
    # 多个token的情况
    results = []
    success_count = 0
    total_count = len(tokens)
    
    for i, token in enumerate(tokens):
        # 获取对应的dxrisk_token，如果没有足够的则使用第一个或空字符串
        dxrisk_token = dxrisk_tokens[i] if i < len(dxrisk_tokens) else (dxrisk_tokens[0] if dxrisk_tokens else "")
        
        print(f"\n处理第 {i+1}/{len(tokens)} 个账号...")
        success, msg = longfor_sign_single(token, dxrisk_token)
        results.append(f"账号{i+1}: {msg}")
        
        if success:
            success_count += 1
    
    combined_msg = "\n".join(results)
    # 返回成功状态和详细信息（包含成功数量）
    all_success = (success_count == total_count)
    return all_success, combined_msg, success_count, total_count


if __name__ == "__main__":
    ok, msg = longfor_sign()
    print(ok, msg)


