from itertools import product
from typing import List, Tuple

from contradiction.contradiction_util import entity_lower, entity_higher, data_lower, data_higher
from contradiction.contradiction_util import entity_related, data_related, condition_related
from node import CollectionNode

# In this file, we define 9 rules for node1.condition == node2.condition, which means we ignore 'condition' attribute
# The 9 rules are from 'USENIX 2019 Paper: PolicyLint: Investigating Internal Privacy Policy Contradictions on Google Play'
# They are descibed in Section 2 PolicyLint

"""
Bibtex:
@inproceedings{andow_policylint_2019,
	title = {\{{PolicyLint}\}: {Investigating} {Internal} {Privacy} {Policy} {Contradictions} on {Google} {Play}},
	isbn = {978-1-939133-06-9},
	url = {https://www.usenix.org/conference/usenixsecurity19/presentation/andow},
	author = {Andow, Benjamin and Mahmud, Samin Yaseer and Wang, Wenyu and Whitaker, Justin and Enck, William and Reaves, Bradley and Singh, Kapil and Xie, Tao},
	year = {2019},
	pages = {585--602},
}
"""

# c1cnt, c2cnt, c3cnt, c4cnt, c5cnt = 0, 0, 0, 0, 0
# n1cnt, n2cnt, n3cnt, n4cnt = 0, 0, 0, 0


# c1: base contradiction
# (companyX, collect, email) vs (companyX, not collect, email)
def lc1(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and node1.data == node2.data:
        contradictions.append((node1, node2))

# (companyX, collect, email) vs (companyX, not collect, personal info)
def lc2(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and data_lower(node1.data, node2.data):
        contradictions.append((node1, node2))

# (companyX, collect, email) vs (advertiser, not collect, email)
def lc3(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and node1.data == node2.data:
        contradictions.append((node1, node2))


# (companyX, collect, email) vs (advertiser, not collect, personal info)
def lc4(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and data_lower(node1.data, node2.data):
        contradictions.append((node1, node2))


# c5
# (advertiser, collect, email) vs (companyX, not collect, personal info)
def lc5(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and data_lower(node1.data, node2.data):
        contradictions.append((node1, node2))


# there is a principle in narrowing that the negation should always use a lower/equal data item
# n1: base narrowing
# (companyX, collect, personal info) vs (companyX, not collect, email)
def ln1(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and data_higher(node1.data, node2.data):
        narrowed.append((node1, node2))


# n2
# (companyX, collect, personal info) vs (advertiser, not collect, email)
def ln2(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and data_higher(node1.data, node2.data):
        narrowed.append((node1, node2))


# n3
# (advertiser, collect, email) vs (companyX, not collect, email)
def ln3(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and node1.data == node2.data:
        narrowed.append((node1, node2))


# n4:
# (advertiser, collect, personal info) vs (companyX, not collect, email)
def ln4(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and data_higher(node1.data, node2.data):
        narrowed.append((node1, node2))

c_rules=[lc1,lc2,lc3,lc4,lc5]
n_rules=[ln1,ln2,ln3,ln4]
def no_condition_rule_cmp(node1: CollectionNode, node2: CollectionNode,
                      contradictions: List[Tuple[CollectionNode, CollectionNode]],
                      narrowed: List[Tuple[CollectionNode, CollectionNode]],
                    cr_cnts:list[int],nr_cnts:list[int]
                          ):
    v1, v2 = node1.verb.lower().strip(), node2.verb.lower().strip()
    if v1 == 'collect' and v2 == 'not collect':
        for i in range(5):
            old_len=len(contradictions)
            c_rules[i](node1, node2, contradictions)
            if len(contradictions)>old_len:
                cr_cnts[i]+=1

        for i in range(4):
            old_len=len(narrowed)
            n_rules[i](node1, node2, narrowed)
            if len(narrowed)>old_len:
                nr_cnts[i]+=1




def apply_rule_cmp(pos: list[CollectionNode],
               neg: list[CollectionNode],
               contradictions: list[tuple[CollectionNode, CollectionNode]],
               narrowings: list[tuple[CollectionNode, CollectionNode]]):

    no_condition_cnt = 0
    no_condition_contractions_cnt, no_condition_narrowings_cnt = 0, 0
    cr_cnts=[0,0,0,0,0]
    nr_cnts=[0,0,0,0]

    # make a combination of all the nodes: node1 from pos, node2 from neg
    for node1, node2 in product(pos, neg):
        try:
            contradictions_cnt,narrowings_cnt = len(contradictions),len(narrowings)

            if (not entity_related(node1, node2)) or (not data_related(node1, node2)) or (
                    not condition_related(node1.condition, node2.condition)):
                continue
            no_condition_rule_cmp(node1, node2, contradictions, narrowings,cr_cnts,nr_cnts)
            no_condition_cnt += 1
            if len(contradictions) > contradictions_cnt:
                no_condition_contractions_cnt += 1
            if len(narrowings) > narrowings_cnt:
                no_condition_narrowings_cnt += 1

        except Exception as e:
            print("Error when applying rules: ", str(node1), str(node2))

    print(f"no_condition: cnt: {no_condition_cnt}, contractions: {no_condition_contractions_cnt}, narrowings: {no_condition_narrowings_cnt}")
    for i in range(5):
        print(f"c{i+1}: {cr_cnts[i]}")
    for i in range(4):
        print(f"n{i+1}: {nr_cnts[i]}")

    return cr_cnts