#!/usr/env python36

# Standard libs
from os import path
from re import search
from configparser import ConfigParser

# PySide
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QTimer, Qt

# Local modules
from Student import StudentWidget, Student, TEST_STUDENT
from Event import Event
from Database import FirestoreDatabase

class GUI(QtWidgets.QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Initalizing the UI
		loader = QUiLoader()
		# loader.registerCustomWidget(StudentWidget)
		self.UI = loader.load(path.join('attendanceTracker', 'assets', 'main.ui'))
		self.grabKeyboard()

		self.studentWidget = StudentWidget()
		self.UI.studentWidget.layout().addWidget(self.studentWidget.UI)
		self.studentWidget.setWidgetInformation(None)
		self.studentWidget.UI.saveButton.pressed.connect(self.saveStudentInfo)
		self.studentWidget.UI.clearButton.pressed.connect(self.grabKeyboard)
		# self.UI.menuButton.pressed.connect(self.foobar)

		self.database = FirestoreDatabase({
			'certificatePath': path.join('attendanceTracker', 'assets', 'firestoreCertificate.json'),
			'groupName': 'test',
			'semesterName': 'spring2020',
		})

		# Setting some state flags
		self.swipeData = ''

	def setup_show(self):
		# Creating the windows so we have something to find when looking for the window
		self.UI.show()

	def keyPressEvent(self, event):
		# Recording input text
		self.swipeData += event.text()

		# Ending our input when we see a return
		if event.text() in ['\r', '\n']:
			self.releaseKeyboard()
			self.processData(117)
			self.swipeData = ''

	def processData(self, expectedLength):
		if len(self.swipeData) < expectedLength:
			self.studentWidget.setWidgetInformation(None)

		else:
			studentID = self.getID(self.swipeData)
			student = self.database.studentLookup(studentID)
			if student is None:
				student = Student(
					self.getName(self.swipeData),
					self.getID(self.swipeData),
				)
			self.studentWidget.setWidgetInformation(student, Event('Febuary Lock-in', 'lockin'))

	def getName(self, data):
		return data.split('^')[1].strip()

	def getID(self, data):
		return search('[A-Z]\d\d\d[A-Z]\d\d\d', data).group()

	def saveStudentInfo(self):
		student = self.studentWidget.getWidgetInformation()
		from pprint import pprint
		print('Saving student:')
		pprint(dict(student))
		print('')
		self.database.saveStudent(student)

app = QtWidgets.QApplication()
gui = GUI()
gui.setup_show()
app.exec_()