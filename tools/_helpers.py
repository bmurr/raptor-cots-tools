import struct

def read_int32(data):
    return struct.unpack('i', data[:4])[0]

def read_int16(data):
    return struct.unpack('h', data[:2])[0]

def read_uint32(data):
    return struct.unpack('I', data[:4])[0]    

def read_uint16(data):
    return struct.unpack('H', data[:2])[0]  