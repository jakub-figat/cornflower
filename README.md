## Cornflower
### Library for writing RabbitMQ message handlers with [pydantic](https://github.com/samuelcolvin/pydantic) validation.

## Installation
`$ pip install cornflower`

## Example use:


Handler callback can accept zero or one argument of `pydantic.BaseModel` type. Message body will be validated automatically against specified schema.

```python
from cornflower import MessageQueue, OutputMessage, MessageDeliveryMode
from pydantic import BaseModel


class UserMessage(BaseModel):
    username: str
    message: str


queue = MessageQueue(url="amqp://user:password@host:port")


@queue.listen(routing_key="user.registered")
def handle_user_register(message: UserMessage) -> None:
    # do something with validated message
    ...


@queue.listen(routing_key="user.login")
def handle_user_login() -> None:
    # callback with no arguments, handle message without
    # validating its body
    
    # sending message
    user_message = UserMessage(username="example", message="this is example")
    
    queue.dispatch(
        message=OutputMessage(
            body=user_message.dict(),
            routing_key="user.logout",
            delivery_mode=MessageDeliveryMode.PERSISTENT,
        )
    )


if __name__ == "__main__":
    queue.run()
```


## Optional configuration

```python
from cornflower import MessageQueue
from cornflower.options import QueueOptions, TransportOptions, ConsumerOptions

queue = MessageQueue(
    queue_options=QueueOptions(
        durable=True,
        exclusive=False,
        auto_delete=False,
    ),
    consumer_options=ConsumerOptions(
        prefetch_count=10
    ),
    transport_options=TransportOptions(
        confirm_publish=True,
    )
)
```