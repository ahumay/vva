#!/bin/python

from nltk.corpus import cmudict
from nltk.tokenize import RegexpTokenizer
import sys
import operator # Necessary for sorting dictionaries by value
import hyphen # Necessary for syllabification

CMU = cmudict.dict()
PRIVATEDICTIONARYFILENAME = 'private.dictionary'

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

privateDictionary = {}

def loadPrivateDict():
    """
    This function loads the private dictionary file found in the global variable 
    PRIVATEDICTIONARYFILENAME. It also calculates normalized scores for each of the 
    terms. These scores represent how many of the scanned instances of a key term are
    represented by a single scanscion. If, for instance, we have seen the word "almost" 
    three, times, always scanned as a trochee, it would have one entry in our private 
    dictionary, with a score of 1.00. If however we observe it four times, twice as a trochee,
    one as an iamb (!) and once as a pyrhuss (!!), our private dictionary would have three
    entries for the single key "almost": the iambic entry would have a score of 0.50, the 
    pyrhic and trochaic entries would each have scores of 0.25.
    """
    privateDict = {}

    for line in open(PRIVATEDICTIONARYFILENAME,'r').readlines():
        if not(line.startswith('#')):
            word, scanscion, frequency = line.split(',')
            if word in privateDict:
                privateDict[word].append((scanscion, int(frequency)))
            else:
                privateDict[word] = [(scanscion, int(frequency))]

    # Now loop back through to normalize scores.
    for word in privateDict.keys():
        total = 0

        for scantuple in privateDict[word]:
            total += scantuple[1]

        normalized = []
        for scantuple in privateDict[word]:
            normalized.append((scantuple[0], float(scantuple[1])/float(total)))

        # Now replace the entry for the word with the normalized list.
        privateDict[word] = normalized
                                 
    return privateDict

class Poem():
    global privateDictionary 
    privateDictionary = loadPrivateDict()

    def __init__(self,rawtext):
        self.lines = []

        # The following three variables count lists that 
        # store information about the location of stress
        # throughout the poem used to guess its prevailing meter.
        self.beforeFirstList = []
        self.afterLastList = []
        self.betweenList = []

        text = rawtext.split('\n')

        self.title = text[0].strip('#').strip()
        
        for line in text:
            if not(line.startswith('#')) and (line):
                self.lines.append(PoeticLine(line))

        for line in self.lines:
            self.beforeFirstList.append(line.unstressedBeforeFirst)
            for val in line.unstressedBetween:
                self.betweenList.append(val)
            self.afterLastList.append(line.unstressedAfterLast)

    def __str__(self):
        output = ""

        for line in self.lines:
            output += line.rawtext + '\n'

        return output

    def promoteUnstressed(self):
        if(self.doubleMeter):
            for line in self.lines:
                line.promote_unstressed(meter='double')
                line.update_counts()
        if(self.tripleMeter):
            for line in self.lines:
                line.promote_unstressed(meter='triple')
                line.update_counts()

    def doubleMeter(self):
        """
        Guesses whether this poem is written in a double meter (iambic, trochaic).
        Returns True or False.
        """
        if self.guessMeter()[0] in ['iambic', 'trochaic', 'trochaic catalectic']:
            return True
        else:
            return False

    def tripleMeter(self):
        """
        Guesses whether this poem is written in a triple meter (anapestic, dactylic).
        Returns True or False.
        """
        if self.guessMeter()[0] in ['anapestic', 'dactylic', 'amphibrachic']:
            return True
        else:
            return False

    def html(self):
        # Print HTML header
        print """
          <!DOCTYPE html>
          <html>
            <head>
              <meta charset='utf-8'>
              <title>"""+self.title+"""</title>
              <link rel='stylesheet' href='scansion.css'>
            </head>

            <body>
          """

        current_line = 0

        # Start looping through poem.
        for line in self.lines:
            current_line += 1
            line_output = "<p class='line'>"
            capitalized = False
            terminalPunctuation = ''

            position = 0

            for word in line.words:
                # Let's save initial capitalization and terminal punctuation
                # in the original to restore it in the output. We could add hyphenation
                # here, and other things that we are stripping out in the interest 
                # of analysis.
            
                if(word.text[0].isupper()): 
                    capitalized = True
                    if(word.text[:-1] in PUNCTUATION): 
                        terminalPunctuation = word.text[:-1]

#                print "Word: ", word.text, "Syllables: ", word.syllables, " Scanscion: ", word.scansion
                outword = ''
                syllNo = 0
                syllTotal = len(word.syllables)
                for syllable in word.syllables:
                    syllNo += 1

                    stress = line.scanned_line[position]

                    if not(stress):
                        outword += syllable
                    elif (stress == 2):
                        outword += "<span class='secondary'>"+syllable+"</span>"
                    else:
                        outword += '<strong>'+syllable+'</strong>'
                    if (syllNo < syllTotal):
                        outword += '&middot;'
                    position += 1

                outword += terminalPunctuation

                line_output += outword + ' ' 

            line_output += "</p>"
            print line_output


            # Print html footer
        print """
                </body>
              </html>"""

    def guessMeter(self):
        """
        Following Plamondon's rules, this function uses lists of three values:
        - number of unstressed syllables before first stress
        - number of unstressed syllables between stresses
        - number of unstressed syllables after last stress
        to guess the meter (one of six: iambic, trochaic, trochaic catalectic,
        anapestic, dactylic, amphibrachic). This is returned as a string. 
        It also returns a confidence interval.
        """
        beforeFirst = most_common_values(self.beforeFirstList)[0]
        between = most_common_values(self.betweenList)[0]
        afterLast = most_common_values(self.afterLastList)[0]

        confidence = float(self.betweenList.count(between)) / float(len(self.betweenList))

