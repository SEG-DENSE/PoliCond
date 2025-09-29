import re
import yaml
from itertools import product
from config import *
from ontology.data.handler import DataHandler
from ontology.entity.Entity import Entity

DataHandler.preload(data_ontology_path, data_relation_yml)
# WE_PRONOUNS = ['we', 'our', 'us', 'ourselves', 'ours', 'myself', 'my']
third_party_alias = [entity.value for entity in Entity if entity != Entity.UNSPECIFIED and entity != Entity.WE]

"""
This file is to process post-analysis results from YAML files. It resolves unspecified entities and adds missing tuples.
"""

def load_yaml_content(yaml_path: str) -> dict:
    """
    Load and parse YAML file content.
    
    Args:
        yaml_path (str): Path to the YAML file
        
    Returns:
        dict: Parsed YAML content as dictionary
    """
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def resolve_unspecified_entities(content: dict) -> dict:
    """
    Resolve unspecified entities in the content by determining whether they should be classified 
    as 'we' or 'third parties' based on context and evidence.
    
    Args:
        content (dict): The content dictionary containing nodes with entities
        
    Returns:
        dict: Mapping of old nodes to new nodes with resolved entities
    """
    nodes = content['nodes']
    unspecified = list(filter(lambda x: 'unspecified' in x['entity'], nodes))
    we_collect = list(filter(lambda x: 'we' in x['entity'], nodes))
    other_collect = list(filter(lambda x: x not in unspecified and x not in we_collect, nodes))
    we_collect_data = set(map(lambda x: x['data'], we_collect))
    other_collect_data = set(map(lambda x: x['data'], other_collect))

    to_append = []
    new_nodes = {}
    for aTuple in unspecified:
        has_third_party_flag = False
        for anEvidence in aTuple['evidence']:
            candidateEntity = anEvidence['candidateEntity']
            if any([True for alias in third_party_alias if alias in candidateEntity]):
                has_third_party_flag = True
                break

        if aTuple['data'] in we_collect_data:
            new_tuple = aTuple.copy()
            new_tuple['entity'] = Entity.THIRD_PARTIES.value
            new_tuple['tuple'] = re.sub(r'unspecified.*?entity', Entity.THIRD_PARTIES.value, new_tuple['tuple'])
            new_nodes[str(aTuple)] = new_tuple
            to_append.append(new_tuple)
        elif has_third_party_flag:
            new_tuple = aTuple.copy()
            new_tuple['entity'] = Entity.THIRD_PARTIES.value
            new_tuple['tuple'] = re.sub(r'unspecified.*?entity', Entity.THIRD_PARTIES.value, new_tuple['tuple'])
            new_nodes[str(aTuple)] = new_tuple
            to_append.append(new_tuple)
        else:
            new_tuple = aTuple.copy()
            new_tuple['entity'] = Entity.WE.value
            new_tuple['tuple'] = re.sub(r'unspecified entity', Entity.WE.value, new_tuple['tuple'])
            new_nodes[str(aTuple)] = new_tuple
            to_append.append(new_tuple)

    for node in unspecified:
        del content['nodes'][content['nodes'].index(node)]
    content['nodes'].extend(to_append)

    return new_nodes


def add_missing_tuples_from_candidates(content: dict) -> list[dict]:
    """
    Add missing tuples based on candidate data and entities to account for potential network 
    failures or other reasons that may cause data types to be missing.
    
    Args:
        content (dict): The content dictionary containing nodes with entities
        
    Returns:
        list[dict]: List of complementary nodes that were added
    """
    nodes = content['nodes']
    we_not_collect = list(filter(lambda x: 'not' in x['verb'] and 'we' in x['entity'], nodes))
    we_not_collect_data = set(map(lambda x: x['data'], we_not_collect))
    other_not_collect = list(filter(lambda x: x not in we_not_collect, nodes))
    other_not_collect_data = set(map(lambda x: x['data'], other_not_collect))

    collect_nodes = [node for node in nodes if 'unspecified' not in node['entity'] and 'not' not in node['verb']]

    we_collect_nodes = list(filter(lambda x: 'we' in x['entity'], collect_nodes))
    other_collect_nodes = list(filter(lambda x: x not in we_collect_nodes, collect_nodes))

    covered_pair = [(node['entity'], node['data']) for node in nodes]
    uncovered_pair = set()
    for node in collect_nodes:
        evidences = node['evidence']
        candidate_data = []
        candidate_entity = []
        for evid in evidences:
            parser = lambda string: string.strip('{}').split(',')
            candidate_data.extend(list(parser(evid['candidateData'])))
            candidate_entity.extend(list(parser(evid['candidateEntity'])))

            context = ''
            if 'context' in evid:
                context = evid['context']
            if 'sentence' in evid:
                context += evid['sentence']
            context = context.strip().lower()
            new_candidate_data = DataHandler.recognize_as_Data(context)
            candidate_data.extend(map(lambda x: x.value, new_candidate_data))

        if not isinstance(candidate_data, list):
            candidate_data = [candidate_data]
        if not isinstance(candidate_entity, list):
            candidate_entity = [candidate_entity]
        candidate_data = list(set(candidate_data))
        candidate_entity = list(set(candidate_entity))
        for e, d in product(candidate_entity, candidate_data):
            if d and (e, d) not in covered_pair:
                if e == Entity.WE.value:
                    if d not in we_not_collect_data:
                        uncovered_pair.add((e, d))
                elif e == Entity.ANDROID.value:
                    if d not in we_not_collect_data:
                        e = Entity.WE.value
                        uncovered_pair.add((e, d))
                elif e:
                    if d not in other_not_collect_data:
                        uncovered_pair.add((Entity.THIRD_PARTIES.value, d))
                elif not e:
                    e = Entity.WE.value
                    if d not in we_not_collect_data:
                        uncovered_pair.add((e, d))

    complementary_nodes = []
    if uncovered_pair:
        for e, d in uncovered_pair:
            complementary_nodes.append({
                'entity': e,
                'data': d,
                'verb': 'collect',
                'tuple': f"({e}, collect, {d}, any condition)",
            })

    content['rule2'] = list(complementary_nodes)
    return complementary_nodes


def process_post_analysis_results(content: dict) -> dict:
    """
    Process content by resolving unspecified entities.
    
    Args:
        content (dict): The content dictionary containing nodes with entities
        
    Returns:
        dict: Mapping of old nodes to new nodes with resolved entities
    """
    mapping_old2new: dict = resolve_unspecified_entities(content)

    nodes = content['nodes']
    new_tuples = [node['tuple'] for node in mapping_old2new.values()]
    content['rule1'] = new_tuples

    content['tuples'] = [node['tuple'] for node in nodes if 'unspecified' not in node['entity']]
    return mapping_old2new