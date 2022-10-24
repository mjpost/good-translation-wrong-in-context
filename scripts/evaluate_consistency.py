#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Lena Voita

import os
import numpy as np
import json
import argparse

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
    result = {'total': np.mean(group_scores)}

    if not testset_name in ['ellipsis_vp', 'ellipsis_infl']:
        scores_by_distance = {}
        for distance in range(1, 4):
            scores_by_distance[distance] = np.mean([el for i, el in enumerate(group_scores)\
                                                    if json_data[i]['ctx_dist'] == distance])
        result['by_distance'] = scores_by_distance
    return result

def evaluate_gen(repo_dir, testset_name, output_fname):
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
        good = elem["correct_phrase"]
        bads = elem["incorrect_phrases"]

        dist = elem["ctx_dist"]

        output = outputs[0].split("<eos>")[-1]
        outputs = outputs[len(elem["dst"]):]

        if good in output and all([bad not in output for bad in bads]):
            result["correct"] += 1
            distances[dist]["correct"] += 1

        result["count"] += 1
        distances[dist]["count"] +=1

    result["total"] = result["correct"] / result["count"]

    if not testset_name in ['ellipsis_vp', 'ellipsis_infl']:
        result["by_distance"] = {}
        for distance in range(1, 4):
            result["by_distance"][distance] = distances[distance]["correct"] / distances[distance]["count"]

    return result

def print_results(testset_name, result):
    print("Test set: ", testset_name)
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

    args = parser.parse_args()
    if args.gen:
        result = evaluate_gen(args.repo_dir, args.test, args.scores)
    else:
        result = evaluate(args.repo_dir, args.test, args.scores)
    print_results(args.test, result)


