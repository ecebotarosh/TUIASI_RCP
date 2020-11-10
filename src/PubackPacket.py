#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData


class ConnectPacket(MQTTPacket):
    
    def parseVariableHeader(self)->None:
        variableHeader=self.data[self.fixed_size:]
        packet_identifier_msb,packet_identifier_lsb,reason_code=struct.unpack("!3b",variableHeader[:4])
        self.variable['packetIdentifier']=packet_identifier_msb<<8+packet_identifier_lsb
        self.variable['reasonCode']=reason_code
        switch(self.variable['reason_code'])
        variableHeader=variableHeader[4:]




