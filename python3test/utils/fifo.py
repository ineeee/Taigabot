SEPARATOR_UNIT = '\u241f'
SEPARATOR_RECORD = '\r\n'
SEPARATOR_RECORD_BYTES = b'\r\n'
FIFO_NAME = '../test-fifo-pipe'


def write(data: str):
    fifo = open(FIFO_NAME, 'wb')
    fifo.write(bytes(data, encoding='utf-8') + SEPARATOR_RECORD_BYTES)  # fucking encoding hacks
    fifo.close()


def read() -> bytes:
	fifo = open(FIFO_NAME, 'rb')
	data = b""

	while True:
	    temp = fifo.read()
	    if len(temp) == 0:
	        break
	    else:
	        # encoding: both "data" and "temp" are bytes
	        data = data + temp

	return data


# see format.txt
def serialize(command: str, *args) -> str:
    raw = raw.replace(SEPARATOR_UNIT, '_')

    return SEPARATOR_UNIT.join([
        command,
        *args  # unpack all items from list
    ])


def unserialize(data: str) -> list:
    return data.split(SEPARATOR_UNIT, 8)  # TODO explain this number
