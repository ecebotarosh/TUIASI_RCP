#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData

class PublishPacket(MQTTPacket):
	def parseFixedHeader(self):
		fixed_part = self.data[:1]
		num=b""
		for byte in self.data[1:]:
			num+=struct.pack("!B", byte)
			if byte<0x80:
				break
		required=len(num)
		self.fixed['type'], self.fixed['remainingLength'] = struct.unpack("!B{}s".format(required), fixed_part+num)
		self.fixed['DUP_flag']=(self.fixed['type'] & 8 == 8)
		self.fixed['QoSLevel']=((self.fixed['type'] & 6)>>1 )
		if self.fixed['QoSLevel']==3:
			raise MQTTError("Malformed Packet : QoSLevel '11' reserved – must not be used ")
		self.fixed['retain']=(self.fixed['type'] & 1 == 1)
		self.fixed['type']>>=4
		self.fixed['remainingLength']=VariableByte.decode(self.fixed['remainingLength'])
		self.fixed_size=1+required

	def parseVariableHeader(self)->None:
		variableHeader=self.data[self.fixed_size:]
		length_msb,length_lsb = struct.unpack("!2B", variableHeader[:2])
		self.variable['length']=(length_msb<<8)+length_lsb
		variableHeader=variableHeader[2:]
		name=struct.unpack("!{}s".format(self.variable['length']), variableHeader[:self.variable['length']])[0]
		self.variable['name']=name.decode("utf-8")
		variableHeader=variableHeader[self.variable['length']:]
		packet_identifier_msb,packet_identifier_lsb=struct.unpack("!2B",variableHeader[:2])
		packet_identifier=(packet_identifier_msb<<8 )+ packet_identifier_lsb
		self.variable['packetIdentifier']=packet_identifier
		variableHeader=variableHeader[2:]
		# 7 bytes is the common variable header, without properties
		properties=self.data[4+self.variable['length']+self.fixed_size:]
		#variable byte integer
		num = b""
		for byte in properties:
			num += struct.pack("!B", byte)
			if byte < 0x80:
				break
		required = len(num)
		self.variable['propertyLength'] = struct.unpack("!{}s".format(required), num)[0]
		self.variable['propertyLength'] = VariableByte.decode(self.variable['propertyLength'])
		self.variable['properties']={}
		self.variable['properties']['userProperty']={}
		self.variable_size=self.variable['propertyLength']+self.variable['length']+4+required
		properties=properties[required:]
		#============================================================================================

		i=0
		while i<self.variable['propertyLength']:
			if properties[i]==0x01:
				if 'payloadFormatIndicator' not in self.variable['properties'].keys():
					self.variable['properties']['payloadFormatIndicator'] = struct.unpack("!B", properties[i+1:i+2])[0]
				else:
					raise MQTTError("Malformed Packet : payloadFormatIndicator already exists")
				i += 1
			if properties[i]==0x02:
				if 'messageExpiryInterval' not in self.variable['properties'].keys():
					self.variable['properties']['messageExpiryInterval']=struct.unpack("!I",properties[i+1:i+5])[0]
					#i+=4 
				else:
					raise MQTTError("Malformed Packet : messageExpiryInterval already exists")
				i+=4
			if properties[i]==0x23:
				if 'topicAlias' not in self.variable['properties'].keys():
					self.variable['properties']['topicAlias']=struct.unpack("!H",properties[i+1:i+3])[0]
					if self.variable['properties']['topicAlias']==0:
						raise MQTTError("Malformed Packet : topicAlias it doesn't to be 0")
					# 0< topicAlias <=valMax din ConnackPacket
					#i+=2
				else:
					raise MQTTError("Malformed Packet : topicAlias already exists")
				i+=2
			if properties[i]==0x08:
				OFFSET_TO_READ_1_START = i+1
				OFFSET_TO_READ_1_END = i+3
				to_read = properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
				str1size = struct.unpack("!H", to_read)[0]
				if 'responseTopic' not in self.variable['properties'].keys():	
					self.variable['properties']['responseTopic'] = CustomUTF8.decode(struct.unpack("!{}s".format(
						str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START), properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0])
				else:
					raise MQTTError("Malformed Packet : responseTopic already exists")
				i += OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START+str1size
			if properties[i]==0x09:
				if 'correlationData' not in self.variable['properties'].keys():
					length = struct.unpack("!H", properties[i+1:i+3])[0]
					self.variable['properties']['correlationData'] = properties[i+1:i+3+length]
				else:
					raise MQTTError("Malformed Packet : correlationData already exists")
				i += 2+length
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
			if properties[i]==0x0B:
				buff=properties[i+1:]
				num = b""
				for byte in buff:
					num += struct.pack("!B", byte)
					if byte < 0x80:
						break
				if 'subscriptionIdentifier' not in self.variable['properties'].keys():
					self.variable['properties']['subscriptionIdentifier'] = VariableByte.decode(num)
				i+=len(num)
			if properties[i]==0x03:
				OFFSET_TO_READ_1_START = i+1
				OFFSET_TO_READ_1_END = i+3
				to_read = properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
				str1size = struct.unpack("!H", to_read)[0]
				if 'contentType' not in self.variable['properties'].keys():	
					self.variable['properties']['contentType'] = CustomUTF8.decode(struct.unpack("!{}s".format(
						str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START), properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0])
				else:
					raise MQTTError("Malformed Packet : rcontentType already exists")
				i += OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START+str1size

			i+=1

		if 'payloadFormatIndicator' not in self.variable['properties'].keys():
			self.variable['properties']['payloadFormatIndicator'] = 0

if __name__=="__main__":
	header=b"\x31"

	
	packetIdentifier = b"\x00\x0f"
	
	
	mess=b"\x02"+struct.pack("!I", 32)
	respons=b"\x08"+CustomUTF8.encode("Raspuns")
	topic=b"\x23\x00\x10"
	user = b"\x26"+CustomUTF8.encode("salut_din")+CustomUTF8.encode("dev")+b"\x26"+CustomUTF8.encode("KY")+CustomUTF8.encode("IZI")
	prop=b"\x01\x01"+mess+respons+topic+user+b"\x09\x00\x05Binar"+b"\x0B"+VariableByte.encode(115)
	propLength = VariableByte.encode(len(prop))
	varHeader=CustomUTF8.encode("test/rc")+packetIdentifier+propLength+prop

	payload = CustomUTF8.encode("buna ziua")


	remainingLength = VariableByte.encode(len(varHeader+payload))

	data = header + remainingLength + varHeader + payload
	dataLen = len(data)
	data=struct.pack("!{}s".format(dataLen), data)
	packet=PublishPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	print(packet.fixed)
	print(packet.variable)