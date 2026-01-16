import os
import requests


def longfor_sign_single(token: str, dxrisk_token: str):
    """
    执行单个token的龙湖天街每日签到
    """
    url = "https://gw2c-hw-open.longfor.com/lmarketing-task-api-mvc-prod/openapi/task/v1/signature/clock"
    activity_no = "11111111111686241863606037740000"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://longzhu.longfor.com",
        "Referer": "https://longzhu.longfor.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.7(0x13080712) UnifiedPCMacWechat(0xf264162f) XWEB/18152 miniProgram/wx50282644351869da",
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

    resp = requests.post(url, headers=headers, json=json_data, timeout=10)
    print("status:", resp.status_code)
    print("body:", resp.text)

    try:
        data = resp.json()
    except Exception:
        return False, "返回不是 JSON"

    if data.get("code") == "0000":
        reward_info = data.get("data", {}).get("reward_info", [])
        msg = f"【龙湖天街】签到成功: {reward_info or '无（可能当日已签到）'}"
        return True, msg
    else:
        return False, f"【龙湖天街】签到失败: {data}"


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


