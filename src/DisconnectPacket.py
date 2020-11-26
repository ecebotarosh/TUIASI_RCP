#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *

class DisconnectPacket(MQTTPacket):
	def parseVariableHeader(self)->None:
		variableHeader=self.data[self.fixed_size:]

		self.variable['disconnectReasonCode']=struct.unpack("!B",variableHeader[:1])[0]
		variableHeader=variableHeader[1:]
		if(self.fixed['remainingLength'] == 2):
			self.variable['disconnectReasonCode'] = 0x00
		
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
			if properties[i] == 0x11:
				if 'sessionExpiry' not in self.variable['properties'].keys():
					self.variable['properties']['sessionExpiry'] = struct.unpack("!I", properties[i+1:i+5])[0]
					i += 4
				else:
					raise MQTTError("Malformed Packet : sessionExpiry already exists")
			if properties[i]==0x1F:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'reasonString' not in self.variable['properties'].keys():	
					self.variable['properties']['reasonString'] = str1
				else:
					raise MQTTError("Malformed Packet : responseTopic already exists")
				i += offset1
			if properties[i] == 0x26:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				offset2,str2=readCustomUTF8String(properties[i+1+offset1:])
				if str1 not in self.variable['properties']['userProperty'].keys():
					self.variable['properties']['userProperty'][str1] = [str2]
				else:
					self.variable['properties']['userProperty'][str1].append(str2)
				i += offset1+offset2
			if properties[i]==0x1C:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'serverReference' not in self.variable['properties']:
					self.variable['properties']['serverReference']=str1
				else:
					raise MQTTError("Malformed Packet : serverReference already exists")
				i+=offset1
			i+=1


if __name__=="__main__":

	fixed=b"\xe0"

	reason_code=b"\x81"
	session_expiry=b"\x11"+struct.pack("!I",128)
	reason_string=b"\x1f"+CustomUTF8.encode("reason for disconnect")
	userProperty=b"\x26"+CustomUTF8.encode("user1")+CustomUTF8.encode("checkout main")+b"\x26"+CustomUTF8.encode("user2")+CustomUTF8.encode("add commit")
	server_reference=b"\x1c"+CustomUTF8.encode("serverReference for Client")
	properties=session_expiry+reason_string+userProperty+server_reference

	property_length=VariableByte.encode(len(properties))
	variableHeader=reason_code+property_length+properties
	len_var_header=len(variableHeader)
	remainigLength=VariableByte.encode(len_var_header)

	data=fixed+remainigLength+variableHeader
	data=struct.pack("!{}s".format(len(data)),data)

	packet=DisconnectPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	print(packet.fixed)
	print(packet.variable)