#!/usr/bin/env python3

import struct 
import sys
from MQTTPacket import MQTTPacket 
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData

class PubrelPacket(MQTTPacket):
	def __init__(self, data):
		self.data = data
		self.fixed = {}
		self.fixed_size = 0
		self.variable = {}
		self.variable_size =0
			

	def parseVariableHeader(self): 
		variableHeader = self.data[self.fixed_size:]

		#pubrel packed id
		packet_id_MSB, packet_id_LSB =  struct.unpack("!2b", variableHeader[:2])
		self.variable['packet_id'] = (packet_id_MSB << 8) + packet_id_LSB
		print('packet_id: ' + str(self.variable['packet_id']))
		variableHeader = variableHeader[2:]

		#pubrel reason code
		pubrec_reason_code = struct.unpack("!B", variableHeader[:1])[0]
		self.variable['pubrec_reason_code'] = pubrec_reason_code
		if(self.fixed['remainingLength'] == 2):
			self.variable['pubrec_reason_code'] = 0x00
		print('pubrec_reason_code: ' + str(self.variable['pubrec_reason_code']))
		variableHeader = variableHeader[1:]
		
		#properties can be omitted if the reason code is Success
		#3 bytes so far

		#in case if reason code isn't Success, properties can't be omitted
	
		properties = self.data[self.fixed_size+3:]
		num = b""
		for byte in properties:
			num += struct.pack("!B", byte)
			if byte < 0x80:
				break
		required = len(num)

		self.variable['propertyLength'] = struct.unpack("!{}s".format(required), num)[0]

		#fac decode ca sa am prop length intr un int
		self.variable['propertyLength'] = VariableByte.decode(self.variable['propertyLength'])

		if(self.fixed['remainingLength'] < 4):
			self.variable['propertyLength'] = 0
		else:
			self.variable['properties'] = {}
			self.variable['properties']['userProperty'] = {} 
			self.variable_size = self.variable['propertyLength'] + 3
			properties = properties[required:]	

			i = 0
			while i < self.variable['propertyLength']:
				if properties[i] == 0x1f:
					if 'reason_string' not in self.variable['properties'].keys():
						OFFSET_TO_READ_START = i + 1
						OFFSET_TO_READ_END = i + 3 
						to_read = properties[OFFSET_TO_READ_START : OFFSET_TO_READ_END] #octetii care arata lungimea
						#print("to read: " + str(to_read))
						efective_length = struct.unpack("!H", to_read)[0] #transf in nr => lungimea stringului meu de 2 bytes
						#print("efective_lentgh: " + str(efective_length))
						self.variable['properties']['reason_string'] = CustomUTF8.decode(struct.unpack("!{}s".format(2 + efective_length), properties[i+1 : i + 3 + efective_length ])[0])
						i = i + 2 + efective_length
					else:
						raise MQTTError("Malformed Packet : reason string already exists")	
				if properties[i] == 0x26:
					OFFSET_TO_READ_1_START = i+1
					OFFSET_TO_READ_1_END = i+3
					to_read = properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
					str1size = struct.unpack("!H", to_read)[0]
					str1 = struct.unpack("!{}s".format(str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START), properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0]
					OFFSET_TO_READ_2_START = i+3+str1size
					OFFSET_TO_READ_2_END = i+5+str1size
					to_read2 = properties[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END]
					str2size = struct.unpack("!H", to_read2)[0]
					str2 = struct.unpack("!{}s".format(str2size+OFFSET_TO_READ_2_END-OFFSET_TO_READ_2_START), properties[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END+str2size])[0]
					if CustomUTF8.decode(str1) not in self.variable['properties']['userProperty'].keys():
						self.variable['properties']['userProperty'][CustomUTF8.decode(str1)] = [CustomUTF8.decode(str2)]
					else:
						self.variable['properties']['userProperty'][CustomUTF8.decode(str1)].append(CustomUTF8.decode(str2))
						i += 4+len(CustomUTF8.decode(str1))+len(CustomUTF8.decode(str2))
				i = i + 1

	@staticmethod
	def generatePacketData(packetID : int, reasonCode : int, reasonString : str, userProperties : dict) -> bytes:
		"""
		userProperties e un dictionar cu cheie string si valori de tip lista de string
		"""
		fixed = b"\x60"
		packet_id = struct.pack("!H", packetID)
		variable = packet_id + struct.pack("!B", reasonCode)
		properties = b"\x1f"+CustomUTF8.encode(reasonString)
		for key in userProperties.keys():
			for value in userProperties[key]:
				properties+=b"\x26"+CustomUTF8.encode(key)+CustomUTF8.encode(value)
		propertyLength = VariableByte.encode(len(properties))
		variable += propertyLength
		variable += properties
		remainingLength = VariableByte.encode(len(variable))
		fixed+=remainingLength
		return fixed+variable


if __name__=="__main__" :
	#fixed header
	fixed = b"\x60"
	
	#variable header
	packet_id = b"\x04\x01"
	pubrec_reason_code =  b"\x92"
	reason_string = b"\x1f" + CustomUTF8.encode("Panda is a cat")
	userProperty = b"\x26" + CustomUTF8.encode("I am mother of 15 cats") + CustomUTF8.encode("and 10 dogs")
	

	#properties 
	properties = reason_string + userProperty
	property_length = VariableByte.encode(len(properties))

	variableHeader = packet_id + pubrec_reason_code + property_length + properties
	length_of_variable_header = len(variableHeader)
	
	remainingLength = VariableByte.encode(length_of_variable_header)

	data = fixed + remainingLength + variableHeader 
	data = struct.pack("!{}s".format(len(data)), data)

	packet = PubrelPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	print(packet.fixed)
	print(packet.variable)

	customData = PubrelPacket.generatePacketData(1025, 146, "Panda is a cat", {"I am mother of 15 cats":["and 10 dogs"]})
	customPacket = PubrelPacket(customData)
	customPacket.parseFixedHeader()
	customPacket.parseVariableHeader()
	print(customPacket.fixed)
	print(customPacket.variable)
