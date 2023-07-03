from can.interface import Bus
from can.message import Message
from can.notifier import Notifier
from cantools.database import load_file


class CANConnector:
    def __init__(self, db_file: str):
        self.bus = Bus()
        self.notifier = Notifier(self.bus, (self.on_message,))
        # TODO: `.dbc` resources are needed to decode CAN messages into usable data
        self.db = load_file(db_file)

    def on_message(self, message: Message):
        data = self.db.decode_message(message.arbitration_id, message.data)
        print(data)

    def stop(self):
        self.notifier.stop()
        self.bus.shutdown()
