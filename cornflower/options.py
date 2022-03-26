from pydantic import BaseModel, validator


class QueueOptions(BaseModel):
    """
    durable:
    If set to true, queue remains after restarting RabbitMQ server

    exclusive:
    If set to true, the queue can be consumed only by current connection

    auto_delete:
    If set to true, the queue is deleted when all consumers finish consuming
    """

    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False


class ConsumerOptions(BaseModel):
    """
    prefetch_count:
    A max number of messages directed to one consumer at one time
    """

    prefetch_count: int

    @validator("prefetch_count")
    def validate_prefetch_count(cls, prefetch_count: int) -> int:
        if prefetch_count < 0:
            raise ValueError("prefetch_cont must be greater or equal to 0")

        return prefetch_count


class TransportOptions(BaseModel):
    """
    confirm_publish:
    If set to True, publisher will wait for publish confirmation from message broker
    """

    confirm_publish: bool
