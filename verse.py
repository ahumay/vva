#!/bin/python

from nltk.corpus import cmudict
from nltk.tokenize import RegexpTokenizer
import sys
import operator # Necessary for sorting dictionaries by value

CMU = cmudict.dict()
PRIVATEDICTIONARYFILENAME = './private.dictionary'
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

class Poem():

    def __init__(self,rawtext):
        self.lines = []
        text = rawtext.split('\n')

        self.title = text[0].strip('#').strip()
        
        for line in text:
            if not(line.startswith('#')) and (line):
                self.lines.append(PoeticLine(line))

    def __str__(self):
        output = ""

        for line in self.lines:
            output += line.rawtext + '\n'

        return output

    def html(self):
        # Print HTML header
        print """
          <!DOCTYPE html>
          <html>
            <head>
              <meta charset='utf-8'>
              <title>"""+self.title+"""</title>
              <link rel='stylesheet' href='scanscion.css'>
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
            for word in line.words:
                # Let's save initial capitalization and terminal punctuation
                # in the original to restore it in the output. We could add hyphenation
                # here, and other things that we are stripping out in the interest 
                # of analysis.
            
                if(word.text[0].isupper()): 
                    capitalized = True
                    if(word.text[:-1] in PUNCTUATION): 
                        terminalPunctuation = word.text[:-1]

                outword = ''
                syllables = len(word.scansion)

                syllLen = (len(word.text) / syllables)+1
                splitWord = [word.text[x:x+syllLen] for x in range(0,len(word.text),syllLen)]

                syllNo = 0
                
                for syllable in splitWord:
                    if(str(word.scansion[syllNo]) == '0'):
                        outword += syllable
                    else:
                        outword += '<strong>'+syllable+'</strong>'
                    syllNo += 1

                    if syllNo < syllables:
                        outword += '&middot;'

                outword += terminalPunctuation

                line_output += outword + ' ' 
            line_output += "</p>"
            print line_output


            # Print html footer
        print """
                </body>
              </html>"""



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
