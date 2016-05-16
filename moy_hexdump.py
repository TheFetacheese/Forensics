#Alexander Moy
#cs365 hw1
import sys

def main():
	try:
		filename = sys.argv
	except:
		print("Improper input") #don't think this line can be encountered
		sys.exit(0)
	try:
		f = open(filename[1], 'rb')
	except IndexError:
		print("No input was given")
		sys.exit(0)
	except IOError:
		print(filename[1] + " does not exist")
		sys.exit(0)
	except:
		print("Unknown Error", sys.exec_info()[0])
		sys.exit(0)
		
	
	counter = 0 #number of bytes read so far
	try:	
		line = f.read(16)
	except:
		print("No data could be read") #don't think this line can be encountered
	try:
		while(len(line) > 0):
			print(format(counter, 'x').zfill(8), end="  ") #print bytes read with at least 8 digits
		
			#iterate byte hex values
			for x in range (0,len(line)):	
				print(hex(line[x])[2:].zfill(2), end=" ")
				if (x == 7): #awkward space
					print(" ", end="")
				counter += 1 #increment amount of bytes readi
	
			#adjust spaces on last line
			if(len(line) < 16):
				for x in range (0, 16-len(line)):
					print("   ", end="")
				if(len(line) < 8): #awkward space
					print(" ", end="")
	
			print(" |", end="")

			for x in range (0,len(line)):
				if(line[x] > 31 and line[x] < 127): #print character if ascii
					print(chr(line[x]), end="")
				else:
					print(".", end="")	#print . if not ascii
			print("|")
	
			line = f.read(16)
		f.close
		print(format(counter, 'x').zfill(8)) #print total bytes
	except:
		print("Unknown error", sys.exc_info()[0])
		sys.exit(0)
if __name__=='__main__':
	main()
