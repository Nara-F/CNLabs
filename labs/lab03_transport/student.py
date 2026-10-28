"""学生实现教学协议；数据类型来自公共接口。"""
from labs.lab03_transport.api import Segment, Ack, Sender as SenderAPI, Receiver as ReceiverAPI

class Sender(SenderAPI):
    pass

class Receiver(ReceiverAPI):
    pass
