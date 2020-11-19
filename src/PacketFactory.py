#!/usr/bin/env python3

from MQTTPacket import MQTTPacket
from ConnackPacket import ConnackPacket, generateConnackPacketData

class PacketFactory():
	def generatePacket(self, _type : str, ack_flags : bool, reason_code: int, properties:dict) -> MQTTPacket:
		if _type=="connack":
			packet = ConnackPacket(generateConnackPacketData(ack_flags, reason_code, properties))