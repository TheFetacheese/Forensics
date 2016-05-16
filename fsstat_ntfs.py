##Alexander Moy
#cs365 hw5

import sys
import struct
from datetime import datetime, timedelta
"""Global variables """
MFT = 0                         ##Bytearray: used as a copy of the MFT currently being parsed
data_pos = 0                    ##Int: incremented whenever a new runlist is added to keep offset
cluster_array_behemoth = list() ##List: stores the runlist. It is big.
location = 0                    ##Int: contains the position of the desired MFT once it is confirmed
def open_file(filename):
  """ Opens filename, and calls usage() on error.                    
  Args:
    filename (string): file to be opened (assumes a valid path)
  Returns:
    an open file descriptor
  """
  try:
    return(open(filename, "rb"))
  except IOError as err:
    print("IOError opening file: \n\t%s" % err)
    usage()
  except:
    print("Unexpected error:", sys.exc_info()[0])
    usage()

def MFT_offset(fd):
  """ Args:
    fd (file descriptor): volume being parsed 
    Returns:
      The cluster offset of MFT#0"""
  fd.seek(48)
  location = struct.unpack('<Q', fd.read(8))[0]
  return location

def bytes_per_sector(fd):
  """ Args:
    fd (file descriptor): volume being parsed 
    Returns:
      The amount of bytes in one sector"""
  fd.seek(11)
  bps = struct.unpack('<H', fd.read(2))[0]
  return bps

def sectors_per_cluster(fd):
  """ Args:
    fd (file descriptor): volume being parsed 
    Returns:
      The amount of sectors in one cluster"""
  fd.seek(13)
  spc = struct.unpack('<B', fd.read(1))[0]
  return spc

def MFT_start(fd):
  """ Args:
    fd (file descriptor): volume being parsed 
    Returns:
    The location of MFT#0 in bytes      """
  return MFT_offset(fd) * bytes_per_sector(fd) * sectors_per_cluster(fd)

##get methods for task 1 appear below

def MFT_set(fd):
  """ Args:
    fd (file descriptor): volume being parsed 
      This method sets the active MFT. It is first used to parse MFT#0, 
      and later for the desired MFT"""
  try:
    fd.seek(MFT_start(fd))
    if (location != 0):
      fd.seek(location)
    global MFT
    MFT = bytearray(fd.read(1024))
    fixup(fd)
  except:
    print('Error setting MFT')
    usage()
"""Assorted MFT parser methods"""
def signature():
  return MFT[0:4].decode('utf-8')

def fixup_offset():                         ##        Hello!
  return struct.unpack('<H', MFT[4:6])[0]   ##  () () /
                                            ##  ()_()/ 
def fixup_entries():                        ##  ('.')
  return struct.unpack('<H', MFT[6:8])[0]   ##  (___)()

def LSN():
  return struct.unpack('<Q', MFT[8:16])[0]

def sequence_value():
  return struct.unpack('<H', MFT[16:18])[0]

def link_count():
  return struct.unpack('<H', MFT[18:20])[0]

def att_offset():
  return struct.unpack('<H', MFT[20:22])[0]

def flags():
  return struct.unpack('<H', MFT[22:24])[0]

def used_size():
  return struct.unpack('<L', MFT[24:28])[0]

def allocated_size():
  return struct.unpack('<L', MFT[28:32])[0]

def file_reference():
  return struct.unpack('<Q', MFT[32:40])[0]

def next_attribute():
  return struct.unpack('<H', MFT[40:42])[0]
"""end assorted MFT"""

