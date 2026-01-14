import os
import requests


def longfor_sign():
    """
    执行龙湖天街每日签到
    """
    url = "https://gw2c-hw-open.longfor.com/lmarketing-task-api-mvc-prod/openapi/task/v1/signature/clock"

    token = os.environ.get("LONGFOR_TOKEN", "")
    dxrisk_token = os.environ.get("LONGFOR_DXRISK_TOKEN", "")
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


if __name__ == "__main__":
    ok, msg = longfor_sign()
    print(ok, msg)


