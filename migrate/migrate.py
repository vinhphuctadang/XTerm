from zipfile import ZipFile
import json
from os import path
from os import chdir

def customSplitExt (name):
	custom = path.splitext (name)
	if len (custom[0])>0 and custom[0][0] == '.':
		return ('', custom [0])
	return custom

def zipson (myzip, j, dir='.',space=0) :

	if 'content' not in j:
		raise ValueError ('Json wrong format: Container has no content key')
	for file in j['content']:
		if 'name' not in file:
			raise ValueError ('Json wrong format: %s' % str (file))
		tmp =  customSplitExt (file['name'])[1]
		# print (tmp);

		if (tmp == '.drive'):
			continue

		if 'content' not in file:
			print (' ' * space, "%-30s" % file['name'], sep ='', end='')
			try:
				myzip.write (dir+"\\"+file['name']);
			except Exception as e:
				print ('... ERROR:', e)
			print ('... %d byte(s)' % path.getsize (dir+"\\"+file['name']))
		else:
			print (' ' * space, file['name']+"\\", sep ='')
			zipson (myzip, file, dir+"\\"+file['name'], space+3)


def function (name = '.drive'):

	f = open (name, 'r')
	j = json.loads (f.read ())
	f.close ()
	
	fname = path.basename (name)
	fBaseNameNoExt = customSplitExt (fname) [0]
	fdir  = name [0:len (name)-len (fname)]	
	
	if (fdir == ''):
		fdir = '.'
	chdir (fdir)
	print ('At %s:' % path.abspath (fdir))
	myzip = ZipFile (fBaseNameNoExt+'.migration.zip', 'w')
	zipson (myzip, j)
	myzip.write (fname)

	print ('Done.')

def main ():
	import argparse
	import sys
	parser = argparse.ArgumentParser(description='Zipping for migration')
	parser.add_argument('--file', help='Specify which .drive file for migration', default = '.drive', type=str)
	# parser.add_argument('--help', help='Specify which .drive file for migration')
	try:
		args = parser.parse_args (sys.argv[1: ])
		function (args.file)
	except Exception as e:
		print ("Error found:", e)

	
if __name__ == '__main__':
	main ()