#        print "BETWEEN: ", between, ";", self.betweenList.count(between) , ":", len(self.betweenList)

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

        


class PoeticWord():
    def __init__(self,raw_text=""):
        self.inDict = False
        self.text = raw_text.strip()
        self.scansion = self.word_lookup()
        self.syllables = self.syllabify()
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
                verseList.append(int(item[-1]))

        return verseList

    def PrivDict_to_scansion(self, privString):
        """
        This function takes an entry from our Private Dictionary and simplifies it. 
        Private Dictionary gives a string representing scansion:
        lovely = "love* ly"
        But we want not phonemes, but syllables and stresses.
        lovely = [1, 0]. 
        Total length of our list should be the total number of syllables, 
        with 0 representing no stress, 1 representing primary stress, and 2 as secondary stress.
        """
        verseList = []
        
        for syllable in privString.split():
            # See if the last character of the string representation of this syllable
            # is an asterisk (i.e. does it mark a stress).
            if syllable[-1] == '*':
                verseList.append(1)
            else:
                verseList.append(0)

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
        elif word in privateDictionary:
            self.inDict = True

            # Right now we return the scanscion with the greatest frequency.
            return self.PrivDict_to_scansion(privateDictionary[word][0][0])

        else:
            return self.fallback(word)

    def syllabify(self):
        """
        This function uses the hyphen package to develop a plausible hyphenation
        of a term. If first grabs all places, according to hyphen, a word could be 
        hyphenated; it then reduces that list based on what we observed. This is a
        some janky way of trying to maintain information about the word and the scanscion
        so that we can have a nice, pleasing output.
        """
#        hyphenator = hyphen.Hyphenator('en_GB')
        # I've had better luck with the US hyphenator.
        hyphenator = hyphen.Hyphenator('en_US')
        syllables = hyphenator.syllables(unicode(self.text))

        # Hyphenator returns unicode; for simplicity, let's convert it back to 
        # to ascii.

        syllables = [syll.encode('ascii','ignore') for syll in syllables]

#        print "Starting text: ", self.text
#        print "Starting Syllables: ", syllables

        # If syllables is *shorter* than our scanscion, we have 
        # a problem.
 #       if(len(syllables) < len(self.scansion)):
 #           syllables = [self.text]
 #           return syllables

        while(len(syllables) > len(self.scansion)):
            syllables = [syllables[0].encode('ascii','ignore') + syllables[1]] + syllables[2:]

        # I'm sometimes getting empty lists and I don't know why, so 
        # I've added this rule until I can figure out what's going on.
        if not syllables:
            syllables = [self.text]

#        print "Ending Syllables: ", syllables

        return syllables
               

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

    def promote_unstressed(self, meter='double'):
        """
        This function promotes unstressed syllables to stress 
        based on postion.
        """
        if(meter =='double'):
            for i in range(1, len(self.scanned_line[1:-1])):
#                print "current:" , self.scanned_line[i], " previous:" , self.scanned_line[i-1], " next:" , self.scanned_line[i+1]
                if((self.scanned_line[i] == 0) and (self.scanned_line[i-1] == 0) and (self.scanned_line[i+1] == 0)):
                    # Promote this syllable to stressed!
#                    print "Promoted!"
                    self.scanned_line[i] = 1

            # This separate rule handles instances where the last syllable
            # of a line should be promoted.
            if((self.scanned_line[-1] == 0) and (self.scanned_line[-2] == 0)):
                self.scanned_line[-1] = 1

        if(meter == 'triple'):
            for i in range(2, len(self.scanned_line[2:-2])):
                if((self.scanned_line[i] == 0) and (self.scanned_line[i-2] == 0) and (self.scanned_line[i-1] == 0) and (self.scanned_line[i+2] == 0) and (self.scanned_line[i+1] == 0)):
                    self.scanned_line[i] = 1

            # This separate rule handles instances where the last syllable
            # of a line should be promoted.
            if((self.scanned_line[-1] == 0) and (self.scanned_line[-2] == 0) and (self.scanned_line[-3] == 0)):
                self.scanned_line[-1] = 1


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
            
def tokenize_line(line):
    # We check for a hash mark at the start; this is a way to comment a line, and to 
    # give poems titles.
    if not(line.startswith('#')):
        tokenizer = RegexpTokenizer('\s+', gaps=True)
        words = tokenizer.tokenize(line)

        # Remove punctuation from our punctuation list; this only
        # catches floating punctuation. Puncutation at the end of 
        # word remains, and will be stripped out during lookup.
        words = filter(lambda word:word not in EXCLUDE, words)
    else:
        words=[]

    return words

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
    
