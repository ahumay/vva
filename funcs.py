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