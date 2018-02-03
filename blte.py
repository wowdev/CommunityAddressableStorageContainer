import os
import sys
import bin

def block_dumb(data):
  return b'N' + data

def encode_dumb(data):
  return ( b'BLTE'             # magic
         + bin.BE_uint32_t (0) # headerSize
         + block_dumb(data)
         )

def encode_file_dumb(file, output):
  with open(file, u"rb") as f:
    data = f.read()
  with open(output, u"wb+") as f:
    f.write(encode_dumb(data))
    
if __name__ == '__main__':
  encode_file_dumb(sys.argv[1], sys.argv[2])
