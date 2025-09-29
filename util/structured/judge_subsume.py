import re
from typing import Union

# a set of words related to "subsume"
subsumes = {'comprehension', 'comprisal', 'comprise', 'constitute', 'constitution', 'contain', 'containment', 'cover',
            'coverage', 'embody', 'embodyinclusion', 'embodyment', 'embrace', 'embracement', 'encompass',
            'encompassment', 'enfold', 'enfoldment', 'entail', 'entailment', 'include', 'inclusion', 'incorporate',
            'incorporation', 'involve', 'involvement', 'represent', 'representation', 'subsume', 'subsumption',
            'subsumptive', 'subsumptiveness', 'subsumptivity', 'subsumptor', 'subsumptory','such as',
            'for example', 'like', 'including', 'e.g.', 'i.e.', 'namely', 'specifically', 'in particular',
            'for instance', 'as an illustration', 'to illustrate', 'to demonstrate', 'to clarify', 'to explain',
            }

# whether a word is related to "subsume"
def is_subsume(input: str) -> bool:
    return input.lower() in subsumes

# find all words related to "subsume" in the text
def find_all_subsume(text: str) -> Union[list[str], None]:
    words = re.findall(r'\b\w+\b', text.lower())  
    subsumes_found = [word for word in words if is_subsume(word)] 

    if subsumes_found:
        return subsumes_found  
    return None  


def has_subsume(text: str) -> bool:
    return find_all_subsume(text) is not None

def test1():
    test_texts = [
        "Alice is collecting data from the users, which includes personal information.",
        "The project involves gathering information.",
        "They are accumulating resources for the event.",
        "She is not interested in collecting stamps.",
        "This book is not related to subsume at all.",
        "We gather and accumulate data regularly."
    ]

    for text in test_texts:
        print(f"Text: '{text}'")
        print(f"Has subsume-related word? {has_subsume(text)}")
        print(f"subsume-related words found: {find_all_subsume(text)}\n")

if __name__ == '__main__':
    test1()
