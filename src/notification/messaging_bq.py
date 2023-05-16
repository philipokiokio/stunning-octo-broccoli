import json
import pika
from src.notification.websocket_manager import manager
from asgiref.sync import async_to_sync


class MessageQueue:
    def __init__(self) -> None:
        # Initializing the Message Queue
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", port=5672, heartbeat=600)
        )
        self.channel = self.connection.channel()
        self.wsok_manager = manager
        self.exchange = "demo_notification"
        self.queue = "test_case_queue"
        self.channel.exchange_declare(exchange=self.exchange, exchange_type="fanout")
        self.channel.queue_declare(queue=self.queue)
        self.channel.queue_bind(
            exchange=self.exchange, queue=self.queue, routing_key="notfy-x"
        )
        self.channel.basic_qos(prefetch_count=1)

    # PUBLISHING MESSAGES TO THE QUEUE
    def publish_notification(self, message: dict):
        # publishing to the queue
        self.channel.basic_publish(
            exchange=self.exchange, routing_key="notfy-x", body=json.dumps(message)
        )
        return True

    # CONSUMER (BUT LARGELY INACTIVE)
    def consume_messages(self):
        try:
            print("messages are now consumed")

            async def callback_func(ch, method, properties, body):
                # parse the message from the queue

                if self.wsok_manager.active_connections:
                    message_status = await self.wsok_manager.send_personal_message(
                        json.loads(body)
                    )
                    if message_status:
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            # async_tosyn
            self.channel.basic_consume(
                queue=self.queue,
                on_message_callback=async_to_sync(callback_func),
                auto_ack=False,
            )
            self.channel.start_consuming()

        except KeyboardInterrupt:
            print("Consumer closed")

    # FETCH ALL THE MESSAGES
    def fetch_all_messages(self):
        messages = []
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue)
        while method_frame:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue)

            if body:
                messages.append((method_frame, json.loads(body)))

        return messages

    # USERS MESSAGE FILTER
    def get_user_messages(self, user_id: int):
        messages = self.fetch_all_messages()
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

    # RESEND MESSAGES VIA WEBSOCKET PER PERSON
    async def retry_unsent_messages(self, user_id: int):
        user_meesage = self.get_user_messages(user_id)
        if user_meesage != None:
            for message in user_meesage:
                if message != None:
                    message_status = await self.wsok_manager.personal_notification(
                        message
                    )
                    if message_status:
                        self.channel.basic_ack(delivery_tag=message["delivery_tag"])
                    return True
        return True

    # CLOSING CONNECTIONS
    def __del__(self):
        # try catch exceptions
        self.connection.close()


mq = MessageQueue()
