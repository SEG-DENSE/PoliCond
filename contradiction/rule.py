from itertools import product
from contradiction.higher_condition import higher_condition_rule
from contradiction.lower_condition import lower_condition_rule
from contradiction.no_condition import no_condition_rule
from contradiction.contradiction_util import condition_higher, condition_lower, \
    entity_related, data_related, condition_related
from node import CollectionNode


def apply_rule(pos: list[CollectionNode],
               neg: list[CollectionNode],
               contradictions: list[tuple[CollectionNode, CollectionNode]],
               narrowings: list[tuple[CollectionNode, CollectionNode]]):
    global no_condition_cnt, high_condition_cnt, low_condition_cnt

    # reset counter
    no_condition_cnt = 0
    no_condition_contractions_cnt, no_condition_narrowing_cnt = 0, 0
    high_condition_cnt = 0
    high_condition_contractions_cnt, high_condition_narrowing_cnt = 0, 0
    low_condition_cnt = 0
    low_condition_contractions_cnt, low_condition_narrowing_cnt = 0, 0

    # make a combination of all the nodes: node1 from pos, node2 from neg
    for node1, node2 in product(pos, neg):
        try:
            contradictions_cnt, narrowings_cnt = len(contradictions), len(narrowings)

            if (not entity_related(node1, node2)) or (not data_related(node1, node2)) or (
                    not condition_related(node1.condition, node2.condition)):
                continue
            elif node1.condition == node2.condition:
                no_condition_rule(node1, node2, contradictions, narrowings)
                no_condition_cnt += 1
                if len(contradictions) > contradictions_cnt:
                    no_condition_contractions_cnt += 1
                if len(narrowings) > narrowings_cnt:
                    no_condition_narrowing_cnt += 1

            elif condition_higher(node1.condition, node2.condition):
                higher_condition_rule(node1, node2, contradictions, narrowings)
                high_condition_cnt += 1
                if len(contradictions) > contradictions_cnt:
                    high_condition_contractions_cnt += 1
                if len(narrowings) > narrowings_cnt:
                    high_condition_narrowing_cnt += 1

            elif condition_lower(node1.condition, node2.condition):
                lower_condition_rule(node1, node2, contradictions, narrowings)
                low_condition_contractions_cnt += 1
                if len(contradictions) > contradictions_cnt:
                    low_condition_cnt += 1
                if len(narrowings) > narrowings_cnt:
                    low_condition_narrowing_cnt += 1


        except Exception as e:
            print("Error when applying rules: ", str(node1), str(node2))

    # output the results
    print(
        f"no_condition: cnt: {no_condition_cnt}, "
        f"contractions: {no_condition_contractions_cnt}, "
        f"narrowings: {no_condition_narrowing_cnt}")
    print(
        f"high_condition: cnt:{high_condition_cnt}, "
        f"contractions: {high_condition_contractions_cnt}, "
        f"narrowings: {high_condition_narrowing_cnt}")
    print(
        f"low_condition: cnt:{low_condition_cnt}, "
        f"contractions: {low_condition_contractions_cnt}, "
        f"narrowings: {low_condition_narrowing_cnt}")

    return low_condition_contractions_cnt, no_condition_contractions_cnt
