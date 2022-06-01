import os
import sys

from utils import fifo

# [0]: command
# [1]: raw irc line

def handle_irc_message(raw: str) -> str:
	print("fasfsfd", raw)
	# hardcoded cuz im testing
	return "reply" + fifo.SEPARATOR_UNIT + "#prussian" + fifo.SEPARATOR_UNIT + "hello from python {}.{}".format(sys.version_info.major, sys.version_info.minor)


def main():
	while True:
		data = fifo.read()

		# ignore empty lines
		if len(data) <= len(fifo.SEPARATOR_RECORD):
			# the kernel will block if the fifo isnt being read or written
			# this should be safe from infinite loops hogging the cpu
			continue

		if data.endswith(fifo.SEPARATOR_RECORD_BYTES) != True:
			print("WARN: data seems incomplete?")
		else:
			data = data.rstrip()

		# cast bytes to utf-8 string
		data = data.decode('utf-8')

		print("received: " + data)
		command, raw = fifo.unserialize(data)

		if command == 'irc message':
			fifo.write(handle_irc_message(raw))


main()
