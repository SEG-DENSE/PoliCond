import json
import os.path
import re
import sys
import time
from collections import defaultdict
from typing import Optional, Callable

import yaml
from bs4 import BeautifulSoup

from config import *
from contradiction.rule import apply_rule
from node import CollectionNode, CollectionNodeWithContext
from ontology.condition.condition import Condition
from ontology.condition.handler import ConditionHandler
from ontology.data.handler import DataHandler
from ontology.entity.handler import EntityHandler
from util.structured.judge_negation import has_negation


def normalize_condition(best_entry: dict) -> dict:
    """
    Normalize the condition by merging subconditions for third party and user action.
    """
    conds: set[Condition] = ConditionHandler.recognize_as_lower_Condition(best_entry['condition'].lower())
    if Condition.NO_COND in conds and len(conds) > 1:
        conds.remove(Condition.NO_COND)

    # Merge third party service and data sharing to third party
    if Condition.THIRD_PARTY_SERVICE in conds or Condition.DATA_SHARING in conds:
        conds = conds - {Condition.THIRD_PARTY_SERVICE, Condition.DATA_SHARING}
        conds.add(Condition.THIRD_PARTY)

    # Merge user action and input, consent, specific operation to user action
    if Condition.INPUT in conds or Condition.CONSENT in conds or Condition.SPECIFIC_OPERATION in conds:
        conds = conds - {Condition.INPUT, Condition.CONSENT, Condition.SPECIFIC_OPERATION}
        conds.add(Condition.USER_ACTION)

    if Condition.SPECIFIC_AUDIENCE in conds and (Condition.CHILDREN in conds or Condition.REGION in conds):
        conds.remove(Condition.SPECIFIC_AUDIENCE)
    # Note: MANAGEMENT condition has been removed from the new ontology
    # Security and retention conditions are now handled separately

    new_conds_str = ' and '.join(map(lambda x: x.value, conds))
    if not new_conds_str:
        new_conds_str = 'any condition'
    if new_conds_str != best_entry['condition']:
        print(f"Cond trans: {best_entry['condition']} -> {new_conds_str}")
    best_entry['condition'] = new_conds_str
    return best_entry


def get_final_condition(conditions: list[str]) -> str:
    """
    Merge multiple conditions into a single condition string.
    """
    no_cond = Condition.NO_COND.value
    conditions = ConditionHandler.recognize_as_lower_Condition(' '.join(conditions))
    if not conditions:
        return no_cond
    if len(conditions) == 1:
        return list(conditions)[0].value
    return ' and '.join(map(lambda x: x.value, conditions))


def reduce_nodes(nodes: list[CollectionNodeWithContext]) -> list[CollectionNodeWithContext]:
    """
    Reduce nodes by grouping and merging conditions.
    """
    filtered = []
    grouped = defaultdict(list)
    for n in nodes:
        key = (n.entity, n.verb, n.data, n.sentence)
        grouped[key].append(n)

    for key, group in grouped.items():
        if len(group) > 1:
            conditions = [n.condition.value if isinstance(n.condition, Condition) else str(n.condition) for n in group]
            final_condition = get_final_condition(conditions)
            base_node = group[0]
            base_node.condition = final_condition
            filtered.append(base_node)
        else:
            filtered.append(group[0])

    return filtered


def filter_negation_nodes(nodes: list[CollectionNodeWithContext]) -> list[CollectionNodeWithContext]:
    """
    Filter nodes with negation in their verb and context.
    """
    ret = [n for n in nodes if 'not' in n.verb and has_negation(n.context)]
    # differ = [n for n in nodes if n not in ret]
    # if differ:
    #     for n in differ:
    #         print("here is a negation node filtered: ", n.pretty_print())
    #         print("--------------------------------------------")
    #         print(n.context)
    #         print("--------------------------------------------")
    return ret


class Evidence:
    __slots__ = ['sentence', 'context', 'candidateEntity', 'candidateVerb', 'candidateData', 'candidateCondition',
                 'sentenceIntegrity']

    def __init__(self, sentence, context, candidateEntityStr: str, candidateVerb, candidateDataStr: str,
                 candidateConditionStr: str):
        self.sentence = sentence
        self.context = context
        self.candidateEntity = candidateEntityStr
        self.candidateVerb = candidateVerb
        self.candidateData = candidateDataStr
        self.candidateCondition = candidateConditionStr
        self.sentenceIntegrity = (sentence == context)

    def __str__(self):
        return f"Evidence(sentence='{self.sentence}', context='{self.context}', candidateEntity='{self.candidateEntity}', " \
               f"candidateData='{self.candidateData}', candidateCondition='{self.candidateCondition}'," \
               f"sentenceIntegrity={str(self.sentenceIntegrity)})"


