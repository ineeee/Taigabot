# linux kernel version plugin by ine (2020)
# updated 04/2022
from util import hook
from utilities import request
import re


@hook.command(autohelp=False)
def kernel(inp):
    """kernel -- show latest linux kernel versions"""
    data = request.get("https://www.kernel.org/finger_banner")
    lines = data.split('\n')

    versions = []
    old_versions = []
    output = []

    for line in lines:
        info = re.match(r'^The latest stable version of the Linux kernel is:\s*(.*)$', line)
        if info is not None:
            output.append('Current stable Linux kernel is \x02{}\x02'.format(info.group(1)))
            continue

        info = re.match(r'^The latest ([[a-z0-9 \-\.]+) version of the Linux kernel is:\s*(.*)$', line)
        if info is None:
            continue

        name = info.group(1)
        version = info.group(2)

        if 'longterm' in name:
            old_versions.append(version)
        else:
            versions.append(version)

    output.append('Latest versions: {}'.format(', '.join(versions)))

    if len(old_versions) > 0:
        output.append('Old versions: {}'.format(', '.join(old_versions)))

    return '. '.join(output)
