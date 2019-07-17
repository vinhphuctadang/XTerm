import sys
import argparse 
import HNhu
import json

def toDict (args):
	result = {}
	i = 0
	__len = len (args)
	bucket = []
	recent = ''

	while (i<__len):
		if args[i].find ('--') == 0:
			if i < __len - 1:
				if args[i+1].find ('--') != 0:
					recent = args[i][2:] 
					result [recent] = args[i+1]	
					i += 1			
				else:
					result [args[i][2:]] = "true"
			else:
				result [args[i][2:]] = "true"
		else:
			if type(result[recent]) == type ([]):
				result[recent].extends (args[i])
			else:
				result[recent] = [result[recent], args[i]] # As C++ is lacking of the feature
		i += 1
	return result

def main ():
	args = toDict (sys.argv[1:]) # Convert command line to dictionairy
	try:
		nhu = HNhu.HNhu ()
	except Exception as e:
		print (e.what (), '. Stopped')
		return 

	result = nhu.request (args)
	print (result)

if __name__=='__main__':
	main ()