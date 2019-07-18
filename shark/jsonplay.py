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

def present (args, level = 0, newline = True):

	if type (args) == type ({}):
		print (' ' * level if newline else '', '{', sep='')
		keys = list (args.keys ())
		for i in range (len (keys)):
			print (level*' ', '"%s"' % keys[i], ': ', end = '');
			present (args [keys[i]], level + 3, newline = False);
			if i < len (keys) - 1:
				print (',')
			else:
				print ()
		print (level * ' ', '}', end = '', sep='')
	elif type (args) == type ([]):
		print (' ' * level if newline else '', '[', sep='')
		for i in range (len (args)):
			present (args [i], level + 3);
			if i < len (args) - 1:
				print (',')
			else:
				print ()	
		print (level * ' ', ']', sep='', end = '')
	elif type(args) == type(''):
		print (' ' * level if newline else '', '"%s"' % args, end = '', sep = '')
	else:
		print (' ' * level if newline else '', args, end = '', sep = '')
