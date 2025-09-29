from collections import defaultdict
import os
import yaml
import csv
import pandas as pd

# Config 1
# USE_POLIGRAPH_CONTRADICTION_RULE = True
# Config 2: use simpler contradiction rule
USE_POLIGRAPH_CONTRADICTION_RULE = False

dir_path = r'..\datasets\apps-PoliGraph\yamls'
output_file = os.path.join(dir_path, 'contradictions.csv')
output_file2 = os.path.join(dir_path, 'contradiction_context.csv')
output_file3 = os.path.join(dir_path, 'contradiction_context_updated.csv')
to_delete_files = [
    'accessibility_tree.json',
    'cleaned.html',
    'pageText.txt',
    'readability.json',
    'document.pickle'
]
to_kept = [
    'graph-extended.full.yml',
    'graph-extended.yml',
    'graph-original.full.yml',
    'graph-original.yml',
    'misleading_definitions.csv'
]
yamls = ['graph-extended.full.yml']

word_map = {
    'BE_SHARED': 'NOT_BE_SHARED',
    'COLLECT': 'NOT_COLLECT',
    'BE_SOLD': 'NOT_BE_SOLD',
    'STORE': 'NOT_STORE',
    'USE': 'NOT_USE',
    'NOT_USE': 'USE',
    'NOT_COLLECT': 'COLLECT',
    'NOT_BE_SHARED': 'BE_SHARED',
    'NOT_BE_SOLD': 'BE_SOLD',
    'NOT_STORE': 'STORE',
}
positive = ['COLLECT', 'BE_SHARED', 'BE_SOLD', 'STORE', 'USE']
negative = ['NOT_COLLECT', 'NOT_BE_SHARED', 'NOT_BE_SOLD', 'NOT_STORE', 'NOT_USE']


def delete():
    cnt = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file not in to_kept:
                os.remove(os.path.join(root, file))
                print(f"Deleted {file} from {root}")
                cnt += 1

    print(f"Deleted {cnt} files")


