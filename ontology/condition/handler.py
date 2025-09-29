import re
from collections import deque
from functools import lru_cache
from itertools import combinations
from typing import Union, Optional
import os
import yaml

try:
    from .condition import Condition
    from .dto import ConditionDTO
except ImportError:
    # For direct execution
    try:
        from condition import Condition
        from dto import ConditionDTO
    except ImportError:
        from ontology.condition.condition import Condition
        from ontology.condition.dto import ConditionDTO
    


class ConditionHandler:
    expressions: dict[Condition, list] = {}
    reversed_expr: dict[str, Condition] = {}
    synonyms: dict[Condition, list[str]] = {}
    reversed_syns: dict[str, Condition] = {}

    sub_mapping: dict[Condition, list] = {}
    compiled_expr: dict[str, re.Pattern] = {}
    compiled_syns: dict[str, re.Pattern] = {}

    @classmethod
    def preload(cls, dir_path: str, relation: str):
        """
        Preload condition definitions and relations
        """
        cls.load_definitions(dir_path)
        cls.load_relations(relation)
        return cls

    @classmethod
    def load_definitions(cls, dir_path: str) -> None:
        """
        Load YAML definition files from directory
        """
        files = os.listdir(dir_path)
        yaml_files = [f for f in files if f.endswith('.yaml') or f.endswith('.yml')]
        
        for file in yaml_files:
            filename = file.split(".")[0]
            fullpath = os.path.join(dir_path, file)
            
            try:
                with open(fullpath, 'r', encoding='utf-8') as f:
                    item = yaml.safe_load(f)
                
                if not item or 'name' not in item:
                    print(f"Warning: Invalid YAML structure in {file}")
                    continue
                
                condition = Condition(item['name'].lower())
                
                # Load patterns
                if 'patterns' in item and item['patterns']:
                    cls.expressions[condition] = [pattern.lower() for pattern in item['patterns']]
                    for pattern in cls.expressions[condition]:
                        cls.reversed_expr[pattern] = condition
                        try:
                            cls.compiled_expr[pattern] = re.compile(pattern, re.IGNORECASE)
                        except re.error as e:
                            print(f"Warning: Invalid regex pattern '{pattern}' in {file}: {e}")
                
                # Load synonyms
                if 'synonym' in item and item['synonym']:
                    cls.synonyms[condition] = [syn.lower() for syn in item['synonym']]
                    for synonym in cls.synonyms[condition]:
                        cls.reversed_syns[synonym] = condition
                        try:
                            # Escape special characters for exact matching
                            escaped_syn = re.escape(synonym)
                            cls.compiled_syns[synonym] = re.compile(f"\\b{escaped_syn}\\b", re.IGNORECASE)
                        except re.error as e:
                            print(f"Warning: Invalid synonym pattern '{synonym}' in {file}: {e}")
                            
            except Exception as e:
                print(f"Error loading {file}: {e}")

    @classmethod
    def load_relations(cls, relation_yaml_path: str) -> None:
        """
        Load relation.yml for condition hierarchy
        """
        try:
            with open(relation_yaml_path, 'r', encoding='utf-8') as file:
                content = yaml.safe_load(file)
                
                if not content:
                    print(f"Warning: Empty relation file {relation_yaml_path}")
                    return
                
                for edge in content:
                    try:
                        src, tgt = edge['source'].lower(), edge['target'].lower()
                        src_, tgt_ = Condition(src), Condition(tgt)
                        if src_ and tgt_:
                            if src_ not in cls.sub_mapping:
                                cls.sub_mapping[src_] = []
                            cls.sub_mapping[src_].append(tgt_)
                    except Exception as e:
                        print(f"Error parsing edge {edge}: {e}")

            # Compute transitive closure
            cls.closure()
            
        except Exception as e:
            print(f"Error loading condition relation map from {relation_yaml_path}: {e}")

    @classmethod
    def closure(cls):
        """
        Compute transitive closure of the relation
        """
        for src in list(cls.sub_mapping.keys()):
            visited = set()
            queue = deque(cls.sub_mapping[src][:])  # Copy the list
            
            while queue:
                tgt = queue.popleft()
                if tgt not in visited:
                    visited.add(tgt)
                    if tgt not in cls.sub_mapping[src]:
                        cls.sub_mapping[src].append(tgt)
                    if tgt in cls.sub_mapping:
                        queue.extend(cls.sub_mapping[tgt])

            # Remove duplicates
            cls.sub_mapping[src] = list(set(cls.sub_mapping[src]))

    @classmethod
    def is_lower(cls, data1: Union[Condition, str], data2: Union[Condition, str]) -> bool:
        """
        Check if data1 is a subset of data2 (data1 is more specific than data2)
        """
        if isinstance(data1, str):
            data1 = cls.recognize_first(data1)
        if isinstance(data2, str):
            data2 = cls.recognize_first(data2)

        if not data1 or not data2:
            return False

        return data1 in cls.sub_mapping.get(data2, [])

    @classmethod
    def is_higher(cls, data1: Union[Condition, str], data2: Union[Condition, str]) -> bool:
        """
        Check if data1 is a superset of data2 (data1 is more general than data2)
        """
        return cls.is_lower(data2, data1)

    @classmethod
    def is_related(cls, data1: Union[Condition, str], data2: Union[Condition, str]) -> bool:
        """
        Check if data1 and data2 are related (same, subset, or superset)
        """
        if isinstance(data1, str):
            data1 = cls.recognize_first(data1)
        if isinstance(data2, str):
            data2 = cls.recognize_first(data2)
            
        if not data1 or not data2:
            return False
            
        return data1 == data2 or cls.is_lower(data1, data2) or cls.is_higher(data1, data2)

    @classmethod
    def recognize_first(cls, input_text: str) -> Optional[Condition]:
        """
        Recognize the first matching condition from input text
        """
        input_text = input_text.lower()
        
        # Check patterns first
        for pattern, condition in cls.reversed_expr.items():
            if cls.compiled_expr[pattern].search(input_text):
                return condition
        
        # Check synonyms
        for synonym, condition in cls.reversed_syns.items():
            if cls.compiled_syns[synonym].search(input_text):
                return condition
                
        return None

    @classmethod
    def recognize_origin(cls, input_text: str) -> set[str]:
        """
        Recognize the original expression of the condition
        """
        input_text = input_text.lower()
        ret = set()
        
        for pattern in cls.compiled_expr:
            match = cls.compiled_expr[pattern].search(input_text)
            if match:
                ret.add(match.group())
        
        for synonym in cls.compiled_syns:
            match = cls.compiled_syns[synonym].search(input_text)
            if match:
                ret.add(match.group())
                
        return ret

    @classmethod
    def recognize_as_Condition(cls, input_text: str) -> set[Condition]:
        """
        Recognize all matching conditions from input text
        """
        ret = set()
        input_text = input_text.lower()
        
        for pattern, condition in cls.reversed_expr.items():
            if cls.compiled_expr[pattern].search(input_text):
                ret.add(condition)
        
        for synonym, condition in cls.reversed_syns.items():
            if cls.compiled_syns[synonym].search(input_text):
                ret.add(condition)
                
        return ret

    @classmethod
    @lru_cache(maxsize=300)
    def recognize_as_lower_Condition(cls, input_text: str) -> set[Condition]:
        """
        Recognize conditions and return only the most specific ones (lower in hierarchy)
        """
        candidates = cls.recognize_as_Condition(input_text)
        to_remove = set()
        
        for a, b in combinations(candidates, 2):
            if cls.is_lower(a, b):
                to_remove.add(b)
            elif cls.is_lower(b, a):
                to_remove.add(a)

        return candidates - to_remove

    @classmethod
    @lru_cache(maxsize=300)
    def recognize_as_lower_ConditionDTO(cls, input_text: str) -> set[ConditionDTO]:
        """
        Recognize conditions as DTOs and return only the most specific ones
        """
        ret = set()
        input_text_lower = input_text.lower()
        
        for pattern, condition in cls.reversed_expr.items():
            match = cls.compiled_expr[pattern].search(input_text_lower)
            if match:
                ret.add(ConditionDTO(condition, match.group()))

        for synonym, condition in cls.reversed_syns.items():
            match = cls.compiled_syns[synonym].search(input_text_lower)
            if match:
                ret.add(ConditionDTO(condition, match.group()))

        # Remove more general conditions
        to_remove = set()
        for a, b in combinations(ret, 2):
            if cls.is_lower(a.condition, b.condition):
                to_remove.add(b)
            elif cls.is_lower(b.condition, a.condition):
                to_remove.add(a)

        return ret - to_remove

    @classmethod
    def is_which_condition(cls, input_text: str, which_cond: Condition) -> bool:
        """
        Check if input text matches a specific condition
        """
        try:
            input_text = input_text.lower()
            
            # Check patterns
            if which_cond in cls.expressions:
                for pattern in cls.expressions[which_cond]:
                    if cls.compiled_expr[pattern].search(input_text):
                        return True
            
            # Check synonyms
            if which_cond in cls.synonyms:
                for synonym in cls.synonyms[which_cond]:
                    if cls.compiled_syns[synonym].search(input_text):
                        return True
                        
            return False
        except Exception as e:
            print(f"Error checking condition {which_cond}: {e}")
            return False

    @classmethod
    def findall_condition_expression(cls, input_text: str, which_cond: Condition) -> set[ConditionDTO]:
        """
        Find all expressions of a specific condition in input text
        """
        ret = set()
        try:
            input_text = input_text.lower()
            
            # Check patterns
            if which_cond in cls.expressions:
                for pattern in cls.expressions[which_cond]:
                    matches = cls.compiled_expr[pattern].findall(input_text)
                    for match in matches:
                        ret.add(ConditionDTO(which_cond, match))

            # Check synonyms
            if which_cond in cls.synonyms:
                for synonym in cls.synonyms[which_cond]:
                    if cls.compiled_syns[synonym].search(input_text):
                        ret.add(ConditionDTO(which_cond, synonym))
                        
        except Exception as e:
            print(f"Error finding condition expressions for {which_cond}: {e}")

        return ret


