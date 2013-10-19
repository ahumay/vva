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
    # Start looping through poem.
    for line in lines:
        current_line += 1
        for word in line.split():
            dictword = word.strip(PUNCTUATION)
            dictword = dictword.strip()
            dictword = dictword.lower()
            if (dictword not in CMU):
                previously_seen = False
                # The following block reloops through the line
                # in order to colorize the output.
                outstring = ""
                for w in line.split():
                    if (w == word):
                        outstring += bcolors.OKGREEN + w + bcolors.ENDC + ' '
                    else:
                        outstring += w + ' '

                print bcolors.WARNING + "["+str(current_line).zfill(4)+"/"+str(total_lines).zfill(4)+"]: "+bcolors.ENDC +  outstring

                # Have we seen this word before in our private dictionary?
                if(dictword in samJ):
                    previously_seen = True
                    existing_scanscions = samJ[dictword]
                    existing_scanscions.sort(key=lambda a: a[1])

                    i = 0

                    for each_scanscion in existing_scanscions:
                        print bcolors.HEADER + each_scanscion[0] + bcolors.ENDC + ' (' + str(each_scanscion[1]).strip() + ') ['+str(i)+']'
                        i += 1
                        

                # Next block is to request a scanscion as input from user.
                scanscion_string = ''
                # This while loop waits for "valid" input; for now
                # that just means that if you hit enter, it won't
                # write an empty string to our private dictionary.
                while not (valid_scanscion(scanscion_string)):
                    scansion_string = ''
                    if not previously_seen:
                        outstring = "Please scan " + bcolors.OKGREEN + word + bcolors.ENDC + ":"
                    else:
                        outstring = bcolors.OKGREEN + word + bcolors.ENDC + " or number of scanscion.\n Enter to accept most frequent."
                    scanscion_string = raw_input(outstring)
                    print "You inputted:", scanscion_string

                    if (previously_seen) and (scanscion_string == ''):
                        selected = existing_scanscions[0]
                        scanscion_string = selected[0]
                        print "BING!", existing_scanscions
                    else:
                        if (previously_seen) and (scanscion_string.isdigit()):
                            try:
                                index = int(scanscion_string)
                                selected = existing_scanscions[index]
                                print "selected", selected
                                scanscion_string = selected[0]
                            except:
                                print "Not a valid encoding."
                                scanscion_string = ''
                                
                                
                # Add our scanscion string to our dictionary.
                if previously_seen:
                    found = False
                    scanscion_list = samJ[dictword]
                    new_list = []
                    for item in scanscion_list:
                        if item[0] == scanscion_string:
#                            print "Ding: ", item
#                            print "Item[0]", item[0]
#                            print "Item[1]", item[1]
                            count = item[1] + 1
                            item = (scanscion_string, count)
                            new_list.append(item)
                            found = True
                        else:
                            new_list.append(item)
                    if found:
                        samJ[dictword] = new_list
                    else:
                        samJ[dictword].append((scanscion_string, 1))

                else:
                   samJ[dictword] = [(scanscion_string, 1)]
                
                # Write out our dictionary.
                outfile = open(PRIVATEDICTIONARYFILENAME, 'w')
                outfile.write('#term,scanscion,frequency\n')

                keys = sorted(samJ.keys())
                print "Keys: ", keys
                for key in keys:
                    scanscion_list = samJ[key]
                    for each_scanscion in scanscion_list:
                        outputstring = key + ',' + each_scanscion[0] + ',' + str(each_scanscion[1]) + '\n'
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
