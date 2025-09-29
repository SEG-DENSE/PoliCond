from enum import Enum
import os
from logging import Logger

SENTENCE_SPLIT= r"(?<=[.!?;:()…。！？])\s+"
TUPLE_PATTERN = r"\((.*?)[;,](.*?)[;,](.*?)[;,](.*?)\)"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
YOUR_ENTITY_ONTOLOGY_PATH = os.path.join(PROJECT_ROOT,'ontology', 'entity')
YOUR_DATA_ONTOLOGY_PATH = os.path.join(PROJECT_ROOT,'ontology', 'data')
YOUR_COND_ONTOLOGY_PATH = os.path.join(PROJECT_ROOT,'ontology', 'condition')
entity_relation_yml = os.path.join(YOUR_ENTITY_ONTOLOGY_PATH, 'relation.yml')
entity_ontology_path = os.path.join(YOUR_ENTITY_ONTOLOGY_PATH, 'entity_ontology.yml')
data_relation_yml = os.path.join(YOUR_DATA_ONTOLOGY_PATH, 'relation.yml')
data_ontology_path = os.path.join(YOUR_DATA_ONTOLOGY_PATH, 'data_ontology.yml')

condition_relation_yml= os.path.join(YOUR_COND_ONTOLOGY_PATH, 'relation.yml')
condition_dir_path= os.path.join(YOUR_COND_ONTOLOGY_PATH, 'definition')

children_yml = os.path.join(condition_dir_path, 'children.yml')
consent_yml = os.path.join(condition_dir_path, "consent.yml")
input_yml = os.path.join(condition_dir_path, "input.yml")
management_yml = os.path.join(condition_dir_path, "management.yml")
no_cond_yml = os.path.join(condition_dir_path, "no_cond.yml")
region_yml = os.path.join(condition_dir_path, "region.yml")
specific_yml = os.path.join(condition_dir_path, "specific.yml")
thirdp_yml = os.path.join(condition_dir_path, "thirdp.yml")


gpt_key = '<YOUR_GPT_KEY>'
gpt_base = '<YOUR_GPT_BASE>'
gpt_4o_mini = 'gpt-4o-mini-2024-07-18'
gpt_4o = 'gpt-4o-2024-08-06'
gpt_4o_11='gpt-4o-2024-11-20'
gpt_3dot5_turbo = 'gpt-3.5-turbo-0125'
gpt_o1_mini = 'o1-mini-2024-09-12'  # failed
deepseek_model = 'deepseek-chat'
deepseek_model_new = 'deepseek-ai/DeepSeek-V3'
llama33_model = 'meta-llama/Llama-3.3-70B-Instruct'
qwen25 = 'qwen2.5-72b-instruct'
EREIE_free='ERNIE-Speed-8K'


# def get_logger() -> Logger:
#     import logging
#     from logging.handlers import RotatingFileHandler
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024)
#     logger = logging.getLogger(__name__)
#     logger.addHandler(handler)
#     return logger

def get_logger() -> Logger:
    import logging
    from logging.handlers import RotatingFileHandler
    import re
    import os

    class UTF8RotatingFileHandler(RotatingFileHandler):
        def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding='utf-8', delay=False):
            super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)

    class BlindFormatter(logging.Formatter):
        def __init__(self, fmt=None, datefmt=None):
            super().__init__(fmt, datefmt)
            self.blind_mode = os.getenv('BLIND_MODE', 'false').lower() == 'true'

            self.sanitization_rules = {
                '': '[INSTITUTION]',
            }

        def format(self, record):
            msg = super().format(record)

            msg = self._remove_non_utf8_chars(msg)

            if self.blind_mode:
                sorted_rules = sorted(self.sanitization_rules.items(),
                                      key=lambda x: len(x[0]), reverse=True)

                for sensitive_word, replacement in sorted_rules:
                    pattern = re.escape(sensitive_word)
                    msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
            return msg

        def _remove_non_utf8_chars(self, text):
            if not isinstance(text, str):
                return text

            try:
                return text.encode('utf-8', errors='ignore').decode('utf-8')
            except Exception:
                cleaned = ""
                for char in text:
                    try:
                        char.encode('utf-8')
                        cleaned += char
                    except UnicodeEncodeError:
                        cleaned += '?'
                return cleaned

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = BlindFormatter('%(asctime)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = UTF8RotatingFileHandler('app.log', maxBytes=1024 * 1024, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
logger = get_logger()


class InputMode(Enum):
    BATCH = 0
    SINGLE = 1


class ExecutionType(Enum):
    SYNC = 0
    ASYNC = 1