def parse_attribs(offset, fd, flag):
  """ Args:
    fd (file descriptor): volume being parsed 
    offset (int): current offset used in recursion to parse through attributes
    flag (int): causes the method to ignore prints until it is done with MFT#0
    This method uses recursion to search through all attributes and parse them when required""" 
  
  att = MFT[offset + att_offset():att_offset() + 16 + offset] ##attribute header
  full = MFT[att_offset() + offset: att_offset() + offset + 16 + att_length(att)]
  ##print(MFT[att_offset() + offset + 16 + att_length(att):att_offset() + offset + 16 + att_length(att)+4])
  if(offset > 351): #band aid fix, could not locate xFFFFFFFF
    return
  if(att_type(att) == 16 and flag == 1):
    STD_INFO(full, att)
  if(att_type(att) == 48 and flag == 1):
    FILE_NAME(full, att)
  if(att_type(att) == 128 and flag == 0):
    start = offset + att_offset() + DATA_rl_offset(full)
    DATA(full)
  try:
    return parse_attribs(offset+ att_length(att), fd, flag)
  except:
    print('Some errors may have resulted with this specific input due to incomplete coding in parse_attribs (lines 116-138')

def fixup(fd):
  """ Alters some values based on fixup arrays. """
  ##print(MFT[fixup_offset():fixup_offset()+2])
  MFT[bytes_per_sector(fd)-2:bytes_per_sector(fd)] = MFT[fixup_offset()+2:fixup_offset()+4]
  MFT[2*bytes_per_sector(fd) -2: 2* bytes_per_sector(fd)]  = MFT[fixup_offset()+2:fixup_offset()+4]

"""Attribute header statements"""
def att_type(att):
  """ Args:
    att (bytearray): attribute header"""  
  return struct.unpack('<L', att[0:4])[0]

def att_length(att):
  """ Args:
    att (bytearray): attribute header""" 
  return struct.unpack('<L', att[4:8])[0]

def att_rflag(att):
  """ Args:
    att (bytearray): attribute header"""  
  return struct.unpack('<B', att[8:9])[0]

def att_name_length(att):
  """ Args:
    att (bytearray): attribute header"""  
  return struct.unpack('<B', att[9:10])[0]

def att_name_offset(att):
  """ Args:
    att (bytearray): attribute header"""  
  return struct.unpack('<H', att[10:12])[0]

def att_flags(att):
  """ Args:
    att (bytearray): attribute header"""  
  return struct.unpack('<H', att[12:14])[0]

def att_ID(att):
  """ Args:
    att (bytearray): attribute header"""  
  return struct.unpack('<H', att[14:16])[0]
""" End attribute header statements """

def STD_INFO(std, att):
  """ Args:
    att (bytearray): attribute header
    std (bytearray): Standard_INFO attribute
  Parses the STD_INFO attribute"""

  print("Type: $Standard_INFO (0-16) NameLen: (",att_name_length(att), ") Resident   size: ", att_length(att))
  print("        file_accessed ", datetime.fromtimestamp((STD_accessed(std) / 10000000)-11644473600))
  print("             Owner ID ", STD_owner_ID(std))
  print("       version number ", STD_version(std))
  print("             creation ", datetime.fromtimestamp((STD_creation(std) / 10000000)-11644473600))
  print("          Security ID ", STD_security_ID(std))
  print("          mft altered ", datetime.fromtimestamp((STD_MFT_altered(std) / 10000000)-11644473600))
  print("         Update seq # ", STD_update(std))
  print("                flags")
  print("       max # versions ", STD_max(std))
  print("             Class ID ", STD_class_ID(std))
  print("        Quota Charged ", STD_quota(std))
  print("         file altered ", datetime.fromtimestamp((STD_file_altered(std) / 10000000)-11644473600))

