# -*- coding: utf-8 -*-
import os, sys

from PyQt4 import QtCore
import taglib
import json

def getAllTags(fileList):
    allTags = {}
    for file in fileList:
        for (key, value) in taglib.File(file).tags.items():
            if key in allTags:
                allTags[key].append(', '.join(value))
            else:
                allTags[key] = [', '.join(value)]
            # One liner to replace the if statement
            #allTags.setdefault(key,[]).append(', '.join(value))
    return allTags

'''
def getRepresentationAllTags(fileList):
    allTags = getAllTags(fileList)
    allRepr = {}
    for (key, value) in allTags.items():
        if len(value) != len(fileList):
            allRepr[key] = 'Multiple Values'
        elif value.count(value[0]) == len(value): #All items are equal
            allRepr[key] = value[0]
        else:
            allRepr[key] = 'Multiple Values'
    return allRepr
'''

def getRepresentationAllTags(fileList):
    allTags = getAllTags(fileList)
    return {key; value[0] if value.count(value[0]) == len(value) else 'Multiple Values' for (key, value) in allTags.item()}



def exploreMusicFolder(musicFolder, append):
	database =[]
	for root, dirs, files in os.walk(musicFolder, topdown=True):
		for name in files:
			if name.lower().endswith(".flac") or name.lower().endswith(".mp3"):
				path=os.path.join(root, name)
				file = taglib.File(path)
				dico = file.tags
				for key, value in dico.items():
					#if it's a list, concatenate, otherwise, take the value
					if len(dico[key]) == 1:
						dico[key]=value[0]
					else :
						dico[key]=', '.join(value)
				# Dict comprehension 1 liner
				# dico = {key: value[0] if len(file.tag[key]) == 1 else key: ', '.join(value) for (key, value) in file.tags.items()}
				dico['FILE'] = os.path.join('file://'+root, name)
				dico['LENGTH'] = file.length
				dico['SAMPLERATE'] = file.sampleRate
				dico['CHANNELS'] = file.channels
				dico['BITRATE'] = file.bitrate
				database.append(dico)

	sanitize(database)
	if append:
		db = load()
		database.extend(db)
		
	save(database)
	print('Finished scanning music folder')
	return database



def save(database):
	localFolder=os.path.dirname(os.path.realpath(__file__))
	with open(os.path.join(localFolder,'musicDatabase.json'), mode='w', encoding='utf-8') as f:
		json.dump(database, f, indent=2)
  

def load():
	localFolder=os.path.dirname(os.path.realpath(__file__))
	try:
		with open(os.path.join(localFolder,'musicDatabase.json'), 'r', encoding='utf-8') as f:
			return json.load(f)
	except IOError:
   		return []
     


def sanitize(database):
	for dico in database:
		if 'TRACKNUMBER' in dico:	
			try: 
				int(dico['TRACKNUMBER'])
				isInt = True
			except ValueError:
				isInt = False
			if isInt:
				dico['TRACKNUMBER']=str(int(dico['TRACKNUMBER']))

#Update the database, replacing all dicts in listDictTags
def updateDB(listDictTags):
    database = load()
    for i in range(len(database)):
        for j in range(len(listDictTags)):
            if database[i]['FILE'] == listDictTags[j]['FILE']:
                print('found')
                database[i] = listDictTags[j]
    save(database)

class WorkThread(QtCore.QThread):
	def __init__(self, musicFolder, append):
		QtCore.QThread.__init__(self)
		self.musicFolder = musicFolder
		self.append = append
		
	def run(self):
		exploreMusicFolder(self.musicFolder, self.append)




class WorkThreadPipe(QtCore.QThread):

	hotKey = QtCore.pyqtSignal(str)
   
	def __init__(self):
		QtCore.QThread.__init__(self)

	def run(self):
		#constantly read the pipe and emit a signal every time there is something to read
		pipein = open(os.path.join(sys.path[0], "pipe"), 'r')
		while True:
			line = pipein.read()
			if line != '':
				self.hotKey.emit(line.replace('\n', ''))
				#reopen because is kind of blocking and waiting for a new input
				pipein = open(os.path.join(sys.path[0], "pipe"), 'r')

