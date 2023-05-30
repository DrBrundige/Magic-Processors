# I have no idea what this does or why I wrote it

class Condition:
	def __init__(self, key, value):
		self.key = key
		self.value = value

	def check(self, card):
		key = self.key
		value = self.value
		try:
			if key not in card:
				return False
			elif card[key] != value:
				return False
			else:
				return True
		except Exception as E:
			print("Errant operation!")
			print(E)
			return False


class ConditionList(Condition):
	def check(self, card):
		key = self.key
		value = self.value
		try:
			if key not in card:
				return False
			elif value not in card[key]:
				return False
			else:
				return True
		except Exception as E:
			print("Errant operation!")
			print(E)
			return False
