#!/bin/env python36

# Firebase modules
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Local modules
from Student import Student
from Event   import Event

class FirestoreDatabase():
	'''
		Expects a dictionary with the following keys:
			certificatePath: The firestore database certificate dictionary. Usually parsed from a json file
			groupName: The name of the group using the attendance tracker.
			semesterName: The name of the current semester as a string in {season}{year} format. i.e. 'spring2020'
	'''
	def __init__(self, firestoreSettings):
		self._firebaseApp = firebase_admin.initialize_app(credentials.Certificate(str(firestoreSettings['certificatePath'])))
		self._firestoreClient = firestore.client()
		self._database = self._firestoreClient.collection(firestoreSettings['groupName']).document(firestoreSettings['semesterName'])
		self.students = self._database.collection('students')
		self.events = self._database.collection('events')

	### Student accessors
   #####################################
	def studentLookup(self, studentID=None):
		# Checking if studentID is a student
		if type(studentID) == Student:
			studentID = studentID.ID
		# Trying to find the ID as a document
		student = self.students.document(f'{studentID.upper()}@wichita.edu')
		studentDict = student.get().to_dict()
		if studentDict is None:
			print('Student not found', flush=True)
			return None
		studentDict['ID'] = student.id[:8]
		studentDict['events'] = []
		for event in student.collection('events').get():
			eventDict = event.to_dict()
			eventDict['title'] = event.id
			studentDict['events'].append(Event(**eventDict))
		return Student(**studentDict)

	def addStudent(self, student):
		self.saveStudent(student, new=True)

	def setStudent(self, student):
		self.saveStudent(student)

	def saveStudent(self, student, new=False):
		# Making sure the student doesn't already exist
		if new and self.studentLookup(student.ID) not in [[], None]:
			# Telling our caller that there was an error
			return 1
		else:
			# Casting our student to a dictionary
			studentDict = dict(student)
			# Translating student ID to an email
			del studentDict['ID']
			del studentDict['events']
			# Pushing that student's information to firebase
			self.students.document(f'{student.ID}@wichita.edu').set(studentDict)
			# Writing each event in our student to the database
			for event in student.events:
				eventDict = dict(event)
				del eventDict['title']
				eventDict['payment'] = str(event.payment)
				self.students.document(f'{student.ID}@wichita.edu').collection('events').document(event.title).set(eventDict)
			# Telling our caller that we added the student successfully
			return 0

# 	### Event accessors
#    #####################################
# 	def eventLookup(self, eventName=None):
# 		# Checking if eventName is an event
# 		if type(eventName) == Event:
# 			eventName = eventName.name
# 		try:
# 			for event in self.events.get():
# 				if eventName == event.name:
# 					return event
# 		except google.cloud.exceptions.NotFound:
# 			return None

# 	def getEvents(self):
# 		events = self._database.document('events').get()
# 		return [Event(**event) for event in events]

# 	def addEvent(self, event):
# 		self.saveEvent(self, event, new=True)

# 	def saveEvent(self, event, new=False):
# 		# Checking if event exists
# 		if self.eventLookup(self, eventName=None)

if __name__ == '__main__':
	from os import path
	from pprint import pprint

	foo = FirestoreDatabase({
		'certificatePath': path.join('assets', 'firestoreCertificate.json'),
		'groupName': 'test',
		'semesterName': 'spring2020',
	})

	from Student import TEST_STUDENT as bar

	print('`foo` is reference to firestore database', flush=True)
	print('`bar` is reference to test student', flush=True)
