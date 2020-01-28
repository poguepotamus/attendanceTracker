from enum import Enum
class PaymentType(Enum):
	NONE = 'No payment received'
	GOOD = 'No payment required'
	CASH = 'Payed in cash'
	CARD = 'Payed with card'
	OTHER = 'Some other form of payment acquired'

	def __str__(self):
		return self.name

def strToPaymentType(paymentType):
	if paymentType.upper() == 'NONE':
		return PaymentType.NONE
	elif paymentType.upper() == 'GOOD':
		return PaymentType.GOOD
	elif paymentType.upper() == 'CASH':
		return PaymentType.CASH
	elif paymentType.upper() == 'CARD':
		return PaymentType.CARD
	elif paymentType.upper() == 'OTHER':
		return PaymentType.OTHER
	else:
		return None

class Event():
	def __init__(self, title, eventType, payment=None, cost=0):
		self.title = title
		self.eventType  = eventType
		self.cost  = cost
		if payment is None:
			self.payment = PaymentType.NONE
		else:
			if type(payment) is PaymentType:
				self.payment = payment
			elif type(payment) is str:
				payType = strToPaymentType(payment)
				self.payment = payType if payType is not None else PaymentType.NONE

	def __iter__(self):
		yield 'title', self.title
		yield 'eventType', self.eventType
		yield 'cost', self.cost
		yield 'payment', self.payment