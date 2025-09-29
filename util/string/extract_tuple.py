import json
import re

from node import CollectionNode
from util.translate import translate_word_poli2my


def search_tuple(content: str, chunk_id: int = -1, context_id: int = -1) -> list[dict]:
    tuple_ptn = r"\((.*?)[;,](.*?)[;,](.*?)[;,](.*?)\)"
    ret = []
    try:
        try:
            processed = json.loads(content)['choices'][0]['message']['content']
        except Exception:
            processed = content
        # using re.split and finditer to avoid using re.findall and triggering the memory limit
        # matcher = re.findall(tuple_ptn, content)
        if re.split(";|,", processed).count('') > 20:
            return ret

        matcher = re.findall(tuple_ptn, processed)

        if matcher and len(matcher) > 0:
            for tuple in matcher:
                try:
                    tuple = list(map(str.strip, tuple))
                    entity, verb, data, cond = tuple[0].strip(), tuple[1], tuple[2], tuple[3]
                    data = translate_word_poli2my(str(data))
                    if verb not in ['collect', 'not collect']:
                        if "no" in str(verb) or "not" in str(verb):
                            verb = 'not collect'
                        else:
                            verb = 'collect'
                    ret.append({
                        "entity": entity,
                        "verb": verb,
                        "data": data,
                        "condition": cond,
                        "chunk_id": chunk_id,
                        "context_id": context_id,
                    })
                except Exception as e:
                    continue
    except Exception as e:
        print(f"Exception in strategy.py when search tuple: {e}")
    return ret


def extract(path: str) -> list[dict]:
    results = []
    try:
        if path.endswith(".jsonl"):
            with open(path, mode='r', encoding='utf-8', errors='ignore') as f:
                try:
                    content = f.read()
                    lines = [line for line in content.split('\n') if line and len(line) > 0 and line != '\n']
                    for i, row in enumerate(lines):
                        try:
                            if 'not a collection' in row:
                                continue

                            if not row.startswith("{") or not row.endswith("}"):
                                pattern = r"\{.*\}"
                                row = re.search(pattern, row)
                                if row:
                                    row = row.group()
                                else:
                                    continue

                            row = json.loads(row)
                            chunk_id = int(row['chunk_id']) if 'chunk_id' in row else -1
                            context_id = int(row['context_id']) if 'context_id' in row else -1
                            parsed_result = row['parsed_result'] if 'parsed_result' in row else ""

                            ls = search_tuple(parsed_result, chunk_id, context_id)
                            if ls and len(ls) > 0:
                                results.extend(ls)
                        except Exception as e:
                            print(f"Exception when extracting: {e}, process:{i + 1}/{len(lines)}, line: {row}\n")
                            continue
                except Exception:
                    print(f"Error: The file {path} is empty.")
    except FileNotFoundError:
        print(f"Error: The file {path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return results


if __name__ == '__main__':
    path = r'.\test\919_uh.edu_results.jsonl'
    res = extract(path)
    func = lambda x: CollectionNode(x['entity'], x['verb'], x['data'], x['condition'],
                                    text=f"chunk_id={x['chunk_id']}, context={x['context_id']}")
    to_print = []
    for r in res:
        to_print.append(func(r).pretty_print())

    to_print = sorted(to_print)
    for t in to_print:
        print(t)
