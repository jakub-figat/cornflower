import inspect
from functools import wraps

from kombu.mixins import ConsumerProducerMixin


class MessageQueue(ConsumerProducerMixin):
    def __init__(self, url: str, *args, **kwargs) -> None:
        self.url = url

    def listen(self, topic: str):
        pass
