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
	for line in poem:
		print line['stressArray']
		line['unstressPRE'] = findPRE(line['stressArray'])
		line['unstressPOST'] = findPOST(line['stressArray'])
		line['unstressTWEEN'] = findTWEEN(line['stressArray'])
# -- get stats -- 
	stats = {}
	stats['pre'] = -9
	stats['post'] = -9
	stats['tween'] = -9
# store stuff in a dictionary	
	pre = freqStats(poem, 'unstressPRE')
	post = freqStats(poem, 'unstressPOST')
	tween = freqStats(poem, 'unstressTWEEN')
	
	stats['pre'] = pre
	stats['post'] = post
	stats['tween'] = tween

	print stats
	
	spenser = pre.keys()
	prePrim, preSec = spenser[0], spenser[1]
	print prePrim, pre[spenser[0]]
	print preSec, pre[spenser[1]]

			#	spenser = post.keys()
			#	print spenser
			#	postPrim, postSec = spenser[0], spenser[1]

			#	print postPrim, pre[spenser[0]]
			#	print postSec, pre[spenser[1]]

				# spenser = tween.keys()
				# tweenPrim, tweenSec = spenser[0], spenser[1]
				# print tweenPrim, pre[spenser[0]]
				# print tweenSec, pre[spenser[1]]

				# #-- { #unstressBeforeStress: value} etc
				# print "pre: ", pre
				# print "post: ", post
				# print "tween: ", tween

				# prePrim = firstSecond(pre)
				# print prePrim, "shows up: ", pre[prePrim]



				# # form = determineFoot(pre, post, tween)


def firstSecond(motorola):
	return max(motorola.iteritems(), key=operator.itemgetter(1))[0]
# http://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
# ^ sweeeeeeet

def determineFoot(pre, post, tween):
	form = dict(
		iambic={'before':1, 'after':0, 'tween':0},
		trochaic={'before':0, 'after':1, 'tween':1})


def freqStats(poem, thing):
	stats = {}
	x = []
	for line in poem:
		x.append(line[thing])
	for item in x:
		if item in stats:
			stats[item] += 1
		else: 
			stats[item] = 1
	return stats 



## main
if __name__ == '__main__':
	if len(sys.argv) < 2:
		filename = 'sample.txt'
	elif len(sys.argv) >= 2:
		filename = sys.argv[1]
	print '*** Using ', filename, ' ***'
	sys.exit(main(filename))