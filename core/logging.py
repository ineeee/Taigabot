import queue
from datetime import datetime


# silently grab all tcp queues and print the send/recv lines
# TODO add the network name to the output
# TODO save it to a file
class LoggingQueue(queue.Queue):
    def __init__(self, kind: str):
        super().__init__()

        self.kind = kind

    def put(self, item, block=True, timeout=None):
        if self.kind == 'output':
            self.log(item)

        super().put(item, block, timeout)

    def get(self, block=True, timeout=None):
        item = super().get(block, timeout)

        if self.kind == 'input':
            self.log(item)

        return item

    def log(self, data):
        text = ''

        # loop through all of the bytes in the input data
        # if its a control character, show its hex representation instead
        for character in data:
            if ord(character) < 32:
                text += '\\x{:02x}'.format(ord(character))
            else:
                text += character

        current_time = datetime.now()
        pretty_time = current_time.strftime('%H:%M:%S')

        if self.kind == 'input':
            text = f'[{pretty_time}] << {text}'
        elif self.kind == 'output':
            text = f'[{pretty_time}] >> {text}'

        print(text)
