import re
from collections import deque
from functools import lru_cache
from itertools import combinations
from typing import Union, Optional
import os
from ontology.condition.condition import Condition
import yaml

from ontology.condition.dto import ConditionDTO


class ConditionHandler:
    expressions: dict[Condition, list] = {}
    reversed_expr: dict[str, Condition] = {}
    synonyms: dict[Condition, list[str]] = {}
    reversed_syns: dict[str, Condition] = {}

    sub_mapping:  dict[Condition, list] = {}
    compiled_expr:  dict[str, re.Pattern] = {}
    compiled_syns:  dict[str, re.Pattern] = {}

    @classmethod
    def preload(cls, dir_path: str, relation: str):
        cls.load_definitions(dir_path)
        cls.load_relations(relation)

    @classmethod
    def load_definitions(cls, dir_path: str) -> None:
        """
        load yamls
        """
        files = os.listdir(dir_path)
        for file in files:
            filename = file.split(".yml")[0]
            fullpath = os.path.join(dir_path, file)
            with open(fullpath, 'r', encoding='utf-8') as file:
                item = yaml.safe_load(file)
            condition = Condition(item['name'].lower())
            cls.expressions[condition] = list(map(lambda x: x.lower(), item['patterns']))
            cls.synonyms[condition] = list(map(lambda x: x.lower(), item['synonym']))
            for pattern in cls.expressions[condition]:
                cls.reversed_expr[pattern] = condition
                cls.compiled_expr[pattern] = re.compile(pattern)  
            for synonym in cls.synonyms[condition]:
                cls.reversed_syns[synonym] = condition
                cls.compiled_syns[synonym] = re.compile(synonym)  

    @classmethod
    def load_relations(cls, relation_yaml_path: str) -> None:
        """
        load relation.yml 
        """
        try:
            with open(relation_yaml_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)
                for edge in content:
                    try:
                        src, tgt = edge['source'].lower(), edge['target'].lower()
                        src_, tgt_ = Condition(src), Condition(tgt)
                        if src_ and tgt_:
                            cls.sub_mapping[src_] = cls.sub_mapping.get(src_, []) + [tgt_]
                    except Exception as e:
                        print(
                            f"Error parsing ({src},{tgt}) loading condition relation map from {relation_yaml_path}: {e}")

            # transitive closure
            cls.closure()
        except Exception as e:
            print(f"Error loading condition relation map from {relation_yaml_path}: {e}")

    @classmethod
    def closure(cls):
        """
        transitive closure
        """
        for src in list(cls.sub_mapping.keys()):
            visited = set()
            queue = deque(cls.sub_mapping[src])
            while queue:
                tgt = queue.popleft()
                if tgt not in visited:
                    visited.add(tgt)
                    if tgt not in cls.sub_mapping[src]:
                        cls.sub_mapping[src].append(tgt)
                    if tgt in cls.sub_mapping:
                        queue.extend(cls.sub_mapping[tgt])

            # deduplicate
            cls.sub_mapping[src] = list(set(cls.sub_mapping[src]))

    @classmethod
    def is_lower(cls, data1: Union[Condition, str], data2: Union[Condition, str]) -> bool:
        """
        whether data1 is a subset of data2
        """
        if isinstance(data1, str):
            data1 = ConditionHandler.recognize_first(data1)
        if isinstance(data2, str):
            data2 = ConditionHandler.recognize_first(data2)

        if not data1 or not data2:
            return False

        if data1 and data1 in cls.sub_mapping.get(data2, []):
            return True
        return False

    @classmethod
    def is_higher(cls, data1: Union[Condition, str], data2: Union[Condition, str]) -> bool:
        """
        whether data1 is a superset of data2
        """
        return cls.is_lower(data2, data1)

    @classmethod
    def is_related(cls, data1: Union[Condition, str], data2: Union[Condition, str]) -> bool:
        """
        whether data1 and data2 are related, including same, subset or superset relationship
        """
        return data1 == data2 or cls.is_lower(data1, data2) or cls.is_higher(data1, data2)

    @classmethod
    def recognize_first(cls, input: str) -> Optional[Condition]:
        input = input.lower()
        for expr in cls.compiled_expr:
            if cls.compiled_expr[expr].search(input):
                return cls.reversed_expr[expr]
        for syn in cls.compiled_syns:
            if cls.compiled_syns[syn].search(input):
                return cls.reversed_syns[syn]
        return None

    @classmethod
    def recognize_origin(cls, input: str) -> set[str]:
        """
        recognize the original expression of the condition
        """
        input = input.lower()
        ret = set()
        for expr in cls.compiled_expr:
            matcher = cls.compiled_expr[expr].search(input)
            if matcher:
                ret.add(str(matcher.group()))
        for syn in cls.compiled_syns:
            matcher = cls.compiled_syns[syn].search(input)
            if matcher:
                ret.add(str(matcher.group()))
        return ret

    @classmethod
    def recognize_as_Condition(cls, input: str) -> set[Condition]:
        ret = set()
        input = input.lower()
        for expr in cls.compiled_expr:
            if cls.compiled_expr[expr].search(input):
                ret.add(cls.reversed_expr[expr])
        for syn in cls.compiled_syns:
            if cls.compiled_syns[syn].search(input):
                ret.add(cls.reversed_syns[syn])
        return ret

    @classmethod
    @lru_cache(maxsize=300)
    def recognize_as_lower_Condition(cls, input: str) -> set[Condition]:
        candidates = cls.recognize_as_Condition(input)
        to_remove = set()
        for a, b in combinations(candidates,2):
            if cls.is_lower(a, b):
                to_remove.add(b)
            elif cls.is_lower(b, a):
                to_remove.add(a)

        return candidates - to_remove

    @classmethod
    @lru_cache(maxsize=300)
    def recognize_as_lower_ConditionDTO(cls, input: str) -> set[ConditionDTO]:
        ret = set()
        input = input.lower()
        for expr in cls.compiled_expr:
            match = cls.compiled_expr[expr].search(input)
            if match:
                cond = cls.reversed_expr[expr]
                ret.add(ConditionDTO(cond, str(match.group())))

        for syn in cls.compiled_syns:
            match = cls.compiled_syns[syn].search(input)
            if match:
                cond = cls.reversed_syns[syn]
                ret.add(ConditionDTO(cond, str(match.group())))

        to_remove = set()
        for a, b in combinations(ret,2):
            if cls.is_lower(a.condition, b.condition):
                to_remove.add(b)
            elif cls.is_lower(b.condition, a.condition):
                to_remove.add(a)

        return ret-to_remove

    @classmethod
    def is_which_condition(cls, input: str, which_cond: Condition) -> bool:
        try:
            input = input.lower()
            patterns = cls.expressions[which_cond]
            for pattern in patterns:
                if cls.compiled_expr[pattern].search(input):
                    return True
            for synonym in cls.synonyms[which_cond]:
                if cls.compiled_syns[synonym].search(input):
                    return True
            return False
        except Exception as e:
            print(f"Error checking condition {which_cond}: {e}")
            return False

    @classmethod
    def findall_condition_expression(cls, input: str, which_cond: Condition) -> set[ConditionDTO]:
        ret = set()
        try:
            input = input.lower()
            patterns = cls.expressions[which_cond]
            for pattern in patterns:
                matches = cls.compiled_expr[pattern].findall(input)
                for match in matches:
                    ret.add(ConditionDTO(which_cond, match))

            # Synonyms
            synonyms = cls.synonyms[which_cond]
            for synonym in synonyms:
                if cls.compiled_syns[synonym].search(input) and which_cond not in ret:
                    ret.add(ConditionDTO(which_cond, synonym))
        except Exception as e:
            print(f"Error finding condition expressions for {which_cond}: {e}")

        return ret

if __name__ == '__main__':
    path1 = r'.\definition'
    path2 = r'.\relation.yml'
    handler = ConditionHandler.preload(path1, path2)
    s1, s2 = "children", "special audience and user action and user consent"
    s3 = 'no condition'
    d3 = Condition(s3)
    condition2=ConditionHandler.recognize_as_lower_Condition(s2)
    print(condition2)
    condition22=ConditionHandler.recognize_as_lower_ConditionDTO(s2)
    print(condition22)
    if condition22:
        print(condition22.pop().condition)
        print(condition22.pop().text)
    condition3=ConditionHandler.recognize_as_Condition(s2)
    print(condition3)
    # True
    print(ConditionHandler.is_related(s1, s2))
    # False
    print(ConditionHandler.is_higher(s1, s2))
    # True
    print(ConditionHandler.is_lower(s1, s2))
    # False
    print(ConditionHandler.is_higher(s1, s3))
    # True
    print(ConditionHandler.is_higher(s3, s1))
    # True
    print(ConditionHandler.is_lower(s1, d3))
    # True
    print(ConditionHandler.is_higher(d3, s1))
