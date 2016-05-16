#ALEXANDER MOY
#cs365 hw3

import sys
import struct
from tags import TAGS

def open_file(filename):
	"""" Opens filename
	     Args:
	       filename (string: file to be opened (assumes a valid path)
	     Returns:
	       an open file descriptor
	"""
	try:
		return(open(filename, "rb"))
	except IOError:
		print('File does not exist')
		sys.exit()
	except:
		it_broke()

def check_jpeg(fd):
	"""" Checks to make sure file is a JPEG
		 Args:
		 	fd (file: file being checked)
		 Returns:
		 	1 if JPEG, exits program otherwise
	"""
	try:
		data = fd.read(2)	#these should be FFD8
	except:
		it_broke()
	if (data == b'\xFF\xD8'):
		#recognized jpeg
		return 1
	else:
		print('This file is not a recognized JPEG. Exitting.')
		sys.exit()
		return 0

def find_markers(fd):
	"""" Searches for markers until FFDA is encountered
		 Args
		 	fd (file: master file)
	"""
	global count	#count keeps track of the current position
	count = 2
	stop = 0
	while (stop == 0): #loop continues until FFDA is found
		try:
			data = fd.read(1)
		except:
			it_broke()
		count += 1
		if (data == b'\xFF'):
			if(marker_stuff(fd) == 1):
				break


def marker_stuff(fd):
	"""" Prints each marker. Calls search for EXIF on each marker. Calls IFD processor when it is found
		 Args
		 	fd (file: master file)
		 Returns
		 	0 normally, 1 when FFDA is found to stop the loop
	"""
	global count
	try:
		mark	= b'\xFF' + fd.read(1)					#read marker and size
		size	= struct.unpack(">H", fd.read(2))[0]
	except:
		it_broke()
	if (mark == b'\xFF\xFF'):
		return
	print('[',hex(count - 1), '] ', end = '')		#print values
	print('Marker ', end = '')
	print(hex(struct.unpack(">H", mark)[0]), end = '')
	print(' size=', end = '')
	print(hex(size))
	count += 3
	if (exif_check(fd,size) == 1):	#execute ifd processor when EXIF is found
		idf_stuff(fd, size)
	if (mark == b'\xFF\xDA'):	#end when FFDA is found
		return 1
	else:
		return 0

def exif_check(fd,size):
	"""" Checks if EXIF is present.
		 Args
		 	fd (file: master file)
		 	size (int: size of marker. method does not continue if under 6)
		 Returns
		 	0 if not EXIF, 1 if EXIF
	"""
	global count
	global magic_pos #position of 4d
	if(size > 6):
		try:
			data = fd.read(6)
		except:
			it_broke()
		fd.seek(-6,1)
		if (data == b'\x45\x78\x69\x66\x00\x00'): #EXIF
			fd.seek(6,1)
			try:
				data = fd.read(4)
			except:
				it_broke()
			count += 10
			magic_pos = count -4
			if (data != b'\x4D\x4D\x00\x2A'): #checks for big endian
				sys.exit()
			else:
				return 1
	#fd.seek(size -4, 1)
	#count += size - 4
	return 0

def idf_stuff(fd, size):
	"""" Finds the number of EXIF entries and loops according to the IFD offset
		 Args
		 	fd (file: master file)
		 	size (int: size of EXIF, used to ignore non-markers)
	"""
	global count
	fd.seek(magic_pos + 4)
	try:
		idfOffset = struct.unpack(">L", fd.read(4))[0]
		fd.seek(idfOffset - 8, 1)
		entries = struct.unpack(">H", fd.read(2))[0]
	except:
		it_broke()
	count += 6
	print ('Number of IFD entries: ', entries)
	for x in range(0, entries):
		tag_stuff(fd)
	fd.seek(size - (entries * 12) - 4, 1)
	count += size - (entries * 12) - 4


def tag_stuff(fd):
	"""" Prints the EXIF data for each entry
		 Args
		 	fd (file: master file)
	"""
	global magic_pos
	global count
	bpc			= (0,1,1,2,4,8,1,1,2,4,8,4,8)	#format table
	try:
		tag			= struct.unpack(">H", fd.read(2))[0]	#read EXIF entry values
		format		= struct.unpack(">H", fd.read(2))[0]
		components	= struct.unpack(">L", fd.read(4))[0]
		data		= struct.unpack(">L", fd.read(4))[0]
	except:
		it_broke()
	count += 12
	length		= bpc[format] * components
	try:
		if (length <= 4):
			value	= data
		else:
			oldpos	= count
			fd.seek(magic_pos + data)
			data	= fd.read(length)
			#unsigned byte
			if (format == 1):
				value = struct.unpack(">B", data[0:1])
			#ASCII String
			if (format == 2):
				value = bytes.decode(data[0:length])
			#Unsigned Short
			if (format == 3):
				value = struct.unpack(">%dH" % components, data[0:length])
			#Unsigned Long
			if (format == 4):
				value = struct.unpack(">L", data[0:4])
			#Unsigned Rational
			if (format == 5):
				value = (numerator, denominator) = struct.unpack(">LL",data[0:8])
				"%s/%s" % (numerator,denominator)
			#Undefined (Raw)
			if (format == 7):
				value = unpack(">%dB" % length, data[0:length])
				"".join("%c" % x for x in value)
			#value	= fd.read(length)
			fd.seek(oldpos)

		print(TAGS[tag], end=': ')
		print(value)
	except:
		print("Unexpected data type found in EXIF. Attempting to continue")




def it_broke(): #error statement while reading file
	print("Unexpected error while reading file:", sys.exc_info()[0])
	sys.exit()


def main():
	fd = open_file(sys.argv[1])
	check_jpeg(fd)
	find_markers(fd)


if __name__== '__main__':
	main()