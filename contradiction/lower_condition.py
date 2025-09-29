from node import CollectionNode
from typing import List, Tuple
from contradiction.contradiction_util import entity_lower, entity_higher, data_lower, data_higher, condition_higher, condition_lower


# in this file, we define 9 rules for node1.condition < node2.condition;
# there is a principle that the negation statement should be treated seriously, it should have a higher priority
# (xxx,not collect, email, not mentioned) means you should not collect user's email in any case

def lower_condition_rule(node1: CollectionNode, node2: CollectionNode,
                         contradictions: List[Tuple[CollectionNode, CollectionNode]],
                         narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    v1, v2 = node1.verb.lower().strip(), node2.verb.lower().strip()
    if v1 == 'collect' and v2 == 'not collect':
        # c1~c3, node1.data = node2.data, node1.cond < node2.cond
        c1(node1, node2, contradictions)
        c2(node1, node2, contradictions)
        c3(node1, node2, contradictions)
        # c4~c6, node1.data > node2.data, node1.cond < node2.cond
        c4(node1, node2, contradictions)
        c5(node1, node2, contradictions)
        c6(node1, node2, contradictions)
        # c7~c9,  node1.data < node2.data, node1.cond < node2.cond
        c7(node1, node2, contradictions)
        c8(node1, node2, contradictions)
        c9(node1, node2, contradictions)


# c1 base contradiction
# (companyX, collect, email, children) vs (companyX, not collect, email, not mentioned)
# 'not mentioned' means all possibility, which is higher/more general than 'children info'
def c1(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and \
            node1.data == node2.data and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# (advertiser, collect, email, children) vs (companyX, not collect, email, not mentioned)
def c2(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and \
            node1.data == node2.data and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# (companyX, collect, email, children) vs (advertiser, not collect, email, not mentioned)
def c3(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and \
            node1.data == node2.data and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# c4~c6, node1.data > node2.data, node1.cond < node2.cond
# (companyX, collect, personal info, children) vs (companyX, not collect, email, not mentioned)
def c4(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and \
            data_higher(node1.data, node2.data) and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# (advertiser, collect, personal info, children) vs (companyX, not collect, email, not mentioned)
def c5(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and \
            data_higher(node1.data, node2.data) and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# (companyX, collect, personal info, children) vs (advertiser, not collect, email, not mentioned)
def c6(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and \
            data_higher(node1.data, node2.data) and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# c7~c9, node1.data < node2.data, node1.cond < node2.cond
# (companyX, collect, email, children) vs (companyX, not collect, personal info, not mentioned)
def c7(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and \
            data_lower(node1.data, node2.data) and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# (advertiser, collect, email, children) vs (companyX, not collect, personal info, not mentioned)
def c8(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and \
            data_lower(node1.data, node2.data) and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))


# (companyX, collect, email, children) vs (advertiser, not collect, personal info, not mentioned)
def c9(node1: CollectionNode, node2: CollectionNode, contradictions: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and \
            data_lower(node1.data, node2.data) and \
            condition_lower(node1.condition, node2.condition):
        contradictions.append((node1, node2))
