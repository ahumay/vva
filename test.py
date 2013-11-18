#!/usr/bin/python
# This script reads an input file (given as a command line argument)
# and scans it using:
# - Our Private Dictionary
# - CMU Dict
# - A dumb heuristic if all fails.
# (In that order).
# It then outputs the scanned poem to HTML, marking stress with bold.

import verse
import sys

def main(argv):
    try: 
        lines = open(argv[0],'r').read()
    except:
        print "Trouble opening ", argv[0]

    poem = verse.Poem(lines)

    poem.promoteUnstressed()

    print poem.html()


if __name__ == "__main__":
    main(sys.argv[1:])
