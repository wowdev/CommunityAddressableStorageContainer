import struct

def uint8_t(value):
  return struct.pack ("<B", value)
def BE_uint8_t(value):
  return uint8_t(value)
  
def uint16_t(value):
  return struct.pack ("<H", value)
def BE_uint16_t(value):
  return struct.pack (">H", value)
  
def uint32_t(value):
  return struct.pack ("<I", value)
def BE_uint32_t(value):
  return struct.pack (">I", value)
  
def uint40_t(value):
  return uint32_t((value & 0xFFFFFFFF) >> 00) + uint8_t((value & 0xFF00000000) >> 32)
def BE_uint40_t(value):
  return BE_uint8_t((value & 0xFF00000000) >> 32) + BE_uint32_t((value & 0xFFFFFFFF) >> 00)
  
def many(fun, values):
  res = bytes()
  for value in values:
    res += fun(value)
  return res