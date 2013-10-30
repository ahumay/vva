#!/usr/bin/python
# This script reads an input file (given as a command line argument)
# and scans it using:
# - Our Private Dictionary
# - CMU Dict
# - A dumb heuristic if all fails.
# (In that order).
# It then outputs the scanned poem to HTML, marking stress with bold.

from nltk.corpus import cmudict
from nltk.tokenize import RegexpTokenizer
import sys

CMU = cmudict.dict()
PRIVATEDICTIONARYFILENAME = './private.dictionary'
PUNCTUATION = '!"#$%&()*+,./:;<=>?@[\\]^_`{|}~\-'


def main(argv):
    try: 
        lines = open(argv[0],'r').readlines()
    except:
        print "Trouble opening ", argv[0]

    # Load private dictionary; stored as a dictionary where the keys 
    # are words, the values are lists of tuples (scanscion, frequency).
    samJ = {}
    
    try:
        for line in open(PRIVATEDICTIONARYFILENAME,'r').readlines():
            if not(line.startswith('#')):
                word, scanscion, frequency = line.split(',')
                if word in samJ:
                    samJ[word].append((scanscion, int(frequency)))
                else:
                    samJ[word] = [(scanscion, int(frequency))]
    except:
        print "No existing dictionary found; using ", PRIVATEDICTIONARYFILENAME
            
    total_lines = len(lines)
    current_line = 0

    # Print header
    print """
          <!DOCTYPE html>
          <html>
            <head>
              <meta charset='utf-8'>
              <title>Poetry Output</title>
              <link rel='stylesheet' href='scanscion.css'>
            </head>

            <body>
          """

    # Start looping through poem.
    for line in lines:
        current_line += 1
        line_output = "<p class='line'>"
        capitalized = False
        terminalPunctuation = ''
        for word in line.split():
            dictword = word.strip(PUNCTUATION)
            dictword = dictword.strip()
            dictword = dictword.lower()

            # Let's save initial capitalization and terminal punctuation
            # in the original to restore it in the output. We could add hyphenation
            # here, and other things that we are stripping out in the interest 
            # of analysis.
            
            if(word[0].isupper()): 
                capitalized = True
            if(word[:-1] in PUNCTUATION): 
                terminalPunctuation = word[:-1]

            outword = ''
            if(dictword in samJ):
                outword += privDictToHTML(dictword)
            elif (dictword in CMU):
                outword += CMUDictToHtml(dictword)
            else:
                outword += guess(dictword)

            if(capitalized):
                outword = capitalize(outword)

            outword += terminalPunctuation

            line_output += outword + ' ' 
        line_output += "</p>"
        print line_output


    # Print html footer
    print """
            </body>
          </html>"""


def capitalize(word):
    """
    This function will capitalize the first letter of a word; the one hiccup
    it solves is that it will ignore any HTML tags at the start of a string.
    """
    i = 0

    if(word[i] == '<'):
        while(word[i] != '>'):
            i += 1
        i +=1

    return word[0:i] + word[i:].capitalize()


def CMUDictToHtml(word):                
    cmuList = CMU[word][0]
    verseList = []

    for item in cmuList:
        if item[-1].isdigit():
            verseList.append(item[-1])


    # For ease, we split on "syllables" not at the real division, 
    # but at equal points within the word.
    syllables = len(verseList)
    syllLen = (len(word) / syllables)+1
    
    splitWord = [word[x:x+syllLen] for x in range(0,len(word),syllLen)]

    syllNo = 0
    outstring = ''
    for syllable in splitWord:
        if(verseList[syllNo] == '0'):
            outstring += syllable
        else:
            outstring += '<strong>'+syllable+'</strong>'
        syllNo += 1

        if syllNo < syllables:
            outstring += '&middot;'

    return outstring
    

def privDictToHTML(scanscion):
    outstring = ""
    scannedList = scanscion.split('-')
    syllables = len(scannedList)

    syllNo = 0
    for string in scanscion.split('-'):
        if string.endswith('*'):
            outstring += '<strong>'+string[:-1]+'</strong>'
        else:
            outstring += string

        syllNo += 1 
        if syllNo < syllables:
            outstring += '&middot;'

    return outstring

def guess(string):
    return string


if __name__ == "__main__":
    main(sys.argv[1:])
