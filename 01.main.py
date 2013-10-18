
import sys, nltk, string
from nltk.corpus import cmudict

cmu = cmudict.dict()

def main(filename, privDict):
	pDict = []
	for line in open(privDict, 'r').readlines():
		if not(line.startswith('#')):
			word, syls = line.split(':')
			pDict.append(word.lower())

	for word in pDict:
		word = word.lower()


	poem = []
	poem = openFile(filename)
	poem = replaceStuff(poem)
# just in case there are two hyphens?
	poem = replaceStuff(poem)
# this is pretty terrible and ugly, but, whatever
	poem = fixProblems(poem)
# just in case some blank words got added
# though maybe we could just make words zero syl?

# start doing things
	for line in poem:
		flag = False
		for word in line:
			word = word.lower()
			if (word not in cmu) and (word not in pDict):
				print line
				outString = "What's this: " + word + " ?"
				stuff = raw_input(outString)
				x = open(privDict, 'a')
				y = word + ':' + stuff + '\n'
				x.write(y)
				x.close()



def PromptUser(line, query = "What should you do for this:"):
	print line

def fixProblems(poem):
	''' for items that may be just '' '''
	counter = 0
	for line in poem:
		for word in line:
			if word == '':
				pos = poem[counter].index('')
				del poem[counter][pos]
		counter += 1
	return poem

def replaceStuff(poem):
	counter = 0
	for line in poem:
		for word in line:
			if word == ' - ': 
				pos = poem[counter].index(' - ')
				del poem[counter][pos]
			elif word == '-':
				pos = poem[counter].index('-')
				del poem[counter][pos]
			elif '-' in word:
				wordA, wordB = replaceHyphen(word)
				pos = poem[counter].index(word)
				del poem[counter][pos]
				poem[counter].insert(pos, wordA)
				poem[counter].insert(pos+1, wordB)
		counter += 1
	return poem
#	findMissing(cmu, poem)

def replaceHyphen(word):
	# gets a word that has a hyphen, replaces the hyphen w/ a space
	# returns two words, wordA and wordB (left/right respectively)
	temp = word #store the word
	pos = temp.find('-') #find index of hyphen
	wordA = temp[:pos]
	wordB = temp[pos+1:]
	return wordA, wordB

def openFile(filename):
	''' opens a file, reads lines into list, returns list '''
	EXCLUDE = set('!"#$%&()*+,./:;<=>?@[\\]^_`{|}~')
	x = []
	f = open(filename)
	data = f.readlines()
	for datum in data:
		datum = ''.join(ch for ch in datum if ch not in EXCLUDE)
		temp = nltk.WhitespaceTokenizer().tokenize(datum)
		x.append(temp)
	return x

## main
if __name__ == '__main__':
	if len(sys.argv) < 2:
		filename = 'frost_woods.txt'
	elif len(sys.argv) >= 2:
		filename = sys.argv[1]
		privDict = sys.argv[2]
	print '*** Using ', filename, ' ***'
	sys.exit(main(filename, privDict))