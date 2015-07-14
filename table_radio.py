from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QStandardItemModel, QAbstractItemView, QStandardItem,
			QItemSelection, QItemSelectionModel, QTableView)

from PyQt4 import QtCore
from PyQt4 import QtGui

import song
from song import Song
from table_mother import TableMother

'''
Table interface
signal runAction(str) connected to Foo.tableAction
playingID
displays...
getStatus
'''

class TableRadio(TableMother):

	def addRow(self, song):
		attribs = song.getOptionalValuesDebug('%name%|'+self.radioConfig['prefered_informations'])
		
		
		nodes = [QStandardItem('')]
		nodes[-1].setData(song) #[-1] is last element
		for i in attribs:
			nodes.append(QStandardItem(i))
			nodes[-1].setData(song) #[-1] is last element
		self.model().appendRow(nodes) 

	def onTag(self, bus, msg):
		taglist = msg.parse_tag()
		
		song = self.model().item(self.playingId, 0).data()
		(emptiedStr, tagNames) = Song.getTagName(self.radioConfig['prefered_informations'])
		
		tagliststringarray = taglist.to_string()[:-1].split(',')[1:]
		for tagstring in tagliststringarray:
			(tagName, value) = tagstring.lstrip().split('=', 1)
			if tagName in tagNames:
				if 'string' in value:
					value = value.replace('(string)', '').replace('"', '')
				elif 'uint' in value:
					value = value.replace('(uint)', '')
				song.tags[tagName] = value.replace("\\", '')
		
		#self.model().columnCount()
		attribs = song.getOptionalValuesDebug(self.radioConfig['prefered_informations'])
		
		self.model().item(self.playingId, 2).setText(attribs[0])
		

	def __init__(self, parent, radioConfig):
		super(QtGui.QTableView, self).__init__(parent)
		self.radioConfig = radioConfig
		
		self.initUI()
        
	def initUI(self):
		
		self.playingId = -1

		model = QStandardItemModel()
		self.setModel(model)
		
		#self.selectionModel().selectionChanged.connect(self.selectionChangedCustom)
		


		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setTabKeyNavigation(False)		#Pas de changement de cellules avec tab
		self.setShowGrid(False)			#pas de traits entre les celules
		self.setAlternatingRowColors(True)	#Alternance des couleurs de lignes
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)	#Cellules pas editables
		self.setWordWrap(False)		#Pas de retour a la ligne
		
		#Dummy line to display headers
		self.addRow(Song({'FILE': '', 'LENGTH': '','CHANNELS': '', 'SAMPLERATE': '','BITRATE': None, 'NAME':''}, '%name%'+self.radioConfig['prefered_informations']))
		self.model().removeRow(0)

		#Fill in the header, with capital for the first letter(title())
		headers = ['Name','Informations']
		model.setHeaderData(0,QtCore.Qt.Horizontal,'')
		for i,h in enumerate(headers):
			model.setHeaderData(i+1,QtCore.Qt.Horizontal,h)

				
		#Don't bold header when get focus
		self.horizontalHeader().setHighlightSections(False)
		self.verticalHeader().hide()
		self.horizontalHeader().setStretchLastSection(True)
		self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive) #Interactive, ResizeToContents, Stretch
		
		
		stations = self.radioConfig['stations'].split('|')
		for station in stations:
			tags = dict(zip(['NAME','FILE'], [st.strip() for st in station.split('!')]))
			tags['LENGTH']=''
			tags['CHANNELS']=''
			tags['SAMPLERATE']=''
			tags['BITRATE']=''
			 
			self.addRow(Song(tags, '%name%'+self.radioConfig['prefered_informations']))
		
		self.resizeColumnsToContents()
		self.resizeRowsToContents()

		self.show()
		
		

	def keyPressEvent(self, event):
		
		if event.key() == Qt.Key_Return:
			self.runAction.emit('play')
		QTableView.keyPressEvent(self, event)



		
	def getStatus(self):
		#print(self.model().item(self.playingId, 0).data().toString())
		radioName = self.model().item(self.playingId, 0).data().tags['name']
		status = 'Radio '+ radioName +' - Playing'
		return status

