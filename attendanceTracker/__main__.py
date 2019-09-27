#!/usr/env python36

from PySide2 import QtCore, QtUiTools, QtWidgets
from PySide2.QtCore import QTimer
from os import path
from re import search
# from googleapiclient import discovery
from configparser import ConfigParser

class remoteInfo():
	def __init__(self, remoteSettings):
		service = discovery.build(
			'sheets',
			'v4',
			credentials = remoteSettings['credentials'],
		)
		self.request = service.spreadsheets().values().get(
			spreadsheet_id = remoteSettings['spreadsheetID'],
		)

	def pullAllInfo(self):
		return self.request.execute()


class GUI(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		# Initalizing the UI
		self.window = QtUiTools.QUiLoader().load(path.join('attendanceTracker', 'assets', 'main.ui'))
		self.grabKeyboard()

		# Getting settings
		# self.config = self.setup_collectSettings(path.join('attendanceTracker', 'assets', 'settings.ini'))

		# Setting some state flags
		self.capture = False
		self.swipeData = ''
		self.timer = QTimer()

	def setup_collectSettings(self, file):
		config = ConfigParser()
		config.read(file)
		return config._sections

	def setup_show(self):
		# Creating the windows so we have something to find when looking for the window
		self.window.create()
		self.window.show()

	def keyPressEvent(self, event):
		# If our character represents the start of magstripe data
		if event.text() == '%' and not self.capture:
			print('Starting input capture')
			self.capture = True
			self.timer.singleShot(800, self.processData)

		# Capture is enabled, so we record the key
		if self.capture:
			self.swipeData += event.text()

	def processData(self):
		self.capture = False
		if len(self.swipeData) < 75:
			self.setStudentInfo('ERROR: Swipe data not received', f'Bad data: "{self.swipeData}"')
			self.swipeData = ''

		else:
			name  = self.getName(self.swipeData)
			stuID = self.getID(self.swipeData)
			numTickets = 0
			discordName = 'NOT PROVIDED'

			for num, line in enumerate(open('driveContent.csv')):
				if search(stuID, line):
					(name, discordName, stuID, numTickets) = [bite.strip() for bite in line.split(',')]

			self.setStudentInfo(
				self.getName(self.swipeData),
				self.getID(self.swipeData),
				str(int(numTickets) + 1),
			)

		self.swipeData = ''

	def getName(self, data):
		return data.split('^')[1].strip()

	def getID(self, data):
		return search('[A-Z]\d\d\d[A-Z]\d\d\d', data).group()

	def setStudentInfo(self, name='__name__', idNum='__id__', tickets='__##__'):
		self.window.student_name.setText(f'Full Name: {name}')
		self.window.student_id.setText(f'Student ID: {idNum}')
		self.window.student_tickets.setText(f'Ticket Count: {tickets}')


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