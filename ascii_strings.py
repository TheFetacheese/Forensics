#Alexander Moy
#cs365 hw2
import sys


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

def magic(minlen, fd):
	""" Prints all consecutive ascii characters found in file
	    that occur in strings of at least minlen characters
	    An unprintable character will cause a string to be broken

	    Unicode characters in ascii range will be printed
	    If two 00 values occur consecutively, it will be treated
	    as an unprintable character

	    Commented out code exists from when the assignment was to
	    exclude big-endian unicode characters
	    To revert to old functionality, delete lines marked with NEW
	    and uncomment lines marked with OLD

	    Args:
		minlen(int): minimum string length to be printed
	    	fd(file): an open file descriptor
	"""
	try:
		data = fd.read(16) #checks 16 bytes at a time
	except:
		print('File could not be read')
		sys.exit()
	magic_string = '' #this string will collect characters until an unprintable is reached
	#prev = 'b' OLD
	prevz = 'n' #NEW checks whether the previous byte was a 0, used for unicode
	while data:
		for d in data:
			if((d > 31 and d < 127) or d == 10): #add character to string if printable
				magic_string += chr(d)
				prevz = 'n' #NEW
				#if(prev == 'b'): OLD
					#prev = 'u' OLD
				#elif(prev == 'u' or prev == 'l'): OLD
					#prev = 'b' OLD
			#elif(prev == 'u' and d == 0): OLD
				#prev = 'b' OLD
				#continue OLD
			elif(d == 0 and prevz == 'n'): #NEW skips 0 if previous byte was not 0
				prevz = 'y' #NEW
			else: #breaks string and prints if an unprintable is found
				#if (prev == 'b'): OLD
					#prev = 'l' OLD
				#elif (prev == 'u' or prev == 'l'): OLD
					#prev = 'b' OLD
				prevz = 'n' #NEW
				if (len(magic_string) >= minlen):
					print(magic_string)
				magic_string = ''
		try:
			data = fd.read(16)
		except:
			print('File could not be read')
			sys.exit()
	if(magic_string != ''): #prints the final string
		print(magic_string)

def it_broke(): #generic error statement
	print('Improper input: Expected int(minimum string length) string(filename)')
	sys.exit()

def main():
	if len(sys.argv) == 3:
		try:
			ml = int(sys.argv[1])
		except:
			it_broke()
		magic(ml,open_file(sys.argv[2]))
	else:
		it_broke()
if __name__== '__main__':
	main()
