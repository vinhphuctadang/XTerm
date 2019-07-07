import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google. auth.transport.requests import Request
from apiclient.http import MediaFileUpload,MediaIoBaseDownload
import json
import fnmatch
import io
import sys
import hashlib
from threading import Thread, Lock
import time

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
isDebug = True
stuffCount = 0
mutex = Lock ()
creds = None
credFile = '\\credentials.json'
pickleFile = '\\token.pickle'

def log (msg):
	global isDebug
	if isDebug:
		print (msg)
def __changeQuote (msg):
	__convert = ""
	for i in msg:
		if (i == "'"):
			__convert += '"'
		else:
			__convert += i
	return __convert
def getRootPath ():
	path = os.path.abspath(__file__)
	dir_path = os.path.dirname(path)
	return dir_path

def matchPattern (file, pattern=[]):
	for fPat in pattern:
		if fnmatch.fnmatch (file, fPat):
			return True
	return False

def buildTree(walk,fPat=['*.*'],fSpec='.drive',ignoreSub=False):

	try:
		root, dirs, files = next (walk) # preorder search
	except:
		return []

	fColl = []
	# print (fPat)
	for file in files:
		item = {}
		if (matchPattern (file, fPat) and file != fSpec):
			# f = open (root + "\\" + file, "rb")
			# s = hashlib.md5 (f.read ())
			item['name'] = file
			# item['md5'] = s.hexdigest () 
			fColl.append (item)
		
		
	# print("build tree ig: ", ignoreSub)
	if not ignoreSub:
		for dir in dirs:
			item = {}
			item['name'] = dir
			tmp = buildTree(walk,fPat,ignoreSub)
			item['content'] = tmp
			fColl.append (item)
	return fColl
def listFile (fPat = ['*'],ignoreSub=False):
	result = {}
	result ['name'] = os.getcwd ()
	# print ("LF ignoreSub: ", ignoreSub)
	result ['content'] = buildTree (os.walk('.'), fPat, ignoreSub=ignoreSub)
	return result
def saveFileList (list, fname='.drive'):
	
	content = __changeQuote (str(list))
	
	try:
		f = open (fname, 'w', encoding='utf-8')
		f.write (content)
		f.close ()		
	except Exception as e:
		print ('exception while writing to "%s":' % fname, e)
		return 

def readFileList (fname='.drive'):
	try:
		f = open (fname, 'r', encoding='utf-8')
		content = f.read ()
		j = json.loads (content)
	except Exception as e:	
		print (e)
		return []
	return j

def changeStuffCount (change):
	mutex.acquire ()
	global stuffCount
	stuffCount += change
	mutex.release ()

def getStuffCount ():
	mutex.acquire ()
	global stuffCount
	result = stuffCount
	mutex.release ()
	return result

def wait ():
	while getStuffCount () != 0:
		pass