def choose_best_node_between_group_nodes(group: list[CollectionNode]):
    if len(group) > 1:
        valid_nodes = [n for n in group if 'any condition' not in n.condition]
        votes = {
            Condition.CHILDREN: 0,
            Condition.REGION: 0,
            Condition.USER_ACTION: 0,
            Condition.THIRD_PARTY: 0,
            Condition.SECURITY: 0,
            Condition.RETENTION: 0,
        }
        if len(group) - len(valid_nodes) > 0.6667 * len(group):
            return [n for n in group if 'any condition' in n.condition][0]

        for node in valid_nodes:
            recognise = ConditionHandler.recognize_as_lower_Condition(node.condition)
            for cond in recognise:
                if ConditionHandler.is_lower(cond, Condition.CHILDREN):
                    votes[Condition.CHILDREN] += 1
                elif ConditionHandler.is_lower(cond, Condition.REGION):
                    votes[Condition.REGION] += 1
                elif ConditionHandler.is_lower(cond, Condition.USER_ACTION):
                    votes[Condition.USER_ACTION] += 1
                elif ConditionHandler.is_lower(cond, Condition.THIRD_PARTY):
                    votes[Condition.THIRD_PARTY] += 1
                elif ConditionHandler.is_lower(cond, Condition.SECURITY):
                    votes[Condition.SECURITY] += 1
                elif ConditionHandler.is_lower(cond, Condition.RETENTION):
                    votes[Condition.RETENTION] += 1

        new_base_node = CollectionNodeWithContext(group[0].entity, group[0].verb, group[0].data, group[0].condition,
                                                  group[0].candidateEntity, group[0].candidateVerb, group[0].candidateData,
                                                  group[0].candidateCondition, group[0].sentence, group[0].context)
        new_condition = []
        for key in votes:
            if votes[key] > 0.33 * len(valid_nodes):
                new_condition.append(key.value)
        if not new_condition:
            max_key = max(votes, key=votes.get)
            if votes[max_key] > 0.25 * len(valid_nodes):
                new_condition.append(max_key.value)
        if not new_condition:
            new_condition.append('any condition')
        new_condition_str = ' and '.join(new_condition)
        new_base_node.condition = new_condition_str
        print(f"Choose best node: {new_condition_str} for {len(group)} nodes, i.e. : ({group[0].entity}, {group[0].verb}, {group[0].data}, {new_condition_str})")
        return new_base_node
    else:
        print(f"Single node for this group, that is: ({group[0].entity}, {group[0].verb}, {group[0].data}, {group[0].condition})")
        return group[0]


def merge_node(nodes: list[CollectionNodeWithContext]) -> list[CollectionNode]:
    """
    Merge nodes by grouping and creating CollectionNode objects.
    """
    filtered = []
    grouped = defaultdict(list)
    for n in nodes:
        key = (n.entity, n.verb, n.data)
        grouped[key].append(n)

    for key, group in grouped.items():
        base_node = choose_best_node_between_group_nodes(group)
        contexts = []
        for n in group:
            ctx = Evidence(
                sentence=n.sentence,
                context=n.context,
                candidateEntityStr="{" + ",".join(n.candidateEntity) + "}",
                candidateVerb=n.candidateVerb,
                candidateDataStr="{" + ",".join(n.candidateData) + "}",
                candidateConditionStr="{" + ",".join(n.candidateCondition) + "}",
            )
            contexts.append(ctx)
        collection_node = CollectionNode(
            entity=base_node.entity,
            verb=base_node.verb,
            data=base_node.data,
            condition=base_node.condition,
            text=base_node.text,
            contexts=contexts
        )
        filtered.append(collection_node)

    return filtered