def check_verbs():
    seen_verbs = defaultdict(int)
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file in yamls:
                full_yaml_path = os.path.join(root, file)
                with open(full_yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    nodes = data['links']
                    for node in nodes:
                        key = node['key']
                        if key not in seen_verbs:
                            seen_verbs[key] = 1
                            print("Found first verb:", key)
                        else:
                            seen_verbs[key] += 1
    print(f"Found {len(seen_verbs)} verbs")
    print("Verbs and their counts:")
    for verb, count in seen_verbs.items():
        print(f"{verb}: {count}")




def output_contradiction():
    header = ['id', 'filename', 'entity1', 'verb1', 'data1', 'entity2', 'verb2', 'data2', ]
    header2 = ['id', 'filename', 'context1', 'context2']
    cnt = 0
    ANONYMIZED = ['aggregate / deidentified / pseudonymized information', 'non-personal information',
                  'aggregate information',
                  'anonymized information', 'non-identifiable information', 'non-identifiable data',
                  'pseudonymized data',
                  'pseudonymized information', 'anonymized data', 'deidentified information', 'non-personal data',
                  'aggregate statistical information'
        , 'deidentifie information', 'demographic detail', 'demographic', 'demographic information', 'demographic data',
                  'aggregate', 'non-identifiable', 'non-identifiable', 'non-identifiable information', 'anonymized',
                  'data aggregate', 'cpu information'
                                    'anonymous'
                  ]

    def find_contradiction(nodes):
        nonlocal cnt
        contradictions = []
        positive_nodes = [node for node in nodes if node['key'] in positive]
        negative_nodes = [node for node in nodes if node['key'] in negative]
        subsumes = [node for node in nodes if node['key'] == 'SUBSUM']
        subordinates = defaultdict(list)
        for edge in subsumes:
            source = edge['source']
            target = edge['target']
            subordinates[source].append(target)

        while True:
            old_subordinates = subordinates.copy()
            for father in subordinates:
                for child in subordinates[father]:
                    if child in subordinates:
                        subordinates[father].extend(subordinates[child])

            if old_subordinates == subordinates:
                break

        visited = set()
        for pos in positive_nodes:
            for neg in negative_nodes:
                entity1, verb1, data1 = pos['source'], pos['key'], pos['target']
                entity2, verb2, data2 = neg['source'], neg['key'], neg['target']

                if data1 == 'UNSPECIFIED_DATA' or data2 == 'UNSPECIFIED_DATA':
                    continue
                if data2 == 'personal identifier @children' or '@children' in data2:
                    continue
                if 'personal' in data1 and 'personal' not in data2:
                    continue
                if data1 != data2 and data2 in subordinates[data1]:
                    continue
                if any(d in ANONYMIZED for d in [data1, data2]) and any(d not in ANONYMIZED for d in [data1, data2]):
                    continue
                if any(anony in data1 for anony in ANONYMIZED) and any(anony not in data2 for anony in ANONYMIZED):
                    continue
                if any(anony in data2 for anony in ANONYMIZED) and any(anony not in data1 for anony in ANONYMIZED):
                    continue
                if 'location' in data1 and 'cookie' in data2:
                    continue
                if any(word in [data1, data2] for word in
                       ['time', 'date', 'option', 'setting', 'choice', 'control', 'pixel'
                           , 'encryption', 'encrypt', 'language'
                        ]):
                    continue

                if data1 != data2 and data1 not in subordinates and data2 not in subordinates:
                    continue

                if entity1 == 'we' and entity2 != 'we' and 'we' not in subordinates:
                    continue
                if entity2 == 'we' and entity1 != 'we' and 'we' not in subordinates:
                    continue
                if entity1 != entity2 and entity1 not in subordinates and entity2 not in subordinates:
                    continue

                if USE_POLIGRAPH_CONTRADICTION_RULE:
                    if data1 != data2 and not any(
                            (data1 in subordinates[d] or data1 == d) and (data2 in subordinates[d] or data2 == d) for d
                            in subordinates.keys()):
                        continue

                    if entity1 != entity2 and not any(
                            (entity1 in subordinates[d] or entity1 == d) and (
                                    entity2 in subordinates[d] or entity2 == d) for d in
                            subordinates.keys()):
                        continue

                description = (entity1, data1, entity2, data2, verb1)
                if description in visited:
                    continue

                if word_map[verb1] == verb2 or word_map[verb2] == verb1:
                    cnt += 1
                    visited.add(description)
                    contradictions.append({
                        'id': cnt,
                        'entity1': entity1,
                        'verb1': verb1,
                        'data1': data1,
                        'entity2': entity2,
                        'verb2': verb2,
                        'data2': data2,
                        'context1': pos['text'],
                        'context2': neg['text'],

                    })
        return contradictions

    SEP = ';'

    # with open(output_file, 'w', encoding='utf-8') as out_f:
    #     out_f.write(SEP.join(header) + '\n')

    csv_writer = csv.writer(open(output_file, 'w', encoding='utf-8', newline=''), delimiter=SEP)
    csv_writer.writerow(header)
    csv_writer2 = csv.writer(open(output_file2, 'w', encoding='utf-8', newline=''), delimiter=SEP)
    csv_writer2.writerow(header2)

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file in yamls:
                full_yaml_path = os.path.join(root, file)
                filename = full_yaml_path.split(os.sep)[-2]
                with open(full_yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    nodes = data['links']
                    contradiction_pairs = find_contradiction(nodes)
                    if contradiction_pairs and len(contradiction_pairs) > 0:
                        # with open(output_file, 'a', encoding='utf-8', newline='') as out_f:
                        #     for pair in contradiction_pairs:
                        #         out_f.write(
                        #             f"{pair['id']},{filename},{pair['entity1']},{pair['verb1']},{pair['data1']},"
                        #             f"{pair['context1']},{pair['entity2']},{pair['verb2']},{pair['data2']},"
                        #             f"{pair['context2']}\n")

                        for pair in contradiction_pairs:
                            csv_writer.writerow([
                                pair['id'],
                                filename,
                                pair['entity1'],
                                pair['verb1'],
                                pair['data1'],
                                pair['entity2'],
                                pair['verb2'],
                                pair['data2'],
                            ])

                            csv_writer2.writerow([
                                pair['id'],
                                filename,
                                pair['context1'],
                                pair['context2'],
                            ])

                        print(f"Contradictions found in {filename}: {len(contradiction_pairs)}")
                    else:
                        print(f"No contradictions found in {filename}")

    print(f"Total contradictions found: {cnt}")


def normalize():
    SEP = ';'
    print("normalize:")
    pd1 = pd.read_csv(output_file, sep=SEP)
    pd2 = pd.read_csv(output_file2, sep=SEP)
    pd1.to_csv(output_file, sep=',', index=False)
    pd2.to_csv(output_file2, sep=',', index=False)
    print("normalize done")

    print("dedup:")
    pd2 = pd2.drop_duplicates(subset=['filename', 'context1', 'context2'], keep='first')
    pd2.to_csv(output_file, sep=',')


if __name__ == '__main__':
    output_contradiction()
    normalize()
