import re

def is_compound(word: str) -> bool:
    '''
    judge if a word is a compound word
    '''
    if not( isinstance(word, str) and '\n' not in word and ' ' not in word):
        return is_camel_case(word) or \
            is_pascal_case(word) or \
            has_mixed_case(word) or \
            is_snake_case(word) or \
            is_kebab_case(word)
    return False


def split_compound_word(word: str) -> []:
    """
    Splits a compound word into its constituent parts based on its case.
    Recognizes camel case, pascal case, snake case, kebab case, and mixed case with hyphens.
    If the word is not a recognized compound word, returns it as a single-element list.
    """
    if is_camel_case(word):
        return split_camel_case(word)
    elif is_pascal_case(word):
        return split_pascal_case(word)
    elif is_snake_case(word):
        return split_snake_case(word)
    elif is_kebab_case(word):
        return split_kebab_case(word)
    elif has_mixed_case(word):
        return split_mixed_case_with_hyphen(word)
    else:
        return [word]


def is_camel_case(word: str) -> bool:
    """
    Checks if a given word is in camel case.
    Camel case is characterized by starting with a lowercase letter and having subsequent words start with an uppercase letter.
    For example, "camelCaseWord".
    """
    return bool(re.match(r'^[a-z]+([A-Z][a-z]+)+$', word))


def is_pascal_case(word: str) -> bool:
    """
    Checks if a given word is in pascal case.
    Pascal case is similar to camel case but starts with an uppercase letter.
    For example, "PascalCaseWord".
    """
    return bool(re.match(r'^[A-Z][a-z]+([A-Z][a-z]+)+$', word))


def is_snake_case(word: str) -> bool:
    """
    Checks if a given word is in snake case.
    Snake case consists of lowercase letters and underscores separating words.
    For example, "snake_case_word".
    """
    return bool(re.match(r'^[a-z0-9]+(_[a-z0-9]+)+$', word))


def is_kebab_case(word: str) -> bool:
    """
    Checks if a given word is in kebab case.
    Kebab case consists of lowercase letters and hyphens separating words.
    For example, "kebab-case-word".
    """
    return bool(re.match(r'^[a-z0-9]+(-[a-z0-9]+)+$', word))


def has_mixed_case(word: str) -> bool:
    """
    Checks if a given word has mixed case and contains hyphens/underscores.
    For example, "mixed-Case-word".
    """
    return bool(re.match(r'^[a-zA-Z0-9]+([-_][a-zA-Z0-9]+)+$', word))


def split_camel_case(word: str):
    """
    Splits a camel case word into its constituent parts.
    For example, "camelCaseWord" becomes ["camel", "Case", "Word"].
    """
    parts = []
    current_part = ''
    for char in word:
        if char.isupper() and current_part:
            parts.append(current_part)
            current_part = char
        else:
            current_part += char
    if current_part:
        parts.append(current_part)
    return parts


def split_pascal_case(word: str):
    """
    Splits a pascal case word into its constituent parts.
    """
    parts = []
    current_part = ''
    first=True
    for char in word:
        if first:
            current_part+=char
            first=False
        elif char.isupper() and current_part:
            parts.append(current_part)
            current_part = char
        else:
            current_part += char
    if current_part:
        parts.append(current_part)
    return parts


def split_snake_case(word: str):
    """
    Splits a snake case word into its constituent parts.
    For example, "snake_case_word" becomes ["snake", "case", "word"].
    """
    return word.split('_')


def split_kebab_case(word: str):
    """
    Splits a kebab case word into its constituent parts.
    For example, "kebab-case-word" becomes ["kebab", "case", "word"].
    """
    return word.split('-')


def split_mixed_case_with_hyphen(word: str):
    """
    Splits a word with mixed case and hyphens into its constituent parts.
    For example, "mixed-Case-word" becomes ["mixed", "Case", "word"].
    """
    return re.split(r'[-_]', word)
