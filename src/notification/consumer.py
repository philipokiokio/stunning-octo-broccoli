from src.notification.messaging_bq import mq
import asyncio


def main():
    mq.consume_messages()


if __name__ == "__main__":
    main()
