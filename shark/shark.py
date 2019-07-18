import sys
import argparse 
import HNhu
import json
from jsonplay import toDict, present

def main ():

	args = toDict (sys.argv[1:]) # Convert command line to dictionairy
	try:
		nhu = HNhu.HNhu ()
	except Exception as e:
		print (e, '. Stopped')
		return 

	result = nhu.request (args)

	present (result)

if __name__=='__main__':
	main ()
