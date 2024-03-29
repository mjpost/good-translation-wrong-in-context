#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Lena Voita

import os
import math
import numpy as np
import json
import argparse

from sacremoses import MosesTokenizer

tokenizer = MosesTokenizer(lang="ru")


GTWIC_DIR = os.path.join(os.path.dirname(__file__), "..")


def get_scores(json_data, scores):
    group_lens = [len(elem['dst']) for elem in json_data]
    group_inds = [0] + list(np.cumsum(group_lens))
    true_inds = [elem['true_ind'] for elem in json_data]

    score_groups = [scores[group_inds[k]: group_inds[k + 1]] for k in range(len(group_inds) - 1)]
    res = [1 if np.argmax(score_groups[k]) == true_inds[k] else 0 for k in range(len(score_groups))]

    return res


def evaluate(repo_dir, testset_name, scores_fname):
    json_data = json.load(open("{}/consistency_testsets/{}.json".format(repo_dir, testset_name)))
    scores = list(map(lambda x: float(x.strip().split()[0]), open(scores_fname)))
    assert sum([len(elem['dst']) for elem in json_data]) == len(scores), "Number of lines in scores does not match number of test examples"

    group_scores = get_scores(json_data, scores)
    result = {
        "correct": sum(group_scores),
        "count": len(group_scores),
        'total': np.mean(group_scores),
    }

    if not testset_name in ['ellipsis_vp', 'ellipsis_infl']:
        scores_by_distance = {}
        for distance in range(1, 4):
            scores_by_distance[distance] = np.mean([el for i, el in enumerate(group_scores)\
                                                    if json_data[i]['ctx_dist'] == distance])
        result['by_distance'] = scores_by_distance
    return result


def evaluate_gen(repo_dir, testset_name, output_fname, proportional=False):
    json_data = json.load(open("{}/consistency_testsets/{}.json".format(repo_dir, testset_name)))
    outputs = list(map(str.strip, open(output_fname).readlines()))

    result = {
        "correct": 0,
        "count": 0,
    }
    distances = {
        1: { "correct": 0, "count": 0 },
        2: { "correct": 0, "count": 0 },
        3: { "correct": 0, "count": 0 },
    }

    for elem in json_data:
        good = elem["correct_phrase"].lower()
        bads = list(map(str.lower, elem["incorrect_phrases"]))

        dist = elem["ctx_dist"]

        # extract the sentence and its tokens
        if proportional:
            src = elem["src"].split(" _eos ")[-1]
            payload_pct = len(src.split()) / len(elem["src"].split()) * 1.5

            payload = outputs[0]
            output_len = len(payload.split())
            num_output_tokens = int(output_len * payload_pct * 1.5)

            payload = " ".join(payload.split()[-num_output_tokens:])

            print(f"{num_output_tokens} / {output_len} = {payload}")
        else:
            payload = outputs[0].split("<eos>")[-1].lower()

        tokens = tokenizer.tokenize(payload)

        # trim duplicate outputs
        outputs = outputs[len(elem["dst"]):]

        if good in tokens and all([bad not in tokens for bad in bads]):
            result["correct"] += 1
            distances[dist]["correct"] += 1
        # else:
        #     print(payload)
        #     print(f"-> {good}?", good in tokens)
        #     print(f"-> {bads}?", any([bad in tokens for bad in bads]))

        result["count"] += 1
        distances[dist]["count"] +=1

    result["total"] = result["correct"] / result["count"]

    if not testset_name in ['ellipsis_vp', 'ellipsis_infl']:
        result["by_distance"] = {}
        for distance in range(1, 4):
            result["by_distance"][distance] = distances[distance]["correct"] / distances[distance]["count"]

    return result

def print_results(testset_name, result):
    print("Test set:", testset_name)
    print("Correct:", result["correct"])
    print("Count:", result["count"])
    print("Total accuracy: ", result['total'])
    if 'by_distance' in result:
        print('\nAccuracy for different distances between sentences requiring consistency.')
        for distance in range(1, 4):
            print("{}: {}".format(distance, result['by_distance'][distance]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate accuracy on consistency test sets')
    parser.add_argument('--repo-dir', type=str, default=GTWIC_DIR,
                        help='Path to your local "good-translation-wrong-in-context"')
    parser.add_argument('--test', '-t', type=str, required=True,
                        choices=['deixis_test', 'deixis_dev', 'lex_cohesion_test', 'lex_cohesion_dev', 'ellipsis_vp', 'ellipsis_infl'],
                       help="""Test set name.""")
    parser.add_argument('--gen', '-g', action="store_true",
                        help="Test generative ability")
    parser.add_argument('--scores', '-s', type=str, required=True,
                        help="Loss of your model on the test set examples, one score per line")
    parser.add_argument("--proportional", action="store_true")
    args = parser.parse_args()

    if args.gen:
        result = evaluate_gen(args.repo_dir, args.test, args.scores, proportional=args.proportional)
    else:
        result = evaluate(args.repo_dir, args.test, args.scores)
    print_results(args.test, result)


