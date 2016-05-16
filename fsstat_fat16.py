#Alexander Moy
#cs365 hw4
import sys
import struct

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

def fsstat(offset, fd):
  """ Parses and prints boot sector
  Args:
    offset(int) offset of location of boot sector. default is 0
    fd (file) FAT16 volume to be parsed
  """
  try:
    fd.seek(offset + 11)
    data = fd.read(2)     ##Find bytes per sector
    BPS = struct.unpack('<H', data)[0]
    data = fd.read(1)     ##Find sectors per cluster
    SPC = struct.unpack('<B', data)[0]
    BPC = BPS * SPC       ##bytes per cluster = bytes per sector * sectors per cluster
    fd.seek(offset + 3)   ##Find OEM name
    data = fd.read(8)
    OEM = data.decode('utf-8')
    fd.seek(offset + 39)  ##Find volume ID
    data = fd.read(4)
    volumeID = hex(struct.unpack('<L', data)[0])
    fd.seek(offset + 43)  ##Find volume label
    data = fd.read(11)
    label = data.decode('utf-8')
    fd.seek(offset + 19)  ##Find total number of sectors
    data = fd.read(2)
    total = struct.unpack('<H', data)[0] -1
    fd.seek(offset + 14)  ##Find number of reserved sectors
    data = fd.read(2)
    reserved = struct.unpack('<H', data)[0]
    fd.seek(offset + 16)  ##Find number of FAT
    data = fd.read(1)
    numFAT = struct.unpack('<B', data)[0]
    fd.seek(offset + 22)  ##Find sectors per FAT
    data = fd.read(2)
    SPF = struct.unpack('<H', data)[0]
    begindata = numFAT*SPF+reserved ##Calc end of FATs
    fd.seek(offset + 17)  ##Find files in root
    data = fd.read(2)
    root = struct.unpack('<H', data)[0]
    rootsize  = int(root * 32 / BPS)  ##calc size of root directory
    leftover = (total+1) % SPC  ##calc unclustered sectors
  except IOError as err:
    print("IOError occured while reading file: \n\t%s" % err)
    usage()
  except:
    print("Unexpected error:", sys.exc_info()[0])
    usage()
  print("FILE SYSTEM INFORMATION")
  print("--------------------------------------------")
  print("File System Type: FAT16")
  print("")
  print("OEM Name: ", OEM)
  print("Volume ID:", volumeID)
  print("Volume Label:", label)
  print("")
  print("File System Type Label: FAT16")
  print("")
  print("File System Layout (in sectors)")
  print("Total Range: 0 - ", total)##bootstrap missing
  print("Total Range in Image: 0 - ", total-1)
  print("* Reserved: 0 - ", reserved-1)##bootstrap missing
  print("** Boot Sector: ", int(offset/BPS))
  for x in range(0, numFAT):
    print("* FAT ", x, ": ", reserved + SPF*x, " - ", SPF*(x+1) + reserved-1)
  print("* Data Area: ", begindata, " - ", total)
  print("** Root Directory: ", begindata, " - ", begindata + rootsize - 1)
  print("** Cluster Area: ", rootsize + begindata, " - ", total - leftover)
  print("** Non-clustered: ", total-leftover+1, " - ", total)
  print("")
  print("CONTENT INFORMATION")
  print("--------------------------------------------")
  print("Sector Size: ", BPS)
  print("Cluster Size: ", BPC)
  print("Total Cluster Range: ", SPC, " - ", int(SPC + (total-rootsize-begindata-leftover) / SPC))## strong possibility this equation is wrong


def usage():
  """ Print usage string and exit() """
  print("Usage:\n%s offset filename\n" % sys.argv[0])
  sys.exit()

def main():
  ##check and run
  if (len(sys.argv) == 3):
    offset = int(sys.argv[1])
    fd = open_file(sys.argv[2])
  elif (len(sys.argv) == 2):  ##offset is optional parameter
    offset = 0
    fd = open_file(sys.argv[1])
  else:
    usage()
  fsstat(offset, fd)

if __name__ == '__main__':
  main()