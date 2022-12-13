#!/usr/bin/env python3

import re
import sys

from sacremoses import MosesDetokenizer

detokenizer = MosesDetokenizer()

def detok(line):
    line = line.rstrip().split()
    line = detokenizer.detokenize(line)
    line = line.replace(" _eos ", " <eos>")

    return line

if __name__ == "__main__":
    for line in sys.stdin:
        print("\t".join(map(detok, line.split("\t"))))

