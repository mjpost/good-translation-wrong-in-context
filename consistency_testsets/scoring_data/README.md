# Test sets for scoring

Convert these to our format:

    for prefix in deixis_dev deixis_test ellipsis_infl ellipsis_vp lex_cohesion_dev lex_cohesion_test; do
        paste $prefix.{src,dst} | ./detok.py > $prefix.tsv
    done
