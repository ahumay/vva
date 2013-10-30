#!/bin/python

from nltk.corpus import cmudict
from nltk.tokenize import RegexpTokenizer
import sys
import operator # Necessary for sorting dictionaries by value

CMU = cmudict.dict()
PRIVATEDICTIONARY = dict()
PUNCTUATION = '!"#$%&()*+,./:;<=>?@[\\]^_`{|}~\-'
EXCLUDE = set('!"#$%&()*+,./:;<=>?@[\\]^_`{|}~')



UNSTRESSED = """a an of the am and n for in is on or that to with 
              are as be by he him is her my she them em us we
              its they their were you your 
              at do did from i it me but had has have our shall was will 
              dost hast hath shalt thee thou thy wilt ye 
              if how what when where who why can so this though which 
              could should would all like nor out too yet near through while whose 
              these those came come none one two three four five six eight nine ten 
              ah en et la may non off per re than un his""".split()

def main(argv):
    poem = []

    # Load Private Dictionary
    
    try:
        filename = argv[0]
        infile = open(filename,'r')
    except:
        print "Problem opening ", filename

    # Loop through each line in the input file.
    for rawline in infile:
        poem.append(PoeticLine(rawline))

    beforeFirst = []
    afterLast = []
    between = []

    for line in poem:
        print line.rawtext,
        print line.scanned_line,
        print line.unstressedBetween
        beforeFirst.append(line.unstressedBeforeFirst)
        for val in line.unstressedBetween:
            between.append(val)
        afterLast.append(line.unstressedAfterLast)
        

    guess = guessMeter(beforeFirst, between, afterLast)
    
    print "Meter: ", guess[0]
    print "Confidence: ", guess[1]
#    print beforeFirst
#    print between 
#    print afterLast


#    print "beforefirst:" , beforeFirst
#    print "afterlast: ", afterLast
#    print "between: ", between
#    print "Top two vals unstress before:" , most_common_values(beforeFirst)
#    print "Top two vals unstress between:" , most_common_values(between)
#    print "Top two vals unstress after:" , most_common_values(afterLast)
"""
        for word in line.words:
            if not word.inDict: print '*',
            print word.text, 
            print '(',word.scansion,')'
        print
"""


def guessMeter(beforeFirstList, betweenList, afterLastList):
    """
    Following Plamondon's rules, this function uses lists of three values:
    - number of unstressed syllables before first stress
    - number of unstressed syllables between stresses
    - number of unstressed syllables after last stress
    to guess the meter (one of six: iambic, trochaic, trochaic catalectic,
    anapestic, dactylic, amphibrachic). This is returned as a string. 
    It also returns a confidence interval.
    """
    beforeFirst = most_common_values(beforeFirstList)[0]
    between = most_common_values(betweenList)[0]
    afterLast = most_common_values(afterLastList)[0]

    confidence = float(betweenList.count(between)) / float(len(betweenList))

    print "BETWEEN: ", between, ";", betweenList.count(between) , ":", len(betweenList)

    if(beforeFirst == 1) and (afterLast == 0) and (between == 1):
        meter = "iambic"
    else:
        if(beforeFirst == 0) and (afterLast == 1) and (between == 1):
            meter = "trochaic"
        else: 
            if(beforeFirst == 0) and (afterLast == 0) and (between == 1):
                meter = "trochaic catalectic"
            else:
                if(beforeFirst == 2) and (afterLast == 0) and (between == 2):
                    meter = "anapestic"
                else:
                    if(beforeFirst == 0) and (afterLast == 2) and (between == 2):
                        meter = "dactylic"
                    else:
                        if(beforeFirst == 1) and (afterLast == 1) and (between == 2):
                            meter = "amphibrachic"
                        else:
                            meter = "unknown"

    return (meter, confidence)
    


    



