#!/bin/env python36
# Standard libs
from os.path import join as pathJoin

# PySide2 imports
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QWidget, QLabel, QLineEdit, QPlainTextEdit, QComboBox, QTableWidgetItem as QTableItem, QHeaderView, QSizePolicy
from PySide2.QtCore import Qt, Signal

# Local modules
from Event import Event, PaymentType

class Student():
	def __init__(self, name, ID, nick, questions={}, events=[]):
		self.name = name
		self.ID = ID
		self.nick = nick
		self.questions = questions
		self.events = events

	def addEvent(self, eventAttended):
		newEvents = eventAttended if type(eventAttended) is list else [eventAttended]
		# Checking to make sure we're all events here.
		for newEvent in newEvents:
			assert type(newEvent) == Event
		self.events += newEvents

	def getNumMeetings(self):
		return int(sum(map(lambda x: x.eventType.lower() == 'meeting', self.events)))

	def getNumEvents(self):
		return len(self.events)

	def __iter__(self):
		yield 'name', self.name
		yield 'ID', self.ID
		yield 'nick', self.nick
		yield 'questions', self.questions
		yield 'events', self.events

class StudentWidget(QWidget):
	saveStudentInfo = Signal()
	def __init__(self, student=None, eventTitle=None):
		super().__init__()
		# Loading our ui file and giving it some data
		self.UI = QUiLoader().load(pathJoin('attendanceTracker', 'assets', 'studentWidget.ui'))


		# Collecting variables from constructor
		self.student = student
		self.eventTitle = eventTitle

		# Setting initial values of our widget
		self.setWidgetInformation()

		# Setting some flags to make the window work
		self.editMode = False
		self.toggleEditable(False)

		# Binding some buttons
		self.UI.editButton.pressed.connect(self.toggleEditable)
		self.UI.clearButton.pressed.connect(self._clearInfo)

	def setWidgetInformation(self, student=None, eventTitle=None):
		from pprint import pprint
		if student is not None:
			pprint(dict(student))
		# Changing our student or event title information if given
		self.student = student if student is not None else self.student
		self.eventTitle = eventTitle if eventTitle is not None else self.eventTitle
		print(self.student)

		# Setting to display student details first
		self.UI.studentWidgetTabContainer.setCurrentIndex(0)

		# Setting our student details, questions, and event panel
		self._displayStudentDetails()
		self._displayStudentQuestions()
		self._displayEventDetails()

		# Setting our edit flag to false. This fixes formatting errors
		self.toggleEditable(False)

	def _displayStudentDetails(self):
		# Checking if we have a student currently
		if self.student == None:
			self.UI.studentDetailsStack.setCurrentIndex(0)
			self.UI.studentNickname.setText('')
			return
		self.UI.studentDetailsStack.setCurrentIndex(1)

		# Setting the student's general information
		self.UI.studentNickname.setText(self.student.nick)
		self.UI.studentName.setText(self.student.name)
		self.UI.studentID.setText(self.student.ID)
		self.UI.eventsAttended.setText(str(self.student.getNumEvents()))
		self.UI.meetingsAttended.setText(str(self.student.getNumMeetings()))

	def _displayStudentQuestions(self):
		# Checking if we have a student
		if self.student == None:
			self.UI.studentQuestionsStack.setCurrentIndex(0)
			return
		self.UI.studentQuestionsStack.setCurrentIndex(1)

		# Questions panel
		if self.student.questions not in [None, {}]:
			# Setting our widget and clearing its contents
			studentDetailsWidget = self.UI.studentQuestions
			[studentDetailsWidget.removeRow(0) for _ in range(studentDetailsWidget.rowCount())]

			# Iterating through our student's questions and adding them to our widget
			for currentRow, (label, field) in enumerate(self.student.questions.items()):
				labelWidget = QLineEdit(label)
				labelWidget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
				fieldWidget = QLineEdit(field)
				fieldWidget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
				studentDetailsWidget.addRow(labelWidget,fieldWidget)

	def _displayEventDetails(self):
		# Checking if we have a student
		if self.student == None:
			self.UI.eventDetailsStack.setCurrentIndex(0)
			self.UI.studentEventNoneLabel.setText('No student details found...')
			return
		# Checking if we have an event name
		elif self.eventTitle == None:
			self.UI.eventDetailsStack.setCurrentIndex(0)
			self.UI.studentEventNoneLabel.setText('No event details found...')
			return
		try:
			eventIndex = [event.title.lower() for event in self.student.events].index(self.eventTitle.lower())
		# If we don't have an event in our student structure, then we need to ask to check in
		except ValueError:
			self.UI.studentDetailsStack.setCurrentIndex(1)
			self.UI.studentWidgetTabContainer.setCurrentIndex(2)
			return
		self.UI.studnetDetailsStack.setCurrentIndex(2)

		# Setting event details
		event = self.student.events[eventIndex]
		self.UI.eventTitle.setText(event.title)
		self.UI.eventType.setText(event.eventType)
		self.UI.eventCost.setText(event.cost)
		self.UI.eventCost.setText(event.payment)

	def getWidgetInformation(self):
		# Collecting information from each panel
		studentDict = {
			'nick': self.ID.studentNickname.text(),
			'name': self.ID.studentName.text(),
			'ID':   self.ID.studentID.text(),
			'questions': self._getStudentQuestions()
		}
		return Student(**studentDict)

	def _getStudentQuestions(self):
		layout = self.UI.studentQuestions
		questions = {}
		for row in range(0, layout.rowCount()):
			questions[layout.itemAt(row, QFormLayout.LabelRole)] = layout.itemAt(row, QFormLayout.FieldRole)
		return questions

	def _clearInfo(self):
		print('Clearing information!')
		self.student = None
		self.event = None
		self.setWidgetInformation(None)

	def setup_show(self):
		self.UI.create()
		self.UI.show()

	def toggleEditable(self, editable=None):
		# Letting user specify is editable, or toggle
		self.editMode = (not self.editMode if editable is None else editable)
		print(f'Setting edit mode to {self.editMode}')
		# Setting all QLineEdits to accept changes
		for field in self.UI.findChildren(QLineEdit):
			if type(field) is QLineEdit:
				field.setFrame(False)
				field.setClearButtonEnabled(self.editMode)
			elif type(field) is QPlainTextEdit:
				field.setFrameStyle(0)
			field.setFont(self.UI.studentName.font())
			field.setReadOnly(not self.editMode)
			field.setStyleSheet('none;' if self.editMode else 'background-color: transparent;')

		defaultFont = self.UI.studentName.font()
		defaultFont.setPointSize(24)
		self.UI.studentNickname.setFont(defaultFont)

# Example student
TEST_STUDENT = Student(
	'Matthew Pogue',
	'H735F787',
	'AleX',
	{
		'test Details': 'cause they might be pretty cool!',
		'test Detasdfails': 'cause they might be pretty cool!',
		'test Deafdaftails': 'cause they might be pretty cool!',
		'test Defvdaftails': 'cause they might be pretty cool!',
		'test Defddaftails': 'cause they might be pretty cool!',
		'test Defdcaftails': 'cause they might be pretty cool!',
	},
	[
		Event('testEvent', 'meeting', None),
		Event('First lock-in', 'lock-in', PaymentType.CASH),
		Event('march meeting', 'meeting', PaymentType.CARD),
		Event('april meeting', 'meeting', PaymentType.NONE),
		Event('Another meeting', 'meeting', PaymentType.GOOD),
	],
)
if __name__ == '__main__':

	# Creating a qApplication if there isn't already one running
	from PySide2.QtWidgets import QApplication
	app = QApplication.instance()
	app = QApplication() if app is None else app

	# Creating a GUI
	studentPanel = StudentWidget(TEST_STUDENT)

	# Showing GUI and executing application
	studentPanel.setup_show()
	app.exec_()
