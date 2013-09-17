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

## main
if __name__ == '__main__':
	if len(sys.argv) < 2:
		filename = 'sample.txt'
	elif len(sys.argv) >= 2:
		filename = sys.argv[1]
	print '*** Using ', filename, ' ***'
	sys.exit(main(filename))