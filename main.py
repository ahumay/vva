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

	for line in poem:
		for word in line['line']:
			print word['word']
			print word['stress']

## main
if __name__ == '__main__':
	if len(sys.argv) < 2:
		filename = 'sample.txt'
	elif len(sys.argv) >= 2:
		filename = sys.argv[1]
	print '*** Using ', filename, ' ***'
	sys.exit(main(filename))