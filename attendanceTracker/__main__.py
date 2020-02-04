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
		self.UI.menuButton.pressed.connect(self.foobar)

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
		self.studentWidget.setWidgetInformation(student)

	def getName(self, data):
		return data.split('^')[1].strip()

	def getID(self, data):
		return search('[A-Z]\d\d\d[A-Z]\d\d\d', data).group()

	def saveStudentInfo(self):
		self.database.saveStudent(self.studentWidget.getWidgetInformation())

	def foobar(self):
		self.studentWidget.setWidgetInformation(self.database.studentLookup('h735f787'))
		print('pulling information')

app = QtWidgets.QApplication()
gui = GUI()
gui.setup_show()
app.exec_()




# service = discovery.build('sheets', 'v4', credentials=credentials)

# # The ID of the spreadsheet to retrieve data from.
# spreadsheet_id = 'my-spreadsheet-id'  # TODO: Update placeholder value.

# # The A1 notation of the values to retrieve.
# range_ = 'my-range'  # TODO: Update placeholder value.

# # How values should be represented in the output.
# # The default render option is ValueRenderOption.FORMATTED_VALUE.
# value_render_option = ''  # TODO: Update placeholder value.

# # How dates, times, and durations should be represented in the output.
# # This is ignored if value_render_option is
# # FORMATTED_VALUE.
# # The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
# date_time_render_option = ''  # TODO: Update placeholder value.

# request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
# response = request.execute()

# # TODO: Change code below to process the `response` dict:
# pprint(response)