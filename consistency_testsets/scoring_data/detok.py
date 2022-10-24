#!/usr/bin/env python3

import re
import sys


def detok(line):
    line = line.rstrip()

    line = line.replace(" _eos ", " <eos>")
    line = line.replace(" . ", ". ")
    line = line.replace(" ! ", "! ")
    line = line.replace(" ? ", "? ")
    line = line.replace(" , ", ", ")
    line = line.replace(" ; ", "; ")
    line = line.replace(" ! ", "! ")
    line = line.replace(" ? ", "? ")
    line = line.replace(" 's", "'s")
    line = line.replace(" ' s", "'s")
    line = line.replace(" 't", "'t")
    line = line.replace(" 'm ", "'m ")
    line = line.replace(" 've ", "'ve ")
    line = line.replace(" 'll ", "'ll ")
    line = line.replace(" 're ", "'re ")

    line = re.sub(r'^(.*) " (.*) " (.*)', '\1 "\2" \3', line)

    line = line.replace(" .", ".")
    line = line.replace(" !", "!")
    line = line.replace(" ?", "?")

    return line

if __name__ == "__main__":
    for line in sys.stdin:
        print("\t".join(map(detok, line.split("\t"))))

