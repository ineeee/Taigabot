import os
import sys

# [0]: command
# [1]: raw irc line

SEPARATOR_UNIT = '\u241f'
SEPARATOR_RECORD = '\r\n'
SEPARATOR_RECORD_BYTES = b'\r\n'
FIFO_NAME = '../test-fifo-pipe'


def fifo_write(data: str):
    fifo = open(FIFO_NAME, 'wb')
    fifo.write(bytes(data, encoding='utf-8') + SEPARATOR_RECORD_BYTES)  # fucking encoding hacks
    fifo.close()

def fifo_read() -> bytes:
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


def pipe_serialize(command: str, raw: str) -> str:
    raw = raw.replace(SEPARATOR_UNIT, ' ')

    return SEPARATOR_UNIT.join([
        command,
        raw
    ])


def pipe_unserialize(data: str) -> tuple[str, str]:
    (command, raw) = data.split(SEPARATOR_UNIT, 2)
    return command, raw


def handle_irc_message(raw: str) -> str:
	return "uwu my anxiety is randomly through the roof" + "hello from python {}.{}".format(sys.version_info.major, sys.version_info.minor)


def main():
	while True:
		data = fifo_read()

		# ignore empty lines
		if len(data) <= len(SEPARATOR_RECORD):
			# the kernel will block if the fifo isnt being read or written
			# this should be safe from infinite loops hogging the cpu
			continue

		if data.endswith(SEPARATOR_RECORD_BYTES) != True:
			print("WARN: data seems incomplete?")
		else:
			data = data.rstrip()

		# cast bytes to utf-8 string
		data = data.decode('utf-8')

		print("received: " + data)
		command, raw = pipe_unserialize(data)

		if command == 'irc message':
			fifo_write(handle_irc_message(raw))


main()
