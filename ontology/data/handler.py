import re
from collections import deque
from functools import lru_cache
from itertools import combinations
from typing import Union, Optional

from ontology.data.Data import Data
import yaml

path1 = r'.\data_ontology.yml'
path2 = r'.\relation.yml'
NON_PERSONAL=[Data.PSEUDONYMOUS.value,Data.AGGRAGATE.value,Data.ANONYMOUS.value,
            Data.NON_PERSONAL_INFO.value]
class DataHandler:
    expressions: dict[Data, list[str]] = {}
    reversed_expr: dict[str, Data] = {}
    sub_mapping: dict[str, list[str]] = {}
    compiled_expr: dict[str, re.Pattern] = {}

    @classmethod
    def preload(cls, ontology:str,relation: str):
        cls.load_data_ontology(ontology)
        cls.load_relations(relation)

    @classmethod
    def load_data_ontology(cls, filepath: str) -> None:
        """
        load data_ontology.yml 
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        for item in data:
            dataItem = Data(item['name'].lower())
            cls.expressions[dataItem] = list(map(lambda x: x.lower(), item['patterns']))
            for pattern in cls.expressions[dataItem]:
                cls.reversed_expr[pattern] = dataItem
                cls.compiled_expr[pattern] = re.compile(pattern)

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
                        src_, tgt_ = Data(src), Data(tgt)
                        if src_ and tgt_:
                            cls.sub_mapping[src] = cls.sub_mapping.get(src, []) + [tgt]
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
    def is_lower(cls, data1: Union[Data, str], data2: Union[Data, str]) -> bool:
        """
        whether data1 is a subordinate of data2
        """
        if isinstance(data1, Data):
            data1 = data1.value
        if isinstance(data2, Data):
            data2 = data2.value
        if data1 in cls.sub_mapping.get(data2, []):
            return True
        return False

    @classmethod
    def is_higher(cls, data1: Union[Data, str], data2: Union[Data, str]) -> bool:
        """
        whether data1 is a superior of data2
        """
        return cls.is_lower(data2, data1)

    @classmethod
    def is_related(cls, data1: Union[Data, str], data2: Union[Data, str]) -> bool:
        """
        whether data1 and data2 are related, including same, subset or superset relationship
        """
        if isinstance(data1,str):
            data1=DataHandler.recognize_first(data1)
            if not data1:
                return False
        if isinstance(data2,str):
            data2 = DataHandler.recognize_first(data2)
            if not data2:
                return False
        assert isinstance(data1,Data) and isinstance(data2,Data)
        if data1.value in NON_PERSONAL and data2.value in NON_PERSONAL:
            return True
        elif data1.value in NON_PERSONAL or data2.value in NON_PERSONAL:
            return False

        return data1 == data2 or cls.is_lower(data1, data2) or cls.is_higher(data1, data2)

    @classmethod
    def is_loose_related(cls, data1: Union[Data, str], data2: Union[Data, str]) -> bool:
        """
        whether data1 and data2 are related, including same, subset or superset relationship;
        advertising_id and advertising_statistics are considered the same
        """
        if isinstance(data1, str):
            data1 = DataHandler.recognize_first(data1)
            if not data1:
                return False
        if isinstance(data2, str):
            data2 = DataHandler.recognize_first(data2)
            if not data2:
                return False
        assert isinstance(data1, Data) and isinstance(data2, Data)
        if all(d in [Data.ADVERTISING_ID,Data.ADVERTISING_STATISTICS] for d in [data1,data2]):
            return True

        return DataHandler.is_related(data1, data2)

    @classmethod
    def recognize_first(cls, input: str) -> Optional[Data]:
        for expr in cls.compiled_expr:
            if cls.compiled_expr[expr].search(input):
                return cls.reversed_expr[expr]
        return None

    @classmethod
    def recognize_origin(cls, input: str) -> set[str]:
        """
        recognize the original string of data
        """
        ret = set()
        for expr in cls.compiled_expr:
            matcher = cls.compiled_expr[expr].search(input)
            if matcher:
                ret.add(matcher.group())
        return ret

    @classmethod
    @lru_cache(maxsize=300)
    def recognize_as_Data(cls, input: str) -> set[Data]:
        if input == 'advertising identifier':
            return {Data.ADVERTISING_ID}
        elif input == 'cookie' or input == 'cookies':
            return {Data.COOKIE}
        elif input in ['email address', 'email_addre']:
            return {Data.EMAIL}
        elif input in ["ip addre", "ip address", 'ip_addre']:
            return {Data.IP_ADDRESS}
        elif input in ["mac address","mac_addre"]:
            return {Data.MAC_ADDRESS}
        elif input == "sim serial number":
            return {Data.SIM_SERIAL_NUMBER}
        elif input in ["account",'account_name']:
            return {Data.ACCOUNT}
        elif input in ["device","device information"]:
            return {Data.DEVICE}
        elif input == "addre":
            return {Data.ADDRESS}
        elif input == "application":
            return {Data.APPLICATION}
        elif input == 'ensitive_info':
            return {Data.SENSITIVE_INFO}
        elif input == 'oftware_identifier':
            return {Data.SOFTWARE_IDENTIFIER}
        elif input == 'anonymou':
            return {Data.ANONYMOUS}
        elif input == 'gender':
            return {Data.GENDER}
        elif input == 'wifi':
            return {Data.WIFI}
        elif input == 'operating system':
            return {Data.OS}
        elif input == 'race':
            return {Data.RACE}
        elif input == 'id_card':
            return {Data.ID_CARD}
        elif input == 'passport':
            return {Data.PASSPORT}
        elif input == 'pseudonymou':
            return {Data.PSEUDONYMOUS}
        elif input in ['demographic_data', 'demographic data','demographic information']:
            return {Data.AGGRAGATE}
        elif input in ['card detail','payment data','payment_card_info','payment_info','credit_card_number',
                'debit_card_number','education_information','employment_information','financial_information',
            'health_information','health_insurance_information','health_medical_information','insurance_policy_number',
                       'purchase_history','credit_card_info','credit_card_information','debit_card_info','payment_data']:
            return {Data.PROTECTED_INFORMATION}


        ret = set()
        for expr in cls.compiled_expr:
            if cls.compiled_expr[expr].search(input):
                ret.add(cls.reversed_expr[expr])

        return ret

    @classmethod
    def recognize_as_lower_Data(cls, input: str) -> set[Data]:
        if input in ['os']:
            return {Data.OS}
        elif input in ['anonymous']:
            return {Data.ANONYMOUS}
        elif input in ['security']:
            return {Data.SECURITY}
        elif input in ['sex']:
            return {Data.GENDER}
        elif input in ['fraud_data']:
            return {Data.NON_PERSONAL_INFO}
        elif input in ['disability','physical_description','marital_status','medical_condition','medical_history',]:
            return {Data.PROTECTED_INFORMATION}
        elif input in ['navigation','browsing','interaction','engagement']:
            return {Data.INTERNET_ACTIVITY}


        candidates = cls.recognize_as_Data(input)
        to_remove = set()
        for a, b in combinations(candidates,2):
            if cls.is_lower(a, b):
                to_remove.add(b)
            elif cls.is_lower(b, a):
                to_remove.add(a)
        return candidates - to_remove


if __name__ == '__main__':
    handler = DataHandler.preload(path1, path2)
    str1="email address"
    str2="personal information"
    d1=DataHandler.recognize_first(str1)
    print(d1)
    d2=DataHandler.recognize_first(str2)
    print(d2)
    print(DataHandler.is_related(d1,d2))
