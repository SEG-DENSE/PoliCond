import re
import warnings
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import spacy

warnings.filterwarnings('ignore', message=r'.*The rule-based lemmatizer did not find POS annotation.*')
warnings.filterwarnings('ignore', category=UserWarning, module='spacy')
from spacy import Language
from spacy.tokens.span import Span

from util.structured.judge_compound import split_compound_word, is_compound
from util.structured.judge_email import has_valid_email, find_email
from util.structured.judge_encryption import is_possible_encrypt
from util.structured.judge_proper_noun import find_proper_noun, has_proper_noun
from util.structured.judge_url import find_url, has_url

'''
deprecated code：
# Stem is not suitable for this task
from nltk.stem.snowball import PorterStemmer
stemmer = PorterStemmer()

# No need to use wordnet
# from nltk.corpus import wordnet
# nltk.download('wordnet')

# nltk.stopwords may eliminate negative words, which cannot be accepted
# nltk.download('stopwords')
# stopwords = set(nltk.corpus.stopwords.words('english'))
'''
stopwords = {'.','..','a', 'an', 'the','br', 'd', 's', 'y', 'll', 't', 'o', 'm', 'ma', 've', 're'}
preserve = {
    "we", "us", "our", "no", "not", "nor", "neither", "yes", "yep", "ourselves", "they", "them", "their",
    "theirs", "themselves", "you", "your", "yours", "yourself", "yourselves", "he", "him",
    "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "i", "me",
    "my", "mine", "myself", "this", "that", "these", "those", "what", "which", "who", "whom",
    "whose", "where", "when", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "will", "shall", "can", "could", "may", "might", "must", "would",
    "should", "have", "has", "had", "be", "is", "am", "are", "was", "were", "been", "being"
}

# lemmatizer = WordNetLemmatizer()
SENTENCE_SPLIT= r"(?<=[.!?;:()…。！？])\s+"

# use entityLinker
def initialize_spacy() -> Language:
    """
    load spacy with Entity Linking
    """
    if not Span.has_extension("kb_qid"):
        Span.set_extension("kb_qid", default=None)
    if not Span.has_extension("description"):
        Span.set_extension("description", default=None)
    nlp = spacy.load("en_core_web_lg")
    if 'entity_linker' not in nlp.pipe_names:
        nlp.add_pipe('entityLinker', last=True)
    return nlp

nlp=initialize_spacy()


@lru_cache(maxsize=2000)
def preprocess_string(input_str: str, **kwargs) -> str:
    """
    Preprocess the input string, first recognize the type of the input string
    word, phrase, sentence, or paragraph/long text.txt
    :param input_str: the input string to be preprocessed
    :param kwargs: you can set preserve_case=True to save  the different cases (a/A)
    :return: preprocessed string
    """

    input_str = replace_abbreviations(input_str.strip())
    preserve_case = kwargs.get('preserve_case', False)

    if " " in input_str:
        if re.search(SENTENCE_SPLIT, input_str):
            return preprocess_long_text(input_str,preserve_case)
        else:
            return preprocess_phrase(input_str,preserve_case)
    else:
        if is_compound(input_str):
            return preprocess_compound(input_str,preserve_case)
        else:
            return preprocess_word(input_str,preserve_case)



def parallel_preprocess(strings:list[str], **kwargs) -> list[str]:
    """
    Preprocess a list of strings in parallel
    :param strings:
    :param kwargs:
    :return:
    """
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda s: preprocess_string(s, **kwargs), strings))
    return results

def replace_abbreviations(text: str) -> str:
    abbreviations = {
        '&&': 'and',
        '||': 'or',
        ' & ': ' and ',
        ' | ': ' or ',
        'i.e.': 'that is',
        'e.g.': 'for example',
        'btw': 'by the way',
        'BTW': 'By the way',
        'idk': 'I don’t know',
        'Idk': 'I don’t know',
        'imo': 'in my opinion',
        'Imo': 'in my opinion',
        'lol': 'laugh out loud',
        'LOL': 'laugh out loud',
        'omg': 'oh my god',
        'OMG': 'oh my god',
        'brb': 'be right back',
        'BRB': 'be right back',
        'ttyl': 'talk to you later',
        'TTYL': 'talk to you later',
        'bff': 'best friends forever',
        'asap': 'as soon as possible',
        'fyi': 'for your information',
        'FYI': 'for your information',
        'etc.': 'et cetera',
        'vs.': 'versus',
        'No.': 'Number',
        'nr.': 'Number',
        'Dr.': 'Doctor',
        'Prof.': 'Professor',
        'Mr.': 'Mister',
        'Ms.': 'Miss',
        'Mrs.': 'Missus',
        'Jr.': 'Junior',
        'Sr.': 'Senior',
        "aren't": "are not",
        "won't": "will not",
        "can't": "cannot",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "isn't": "is not",
        "hasn't": "has not",
        "haven't": "have not",
        "hadn't": "had not",
        "wouldn't": "would not",
        "shouldn't": "should not",
        "couldn't": "could not",
        "mightn't": "might not",
        "mustn't": "must not",
        "wasn't": "was not",
        "weren't": "were not",
        "it's": "it is",
        "that's": "that is",
        "there's": "there is",
        "here's": "here is",
        "who's": "who is",
        "what's": "what is",
        "how's": "how is",
        "let's": "let us",
        "i've": "I have",
        "you've": "you have",
        "he's": "he is",
        "she's": "she is",
        "we're": "we are",
        "they're": "they are",
        "i'll": "I will",
        "you'll": "you will",
        "he'll": "he will",
        "she'll": "she will",
        "we'll": "we will",
        "they'll": "they will"
    }
    for abbr, replacement in abbreviations.items():
        text = text.replace(abbr, replacement)
    return text


