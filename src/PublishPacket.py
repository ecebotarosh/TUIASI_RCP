#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *

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
		offset,self.variable['topicName']=readCustomUTF8String(variableHeader)
		variableHeader=variableHeader[2+offset:]
		self.variable['packetIdentifier']=struct.unpack("!H",variableHeader[:2])
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
		i=0
		while i<self.variable['propertyLength']:
			if properties[i]==0x01:
				if 'payloadFormatIndicator' not in self.variable['properties'].keys():
					self.variable['properties']['payloadFormatIndicator'] = struct.unpack("!B", properties[i+1:i+2])[0]
				else:
					raise MQTTError("Malformed Packet : payloadFormatIndicator already exists")
				i += 1
			elif properties[i]==0x02:
				if 'messageExpiryInterval' not in self.variable['properties'].keys():
					self.variable['properties']['messageExpiryInterval']=struct.unpack("!I",properties[i+1:i+5])[0]
				else:
					raise MQTTError("Malformed Packet : messageExpiryInterval already exists")
				i+=4
			elif properties[i]==0x23:
				if 'topicAlias' not in self.variable['properties'].keys():
					self.variable['properties']['topicAlias']=struct.unpack("!H",properties[i+1:i+3])[0]
					if self.variable['properties']['topicAlias']==0:
						raise MQTTError("Malformed Packet : topicAlias it doesn't to be 0")
					# 0< topicAlias <=valMax din ConnackPacket
					#i+=2
				else:
					raise MQTTError("Malformed Packet : topicAlias already exists")
				i+=2
			elif properties[i]==0x08:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'responseTopic' not in self.variable['properties'].keys():	
					self.variable['properties']['responseTopic'] = str1
				else:
					raise MQTTError("Malformed Packet : responseTopic already exists")
				i += offset1
			elif properties[i]==0x09:
				if 'correlationData' not in self.variable['properties'].keys():
					offset1,data1=readBinaryData(properties[i+1:])
					self.variable['properties']['correlationData']=data1
					i +=offset1
				else:
					raise MQTTError("Malformed Packet : correlationData already exists")
				
			elif properties[i] == 0x26:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				offset2,str2=readCustomUTF8String(properties[i+1+offset1:])
				if str1 not in self.variable['properties']['userProperty'].keys():
					self.variable['properties']['userProperty'][str1] = [str2]
				else:
					self.variable['properties']['userProperty'][str1].append(str2)
				i += offset1+offset2
			elif properties[i]==0x0B:
				buff=properties[i+1:]
				num = b""
				for byte in buff:
					num += struct.pack("!B", byte)
					if byte < 0x80:
						break
				if 'subscriptionIdentifier' not in self.variable['properties'].keys():
					self.variable['properties']['subscriptionIdentifier'] = VariableByte.decode(num)
				i+=len(num)
			elif properties[i]==0x03:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'contentType' not in self.variable['properties'].keys():	
					self.variable['properties']['contentType'] = str1
				else:
					raise MQTTError("Malformed Packet : rcontentType already exists")
				i += offset1
			i+=1

		if 'payloadFormatIndicator' not in self.variable['properties'].keys():
			self.variable['properties']['payloadFormatIndicator'] = 0

	def parsePayloadHeader(self):
		offset = self.fixed_size+self.variable_size+1
		self.payload_size = self.fixed['remainingLength']-self.variable_size
		payloadHeader = self.data[offset:]
		self.payload['data']=payloadHeader

if __name__=="__main__":
	header=b"\x31"

	
	packetIdentifier = b"\x00\x0f"
	
	
	mess=b"\x02"+struct.pack("!I", 32)
	respons=b"\x08"+CustomUTF8.encode("Raspuns")
	topic=b"\x23\x00\x10"
	user = b"\x26"+CustomUTF8.encode("user1")+CustomUTF8.encode("utilizeaza dev")+b"\x26"+CustomUTF8.encode("user2")+CustomUTF8.encode("add commit")
	prop=b"\x01\x01"+mess+respons+topic+user+b"\x09\x00\x02\x00\x01"+b"\x0B"+VariableByte.encode(115)
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