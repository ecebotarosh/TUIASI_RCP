#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData


class PubackPacket(MQTTPacket):
	def parseVariableHeader(self)->None:
		variableHeader = self.data[self.fixed_size:]
		packetIdentifierMs