"""Standard_INFO attributes """
def STD_creation(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<Q', std[24:32])[0]

def STD_file_altered(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<Q', std[32:40])[0]

def STD_MFT_altered(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """  
  return struct.unpack('<Q', std[40:48])[0]

def STD_accessed(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<Q', std[48:56])[0]

def STD_flags(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """                        
  return struct.unpack('<L', std[56:60])[0]

def STD_max(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<L', std[60:64])[0]

def STD_version(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<L', std[64:68])[0]

def STD_class_ID(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<L', std[68:72])[0]

def STD_owner_ID(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<L', std[72:76])[0]

def STD_security_ID(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<L', std[76:80])[0]

def STD_quota(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<Q', std[80:88])[0]

def STD_update(std):
  """ Args:
    std (bytearray): Standard_INFO attribute """
  return struct.unpack('<Q', std[88:96])[0]

##end STD_INFO

##begin FILE_INFO
def FILE_NAME(fil, att):
  """ Args:
    att (bytearray) attribute header
    fil (bytearray) FILE_NAME attribute
  Parses the FILE_NAME attribute"""
  print("")
  print("Type: $FILE_NAME (2-48) NameLen: (", att_name_length(att), ") Resident  size: ", att_length(att))
  print("          Alloc. size of file", FILE_allocated(fil))
  print("               Length of name", FILE_name_length(fil))
  print("                 MFT mod time", datetime.fromtimestamp((FILE_MFT_modification(fil) / 10000000)-11644473600))
  print("                         Name", FILE_name(fil))
  print("                    Namespace", FILE_namespace(fil))
  print("      Parent dir (MFT#, seq#) (", FILE_reference1(fil),",", FILE_reference2(fil), ")")
  print("               Real filesize", FILE_real(fil))
  print("               Reparse value", FILE_reparse(fil))
  print("            file access time", datetime.fromtimestamp((FILE_access(fil) / 10000000)-11644473600))
  print("          file creation time", datetime.fromtimestamp((FILE_creation(fil) / 10000000)-11644473600))
  print("               file mod time", datetime.fromtimestamp((FILE_modification(fil) / 10000000)-11644473600))
  print("                       flags", FILE_flags(fil))


def FILE_reference1(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """  
  return struct.unpack('<H', fil[24:26])[0]
def FILE_reference2(fil): #something in the email but I honestly have no idea how this one is supposed to work
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  temp = fil[26:32]
  temp.append(0)
  temp.append(0)
  return struct.unpack('<Q', temp)[0]

def FILE_creation(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<Q', fil[32:40])[0]

def FILE_modification(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<Q', fil[40:48])[0]

def FILE_MFT_modification(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<Q', fil[48:56])[0]

def FILE_access(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<Q', fil[56:64])[0]

def FILE_allocated(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<Q', fil[64:72])[0]

def FILE_real(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<Q', fil[72:80])[0]

def FILE_flags(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<L', fil[80:84])[0] ##flaaaaaags

def FILE_reparse(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<L', fil[84:88])[0]

def FILE_name_length(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<B', fil[88:89])[0]

def FILE_namespace(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return struct.unpack('<B', fil[89:90])[0]

def FILE_name(fil):
  """ Args:
  fil (bytearray) FILE_NAME attribute """
  return fil[90:90 + 2 * FILE_name_length(fil)].decode('utf-8')
"""End FILE_NAME attributes """

def DATA_rl_offset(data):
    """ Args:
      data (bytearray): DATA attribute 
      Returns:
      The offset of the runlist"""
    return struct.unpack('<H', data[32:34])[0]

def DATA_offset_length(data):
  """ Args:
    data (bytearray) DATA attribute 
    Returns:
    The length in bytes of the runlist offset"""
  return struct.unpack('<B', data[DATA_rl_offset(data) + data_pos: DATA_rl_offset(data) + 1 + data_pos])[0] >> 4

def DATA_rl_length(data):
  """ Args:
      data (bytearray) DATA attribute 
      Returns:
      The length in bytes of the runlist length"""
  return struct.unpack('<B', data[DATA_rl_offset(data) + data_pos: DATA_rl_offset(data) + 1 + data_pos])[0] & 0x0F

def DATA_runlist_length(data): ##check lengths
  """ Args:
    data (bytearray) DATA attribute 
    Returns:
    the length of the runlist"""
  temp = data[DATA_rl_offset(data)+1 + data_pos: DATA_rl_offset(data) + 1 + DATA_rl_length(data) + data_pos] 
  if (DATA_rl_length(data) == 1):
    return struct.unpack('<b', data[DATA_rl_offset(data)+1 + data_pos: DATA_rl_offset(data) +1 + data_pos])[0]
  if (DATA_rl_length(data) == 2):
    return struct.unpack('<h', temp)[0]
  if (DATA_rl_length(data) < 5):
    while (len(temp) < 4):
      temp.append(0)
    return struct.unpack('<l', temp)[0]
  if (DATA_rl_length(data) < 9):
    while (len(temp) < 8):
      temp.append(0)
    return struct.unpack('<q', temp)[0]

def DATA_runlist_offset(data):
  """ Args:
    data (bytearray) DATA attribute 
    Returns:
    The offset of the runlist"""
  temp = data[DATA_rl_length(data) + DATA_rl_offset(data)+1 + data_pos: DATA_rl_offset(data) + 1 + DATA_offset_length(data) + DATA_rl_length(data) + data_pos]
  if (DATA_offset_length(data) == 1):
    return struct.unpack('<b', data[DATA_rl_length(data) + DATA_rl_offset(data)+1 + data_pos: DATA_rl_offset(data) +1 + DATA_rl_length(data) + data_pos])[0]
  if (DATA_offset_length(data) == 2):
    return struct.unpack('<h', temp)[0]
  if (DATA_offset_length(data) < 5):
    while (len(temp) < 4):
      temp.append(0)
    return struct.unpack('<l', temp)[0]
  if (DATA_offset_length(data) < 9):
    while (len(temp) < 8):
      temp.append(0)
    return struct.unpack('<q', temp)[0]
## NAME, I will come back to this later if required

def DATA(data):
    """ Args:
    data (bytearray) DATA attribute 
    Loops through the runlist while adding all of the entries in the runlist to a list"""
   
    global data_pos
    global cluster_array_behemoth
    temp_offset = 0
    
   
    while (DATA_rl_length(data) != 0):
    ##  print(DATA_runlist_offset(data))
      temp_offset = temp_offset + DATA_runlist_offset(data)
    ##  print(DATA_runlist_length(data))
      cluster_array_behemoth.extend(range(temp_offset, temp_offset + DATA_runlist_length(data)))

      data_pos = data_pos + 1 + DATA_rl_length(data) + DATA_offset_length(data)

def heat_seeking_MFT_finder_missile(fd, tar):
  """ Args:
    fd (file descriptor): volume being parsed 
    tar (int): the desired MFT entry"""  
  global location
  tar_cluster = int(1024 * tar / (sectors_per_cluster(fd) * bytes_per_sector(fd)))
  tar_pos     = 1024 * tar % (sectors_per_cluster(fd) * bytes_per_sector(fd))
  location = cluster_array_behemoth[tar_cluster]
  location = location * bytes_per_sector(fd) * sectors_per_cluster(fd)
  location = location + tar_pos

def print_values(fd, tar):
  """ Args:
    fd (file descriptor): volume being parsed 
    tar (int): the desired MFT entry"""  
  print("MFT Entry Header Values:")
  print("Sequence:", sequence_value())
  print("$Logfile Sequence Number:", LSN())
  print("Allocated File")
  print("Directory")
  print("")
  print("Used size: ", used_size(), "bytes")
  print("Allocated size: ", allocated_size(), "bytes")
  parse_attribs(0, fd, 1)


def usage():
  """ Print usage string and exit() """
  print("Usage:\n%s offset filename\n" % sys.argv[0])
  sys.exit()




def main():
  if(len(sys.argv) == 3):
    try:
      fd = open_file(sys.argv[2])
      tar = int(sys.argv[1])
      MFT_set(fd)
      ##print(att_offset())
      parse_attribs(0, fd, 0)
      heat_seeking_MFT_finder_missile(fd, tar)
      MFT_set(fd)
      print_values(fd, tar)
    except:
      print('Unknown error')
      usage()
  else:
    usage()


if __name__ == '__main__':
  main()