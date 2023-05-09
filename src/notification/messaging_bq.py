import asyncio
import json
import pika
from src.notification.websocket_manager import manager
from asgiref.sync import async_to_sync
from src.notification.celery_worker import notification


class MessageQueue:
    def __init__(self) -> None:
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", port=5672, heartbeat=600)
        )
        self.channel = self.connection.channel()
        # self.failed_messages = {}
        self.wsok_manager = manager
        self.exchange = "demo_notification"
        self.queue = "test_case_queue"
        self.channel.exchange_declare(
            exchange=self.exchange, exchange_type="fanout"  # , durable=True
        )

        self.channel.queue_declare(queue=self.queue)  # durable=True)

        self.channel.queue_bind(
            exchange=self.exchange, queue=self.queue, routing_key="notfy-x"
        )

        self.channel.basic_qos(prefetch_count=1)

    def publish_notification(self, message: dict):
        print(self.wsok_manager.active_connections)
        self.channel.basic_publish(
            exchange=self.exchange, routing_key="notfy-x", body=json.dumps(message)
        )
        return True

    def consume_messages(self):
        print(self.wsok_manager.active_connections)
        try:
            retry_limit = 3
            print("messages are now consumed")

            async def callback_func(ch, method, properties, body):
                # parse the message from the queue

                # # extract the relevant data from the message
                # workspace_id = message["workspace_id"]
                # team_id = message["team_id"]
                # user_id = message["user_id"]
                # action = message["action"]

                # # send a WebSocket message to clients in the workspace and team
                # message = f"User {user_id} {action} a project."
                print(f"consuming body {body}")

                status_ws = notification.delay(json.loads(body))

                print(status_ws)

                if self.wsok_manager.active_connections:
                    message_status = await self.wsok_manager.send_personal_message(
                        json.loads(body)
                    )
                    print(message_status)
                    if message_status:
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                else:
                    print("requeue")
                    # if (
                    #     method.redelivered
                    #     and method.delivery_tag in self.failed_messages
                    # ):
                    #     if self.failed_messages[method.delivery_tag] < retry_limit:
                    #         # Increment the retry count for this message
                    #         self.failed_messages[method.delivery_tag] += 1
                    #         # Reject the message and requeue it
                    #         ch.basic_nack(
                    #             delivery_tag=method.delivery_tag, requeue=True
                    #         )
                    #     else:
                    # Reject the message and discard it after max retries

                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                    # del self.failed_messages[method.delivery_tag]
                    # else:
                    #     # Reject the message and requeue it for the first time
                    #     ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    #     self.failed_messages[method.delivery_tag] = 1
                    # #     return True
                # return False

            # async_tosyn
            self.channel.basic_consume(
                queue=self.queue,
                on_message_callback=async_to_sync(callback_func),
                auto_ack=False,
            )
            self.channel.start_consuming()

        except KeyboardInterrupt:
            print("Consumer closed")
            pass

    def fetch_all_messages(self):
        messages = []
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue)
        print(method_frame)
        while method_frame:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue)

            if body:
                messages.append((method_frame, json.loads(body)))

        return messages

    def get_user_messages(self, user_id: int):
        messages = self.fetch_all_messages()
        print("all messages", messages)
        if messages:
            user_messages = [
                {"message": message, "delivery_tag": method_frame.delivery_tag}
                for method_frame, message in messages
                if message["user_id"] == user_id
            ]
            if user_messages:
                return user_messages
            else:
                return None
        return None

    async def retry_unsent_messages(self, user_id: int):
        user_meesage = self.get_user_messages(user_id)
        print(user_meesage)
        if user_meesage != None:
            for message in user_meesage:
                if message != None:
                    # print(message)
                    # print(message["message"]["user_id"])
                    message_status = await self.wsok_manager.personal_notification(
                        message
                    )
                    print(message_status)
                    # delete the message from the queue if successfully sent via WebSocket
                    if message_status:
                        self.channel.basic_ack(delivery_tag=message["delivery_tag"])
                    print("Previous Messages for this user have been sent")

    def __del__(self):
        self.connection.close()


# connection= pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))


mq = MessageQueue()
