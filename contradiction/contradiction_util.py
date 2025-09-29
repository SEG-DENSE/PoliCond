from functools import lru_cache
from typing import Union

from node import CollectionNode
from ontology.condition.condition import Condition
from ontology.condition.handler import ConditionHandler
from ontology.data.Data import Data
from ontology.data.handler import DataHandler
from ontology.entity.Entity import Entity
from ontology.entity.handler import EntityHandler

from util.structured.judge_negation import has_negation
@lru_cache(maxsize=100)
def entity_related(node1: CollectionNode, node2: CollectionNode) -> bool:
    if node1.entity == node2.entity: return True
    entity1, entity2 = EntityHandler.recognize_first(node1.entity), EntityHandler.recognize_first(node2.entity)
    if entity1 and entity2:
        return EntityHandler.is_lower(entity1, entity2) or EntityHandler.is_higher(entity1, entity2)
    return False

@lru_cache(maxsize=100)
def entity_lower(entity1: str, entity2: str) -> bool:
    entity1, entity2 = EntityHandler.recognize_first(entity1), EntityHandler.recognize_first(entity2)
    if entity1 and entity2:
        return EntityHandler.is_lower(entity1, entity2)
    return False


def entity_higher(entity1: str, entity2: str) -> bool:
    return entity_lower(entity2, entity1)


@lru_cache(maxsize=100)
def data_related(node1: CollectionNode, node2: CollectionNode) -> bool:
    if node1.data == node2.data: return True
    if node1.data in ['non_personal_info','aggregate','transformed_information','pseudonymous'] or \
        node2.data in ['non_personal_info','aggregate','transformed_information','pseudonymous']:
        return False
    d1, d2 = DataHandler.recognize_first(node1.data), DataHandler.recognize_first(node2.data)
    if has_negation(node1.data) and d1 == Data.PERSONAL_INFO:
        d1 = Data.NON_PERSONAL_INFO
    if has_negation(node2.data) and d2 == Data.PERSONAL_INFO:
        d2 = Data.NON_PERSONAL_INFO
    if d1 and d2:
        return DataHandler.is_lower(d1, d2) or DataHandler.is_higher(d1, d2)
    return False


@lru_cache(maxsize=100)
def data_lower(data1: str, data2: str) -> bool:
    d1, d2 = DataHandler.recognize_first(data1), DataHandler.recognize_first(data2)
    if has_negation(data1)  and d1==Data.PERSONAL_INFO:
        d1=Data.NON_PERSONAL_INFO
    if has_negation(data2) and d2==Data.PERSONAL_INFO:
        d2=Data.NON_PERSONAL_INFO
    if d1 and d2:
        return DataHandler.is_lower(d1, d2)
    return False


def data_higher(data1: str, data2: str) -> bool:
    return data_lower(data2, data1)


def condition_related(condition1: Union[str, Condition], condition2: Union[str, Condition]) -> bool:
    if isinstance(condition1, Condition) and isinstance(condition2, Condition):
        return ConditionHandler.is_related(condition1, condition2)
    if "and" in condition1:
        cond1 = set(map(lambda s: ConditionHandler.recognize_first(s), condition1.split("and")))
    else:
        cond1 = set()
        cond1.add(ConditionHandler.recognize_first(condition1))
    if "and" in condition2:
        cond2 = set(map(lambda s: ConditionHandler.recognize_first(s), condition2.split("and")))
    else:
        cond2 = set()
        cond2.add(ConditionHandler.recognize_first(condition2))

    # NO_COND cannot coexist with other conditions
    if Condition.NO_COND in cond1 and len(cond1) > 1: cond1.remove(Condition.NO_COND)
    if Condition.NO_COND in cond2 and len(cond2) > 1: cond2.remove(Condition.NO_COND)

    # if cond1/cond2 both have only one condition
    if len(cond1) == len(cond2) == 1:
        return ConditionHandler.is_related(cond1.pop(), cond2.pop())

    # composite(children, consent) < consent; composite(children, consent) < children
    # strict condition is less
    # cond1<cond2 is True <=> cond1 condition is more strict than cond2 <=> cond1 has more items <=> cond1 is subset of cond2
    more, less = set(), set()
    if len(cond1) >= len(cond2):
        more, less = cond1, cond2
    else:
        more, less = cond2, cond1

    for c1 in less:
        found = False
        for c2 in more:
            if ConditionHandler.is_related(c1, c2):
                found = True
                break
        if not found:
            return False

    return True


