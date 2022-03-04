from pydantic import BaseModel

from cornflower import MessageQueue

queue = MessageQueue(url="amqp://rabbitmquser:somepassword@rabbitmq:5672")


class UserRegisterCommand(BaseModel):
    user: str


@queue.listen("user.register")
def handle_user_register(command: UserRegisterCommand) -> None:
    print(command.user)


queue.run()
