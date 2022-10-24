#!/usr/bin/env python3

"""
Find the word of interest.
"""

import sys
import json
import difflib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--infile", "-i", default=sys.stdin, type=argparse.FileType("r"))
args = parser.parse_args()

def diff(prev, cur):
    """
    I can't believe this isn't built into difflib.
    """
    result = ""
    prev_action = ""
    buff = ""

    # print("/".join(difflib.ndiff(prev, cur)))

    actions = { "-": [], "+": [] }
    for diff in difflib.ndiff(prev.split(), cur.split()):
        action = diff[0]
        token = diff[2:]
        if action in actions.keys():
            actions[action].append(token)

    return " ".join(actions["-"]), " ".join(actions["+"])


jsondata = json.load(args.infile)
for example in jsondata:
    dst = example["dst"]

    correct_i = int(example["true_ind"])
    correct_sent = dst[correct_i]
    incorrect_phrases = []
    for index, incorrect_sent in enumerate(dst):
        if index != correct_i:
            incorrect_phrase, correct_phrase = diff(incorrect_sent, correct_sent)
            incorrect_phrases.append(incorrect_phrase)

    # print(example["src"])
    # print("-> correct", correct_phrase)
    # print("-> incorrect", incorrect_phrase)
    # print("-> diff", (incorrect_phrase, correct_phrase))

    example["correct_phrase"] = correct_phrase
    example["incorrect_phrases"] = incorrect_phrases

print(json.dumps(jsondata, indent=2, ensure_ascii=False))