if __name__ == '__main__':
    # Test the condition handler with same structure as old version
    import os
    import sys

    # 获取当前脚本所在目录（即 handler.py 所在目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构造 definition 目录和 relation.yml 的路径
    path1 = os.path.join(current_dir, 'definition')
    path2 = os.path.join(current_dir, 'relation.yml')
    
    print("Loading condition handler...")
    handler = ConditionHandler.preload(path1, path2)
    
    # Test strings - updated for new ontology
    s1, s2 = "children", "specific audience and user action and consent"
    s3 = 'any condition'
    d3 = ConditionHandler.recognize_as_Condition(s3)
    if d3:
        d3= list(d3)[0]
    
    print(f"\nTesting with strings:")
    print(f"s1 = '{s1}'")
    print(f"s2 = '{s2}'") 
    print(f"s3 = '{s3}'")
    print(f"d3 = {d3}")
    
    # Test recognition methods
    condition2 = ConditionHandler.recognize_as_lower_Condition(s2)
    print(f"\nrecognize_as_lower_Condition(s2): {condition2}")
    
    condition22 = ConditionHandler.recognize_as_lower_ConditionDTO(s2)
    print(f"recognize_as_lower_ConditionDTO(s2): {condition22}")
    
    if condition22:
        dto_list = list(condition22)
        if len(dto_list) >= 2:
            first_dto = dto_list[0]
            second_dto = dto_list[1]
            print(f"First DTO condition: {first_dto.condition}")
            print(f"First DTO text: '{first_dto.text}'")
            print(f"Second DTO condition: {second_dto.condition}")
            print(f"Second DTO text: '{second_dto.text}'")
        elif len(dto_list) >= 1:
            first_dto = dto_list[0]
            print(f"DTO condition: {first_dto.condition}")
            print(f"DTO text: '{first_dto.text}'")
    
    condition3 = ConditionHandler.recognize_as_Condition(s2)
    print(f"recognize_as_Condition(s2): {condition3}")
    
    # Test relationship methods (matching original test structure)
    print(f"\n--- Relationship Tests ---")
    
    # False
    result1 = ConditionHandler.is_related(s1, s2)
    print(f"ConditionHandler.is_related('{s1}', '{s2}'): {result1}")
    
    # False - children should not be higher than the complex condition
    result2 = ConditionHandler.is_higher(s1, s2)
    print(f"ConditionHandler.is_higher('{s1}', '{s2}'): {result2}")
    
    # False
    result3 = ConditionHandler.is_lower(s1, s2)
    print(f"ConditionHandler.is_lower('{s1}', '{s2}'): {result3}")
    
    # False 
    result4 = ConditionHandler.is_higher(s1, s3)
    print(f"ConditionHandler.is_higher('{s1}', '{s3}'): {result4}")
    
    # True - any condition should be higher (more general) than children
    result5 = ConditionHandler.is_higher(s3, s1)
    print(f"ConditionHandler.is_higher('{s3}', '{s1}'): {result5}")
    
    # True - children should be lower (more specific) than any condition
    result6 = ConditionHandler.is_lower(s1, d3)
    print(f"ConditionHandler.is_lower('{s1}', d3): {result6}")
    
    # True - any/any condition should be higher than children
    result7 = ConditionHandler.is_higher(d3, s1)
    print(f"ConditionHandler.is_higher(d3, '{s1}'): {result7}")
    
    print(f"\n--- Summary ---")
    print(f"Loaded {len(ConditionHandler.expressions)} condition definitions")
    print(f"Loaded {len(ConditionHandler.sub_mapping)} hierarchical relationships")
    print(f"Test completed successfully!")
