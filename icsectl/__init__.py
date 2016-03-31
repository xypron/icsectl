#!/usr/bin/env python
#
# Copyright (c) 2016, Heinrich Schuchardt <xypron.glpk@gmx.de>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Control ICStation USB multi channel relay modules

IcseCtl is a library to control the ICStation USB multi channel relay
modules (ICSE012A, ICSE013A, ICSE014A).

Initialization
--------------

The initialization of the devices is handled by udev.
To set up udev::

    sudo cp examples/icsudev.py /lib/udev
    sudo cp examples/99-icsctl.rules /etc/udev/rules.d
    sudo udevadm control --reload-rules

When a device is plugged in the relays are switched on by default.
After detection the icsudev.py script switches them off.

Symbolic links /dev/ttyICSE012A, /dev/ttyICSE013A, /devttyICSE014A are
created if a respective device is connected. If another PL2303 device
is connected a link /dev/ttyPL2303 is created.

Initialization is logged in the system log.

Permissions
-----------

Per default, only root is allowed to use devices directly.
On Debian and Ubuntu serial USB devices are assigned to group dialout.
To allow a user to use the device call::

    adduser USER dialout

Usage
-----

The script examples/icsctl can be used to switch individual relays.
The status is kept in a file in the user's home directory.
If the file does not yet exist, it is assumed that all relays are switched off.

Links
-----

An overview of udev rules is provided at
http://www.reactivated.net/writing_udev_rules.html.

These are links to the devices on the vendor's site

* http://www.icstation.com/icstation-micro-control-channel-relay-module-p-4012.html

* http://www.icstation.com/icstation-micro-control-channel-relay-module-icse013a-p-4013.html

* http://www.icstation.com/icstation-channel-micro-relay-module-icse014a-p-5185.html

License
-------

Copyright (c) 2016, Heinrich Schuchardt <xypron.glpk@gmx.de>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import os.path
import serial

def getfilename(dev):
	"""
	Gets filename to store status of module.

	:param dev: device name, e.g. "/dev/ttyICSE012A"
	:returns: filename
	"""
	path = os.path.expanduser("~/.icsctl")
	if False == os.path.exists(path):
		os.mkdir(path)
	filename = path + "/icsctl" + dev.replace("/", "-")
	return filename	

def readstatus(dev):
	"""
	Gets bitmask with the status of the module.
	Depending on the module bits 0-1, 0-3, or 0-7 are used.

	:param dev: device name, e.g. "/dev/ttyICSE012A"
	:returns: status bitmask
	"""
	try:
		file = open(getfilename(dev), "r")
	except FileNotFoundError as err:
		return 0
	a = file.readline()
	if (a == "IcsCtl\n"):
		a = file.readline()
		try:
			bits = int(a)
		except ValueError:
			bits = 0
	else:
		bits = 0
	file.close()
	return bits

def writestatus(dev, bits):
	"""
	Sets bitmask with the status of the module.
	Depending on the module bits 0-1, 0-3, or 0-7 are used.

	:param dev: device name, e.g. "/dev/ttyICSE012A"
	:param bits: bitmask
	:return status: bitmask
	:raises serial.serialutil.SerialException: communication error
	"""
	if dev == None:
		return
	# Open serial connection.
	ser = serial.Serial(
		port = dev, \
		baudrate =  9600, \
		stopbits = serial.STOPBITS_ONE, \
		bytesize = serial.EIGHTBITS, \
		timeout = .1)
	ser.write(bytearray([bits]))
	ser.close()
	
	file = open(getfilename(dev), "w")
	file.write("IcsCtl" + "\n")
	file.write(str(bits) + "\n")
	file.close()
