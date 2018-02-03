import os
import sys
import bin
import hashlib
import blte
import binascii
from operator import itemgetter, attrgetter, methodcaller
import itertools
import jenkins

def md5(data):
  return hashlib.md5(data).hexdigest()
  
def chunk(l, n):
  if (len (l) == 0):
    return []
  for i in range(0, len(l), n):
    yield l[i:i + n]
    
def divru (n, d):
  return int ((n + d - 1) / d)

class version_bundler:
  def __init__(self, wwwroot, product):
    self.wwwroot = wwwroot
    self.product = product
    self.cdn_prefix = self.product
    self.encodings = []
    self.root_entries = []
    
  def cdn_path_prefix(self, type):
    return os.path.join ("tpr", self.cdn_prefix, type)
  def md5path(self, hexdigest):
    return os.path.join (hexdigest[0:2], hexdigest[2:4], hexdigest)
    
  def write(self, path, data):
    path = os.path.join (self.wwwroot, path)
    os.makedirs(os.path.dirname(path), exist_ok = True)
    with open(path, u"wb+") as f:
      f.write(data)
  def write_md5(self, path, data):
    digest = md5(data)
    self.write(os.path.join(path, self.md5path(digest)), data)
    return digest
    
  class encoding_entry:
    def __init__(self, size, raw_hash, encoded_hash):
      self.size = size
      self.raw_hash = raw_hash
      self.encoded_hash = encoded_hash
    
  def write_encoded(self, path, data):
    raw_hash, encoded_hash = md5(data), self.write_md5(path, blte.encode_dumb(data))
    #! \todo is len(data) correct?
    self.encodings += [ version_bundler.encoding_entry ( len(data)
                                                       , binascii.unhexlify(raw_hash)
                                                       , binascii.unhexlify(encoded_hash)
                                                       )
                      ]
    return raw_hash, encoded_hash
    
  def encoding(self):
    #! \todo is encoding in encoding?
    return self.write_encoded(self.cdn_path_prefix("data"), self.encoding_data())
  def encoding_data(self):
    def sort_key(entry):
      #! \todo is this encoded_hash or raw_hash?
      return entry.encoded_hash
    self.encodings.sort(key=sort_key)
    
    # todo: multiple keys per entry (-> non-fixed size)
    entry_size = ( 1     # uint8_t keyCount
                 + 5     # uint40_t fileSize
                 + 0x10  # char[16] contentHash
                 + 0x10  # char[16][keyCount=1] encodedHashes
                 )
    entry_count = len(self.encodings)
    block_size = 4096
    entries_per_block = divru(entry_size * entry_count, block_size)
    blocks = list(chunk (self.encodings, entries_per_block))
    #assert (sum(len(blocks)) == len(self.encodings)
  
    # todo self.encodings actually
    header = ( b'EN'                         # magic
             + bin.uint8_t (0)               # version
             + bin.uint8_t (0x10)            # checksumSizeA
             + bin.uint8_t (0x10)            # checksumSizeB
             + bin.uint16_t (0)              # flagsA
             + bin.uint16_t (0)              # flagsB
             # todo: is this block count or entries????
             + bin.BE_uint32_t (len(blocks)) # numEntriesA
             + bin.BE_uint32_t (0)           # numEntriesB
             + bin.BE_uint40_t (0)           # stringBlockSize
             )
             
    blocks_a_register = bytes()
    blocks_a = bytes() # note: size % block_size == 0
    for block in blocks:
      # todo: raw or encoded?
      blocks_a_register += block[0].raw_hash
      blocks_a_register += b'block_hash_what?'
      for entry in block:
        blocks_a += bin.uint8_t (1)
        blocks_a += bin.BE_uint40_t (entry.size)
        blocks_a += entry.raw_hash
        blocks_a += entry.encoded_hash
      padding_len = block_size - len(block) * entry_size
      blocks_a += b'\0' * padding_len
               
    return header + blocks_a_register + blocks_a
    
  class wow_root_entry:
    def __init__(self, fdid, content_hash, name_key):
      self.flags = 0
      self.locale = 0xFFFFFFFF
      self.fdid = fdid
      self.content_hash = content_hash
      self.name_key = name_key
    def __repr__(self):
      return "{} = {}, {}".format(self.fdid, str(self.content_hash), str(self.name_key))
  def add_root(self, fdid, content_hash, name_key):
    self.root_entries += [version_bundler.wow_root_entry(fdid, content_hash, name_key)]

  def root(self, type):
    return self.write_encoded(self.cdn_path_prefix("data"), self.root_data(type))
  def root_data(self, type):
    if type != "wow":
      raise Exception("don't know how to do root files for anything but wow")
      
    self.root_entries.sort(key=attrgetter('flags', 'locale'))
    blocks = [list(g) for k, g in itertools.groupby(self.root_entries, key=attrgetter('flags', 'locale'))]
      
    def cas_record(record):
      return record.content_hash + record.name_key
    #! \todo obvious bogus, once again
    def cas_block(records):
      records.sort(key=attrgetter('fdid'))
      
      last_fdid = 0
      ids = []
      for record in records:
        ids += [record.fdid - last_fdid]
        last_fdid = record.fdid + 1
      
      return ( bin.uint32_t (len(records))      # num_records
             + bin.uint32_t (records[0].flags)  # flags
             + bin.uint32_t (records[0].locale) # locale
             + bin.many(bin.uint32_t, ids)   # filedata id deltas
             + bin.many(cas_record, records) # records
             )
    return bin.many (cas_block, blocks)
    
  def install(self):
    return self.write_encoded(self.cdn_path_prefix("data"), self.install_data())
  def install_data(self):
    # todo: obviously bogus
    return ( b'IN'
           + bin.uint8_t (1)    # version
           + bin.uint8_t (0x10) # hashSize
           + bin.BE_uint16_t (0) # num_tags
           + bin.BE_uint32_t (0) # num_entries
           )
    
  def build_config(self):
    return self.write_md5(self.cdn_path_prefix("config"), self.build_config_data())
  def build_config_data(self):
    lines = []
    lines += [u"root = {}".format(self.root("wow")[0])]
    lines += [u"install = {}".format(self.install()[0])]
    lines += [u"build-uid = {}".format(self.product)]
    encoding_raw, encoding_blte = self.encoding()
    lines += [u"encoding = {} {}".format (encoding_raw, encoding_blte)]
    return bytes('\n'.join(lines), 'utf8')
    
  def archive(self):
    #! \todo bogus
    archive_hash = u"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    #! \todo bogus
    archive_data = bytes()
    
    entries = []
    
    class archive_entry:
      def __init__(self):
        self.header_hash_md5 = b'               '
        self.encoded_size = 0
        self.offset_to_blte_encoded_data_in_archive = 0
    
    def index_entry(entry):
      return ( entry.header_hash_md5   # md5 == 16 bytes
             + bin.BE_uint32_t (entry.encoded_size)
             + bin.BE_uint32_t (entry.offset_to_blte_encoded_data_in_archive)
             )
    index_entry_size = 16 + 4 + 4
    index_block_size = 0x1000
    index_block_entry_count = divru(index_entry_size, index_block_size)
    index_block_count = divru (len(entries), index_block_entry_count)
    
    def index_block(entries):
      if len(entries) > index_block_entry_count:
        raise Exception("logic error: more entries per block than per block")
      res = bytes()
      res += bin.many (index_entry, entries)
      res += b'\0' * (index_block_size - len(entries) * index_entry_size)
      return res
      
    index_data = bytes()
    index_data += bin.many(index_block, entries)
    index_data += b'last_hash_of_blk' * len(entries)
    index_data += b'lower_md5_of_blk' * (len(entries) - 1)
    
    index_data += ( b'idx_blck'                   # index_block_hash
                  + b'toc_hash'                   # toc_hash
                  + bin.uint8_t (1)               # version
                  + bin.uint8_t (0)               # _11
                  + bin.uint8_t (0)               # _12
                  + bin.uint8_t (4)               # _13
                  + bin.uint8_t (4)               # offsetBytes
                  + bin.uint8_t (4)               # sizeBytes
                  + bin.uint8_t (16)              # keySizeInBytes
                  + bin.uint8_t (8)               # checksumSize
                  + bin.uint32_t(len (entries))   # numElements. TODO: bigendian in _old_ versions
                  + b'halfmd5_'                   # lower_part_of_md5_of_footer
                  )
                  
    self.write(os.path.join(self.cdn_path_prefix("data"), self.md5path(archive_hash)), archive_data)
    self.write(os.path.join(self.cdn_path_prefix("data"), self.md5path(archive_hash + ".index")), index_data)
    return archive_hash
    
  def cdn_config(self):
    return self.write_md5(self.cdn_path_prefix("config"), self.cdn_config_data())
  def cdn_config_data(self):
    archives = [self.archive()]
    
    lines = []
    lines += [u"archives = {}".format (u' '.join(archives))]
    return bytes('\n'.join(lines), 'utf8')
    
  def cdns(self, cdns_by_region):
    lines = []
    lines += ["Name!STRING:0|Path!STRING:0|Hosts!STRING:0|ConfigPath!STRING:0|Servers!STRING:0"]
    for region, cdns in cdns_by_region.items():
      lines += ["{}|tpr/{}|localhost|tpr/configs/data|".format(region, self.cdn_prefix, ' '.join(cdns))]
    self.write(os.path.join(self.product, "cdns"), bytes('\n'.join(lines), 'utf8'))
  
  def versions(self):
    lines = []
    lines += ["Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16"]
    #! \todo this is obviously broken
    for region in ['eu']:
      buildconfig = self.build_config()
      cdnconfig = self.cdn_config()
      buildid = 1
      versionname = "0.0.1.{}".format (buildid)
      lines += ["{}|{}|{}||{}|{}|".format(region, buildconfig, cdnconfig, buildid, versionname)]
    self.write(os.path.join(self.product, "versions"), bytes('\n'.join(lines), 'utf8'))
    
# todo: at least cascexplorer really depends on this product string
bundler = version_bundler (os.path.realpath(u"wwwroot"), u"wow")

bundler.add_root(21, b'content_hash____', jenkins.hashpath('interface/cinematics/logo_1024.avi'))
bundler.add_root(22, b'content_hash____', jenkins.hashpath('interface/cinematics/wow_intro_1024.avi'))
bundler.add_root(53183, b'content_hash____', jenkins.hashpath('sound/music/citymusic/darnassus/darnassus intro.mp3'))

bundler.cdns({'eu': ['localhost']})
bundler.versions()
