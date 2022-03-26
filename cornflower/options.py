from pydantic import BaseModel, validator


class QueueOptions(BaseModel):
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    no_ack: bool = False


class ConsumerOptions(BaseModel):
    prefetch_count: int

    @validator("prefetch_count")
    def validate_prefetch_count(cls, prefetch_count: int) -> int:
        if prefetch_count < 0:
            raise ValueError("prefetch_cont must be greater or equal to 0")

        return prefetch_count


class TransportOptions(BaseModel):
    confirm_publish: bool