@lru_cache(maxsize=100)
def condition_lower(condition1: Union[str, Condition], condition2: Union[str, Condition]) -> bool:
    if isinstance(condition1, Condition) and isinstance(condition2, Condition):
        return ConditionHandler.is_lower(condition1, condition2)

    if "and" in condition1:
        cond1 = set(map(lambda s: ConditionHandler.recognize_first(s), condition1.split("and")))
    else:
        cond1 = set()
        cond1.add(ConditionHandler.recognize_first(condition1))
    if "and" in condition2:
        cond2 = set(map(lambda s: ConditionHandler.recognize_first(s), condition2.split("and")))
    else:
        cond2 = set()
        cond2.add(ConditionHandler.recognize_first(condition2))
    # NO_COND cannot coexist with other conditions
    if Condition.NO_COND in cond1 and len(cond1) > 1: cond1.remove(Condition.NO_COND)
    if Condition.NO_COND in cond2 and len(cond2) > 1: cond2.remove(Condition.NO_COND)

    # if cond1/cond2 both have only one condition
    if len(cond1) == 1 and len(cond2) == 1:
        return ConditionHandler.is_lower(cond1.pop(), cond2.pop())
    # composite(children, consent) < consent; composite(children, consent) < children
    # strict condition is less
    # cond1<cond2 is True <=> cond1 condition is more strict than cond2 <=> cond1 has more items <=> cond2 is subset of cond1
    elif cond2.issubset(cond1) and cond1 != cond2:
        return True
    elif len(cond1) >= len(cond2):
        foundParent = 0
        for c2 in cond2:
            for c1 in cond1:
                if ConditionHandler.is_lower(c1, c2):
                    foundParent += 1
        if foundParent == len(cond2):
            return True
    return False


def condition_higher(condition1: Union[str, Condition], condition2: Union[str, Condition]) -> bool:
    # return not condition_lower(condition2, condition1)
    if isinstance(condition1, Condition) and isinstance(condition2, Condition):
        return ConditionHandler.is_higher(condition1, condition2)

    if "and" in condition1:
        cond1 = set(map(lambda s: ConditionHandler.recognize_first(s), condition1.split("and")))
    else:
        cond1 = set()
        cond1.add(ConditionHandler.recognize_first(condition1))
    if "and" in condition2:
        cond2 = set(map(lambda s: ConditionHandler.recognize_first(s), condition2.split("and")))
    else:
        cond2 = set()
        cond2.add(ConditionHandler.recognize_first(condition2))

    # NO_COND cannot coexist with other conditions
    if Condition.NO_COND in cond1 and len(cond1) > 1: cond1.remove(Condition.NO_COND)
    if Condition.NO_COND in cond2 and len(cond2) > 1: cond2.remove(Condition.NO_COND)

    # if cond1/cond2 both have only one condition
    if len(cond1) == len(cond2) == 1:
        return ConditionHandler.is_higher(cond1.pop(), cond2.pop())
    elif cond1.issubset(cond2) and cond1 != cond2:
        return True
    elif len(cond1) <= len(cond2):
        foundParent = 0
        for c1 in cond1:
            for c2 in cond2:
                if ConditionHandler.is_higher(c1, c2):
                    foundParent += 1
        if foundParent == len(cond1):
            return True
    return False
