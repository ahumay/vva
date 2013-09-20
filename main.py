from funcs import *

def main(filename):
	'''
	Takes filename from calling sequence.
	Or defaults to "sample.txt"
	'''
	poem = [] #place to store poem
	poem = openFile(poem, filename)
	poem = makeWords(poem)
	for line in poem:
		procLine(line)
	createStressArray(poem)

#output stuff
	for line in poem:
		outstring = ""
		for word in line['line']:
			outstring += str(word['stress'])
			outstring += word['word']
			outstring += " "
		print outstring
	for line in poem:
		outstring = ""
		for item in line['stressArray']:
			outstring += '  ' + str(item) + ' '
		print outstring

# -- gok --
	unstressPRE = 0
	unstressPOST = 0
	unstressTWEEN = 0
	for line in poem:
		print line['stressArray']
		unstressPRE = findPRE(line['stressArray'])
		unstressPOST = findPOST(line['stressArray'])
		print "      ", "pre = ", unstressPRE, " post = ", unstressPOST


def findTWEEN(line):
	'''
		"It also counts the number of unstressed syllables that occur 
		between two consecutive stressed syllables throughout the poem.
		-- M.R. Plamondon "Virtual Verse Analysis..." p132

		So what if I got 0 1 0 1 0 1 0 1 0 1 0 1... which consecutive?
		"

		
	'''

def findPOST(line):
	counter = 0 #init
	for item in reversed(line):
		if (item == 1):
			break
		elif (item == 0):
			counter += 1
	return counter

def findPRE(line):
	counter = 0 # init
	for item in line:
		if (item == 1):
			break
		elif (item == 0):
			counter += 1
	return counter



## main
if __name__ == '__main__':
	if len(sys.argv) < 2:
		filename = 'sample.txt'
	elif len(sys.argv) >= 2:
		filename = sys.argv[1]
	print '*** Using ', filename, ' ***'
	sys.exit(main(filename))