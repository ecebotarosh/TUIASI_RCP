#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *

class PingResPacket(MQTTPacket):
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
		self.fixed['remainingLength']=VariableByte.decode(self.fixed['remainingLength'])
        
        def parse(self) -> None:
            self.parseFixedHeader()

	@staticmethod
	def generatePacketData():
		return b"\xd0"+struct.pack("!B", 0)

if __name__=="__main__":
	
	fixed=b"\xd0"
	remainingLength=struct.pack("!B", 0)

	data=fixed+remainingLength

	packet=PingResPacket(data)
	packet.parseFixedHeader()
	print(packet.fixed)

	customData = PingResPacket.generatePacketData()
	customPacket = PingResPacket(customData)
	customPacket.parseFixedHeader()
	print(customPacket.fixed)
