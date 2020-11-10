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
		self.fixed['type']>>=4
		self.fixed['DUP_flag']=(self.fixed['type'] & 8 == 8)
		self.fixed['QoSLevel']=(self.fixed['type'] & 6 )
		self.fixed['retain']=(self.fixed['type'] & 1 == 1)
		self.fixed['remainingLength']=VariableByte.decode(self.fixed['remainingLength'])
		self.fixed_size=1+required

	def parseVariableHeader(self)->None:
		variableHeader=self.data[fixed_size:]
		length_msb,length_lsb,name=struct.unpack("!2b3s",variableHeader[:5])
		self.variable['length']=(length_msb<<8)+length_lsb
		self.variable['name']=name.decode("utf-8")
		variableHeader=variableHeader[5:]
		packet_identifier_msb,packet_identifier_lsb=struct.unpack("!2b",variableHeader[:2])
		packet_identifier=packet_identifier_msb<<8+packet_identifier_lsb
		self.variable['packetIdentifier']=packet_identifier
		variableHeader=variableHeader[2:]
		# 7 bytes is the common variable header, without properties
		properties=self.data[7+self.fixed_size:]
		num = b""
		for byte in properties:
			num += struct.pack("!B", byte)
			if byte < 0x80:
				break
		required = len(num)
		self.variable['propertyLength'] = struct.unpack("!{}s".format(required), num)[0]
		self.variable['propertyLength'] = VariableByte.decode(self.variable['propertyLength'])
		self.variable['properties']={}
		self.variable_size=self.variable['propertyLength']+7
		properties=properties[required:]
		#============================================================================================

		i=0
		while i<self.variable['propertyLength']:
			if properties[i]==0x01:
				if 'payloadFormatIndicator' not in self.variable['properties'].keys():
					self.variable['properties']['payloadFormatIndicator']=struct.unpack("!b",properties[i+1])[0]
					if self.variable['properties']['payloadFormatIndicator']==0x00:
						# payload is unspecified bytes====================================================================
						#print('?')
					elif self.variable['properties']['payloadFormatIndicator']==0x01:
						# payload is UTF-8 encoded character data=========================================================
						#print("no")
					else:
						raise MQTTError('Malformed Packet : payloadFormatIndicator is not formatted correctly')
					i+=1
				else:
					raise MQTTError("Malformed Packet : payloadFormatIndicator already exists")	
			if properties[i]==0x02:
				if 'messageExpiryInterval' not in self.variable['properties'].keys():
					self.variable['properties']['messageExpiryInterval']=struct.unpack("!I",properties[i+1:i+5])[0]
					i+=4 # intreb 
				else:
					raise MQTTError("Malformed Packet : messageExpiryInterval already exists")
			if properties[i]==0x23:
				if 'topicAlias' not in self.variable['properties'].keys():
					self.variable['properties']['topicAlias']=struct.unpack("!H",properties[i+1:i+3])[0]
					if self.variable['properties']['topicAlias']==0:
						raise MQTTError("Malformed Packet : topicAlias it doesn't to be 0")
					# 0< topicAlias <=valMax din ConnackPacket=========================================================================
					i+=2
				else:
					raise MQTTError("Malformed Packet : topicAlias already exists")
			#trebuie de completat la struct in jos
			if properties[i]==0x08:
				if 'responseTopic' not in self.variable['properties'].keys():
					self.variable['properties']['topicAlias']=struct.unpack()
					#trebuie de citit un string
			if properties[i]==0x09:
				if 'correlationData' not in self.variable['properties'].keys():
					self.variable['properties']['correlationData']=struct.unpack("")