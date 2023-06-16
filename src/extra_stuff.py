from datetime import datetime, timedelta
# Various small algorithms I carry with me from project to project. Most of them aren't even used here.


# For a given word, returns that word in upper case with all non-letter characters removed
def clean_word(word):
	cleaned = ""
	for char in word.upper():
		if 65 <= ord(char) <= 90:
			cleaned += char
	return cleaned


# For a given string, returns that string with all non-digit characters removed
def clean_word_digits(word):
	cleaned = ""
	for char in word:
		if 48 <= ord(char) <= 57:
			cleaned += char
	return cleaned


def count_words(string):
	num_words = 0
	in_word = False

	for char in string:
		# print(char)
		if in_word:
			if char.isspace():
				in_word = False
		elif not char.isspace():
			in_word = True
			num_words += 1

	return num_words


# Gets the current time with the time and second floored to zero
def get_datetime_rounded():
	time = datetime.now()
	zero = timedelta(microseconds=time.microsecond, seconds=time.second)
	return time - zero


def get_yesterday():
	time = get_datetime_rounded()
	yesterday = timedelta(hours=24)
	return time - yesterday


def get_epoch():
	return get_datetime_rounded().timestamp()