def split_by_punctuation(text: str):
    return re.split(SENTENCE_SPLIT,text)


def preprocess_compound(input_str:str,preserve_case:bool)->str:
    words = split_compound_word(input_str)
    processed_words = []
    for word in words:
        processed_word = preprocess_word(word,preserve_case)
        processed_words.append(processed_word)
    return " ".join(processed_words)

@lru_cache(maxsize=1000)
def preprocess_word(input_str: str,preserve_case:bool) -> str:
    '''
    process single word
    :param input_str:
    :return:
    '''
    try:
        # 1. save email, url, proper noun, and some special words
        if has_url(input_str):
            return find_url(input_str)
        elif has_valid_email(input_str):
            return find_email(input_str)
        elif has_proper_noun(input_str):
            return find_proper_noun(input_str)
        elif input_str.lower() in preserve:
            return input_str
        elif input_str.lower() in ['cookie', 'cookies']:
            return 'cookies'
        # 2. remove special characters
        cleaned_str = re.sub(r'[^a-zA-Z0-9]', '', input_str)
        if not cleaned_str or len(cleaned_str) < 1:
            return ''

        # 3. lemmatize or stem the word
        # words = nltk.word_tokenize(cleaned_str)
        # lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
        # stemmed_words = [stemmer.stem(word) for word in words]
        words=nlp(cleaned_str)
        words = [token.lemma_ for token in words]

        # 4. transform the word to lower case
        if not preserve_case:
            lowercased_word = [word.lower() for word in words][0]
            return lowercased_word
        else:
            return words[0]
    except Exception as e:
        print(f"Error in preprocess_word: {e}")
        return ''


def preprocess_phrase(input_str: str,preserve_case:bool) -> str:
    words = input_str.split()
    processed = []
    for word in words:
        if has_url(word):
            res=find_url(word)
            processed.append(res)
        elif has_valid_email(word):
            res = find_email(word)
            processed.append(res)
        elif has_proper_noun(word):
            res = find_proper_noun(word)
            processed.append(res)
        elif is_possible_encrypt(word):
            processed.append(word)
        else:
            word = re.sub(r'[^a-zA-Z0-9]', '', word)
            try:
                cleaned = preprocess_word(word,preserve_case)
                if cleaned:
                    processed.append(cleaned)
            except Exception as e:
                continue
    filtered_words = [word for word in processed if word not in stopwords]
    return " ".join(filtered_words)


def preprocess_long_text(input_str: str,preserve_case:bool) -> str:
    sentences = split_by_punctuation(input_str)
    ret = []
    for sentence in sentences:
        if sentence.strip():
            processed = preprocess_phrase(sentence,preserve_case)
            ret.append(processed)
    return ". ".join(ret)


if __name__ == '__main__':
    import random

    # randomly pick 15 words from the list
    all_words = ['Running', 'Beautiful', 'Friend&',
                 'Laughing', 'Happy', 'Amazing',
                 'Interesting', 'Studying', 'Reading', 'Writing',
                 'this ; is a random # sentence',
                 "Hello? Good Morning! How are you? I'm fine, thank @ you.",
                 'Creative', 'Joyful', 'Explorer',
                 'Dancing', 'Sunny', 'Incredible',
                 'Curious', 'Learning', 'Thinking', 'Dreaming',
                 'What a lovely day!',
                 "Welcome to the jungle! Enjoy your stay.",
                 "Let's make today amazing! #Motivation",
                 'Adventure awaits: Are you ready?',
                 'Coding is fun; let’s build something great!',
                 'Nature is beautiful & full of surprises.',
                 'Coffee? Yes, please! ☕️',
                 'What do you think about this idea?',
                 ]
    random_words = random.sample(all_words, 15)
    for word in random_words:
        output = preprocess_string(word)
        print(word, "->", output)