def tokenize_line(line):
    tokenizer = RegexpTokenizer('\s+', gaps=True)
    words = tokenizer.tokenize(line)

    # Remove punctuation from our punctuation list; this only
    # catches floating punctuation. Puncutation at the end of 
    # word remains, and will be stripped out during lookup.
    words = filter(lambda word:word not in EXCLUDE, words)

    return words

   

class PoeticWord():
    def __init__(self,raw_text=""):
        self.inDict = False
        self.text = raw_text.strip()
        self.scansion = self.word_lookup()

        return

    def fallback(self, string):
        """
        A simple function to syllabify and assign stress to words that 
        don't appear in CMU or in our personal dictionary.
        """
        return [0]


    def CMUDict_to_scansion(self, cmuList):
        """
        This function takes a CMU Dictionary list and simplifies it. 
        CMU gives a list representing pronunciation. E.g.:
        lovely = ['L', 'AH1', 'V', 'L', 'IY0']
        But we want not phonemes, but syllables and stresses.
        lovely = [1, 0]. 
        Total length of our list should be the total number of syllables, 
        with 0 representing no stress, 1 representing primary stress, and 2 as secondary stress.
        """
        verseList = []
        
        for item in cmuList:
            # See if the last character of the CMU representation of this phoneme is a digit.
            # i.e. does it mark a syllable break.
            if item[-1].isdigit():
                verseList.append(item[-1])

        return verseList


    def word_lookup(self):
        # Strip terminal punctuation from word.
        word = self.text.strip(PUNCTUATION)
        word = word.strip()
        word = word.lower()

        if word in UNSTRESSED:
            return [0]

        if word in CMU:
            self.inDict = True
            # Here we oversimplify CMU Dict's representation of a word by discarding alternate pronunciations
            return self.CMUDict_to_scansion(CMU[word][0])
        elif word in PRIVATEDICTIONARY:
            self.inDict = True
            return PRIVATEDICTIONARY[word]
        else:
            return self.fallback(word)
               

class PoeticLine():
    def __init__(self, rawtextline=""):
        self.rawtext = rawtextline
        self.words = []
        self.scanned_line = []
        self.unstressedBeforeFirst = 0
        self.unstressedBetween = []
        self.unstressedAfterLast = 0

        rawWords = tokenize_line(rawtextline)

        # Do our best to guess at stress for each word.
        for word in rawWords:
            verse_word = PoeticWord(word)
            self.words.append(verse_word)

        # Now add all those word syllables together, 
        # representing the line's scansion.
        for word in self.words:
            for syllable in word.scansion:
                self.scanned_line.append(syllable)

        self.update_counts()

        return 

    def update_counts(self):
        # Reset our list
        self.unstressedBetween = []

        firstFound = False
        count = 0
        
        # Loop through all the syllables.
        for syllable in self.scanned_line:

            if (int(syllable) > 0):        # If we've found a stress
                if not firstFound:         # Is it our first?
                    firstFound = True
                    self.unstressedBeforeFirst = count 
                    count = 0
                else: 
                    self.unstressedBetween.append(count)
                    count = 0
            else:
                count += 1

        # When we exit the loop, whatever value count has, is the
        # number of unstressed after the last stress.
        self.unstressedAfterLast = count
        return
            

def most_common_values(alist):
    """
    This function takes a list of values and returns the most frequently
    occuring value and the second most frequently occurring value as a tuple.
    """
    # We'll loop through our list, converting them to a dictionary 
    # of frequencies.
    freqs = {}
    for value in alist:
        if value in freqs:
            freqs[value] += 1
        else: 
            freqs[value] = 1

    # Sort the dictionary by value and return the two most 
    # frequently occuring values.
    sorted_freqs = sorted(freqs.iteritems(), key=operator.itemgetter(1), reverse=True)

    print sorted_freqs

    if(len(sorted_freqs) > 1):
        return (sorted_freqs[0][0], sorted_freqs[1][0])
    else:
        return (sorted_freqs[0][0], None)
    

if __name__ == "__main__":
    main(sys.argv[1:])
