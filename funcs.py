# funcs.py
# functions appear in order they're called

import nltk
from curses.ascii import isdigit
from nltk.corpus import cmudict
import nltk.data
import string
import sys
import pprint
import string
from copy import deepcopy

'''
Exclude all string.punctuation except apostrophe,
and hyphen.
'''
EXCLUDE = set('!"#$%&()*+,./:;<=>?@[\\]^_`{|}~')

CMU = cmudict.dict()

# Chances are these words should never be stressed.
UNSTRESSED = 'a an of the am and n for in is on or that to with'.split()
UNSTRESSED+= 'are as be by he him is her my she them em us we'.split()
UNSTRESSED+= 'its they their were you your'.split()
UNSTRESSED+= 'at do did from i it me but had has have our shall was will'.split()
UNSTRESSED+= 'dost hast hath shalt thee thou thy wilt ye'.split()
UNSTRESSED+= 'if how what when where who why can so this though which'.split()
UNSTRESSED+= 'could should would all like nor out too yet near through while whose'.split()
UNSTRESSED+= 'these those came come none one two three four five six eight nine ten'.split()
UNSTRESSED+= 'ah en et la may non off per re than un his'.split()

VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']

DIPHTHONGS = ['aa', 'ae', 'ai', 'ao', 'au',
              'ea', 'ee', 'ei', 'eo', 'eu',
              'ia', 'ie', 'ii', 'io', 'iu',
              'oa', 'oe', 'oi', 'oo', 'ou'
              'ua', 'ue', 'ui', 'uo', 'uu']

def openFile(poem, filename):
	'''
		poem(list poem, string filename)
		Opens the filename, reads the lines, tokenizes,
		while removing everything in EXCLUDE, and then
		stores it all in, and returns, "poem."
	'''
	f = open(filename)
	data = f.readlines()
	for datum in data:
		datum = ''.join(ch for ch in datum if ch not in EXCLUDE)
		temp = nltk.WhitespaceTokenizer().tokenize(datum)
		poem.append(temp)
	return poem

def makeWords(poem):
	'''
		Takes list poem.
		Returns a list consisting of:
			tempPoem: the poem as...
				line (dictionary):
					lower bounds for syl count
					upper bounds for syl count
					blank (bool) for blank line
					line (list) for the list of words
		Function iterates through poem, line by line, converting each
		word of the poem into a python dict composed of:
			word: word as string
			low: minimum syl count
			high: minimum syl count
			repl: if something's been replaced (like a 'd)
			inDict: if the word is in the dictionary
			stress: (list to eventually hold the stress symbols)

		for line in tempPoem:
			for word in line['line']:
				word['word']
	'''
	tempPoem = []
	for line in poem:
		tempLine = dict(line=[], lower=0, upper=0, blank=False, stressArray=[])
		if (line == []):
			tempLine['blank'] = True
		for word in line:
			temp = dict(word='', low=0, high=0, repl=False, inDict=False, stress=[])
			temp['word'] = word.lower()
			if '-' in temp['word']:
				tempX = dict(word='', low=0, high=0, repl=False, inDict=False, lastChar=False, stress=[])
				temp, tempX = replaceHyphen(temp, tempX)
					# see replaceHyphen function for description
				if (tempX['lastChar'] == False):
					replaceStuff(temp)
					tempLine['line'].append(temp)
					replaceStuff(tempX)
					tempLine['line'].append(tempX)
				else:
					replaceStuff(temp)
					tempLine['line'].append(temp)
			else:
				replaceStuff(temp)
				tempLine['line'].append(temp)
		tempPoem.append(tempLine)
	return tempPoem

def replaceStuff(word):
	'''
		Takes word (as dict).
		Modifies the dictionary as needed.
		Replaces: 'd endings with ed; 'n with en;
	'''
	temp = word['word'] #store original word to check if we replaced
	if (len(word['word']) > 1):
		if ((word['word'][-2] == "'")):
			if ((word['word'][-1] == "d") or (word['word'][-1] == "n")): # ends in 'd, 'n
				word['word'] = word['word'].replace(word['word'][-2], 'e')
		for punct in string.punctuation:
			word['word'] = word['word'].replace(punct, "") ## strip any other punctuation
	if (word['word'] == temp): ## did we replace anything?
		word['repl'] = False
	else:
		word['repl'] = True

def procLine(line):
	'''
		Receives line of poem
			(dict w/ upper/lower/blank/line (list of words as dicts)
		Checks each word in the line, gets syl count for word/line
	'''
	for w in line['line']: #for each word in line['line']
		w['inDict'] = checkDict(w['word'])
		getSyl(w) # get syl counts for each word
		getStress(w) # get stresses for each word
		line['lower'] += w['low']
		line['upper'] += w['high']

def getStress(w):
	if (w['inDict'] == True) and (w['word'] not in UNSTRESSED):
		lookup = w['word']
		lookup = CMU[lookup]	
		w['stress'] = doStress(lookup)
	elif (w['word'] in UNSTRESSED):
		lookup = w['word']
		w['stress'] = doStress(lookup)

