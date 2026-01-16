from longfor import longfor_sign
from bark_notify import notify_sign_result


def main():
    result = longfor_sign()
    
    # 处理返回值：可能是 (success, msg) 或 (success, msg, success_count, total_count)
    if len(result) == 4:
        success, msg, success_count, total_count = result
    else:
        success, msg = result
        success_count = None
        total_count = None
    
    print("\n" + "="*50)
    print(msg)
    print("="*50)
    # 如果配置了 Bark，则推送结果
    # 将多行消息按行分割为列表
    msg_list = msg.split("\n") if "\n" in msg else [msg]
    notify_sign_result(msg_list, success, success_count, total_count)


if __name__ == "__main__":
    main()


