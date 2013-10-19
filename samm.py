#!/usr/bin/python
# SAMM - Semi Automated Meter Manager; 
# named for the harmless drudge of a lexicographer Samuel Johnson. 
# This script reads through the input file; words that in the input file that 
# do not appear in either the specified "private dictionary" 
from nltk.corpus import cmudict
from nltk.tokenize import RegexpTokenizer
import sys

PRIVATEDICTIONARYFILENAME = './private.dictionary'
PUNCTUATION = '!"#$%&()*+,./:;<=>?@[\\]^_`{|}~\-'

CMU = cmudict.dict()

def main(argv):
    try: 
        lines = open(argv[0],'r').readlines()
    except:
        print "Trouble opening ", argv[0]


    # Load private dictionary.
    samJ = []
    for line in open(PRIVATEDICTIONARYFILENAME,'r').readlines():
        if not(line.startswith('#')):
            word, scanscion = line.split(',')
            samJ.append(word)
    
    for line in lines:

        for word in line.split():
            dictword = word.strip(PUNCTUATION)
            dictword = dictword.strip()
            dictword = dictword.lower()
            if (dictword not in CMU) and (dictword not in samJ):

                # The following block reloops through the line
                # in order to colorize the output.
                outstring = ""
                for w in line.split():
                    if (w == word):
                        outstring += bcolors.OKGREEN + w + bcolors.ENDC + ' '
                    else:
                        outstring += w + ' '

                print outstring

                scanscion_string = ""
                # This while loop waits for "valid" input; for now
                # that just means that if you hit enter, it won't
                # write an empty string to our private dictionary.
                while not (valid_scanscion(scanscion_string)):
                    outstring = "Please scan " + bcolors.OKGREEN + word + bcolors.ENDC + ":"
                    scanscion_string = raw_input(outstring)
                
                # Write it out by appending to our Private Dictionary File.
                # It may be worth considering keeping this in alphabetical 
                # order at some point, if only to make it easier to manually 
                # add things. 
                outfile = open(PRIVATEDICTIONARYFILENAME, 'a')
                outputstring = word + ',' + scanscion_string + '\n'
                outfile.write(outputstring)
                outfile.close()
                

def valid_scanscion(string):
    """
    Simple sanity to check to ensure that a string entered by 
    a user conforms to the basic standards required for output.
    """
    if string:
        return True
    else:
        return False


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


if __name__ == "__main__":
    main(sys.argv[1:])
