#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *

class AuthPacket(MQTTPacket):
	def parseVariableHeader(self)->None:
		variableHeader=self.data[self.fixed_size:]

		self.variable['authReasonCode']=struct.unpack("!B",variableHeader[:1])[0]
		variableHeader=variableHeader[1:]
		if(self.fixed['remainingLength'] ==2):
			self.variable['authReasonCode'] = 0x00
		
		properties=self.data[self.fixed_size+1:]
		num=b""
		for byte in properties:
			num+=struct.pack("!B",byte)
			if byte<0x80:
				break
		required=len(num)
		
		self.variable['propertyLength']=struct.unpack("!{}s".format(required),num)[0]
		self.variable['propertyLength']=VariableByte.decode(self.variable['propertyLength'])
		self.variable['properties']={}
		self.variable['properties']['userProperty']={}
		self.variable_size=self.variable['propertyLength']+1
		properties=properties[required:]

		i=0
		while i<self.variable['propertyLength']:
			if properties[i]==0x15:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'authMethod' not in self.variable['properties'].keys():	
					self.variable['properties']['authMethod'] = str1
				else:
					raise MQTTError("Malformed Packet : authMethod already exists")
				i += offset1
			if properties[i]==0x16:
				if 'authData' not in self.variable['properties'].keys():
					offset1,self.variable['properties']['authData']=readBinaryData(properties[i+1:])
					i +=offset1
				else:
					raise MQTTError("Malformed Packet : authMethod data already exists")

			if properties[i]==0x1F:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'reasonString' not in self.variable['properties'].keys():	
					self.variable['properties']['reasonString'] = str1
				else:
					raise MQTTError("Malformed Packet : reasonString already exists")
				i += offset1
			if properties[i] == 0x26:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				offset2,str2=readCustomUTF8String(properties[i+1+offset1:])
				if str1 not in self.variable['properties']['userProperty'].keys():
					self.variable['properties']['userProperty'][str1] = [str2]
				else:
					self.variable['properties']['userProperty'][str1].append(str2)
				i += offset1+offset2
			i+=1
		if 'authMethod' not in self.variable['properties'].keys():
			raise MQTTError("Malformed Packet : authMethod does not exist")

if __name__=="__main__":

	fixed=b"\xF0"

	reason_code=b"\x18"
	auth_method=b"\x15"+CustomUTF8.encode("it is authMethod()...")
	auth_data=b"\x16"+CustomUTF8.encode("it is authData()...")
	reason_string=b"\x1f"+CustomUTF8.encode("reasonString for AUTH")
	userProperty=b"\x26"+CustomUTF8.encode("user1")+CustomUTF8.encode("checkout main")+b"\x26"+CustomUTF8.encode("user2")+CustomUTF8.encode("add commit")
	properties=auth_data+auth_method+reason_string+userProperty

	property_length=VariableByte.encode(len(properties))
	variableHeader=reason_code+property_length+properties
	len_var_header=len(variableHeader)
	remainigLength=VariableByte.encode(len_var_header)

	data=fixed+remainigLength+variableHeader
	data=struct.pack("!{}s".format(len(data)),data)

	packet=AuthPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	print(packet.fixed)
	print(packet.variable)