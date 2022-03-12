from pydantic import BaseModel


class QueueOptions(BaseModel):
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    no_ack: bool = False
