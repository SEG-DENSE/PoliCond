import re
from collections import deque
from functools import lru_cache
from itertools import combinations
from typing import Union, Optional
from spacy import Language
from ontology.entity.Entity import Entity
import yaml

path1 = r'.\entity_ontology.yml'
path2 = r'.\relation.yml'
ENTITY_SUB_MAPPING = {
    Entity.GOOGLE_ADS: Entity.GOOGLE,
    Entity.GOOGLE_ANALYTICS: Entity.GOOGLE,
    Entity.GOOGLE_CLOUD: Entity.GOOGLE,
    Entity.GOOGLE_MAPS: Entity.GOOGLE,
    Entity.GOOGLE_PLAY: Entity.GOOGLE,
    Entity.GOOGLE_AUTH: Entity.GOOGLE,
    Entity.DOUBLECLICK: Entity.GOOGLE,
    Entity.GMAIL: Entity.GOOGLE,
    Entity.FACEBOOK_ADS: Entity.FACEBOOK,
    Entity.FACEBOOK_GAMING: Entity.FACEBOOK,
    Entity.INSTAGRAM: Entity.FACEBOOK,
    Entity.WHATSAPP: Entity.FACEBOOK,
    Entity.OCULUS: Entity.FACEBOOK,
    Entity.MESSENGER: Entity.FACEBOOK,
    Entity.AMAZON_PRIME: Entity.AMAZON,
    Entity.KINDLE: Entity.AMAZON,
    Entity.AMAZON_MUSIC: Entity.AMAZON,
    Entity.AMAZON_VIDEO: Entity.AMAZON,
    Entity.AWS: Entity.AMAZON,
    Entity.ALEXA: Entity.AMAZON,
    Entity.APPSTORE: Entity.APPLE,
    Entity.ICLOUD: Entity.APPLE,
    Entity.ITUNES: Entity.APPLE,
    Entity.APPLE_MUSIC: Entity.APPLE,
    Entity.APPLE_TV: Entity.APPLE,
    Entity.FACETIME: Entity.APPLE,
    Entity.SIRI: Entity.APPLE,
    Entity.AZURE: Entity.MICROSOFT,
    Entity.XBOX: Entity.MICROSOFT,
    Entity.OUTLOOK: Entity.MICROSOFT,
    Entity.TEAMS: Entity.MICROSOFT,
    Entity.ONEDRIVE: Entity.MICROSOFT,
    Entity.TWEEPY: Entity.TWITTER,
    Entity.TWEETDECK: Entity.TWITTER,
    Entity.SNAPCHAT: Entity.SNAP,
    Entity.SNAP_MAP: Entity.SNAP,
    Entity.BITMOJI: Entity.SNAP,
    Entity.YAHOO_MAIL: Entity.YAHOO,
    Entity.YAHOO_FINANCE: Entity.YAHOO,
    Entity.YAHOO_SPORTS: Entity.YAHOO,
    Entity.VUNGLE_ADS: Entity.VUNGLE,
    Entity.ORACLE_ANALYTICS: Entity.ORACLE,
    Entity.ORACLE_CLOUD: Entity.ORACLE,
    Entity.ORACLE_DATABASE: Entity.ORACLE,
    Entity.ORACLE_ERP: Entity.ORACLE,
    Entity.ORACLE_HCM: Entity.ORACLE,
    Entity.ORACLE_CX: Entity.ORACLE,
    Entity.ORACLE_SCM: Entity.ORACLE,
    Entity.MOAT: Entity.ORACLE,
    Entity.EBAY_STORE: Entity.EBAY,
    Entity.EBAY_AUCTIONS: Entity.EBAY,
    Entity.EBAY_SELLERS: Entity.EBAY,
    Entity.INMOBI_ADS: Entity.INMOBI,
    Entity.INMOBI_ANALYTICS: Entity.INMOBI,
}