def generate_yaml_report(name: str, output_yaml_path: str, contradictions: list[tuple[CollectionNode, CollectionNode]],
                         narrowing: list[tuple[CollectionNode, CollectionNode]], pos_nodes: list[CollectionNode],
                         neg_nodes: list[CollectionNode], policy_content: str):
    entities = list(set([node.entity.strip() for node in pos_nodes + neg_nodes]))
    data_items = list(set([node.data.strip() for node in pos_nodes + neg_nodes]))
    conditions = list(set([node.condition.strip() for node in pos_nodes + neg_nodes]))
    contradiction_pair_num = len(contradictions)
    narrowing_pair_num = len(narrowing)
    policy_length = len(policy_content)

    nodes_info: list[dict] = []
    tuples: set[str] = set()
    for node in pos_nodes + neg_nodes:
        evidence_list = []
        for idx, ctx in enumerate(node.extra.get('contexts', [])):
            context_dict = {
                'evidenceId': (idx + 1),
                'sentence': ctx.sentence,
                'candidateEntity': ctx.candidateEntity,
                'candidateData': ctx.candidateData,
                'candidateCondition': ctx.candidateCondition,
            }
            if ctx.context != ctx.sentence:
                context_dict['context'] = ctx.context
                context_dict['sentenceIntegrity'] = False
            else:
                context_dict['sentenceIntegrity'] = True
            evidence_list.append(context_dict)
            tuples.add(node.pretty_print())
        node_dict = {
            'tuple': node.pretty_print(),
            'entity': node.entity.strip(),
            'verb': node.verb.strip(),
            'data': node.data.strip(),
            'condition': node.condition.strip(),
            'evidence': evidence_list,
        }
        nodes_info.append(node_dict)

    contradiction_pairs = [f"{pair[0].pretty_print()} vs {pair[1].pretty_print()}" for pair in contradictions]
    narrowing_pairs = [f"{pair[0].pretty_print()} vs {pair[1].pretty_print()}" for pair in narrowing]

    contexts_info = []
    for node in pos_nodes + neg_nodes:
        for ctx in node.extra.get('contexts', []):
            context_dict = {
                'sentence': ctx.sentence,
                'context': ctx.context,
                'candidateEntity': ctx.candidateEntity,
                'candidateVerb': ctx.candidateVerb,
                'candidateData': ctx.candidateData,
                'candidateCondition': ctx.candidateCondition,
            }
            contexts_info.append(context_dict)

    data = {
        'tuples': sorted(list(tuples)),
        'basicInfo': {
            'name': name,
            'policyLength': policy_length,
            'tupleNum': len(tuples),
            'entityNum': len(entities),
            'entities': entities,

            'dataItemNum': len(data_items),
            'dataItems': data_items,

            'conditionNum': len(conditions),
            'occuredConditions': conditions,

            'contradictionPairNum': contradiction_pair_num,
            'narrowingPairNum': narrowing_pair_num,
            'collectionTupleNum': len(pos_nodes),
            'negationTupleNum': len(neg_nodes),
        },

        'nodes': sorted(nodes_info, key=lambda x: str(x)),
        'contradictionPairs': sorted(contradiction_pairs, key=lambda x: str(x)),
        'narrowingPairs': sorted(narrowing_pairs, key=lambda x: str(x)),

    }

    with open(output_yaml_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, default_flow_style=False, width=1024)


def analyze_nodes(objects: list[CollectionNodeWithContext]):
    # results: list[dict] = extract(json_path)
    pos: list[CollectionNodeWithContext] = list(filter(lambda x: x.verb.strip() == 'collect', objects))
    neg: list[CollectionNodeWithContext] = list(filter(lambda x: x.verb.strip() == 'not collect', objects))

    # first filter
    pos: list[CollectionNodeWithContext] = reduce_nodes(pos)
    neg: list[CollectionNodeWithContext] = reduce_nodes(neg)
    # second filter
    neg: list[CollectionNodeWithContext] = filter_negation_nodes(neg)

    pos_nodes: list[CollectionNode] = merge_node(pos)
    neg_nodes: list[CollectionNode] = merge_node(neg)

    contradictions: [(CollectionNode, CollectionNode)] = []
    narrowing: [(CollectionNode, CollectionNode)] = []
    apply_rule(pos_nodes, neg_nodes, contradictions, narrowing)

    return contradictions, narrowing, pos_nodes, neg_nodes


