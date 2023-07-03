from can.interface import Bus
from can.message import Message
from can.notifier import Notifier
from cantools.db import decode_message


class CANConnector:
    def __init__(self):
        self.bus = Bus()
        self.notifier = Notifier(self.bus, (self.on_message,))
        # TODO: cantools to decode messages

    def on_message(self, message: Message):
        data = decode_message(message.arbitration_id, message.data)
        print(data)

    def stop(self):
        self.notifier.stop()
        self.bus.shutdown()
