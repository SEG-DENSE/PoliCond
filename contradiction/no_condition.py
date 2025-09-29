from node import CollectionNode
from typing import List, Tuple
from contradiction.contradiction_util import entity_lower, entity_higher, data_lower, data_higher

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


def no_condition_rule(node1: CollectionNode, node2: CollectionNode,
                      contradictions: List[Tuple[CollectionNode, CollectionNode]],
                      narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    v1, v2 = node1.verb.lower().strip(), node2.verb.lower().strip()
    if v1 == 'collect' and v2 == 'not collect':
        c1(node1, node2, contradictions)
        c2(node1, node2, contradictions)
        c3(node1, node2, contradictions)
        c4(node1, node2, contradictions)
        c5(node1, node2, contradictions)
        n1(node1, node2, narrowed)
        n2(node1, node2, narrowed)
        n3(node1, node2, narrowed)
        n4(node1, node2, narrowed)


# c1: base contradiction
# (companyX, collect, email) vs (companyX, not collect, email)
def c1(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and node1.data == node2.data:
        contradictions.append((node1, node2))


# (companyX, collect, email) vs (companyX, not collect, personal info)
def c2(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and data_lower(node1.data, node2.data):
        contradictions.append((node1, node2))


# (companyX, collect, email) vs (advertiser, not collect, email)
def c3(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and node1.data == node2.data:
        contradictions.append((node1, node2))


# (companyX, collect, email) vs (advertiser, not collect, personal info)
def c4(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and data_lower(node1.data, node2.data):
        contradictions.append((node1, node2))


# c5
# (advertiser, collect, email) vs (companyX, not collect, personal info)
def c5(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and data_lower(node1.data, node2.data):
        contradictions.append((node1, node2))


# there is a principle in narrowing that the negation should always use a lower/equal data item
# n1: base narrowing
# (companyX, collect, personal info) vs (companyX, not collect, email)
def n1(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and data_higher(node1.data, node2.data):
        narrowed.append((node1, node2))


# n2
# (companyX, collect, personal info) vs (advertiser, not collect, email)
def n2(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and data_higher(node1.data, node2.data):
        narrowed.append((node1, node2))


# n3
# (advertiser, collect, email) vs (companyX, not collect, email)
def n3(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and node1.data == node2.data:
        narrowed.append((node1, node2))


# n4:
# (advertiser, collect, personal info) vs (companyX, not collect, email)
def n4(node1: CollectionNode, node2: CollectionNode, narrowed: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and data_higher(node1.data, node2.data):
        narrowed.append((node1, node2))