def load_data(self, policy_full_path: str) -> list[str]:
    """
    Load and preprocess data from a policy file.
    Performs sentence splitting first, then lemmatization on each sentence.
    Args:
        policy_full_path (str): Path to the policy file.
    Returns:
        list[str]: A list of preprocessed and lemmatized sentences.
    """
    with open(policy_full_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'svg' in content or 'DOCTYPE' in content:
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text()

        # Step 1: Use spaCy to split content into sentences
        doc = self.nlp(content)
        sentences = [sent.text for sent in doc.sents]

        # Step 2: Perform lemmatization on each sentence
        lemmatized_sentences = []
        for sent in sentences:
            sent = re.sub(r"(\n\n|\t|\r)", "", sent).strip()
            sent_doc = self.nlp(sent)
            lemmatized_sentence = " ".join(token.lemma_ for token in sent_doc)
            lemmatized_sentences.append(lemmatized_sentence)

        return lemmatized_sentences


def load_jsonl_data(jsonl_path: str) -> list[CollectionNodeWithContext]:
    """
    Load and parse JSONL data into a list of NewCollectionNode objects.
    """
    nodes = []
    EntityHandler.preload(entity_ontology_path, entity_relation_yml)
    DataHandler.preload(data_ontology_path, data_relation_yml)
    ConditionHandler.preload(condition_dir_path, condition_relation_yml)

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            json_data = json.loads(line)
            sentence = json_data['sentence']
            context = json_data['context']
            candidate_entities = json_data['candidate_entities']
            candidate_data = json_data['candidate_data']
            candidate_conditions = json_data['candidate_conditions']
            response = json_data['response']

            tuples = re.findall(TUPLE_PATTERN, response)
            for t in tuples:
                entity, verb, data, condition = t
                node = CollectionNodeWithContext(
                    entity, verb, data, condition,
                    candidate_entities, 'None', candidate_data, candidate_conditions,
                    sentence, context
                )
                nodes.append(node)

    return nodes


def process_single_file(jsonl_path: str, output_yaml_path: str, policy_path: str, policy_name: str = "Zynga"):
    """
    Process a single JSONL file and generate a YAML report.
    """
    start_time = time.time()
    nodes = load_jsonl_data(jsonl_path)
    contradictions, narrowing, pos_nodes, neg_nodes = analyze_nodes(nodes)

    print("contradictions num: ", len(contradictions))
    print("narrowing num: ", len(narrowing))
    print("pos_nodes num: ", len(pos_nodes))
    print("neg_nodes num: ", len(neg_nodes))
    for pair in contradictions:
        print(f"{pair[0].pretty_print()}.vs.{pair[1].pretty_print()}")

    with open(policy_path, 'r', encoding='utf-8') as f:
        policy_content = f.read()

    generate_yaml_report(policy_name, output_yaml_path, contradictions, narrowing, pos_nodes, neg_nodes, policy_content)
    running_time = time.time() - start_time
    logger.info(f"Time cost: {running_time:.2f} seconds.")


def process_batch(jsonl_dir: str, yaml_dir: str, policy_dir: str, filter_func: Optional[Callable] = None):
    """
    Process multiple JSONL files in a directory and generate YAML reports.
    """
    logger.info(f"Processing LLM outputs directory: {jsonl_dir} and policies directory: {policy_dir}")
    start_time = time.time()
    for root, _, files in os.walk(jsonl_dir):
        for file in files:
            if file.endswith('.jsonl') and 'analysis' in file:
                jsonl_path = os.path.join(root, file)
                yaml_path = os.path.join(root, "analysis.yaml")
                if os.path.exists(os.path.join(root, "cleaned.html")):
                    content_path =os.path.join(root, "cleaned.html")
                elif os.path.exists(os.path.join(root, "cleaned.md")):
                    content_path =os.path.join(root, "cleaned.md")
                else:
                    html_files=[f for f in os.listdir(root) if f.endswith('.html') or f.endswith(".htm") or f.endswith('.txt') or f.endswith('.md')]
                    print("default naming is: cleaned.html, second for cleaned.md, at last try using the first file with .html/.htm/.txt/.md suffix")
                    content_path = os.path.join(root, html_files[0])

                policy_name = os.path.basename(root)
                if filter_func and filter_func(policy_name):
                    print(f"Skipping {policy_name}")
                    continue

                try:
                    print(f"Processing {policy_name}")
                    process_single_file(jsonl_path, yaml_path, content_path, policy_name)
                except Exception as e:
                    print(f"Error processing {policy_name}: {e.args}")
                    e.with_traceback()
    running_time = time.time() - start_time
    logger.info(f"Overall running time: {running_time:.2f} seconds.")


def redirect_output_to_file(file_path):
    output_file = open(file_path, 'w')

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    sys.stdout = output_file
    sys.stderr = output_file

    try:
        print("This will be written to the file instead of the console.")
        print("Errors will also be written to the file.", file=sys.stderr)
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        output_file.close()