def getCreds ():
	global creds
	if creds:
		return creds

	if os.path.exists(getRootPath ()+pickleFile):
		with open(getRootPath ()+pickleFile, 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				getRootPath ()+credFile, SCOPES)
			creds = flow.run_local_server()
		# Save the credentials for the next run
		with open(getRootPath ()+ '\\token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	return creds

def createService ():
	drive_service = build('drive', 'v3', credentials=getCreds ())
	return drive_service

def checkFolderExist (drive_service, fname, fContainer):

	rId = ''
	page_token = None
	query='name = "%s" and "%s" in parents and mimeType = "application/vnd.google-apps.folder"'%(fname,fContainer)

	rep = drive_service.files ().list (q=query,
											spaces='drive',
											fields='nextPageToken, files(id,name)',
											pageToken = page_token).execute ()

	result = rep.get ('files',[])
	if result != []:
		rId = result[0].get('id')
	return rId
def checkFileExist(drive_service, fname, fparentId):
	rId = ''
	page_token = None
	query='name contains "%s" and "%s" in parents' % (fname, fparentId)
	#print("query=", query)
	rep = drive_service.files ().list (q=query,
											spaces='drive',
											fields='nextPageToken, files(id,name)',
											pageToken = page_token).execute ()
	result = rep.get ('files',[])
	if result != []:
		rId = result[0].get('id')
	
	return rId	
def uploadFile (drive_service, fname, fSrcName, fparentId):
	try:
		id = checkFileExist (drive_service, fname, fparentId)
		media = MediaFileUpload('%s' % (fSrcName),
								mimetype='*/*',
								resumable=True)
		if id != '':
			file_metadata = {
				'name': fname,
				'mimeType': '*/*'
			}
			
			file = drive_service.files().update (fileId=id,body=file_metadata, media_body=media, fields='id').execute ()

			
		else:
			file_metadata = {
				'name': fname,
				'parents': [fparentId],
				'mimeType': '*/*'
			}
			
			file = drive_service.files().create (body=file_metadata, media_body=media, fields='id').execute()
	except Exception as e:
		print (e)
		return ''
	return file.get('id')
def createFolder (drive_service, fCollectName, fContainer):

	id = checkFolderExist (drive_service, fCollectName, fContainer)
	if id != '':
		return id

	file_metadata = {
		'name': fCollectName,
		'parents':[fContainer],
		'mimeType': 'application/vnd.google-apps.folder'
	}
	try:
		
		file = drive_service.files().create(body=file_metadata,
										fields='id').execute ()
	except Exception as e:
		print (e)
		return ''
	return file.get('id')
def getFileNameById (drive_service, fId='root'):
	try:
		file = drive_service.files().get (fileId=fId).execute ()
	except Exception as e:
		print (e)
		return "NotFound"
	return file['name']
def getUploadedFolder (drive_service, fname='.drive'):
	result = []
	rId = ''
	page_token = None
	query='name = "%s"' % fname;
	#print("query=", query)
	
	rep = drive_service.files ().list (q=query,
											spaces='drive',
											fields='nextPageToken, files(id,name,parents)',
											pageToken = page_token).execute ()
	tmp = rep.get ('files',[])
	for file in tmp:
		try:
			parents = file['parents']
		except:
			continue
		if (parents != []):
			result.append ({'name':parents[0], 'id':getFileNameById (drive_service, parents[0])})
	return result
def collectUploadedFiles (drive_service, folderId):
	page_token = None
	query='"%s" in parents' % folderId
	file_service = drive_service.files ()
	request = file_service.list (q=query,
											spaces='drive',
											fields='nextPageToken, files(id,name,mimeType)',
											pageToken = page_token)
	res = []
	while request is not None:
		result = request.execute ()
		files = result.get ('files',[])
		res.extend (files)
		request = file_service.list_next (request, result)
	return res

def __uploadThread (drive_service, name, dir, parentId):
	changeStuffCount (+1)
	try:
		id = uploadFile (drive_service, name, dir + '\\' + name, parentId)
	except Exception as e:
		print ("Problem while uploading:",e)
		changeStuffCount (-1)
		return
	changeStuffCount (-1)
	mutex.acquire ()
	if (id != ''):
		print ("Success:%s(Id=%s)"%(dir + '\\' + name, id))
	else:
		print ("Failed:%s"%(dir + '\\' + name))
	mutex.release ()

def uploadByList (drive_service, dir, node, parentId):
	for file in node:
		if 'content' in file:		
			id = createFolder (drive_service, file['name'], parentId)
			uploadByList (drive_service, dir + '\\' + file['name'], file['content'], id)
			print ("Updated Folder:%s(Id=%s)"%(dir + '\\' + file['name'], id))
		else:
			thread = Thread (target=__uploadThread, args=(createService (), file['name'], dir, parentId,))
			thread.start ()

def driveUpload (drive_service,theWrapFolderName, capFile='.drive'):
	j = readFileList ()
	id = createFolder (drive_service, theWrapFolderName, 'root')
	log ("Folder '%s' created in root" % theWrapFolderName)
	uploadByList (drive_service, '.', j['content'], id)
	uploadFile (drive_service, capFile, capFile, id)

def rawDownloadById (drive_service, fId, fStream):
	
	request = drive_service.files().get_media(fileId=fId)
	downloader = MediaIoBaseDownload(fStream, request)
	done = False
	try:
		while done is False:
			status, done = downloader.next_chunk()
	except:
		log ("Error while downloading file '%s'" % fId)
		return -1
	return 0
	
def downloadById (drive_service, fId, fname): #unhandled exception, download to file
	fh = open (fname, "wb")
	rawDownloadById (drive_service, fId, fh)
	fh.close ()

def driveDownload (drive_service, theWrapFolderName):
	id = checkFolderExist (drive_service, theWrapFolderName, 'root')
	if id == '':
		# log ("Folder '%s' doesn't found or wasn't been uploaded by this driver")
		raise ValueError ("'%s' can not be found"%theWrapFolderName)
		return -1
	log ("Folder '%s' founded: id = %s" % (theWrapFolderName, id))
	driveRawDownload (drive_service, id, '.')
def __downloadThread (drive_service, id, name, dir):
	changeStuffCount (+1)
	try:
		downloadById (drive_service, id, dir+'\\'+name)	
	except Exception as e:
		print ("Problem while downloading:",e)
		changeStuffCount (-1)
		return	
	changeStuffCount (-1)
	print ('Downloaded "%s" to be "%s"' % (id, name))
	# print ('Downloaded')
def driveRawDownload (drive_service, nodeId, dir):
	files = collectUploadedFiles (drive_service, nodeId)
	
	if not os.path.exists (dir):
		print ('There is no "%s", going to create: '%dir,end='...')
		os.makedirs (dir)
		print ('Created')
	
	for file in files:
		if file.get('mimeType','') == 'application/vnd.google-apps.folder':
			driveRawDownload (drive_service, file['id'], dir+'\\'+file['name'])
		else:
			thread = Thread (target = __downloadThread, args=(createService (), file['id'], file['name'], dir,))
			thread.start ()

def matchDir (src, root): #
	__src = src.split ('\\')
	__root = root.split ('\\')
	if os.path.exists (__src[0]):
		return src
	res = __root[0]+"\\"
	for i in range(1, len(__src)):
		res += __src[i]+'\\'
	return res
def driveSync (drive_service, theWrapFolderName, defRDir = getRootPath (), defFname='.drive'):
	id = checkFolderExist (drive_service, theWrapFolderName, 'root')
	if id == '':
		log ("No such folder with name '%s'" % theWrapFolderName)
		return

	capFile = checkFileExist (drive_service, defFname, id)
	if capFile == '':
		log ("No caption file '.drive' found, something might be missing")
		return 
	
	fStream = io.BytesIO ()
	if rawDownloadById (drive_service, capFile, fStream) == 0:
		fStream.seek (0)
		j = json.loads (fStream.read())
		defDir = j['name']#first j name contain dir
		finDir = matchDir (defDir, defRDir)
		if finDir != defDir:
			print ("Sync at %s"%finDir)
		driveRawDownload (drive_service, id, finDir)
	else:
		log("An error occur while reading capFile") 
# interface:

'''
upload <wrapFolderName> == create the '.drive' and upload it to drive with wrapName as the same folder name
download <wrapFolderName> == first download the wrapFolder 
	download throught the discription of .drive, if .drive does not exist, the process failed
sync  <wrapFolderName>: download the find and put it into the static directory given by .drive
'''
def main ():
	now = time.time ()
	
	commandList = ['init - get current directory discription', 'iup - upload with discription in .drive', 'upload - upload with default init call', 'download - download the specific uploaded folder', 'rdirs - list out uploaded folders']
	if len (sys.argv) < 2:
		print ('Command needed. Help shown beblow:')
		for command in commandList:
			print (command)	
	elif sys.argv[1] == 'init':
		ignoreSub = False;
		if len (sys.argv) < 3:
			pattern = '*.*'
		else:
			pattern = sys.argv[2]
		if len (sys.argv) > 3:
			if sys.argv[3] == '-i':
				ignoreSub = True;
		# print (ignoreSub)
		tmp = listFile (pattern.split(','), ignoreSub)
		
		#print (tmp)
		saveFileList (tmp)
	elif sys.argv[1].lower () == 'iup':
		drive_service = createService ()
		try:
			driveUpload (drive_service, sys.argv[2])
			wait ()
		except Exception as e:
			print ("Error ", e)
	elif sys.argv[1].lower () == 'upload':
		log ('initializing...')
		saveFileList (listFile ())
		log ('start uploading')
		drive_service = createService ()
		try:
			driveUpload (drive_service, sys.argv[2])
			wait ()
		except Exception as e:
			print ("Error ", e)
	elif sys.argv[1].lower () == 'download':
		try:
			drive_service = createService ()
			driveDownload (drive_service, sys.argv[2])
			wait ()
		except Exception as e:
			print ("Error ", e)
	elif sys.argv[1].lower () == 'sync':
		try:
			drive_service = createService ()
			driveSync (drive_service, sys.argv[2])
			wait ()
		except Exception as e:
			print ("Error ", e)
	elif sys.argv[1].lower () == 'rdirs':
			drive_service = createService ()
			for element in getUploadedFolder (drive_service):
				print ('name: %-50s, id: %s' % (element['id'], element['name']))
	print ('execution time:', (time.time () - now), 'second(s)')
if __name__ == '__main__':
	main ()
