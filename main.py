from longfor import longfor_sign
from bark_notify import notify_sign_result


def main():
    success, msg = longfor_sign()
    print(msg)
    # 如果配置了 Bark，则推送结果
    notify_sign_result([msg], success)


if __name__ == "__main__":
    main()


