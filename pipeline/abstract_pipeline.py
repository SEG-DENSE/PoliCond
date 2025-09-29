# base_pipeline.py

import os
import spacy
import warnings
warnings.filterwarnings('ignore', message=r'.*The rule-based lemmatizer did not find POS annotation.*')
warnings.filterwarnings('ignore', category=UserWarning, module='spacy')
from enum import Enum
from spacy.language import Language


class RUN_MODE(Enum):
    DEFAULT = 0
    PROMPT_ONLY = 1
    ANALYZE_ONLY = 2


class AbstractPipeline:
    def __init__(self, policy_dir: str,  save_dir: str, model: str):
        self.policy_dir: str = policy_dir
        self.save_dir: str = save_dir
        self.model: str = model
        self.nlp = self.initialize_spacy()
        spacy.prefer_gpu()

    def initialize_spacy(self) -> Language:
        """
        load spacy model
        """
        nlp = spacy.load("en_core_web_lg", disable=["ner", "tagger"])
        return nlp

