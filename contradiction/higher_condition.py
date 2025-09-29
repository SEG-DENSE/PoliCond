from node import CollectionNode
from typing import List, Tuple
from contradiction.contradiction_util import entity_lower, entity_higher, data_lower, data_higher, condition_higher


# in this file, we define 9 rules for node1.condition > node2.condition;
# there is a principle that the negation statement should be treated seriously, it should have a higher priority
# (xxx,not collect, email, not mentioned) means you should not collect user's email in any case

def higher_condition_rule(node1: CollectionNode, node2: CollectionNode,
                          contradictions: List[Tuple[CollectionNode, CollectionNode]],
                          narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    v1, v2 = node1.verb.lower().strip(), node2.verb.lower().strip()
    if v1 == 'collect' and v2 == 'not collect':
        # n1~n3,  node1.data = node2.data, and node1.cond>node2.cond
        n1(node1, node2, narrowing)
        n2(node1, node2, narrowing)
        n3(node1, node2, narrowing)
        # n4~n6,  node1.data > node2.data, and node1.cond>node2.cond
        n4(node1, node2, narrowing)
        n5(node1, node2, narrowing)
        n6(node1, node2, narrowing)
        # n7~n9, node1.data < node2.data, and node1.cond>node2.cond
        n7(node1, node2, narrowing)
        n8(node1, node2, narrowing)
        n9(node1, node2, narrowing)


# n1: base narrowing
# (companyX, collect, email, not mentioned) vs (companyX, not collect, email, children)
# 'not mentioned' means all possibility, which is higher/more general than 'children'
def n1(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and \
            node1.data == node2.data and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# (advertiser, collect, email, not mentioned) vs (companyX, not collect, email, children)
def n2(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and \
            node1.data == node2.data and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# (companyX, collect, email, not mentioned) vs (advertiser, not collect, email, children)
def n3(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and \
            node1.data == node2.data and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# (companyX, collect, personal info, not mentioned) vs (companyX, not collect, email, children)
def n4(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and \
            data_higher(node1.data, node2.data) and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# (advertiser, collect, personal info, not mentioned) vs (companyX, not collect, email, children)
def n5(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and \
            data_higher(node1.data, node2.data) and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# (companyX, collect, personal info, not mentioned) vs (advertiser, not collect, email, children)
def n6(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and \
            data_higher(node1.data, node2.data) and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# n7
# (companyX, collect, email, not mentioned) vs (companyX, not collect, personal info, children)
def n7(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if node1.entity == node2.entity and \
            data_lower(node1.data, node2.data) and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# (advertiser, collect, email, not mentioned) vs (companyX, not collect, personal info, children)
def n8(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_higher(node1.entity, node2.entity) and \
            data_lower(node1.data, node2.data) and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))


# (companyX, collect, email, not mentioned) vs (advertiser, not collect, personal info, children)
def n9(node1: CollectionNode, node2: CollectionNode, narrowing: List[Tuple[CollectionNode, CollectionNode]]):
    if entity_lower(node1.entity, node2.entity) and \
            data_lower(node1.data, node2.data) and \
            condition_higher(node1.condition, node2.condition):
        narrowing.append((node1, node2))
