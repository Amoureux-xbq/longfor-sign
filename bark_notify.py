"""
Bark 推送通知模块
"""

import os
import logging
import requests

# Bark 服务器地址，默认使用官方服务器
BARK_SERVER = os.environ.get('BARK_SERVER') or 'https://api.day.app'
# Bark Key，从环境变量获取
BARK_KEY = os.environ.get('BARK_KEY', '')


def send_bark_notification(title: str, content: str, group: str = '龙湖天街签到') -> bool:
    """
    发送 Bark 推送通知
    """
    if not BARK_KEY:
        logging.info('未配置 BARK_KEY，跳过 Bark 推送')
        return False

    try:
        url = f'{BARK_SERVER}/{BARK_KEY}'
        data = {
            'title': title,
            'body': content,
            'group': group,
        }
        response = requests.post(url, json=data, timeout=10)
        result = response.json()

        if result.get('code') == 200:
            logging.info(f'Bark 推送成功: {title}')
            return True
        else:
            logging.error(f'Bark 推送失败: {result}')
            return False
    except Exception as e:
        logging.error(f'Bark 推送异常: {str(e)}')
        return False


def notify_sign_result(results: list, success: bool):
    """
    发送签到结果通知
    """
    if not BARK_KEY:
        return

    title = '✅ 龙湖天街签到成功' if success else '❌ 龙湖天街签到失败'
    content = '\n'.join(results) if results else ('签到完成' if success else '签到过程中出现错误')

    send_bark_notification(title, content)


