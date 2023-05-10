from src.notification.messaging_bq import mq


def main():
    mq.consume_messages()


if __name__ == "__main__":
    main()
