#!/usr/bin/env python3

import struct

class VariableByte:
    @staticmethod
    def encode(data:int) -> bytes:
        X = data
        output=b""
        while X>0:
            encodedByte = X % 128
            X = X // 128
            if X > 0:
                encodedByte = encodedByte | 128
            output+=struct.pack("!B",encodedByte)
        return output

    @staticmethod
    def decode(data:bytes)->int:
        multiplier = 1
        value = 0
        i=0
        while True:
            encodedByte=data[i]
            value = value + (encodedByte & 127) * multiplier
            if multiplier>128*128*128:
                raise ValueError("Malformed Variable Byte Integer")
            multiplier = multiplier * 128
            i=i+1
            if i>len(data):
                break
            if (encodedByte & 128==0):
                break
        return value


class CustomUTF8:
    @staticmethod
    def encode(msg:str)->bytes:
        length = len(msg)
        length_msb = length // 0x100
        length_lsb = length % 0x100
        return struct.pack("!2B{}s".format(length), length_msb, length_lsb, bytes(msg, 'utf-8'))

    @staticmethod
    def decode(msg:bytes)->str:
        return msg[2:].decode('utf-8')


class BinaryData:
    def __init__(self, data):
        self.data=data
        
    def getLength(self) -> int:
        return struct.unpack("!H", self.data[:2])[0]

    def getData(self) -> bytes:
        return self.data[2:]

if __name__=="__main__": 
    encoded = CustomUTF8.encode("hello")
    print(encoded)
    decoded = CustomUTF8.decode(encoded)
    print(decoded)

    result = VariableByte.encode(16383)
    print(result)
    result = VariableByte.decode(result)
    print(result)


class MQTTError(Exception):
    pass