class EntityHandler:
    expressions: [Entity, list] = {}
    reversed_expr: [str, Entity] = {}
    sub_mapping: [str, str] = {}

    compiled_expr: [str, re.Pattern] = {}

    @classmethod
    def preload(cls, ontology: str, relation: str):
        cls.load_entity_ontology(ontology)
        cls.load_relations(relation)

    @classmethod
    def load_entity_ontology(cls, filepath: str) -> None:
        """
        load entity_ontology.yml
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        for item in data:
            try:
                dataItem = Entity(item['name'].lower())
                cls.expressions[dataItem] = list(map(lambda x: x.lower(), item['patterns']))
                for pattern in cls.expressions[dataItem]:
                    cls.reversed_expr[pattern] = dataItem
                    cls.compiled_expr[pattern] = re.compile(pattern)  
            except Exception as e:
                print(f"Error parsing {item} loading entity ontology from {filepath}: {e}")

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
                        src_, tgt_ = Entity(src), Entity(tgt)
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
    def is_lower(cls, entity1: Union[Entity, str], entity2: Union[Entity, str]) -> bool:
        """
        whether entity1 is a subordinate of entity2
        """
        if isinstance(entity1, Entity):
            entity1 = entity1.value
        if isinstance(entity2, Entity):
            entity2 = entity2.value
        if entity1 in cls.sub_mapping.get(entity2, []):
            return True
        return False

    @classmethod
    def is_higher(cls, entity1: Union[Entity, str], entity2: Union[Entity, str]) -> bool:
        """
        whether entity1 is higher than entity2
        """
        return cls.is_lower(entity2, entity1)

    @classmethod
    def is_related(cls, entity1: Union[Entity, str], entity2: Union[Entity, str]) -> bool:
        """
        whether entity1 is related to entity2, including equal, lower, and higher
        """
        if isinstance(entity1, str):
            entity1 = EntityHandler.recognize_first(entity1)
            if not entity1:
                return False
        if isinstance(entity2, str):
            entity2 = EntityHandler.recognize_first(entity2)
            if not entity2:
                return False
        return entity1 == entity2 or cls.is_lower(entity1, entity2) or cls.is_higher(entity1, entity2)

    @classmethod
    def recognize_first(cls, input: str) -> Optional[Entity]:
        input = input.lower()
        for expr in cls.compiled_expr:
            if cls.compiled_expr[expr].search(input):
                return cls.reversed_expr[expr]
        return None

    @classmethod
    def recognize_origin(cls, input: str) -> set[str]:
        """
        recognize the original entity name from the input
        """
        input = input.lower()
        ret = set()
        for expr in cls.compiled_expr:
            matcher = cls.compiled_expr[expr].search(input)
            if matcher:
                ret.add(matcher.group())
        return ret

    @classmethod
    @lru_cache(maxsize=300)
    def recognize_as_Entity(cls, input: str) -> set[Entity]:
        if input == 'analytic' or input == 'analytics':
            return {Entity.ANALYTICS}
        elif input == 'google_analytic':
            return {Entity.GOOGLE_ANALYTICS}
        elif input == 'ocial_media' or input == 'social_media':
            return {Entity.SOCIAL_MEDIA}
        elif input == 'haystack':
            return {Entity.HEYSTACK}
        elif input == 'itune':
            return {Entity.ITUNES}
        elif input == 'google_map':
            return {Entity.GOOGLE_MAPS}
        elif input == 'regulatory':
            return {Entity.REGULATORY}
        elif input == 'Subsplash':
            return {Entity.SUBSPLASH}
        elif input == 'unity_ad':
            return {Entity.UNITY_ADS}
        elif input == 'crashlytic':
            return {Entity.CRASHLYTICS}
        elif input == '3rd-party':
            return {Entity.THIRD_PARTIES}
        elif input in ['we','the application','our company']:
            return {Entity.WE}
        elif input in ['advertisers','advertiser','Advertisers']:
            return {Entity.ADVERTISER}
        elif input in ['wireless carrier', 'wireless_carrier']:
            return {Entity.WIRELESS_CARRIER}
        elif input in []:
            return {Entity.THIRD_PARTIES}

        input = input.lower()
        ret = set()
        for expr in cls.compiled_expr:
            if cls.compiled_expr[expr].search(input):
                ret.add(cls.reversed_expr[expr])
        return ret

    @classmethod
    def recognize_as_lower_Entity(cls, input: str) -> set[Entity]:
        input = input.lower()
        candidates = cls.recognize_as_Entity(input)
        to_remove = set()
        for a, b in combinations(candidates,2):
            if cls.is_lower(a, b):
                to_remove.add(b)
            elif cls.is_lower(b, a):
                to_remove.add(a)
        return candidates - to_remove

    @classmethod
    def recognize_as_lower_Entity_spacy(cls, input: str, nlp: Language) -> set[Entity]:
        vec = nlp(input)
        for token in vec:
            if token.ent_type_ == 'ORG':
                return {Entity.WE}

        input = input.lower()
        candidates = cls.recognize_as_Entity(input)
        to_remove = set()
        for a, b in combinations(candidates,2):
            if cls.is_lower(a, b):
                to_remove.add(b)
            elif cls.is_lower(b, a):
                to_remove.add(a)
        return candidates - to_remove


if __name__ == '__main__':
    handler = EntityHandler.preload(path1, path2)
    s1, s2 = "Google", "google_ads"
    s1 = s1.lower()
    s3 = 'meta'

    d3 = Entity(s3)
    s4 = 'facebook'
    d4 = Entity(s4)
    print(EntityHandler.is_related(s1, s2))
    print(EntityHandler.is_higher(s1, s2))
    print(EntityHandler.is_lower(s1, s2))
    print(EntityHandler.is_higher(s1, s3))
    print(EntityHandler.is_higher(s3, s1))
    print(EntityHandler.is_higher(s3, s4))
    print(EntityHandler.is_lower(s3, s4))
    print(EntityHandler.is_lower(d3, d4))
    print(EntityHandler.is_lower(d4, d3))

    print(EntityHandler.recognize_as_lower_Entity('google facebook meta'))
    print(EntityHandler.recognize_first('email google'))

    s5 = 'google ads'
    print(EntityHandler.recognize_as_lower_Entity(s5))
