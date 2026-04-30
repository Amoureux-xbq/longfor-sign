"""
钉钉群机器人通知模块
"""

import os
import logging
import requests

# 钉钉机器人 Webhook URL，从环境变量获取
DINGTALK_WEBHOOK = os.environ.get('DINGTALK_WEBHOOK', '')


def send_dingtalk_notification(title: str, content: str) -> bool:
    """
    发送钉钉群机器人消息
    """
    if not DINGTALK_WEBHOOK:
        logging.info('未配置 DINGTALK_WEBHOOK，跳过钉钉推送')
        return False

    try:
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                # 在正文开头添加【签到】作为钉钉安全关键词
                "text": f"【签到】{title}\n\n{content}"
            }
        }
        response = requests.post(DINGTALK_WEBHOOK, json=payload, timeout=10)
        result = response.json()

        if result.get('errcode') == 0:
            logging.info(f'钉钉推送成功: {title}')
            return True
        else:
            logging.error(f'钉钉推送失败: {result}')
            return False
    except Exception as e:
        logging.error(f'钉钉推送异常: {str(e)}')
        return False


def notify_sign_result(results: list, success: bool, success_count: int = None, total_count: int = None, user_info: dict = None):
    """
    发送签到结果通知

    Args:
        results: 签到结果列表
        success: 是否全部成功
        success_count: 成功账号数量（多账号时使用）
        total_count: 总账号数量（多账号时使用）
        user_info: 用户信息字典，包含 growth/level/next_growth
    """
    if not DINGTALK_WEBHOOK:
        return

    # 多账号情况下的标题优化
    if success_count is not None and total_count is not None and total_count > 1:
        if success_count == total_count:
            title = f'龙湖天街签到成功 ({success_count}/{total_count})'
        elif success_count == 0:
            title = f'龙湖天街签到失败 ({success_count}/{total_count})'
        else:
            title = f'龙湖天街部分成功 ({success_count}/{total_count})'
    else:
        title = '龙湖天街签到成功' if success else '龙湖天街签到失败'

    content = '\n\n'.join(results) if results else ('签到完成' if success else '签到过程中出现错误')

    # 用户信息汇总
    if user_info:
        content += f'\n\n---\n等级: {user_info["level"]}  积分: {user_info["growth"]}  距下一级还需: {user_info["next_growth"]}'

    send_dingtalk_notification(title, content)