def doStress(lookup):
	if lookup not in UNSTRESSED:
		return [i[-1] for i in lookup[0] if i[-1].isdigit()]
	else:
		return ['0']

def getSyl(word):
	'''
		Takes dictionary "word." Finds min/max syl count.
		Stores results in word['low'] and word['high'], respectively.
		If in CMU, use that. Otherwise, use dumbGuess.
	'''
	if (word['inDict'] == True) and (word['word'] not in UNSTRESSED):
		try:
			lowercase = word['word']
		except KeyError:
			lowercase = word['word'][:-1]
		word['low'], word['high'] = getSylCMU(lowercase)
	elif (word['word'] not in UNSTRESSED) and (word['inDict'] == False):
		lowercase = word['word']
		word['low'], word['high'] = dumbGuess(lowercase)
	else:
		word['low'] = 0
		word['high'] = 0

def getSylCMU(lowercase):
	'''
		Receives lowercase (a string).
		Returns two values, low and high.
		Checks CMU[dict] for the minimum and maximum syllable counts
	'''
	low = min([len([y for y in x if isdigit(y[-1])]) for x in CMU[lowercase]])
	high = max([len([y for y in x if isdigit(y[-1])]) for x in CMU[lowercase]])
	return low, high

def dumbGuess(lowercase):
	'''
		Receives lowercase (a string).
		Returns two values, low and high.
		Runs a dumb heuristic to determine a dumb syllable count.
	'''
	numSyl = 0
	numVowels = 0
	lastVowel = False
	for ch in lowercase:
		isVowel = False
		for v in VOWELS:
			if ((v == ch) and (lastVowel)):
				isVowel = True
				lastVowel = True
			elif ((v == ch) and not (lastVowel)):
				numVowels = numVowels + 1
				isVowel = True
				lastVowel = True
		if not isVowel:
			lastVowel = False
	if (lowercase[-2:] == 'es') or (lowercase[-1:] == 'e'):
		numVowels = numVowels -1
	return numVowels, numVowels ## low, and high

def replaceHyphen(wordA, wordB):
	'''
		Recieves two 'word' as dict, wordB is blank.
		Called from makeWords.
		Replaces hyphen with a space. Returns two values, the words pre/post-hyphen
		Note, this is really clumsy... replace hyphen in A with a space. Set temp
			to the split word. Split it at the space (thus making a list?). Set 
			wordA to 1st item of temp; wordB to 2nd item. Return both words (as dict)
			UNLESS the hyphen is at the last character.
	'''
	counter = 0
	for ch in wordA['word']:
		if (ch == '-'):
			counter += 1
	if ((counter == 1) and (wordA['word'][-1]=='-')):
		wordB['lastChar'] = True
	for punct in set('-'):
		wordA['word'] = wordA['word'].replace(punct, ' ')
	temp = wordA['word']

	if (wordB['lastChar'] == True):
		temp = temp.split(' ')
		wordA['word'] = temp[0]
		wordB['word'] = ' '
	else:
		temp = temp.split(' ')
		wordA['word'] = temp[0]
		wordB['word'] = temp[1]
	return wordA, wordB

def replaceStuff(word):
	'''
		Takes word (as dict).
		Modifies the dictionary as needed.
		Replaces: 'd endings with ed; 'n with en;
	'''
	temp = word['word'] #store original word to check if we replaced
	if (len(word['word']) > 1):
		if ((word['word'][-2] == "'")):
			if ((word['word'][-1] == "d") or (word['word'][-1] == "n")): # ends in 'd, 'n
				word['word'] = word['word'].replace(word['word'][-2], 'e')
		for punct in string.punctuation:
			word['word'] = word['word'].replace(punct, "") ## strip any other punctuation
	if (word['word'] == temp): ## did we replace anything?
		word['repl'] = False
	else:
		word['repl'] = True

def checkDict(word):
	'''
		Takes string (such as something['word']). Returns a boolean.
		Checks for existence of string in the CMU dict.
	'''
	found = True	
	if word not in CMU:
		if word[:-1] not in CMU:
			found = False
		found = False
	return found

def createStressArray(poem):
	'''
		Takes poem from main. Creates a list from the stresses.
		Stores this list in line['stressArray].
		This list is checked against existing lists of candidate meters (eventually)
			(See settings.py)
	'''
	for line in poem:
		# Do syllable counts for line look good?
		if (line['lower'] == line['upper']):
			# if so, we're gonna do something! yay! Things!
			# make list to hold stuff, descriptively called thing!
			thing = []
			counter = 0 #count syllables
			for word in line['line']:
				if word['word'] in UNSTRESSED:
					thing.append(0)
				elif word['word'] not in UNSTRESSED and word['inDict']:
					for item in word['stress']:
						if item is '1':
							thing.append(1)
						if item is '2':
							thing.append(1)
						if item is '0':
							thing.append(0)
				elif word['word'] not in UNSTRESSED and word['inDict'] == False:
					while counter < word['high']:
						thing.append(9)
						counter += 1
			line['stressArray'] = thing