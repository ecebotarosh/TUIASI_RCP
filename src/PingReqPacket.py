#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *

class PingReqPacket(MQTTPacket):
	def parseFixedHeader(self):
		fixed_part = self.data[:1]
		num=b""
		for byte in self.data[1:]:
			num+=struct.pack("!B", byte)
			if byte<0x80:
				break
		required=len(num)
		self.fixed['type'], self.fixed['remainingLength'] = struct.unpack("!B{}s".format(required), fixed_part+num)
		self.fixed['type']>>=4

if __name__=="__main__":
	
	fixed=b"\xc0"
	remainigLength=VariableByte.encode(0)

	data=fixed+remainigLength
	data=struct.pack("!{}s".format(len(data)),data)

	packet=PingReqPacket(data)
	packet.parseFixedHeader()
	print(packet.fixed)