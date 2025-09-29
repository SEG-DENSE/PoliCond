import json
import os
import re
from datetime import datetime

import openai
from bs4 import BeautifulSoup
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Callable
from spacy import Language
from pipeline.abstract_pipeline import AbstractPipeline
from config import *
from ontology.condition.condition import Condition
from ontology.condition.handler import ConditionHandler
from ontology.data.Data import Data
from ontology.data.handler import DataHandler
from ontology.entity.Entity import Entity
from ontology.entity.handler import EntityHandler
from util.string.preprocess import preprocess_string
from util.structured.judge_collection import has_collection
from pipeline.prompt_template import (
    prompt_template,
    build_query_template,
    build_query_template_no_candidate_ablation,
)

# Initialize OpenAI client
# chat_model = OpenAI(api_key=gpt_key, base_url=gpt_base)


def search_before(sentence_id: int, sentences: list[str], max_before: int = 3) -> str:
    """Retrieve the context before a given sentence."""
    start_idx = max(0, sentence_id - max_before)
    return "\n".join(sentences[start_idx : sentence_id + 1])


def validate(completion: ChatCompletion, messages: list[dict]) -> str:
    """Validate the OpenAI completion response."""
    if completion.choices[0].message.content:
        log_prompt_info(completion, messages, success=True)
        return completion.json()
    else:
        log_prompt_info(completion, messages, success=False)
        raise ValueError("Chat completion failed")


def log_prompt_info(completion: ChatCompletion, messages: list[dict], success: bool):
    """Log details of the OpenAI prompt and response."""
    token_usage = completion.usage.total_tokens
    total_msg_length = sum(len(msg["content"]) for msg in messages if "content" in msg)
    logger.info(
        f"Id: {completion.id}, Model: {completion.model}, Message Length: {total_msg_length}, Tokens used: {token_usage}"
    )
    now_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now_datetime_str} - Id: {completion.id}, Model: {completion.model}, Message Length: {total_msg_length}, Tokens used: {token_usage}")

def generate_and_save_prompt(
    candidate_entities: set[str],
    candidate_data: set[Data],
    candidate_conditions: set[Condition],
    sentence: str,
    context: str,
    model_id: str,
    output_dir: str,
    chat_model: OpenAI = OpenAI(api_key=gpt_key, base_url=gpt_base)
):
    """Generate a prompt and save the results to JSONL files."""
    record_path = os.path.join(output_dir, "record.jsonl")
    analysis_path = os.path.join(output_dir, "analysis.jsonl")
    os.makedirs(output_dir, exist_ok=True)

    prompt = [
        {"role": "system", "content": prompt_template()},
        {
            "role": "user",
            "content": build_query_template(
                candidate_entities, candidate_data, candidate_conditions, context
            ),
        },
        # 'content': build_query_template_no_candidate_ablation(context)}
    ]
    result = chat_model.chat.completions.create(
        model=model_id, messages=prompt, n=1, temperature=0.2, max_tokens=512
    )
    res_json = validate(result, prompt)
    # write to jsonl file PATH

    # Save the raw response to a record file
    with open(record_path, "a", encoding="utf-8") as f:
        f.write(res_json + "\n")

    # Save the analyzed response to our analysis file waiting to be processed
    json_obj = json.loads(res_json)
    analysis_obj = {
        "sentence": sentence,
        "context": context,
        "candidate_entities": [e for e in candidate_entities],
        "candidate_data": [d.value for d in candidate_data],
        "candidate_conditions": [c.value for c in candidate_conditions],
        "model_id": model_id,
        "response": json_obj["choices"][0]["message"]["content"],
    }
    with open(analysis_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(analysis_obj) + "\n")


class PromptPipeline(AbstractPipeline):
    def __init__(
        self,
        policy_dir: str,
        save_dir: str,
        model: str,
        mode: InputMode = InputMode.SINGLE,
        api_key: str = gpt_key,
        api_base_url: str = gpt_base,
        **kwargs,
    ):
        super().__init__(policy_dir, save_dir, model)
        EntityHandler.preload(entity_ontology_path, entity_relation_yml)
        DataHandler.preload(data_ontology_path, data_relation_yml)
        ConditionHandler.preload(condition_dir_path, condition_relation_yml)
        self.mode: InputMode = mode
        self.use_string_preprocess_pipeline: bool = kwargs.get(
            "use_string_preprocess_pipeline", False
        )
        self.use_nlp_for_candidate_entity: bool = kwargs.get(
            "use_nlp_for_candidate_entity", False
        )
        self.chat_model=OpenAI(api_key=api_key, base_url=api_base_url)

    def load_data(self, policy_full_path: str) -> list[str]:
        """
        Load and preprocess data from a policy file.
        Performs sentence splitting first, then lemmatization on each sentence.
        Args:
            policy_full_path (str): Path to the policy file.
        Returns:
            list[str]: A list of preprocessed and lemmatized sentences.
        """
        with open(policy_full_path, "r", encoding="utf-8") as f:
            content = f.read()
            if (
                "svg" in content
                or "DOCTYPE" in content
                or policy_full_path.endswith("html")
            ):
                try:
                    soup = BeautifulSoup(content, "html.parser")
                    content = soup.get_text()
                except:
                    pass

            # Step 1: Use spaCy to split content into sentences
            doc = self.nlp(content)
            sentences = [sent.text for sent in doc.sents]

            processed_sentences = []
            # Step 2: Perform lemmatization on each sentence or use string preprocess pipeline
            # more strict preprocess
            if self.use_string_preprocess_pipeline:
                for sent in sentences:
                    sent = re.sub(r"\s+", " ", sent).strip()
                    processed = preprocess_string(sent)
                    processed_sentences.append(processed)
            # just do lemmatization
            else:
                for sent in sentences:
                    sent = re.sub(r"\s+", " ", sent).strip()
                    sent_doc = self.nlp(sent)
                    lemmatized_sentence = " ".join(token.lemma_ for token in sent_doc)
                    processed_sentences.append(lemmatized_sentence)

            return processed_sentences

    def process_single(self, policy_full_path: str, model_id: str) -> None:
        """Process a single policy file."""
        logger.info(f"start processing {policy_full_path}") # double-blind requirements
        name_piece = os.path.basename(os.path.dirname(policy_full_path))

        assert self.mode in ["batch", "single", InputMode.SINGLE, InputMode.BATCH]
        if self.mode == InputMode.BATCH:
            output_dir = os.path.dirname(policy_full_path) if not self.save_dir else os.path.join(self.save_dir, name_piece)
        elif self.mode == InputMode.SINGLE:
            output_dir = os.path.dirname(policy_full_path) if not self.save_dir else self.save_dir
        else:
            exit(0)

        sentences = self.load_data(policy_full_path)
        for idx, sentence in enumerate(sentences):
            if has_collection(sentence):
                context = search_before(idx, sentences, max_before=3)
                candidate_entity: set[str]
                candidate_data: set[Data]
                candidate_conditions: set[Condition]
                if self.use_nlp_for_candidate_entity:
                    candidate_entity, candidate_data, candidate_condition = (
                        self.extract_candidates(context, sentence, self.nlp)
                    )
                else:
                    candidate_entity, candidate_data, candidate_condition = (
                        self.extract_candidates(context, sentence, nlp=None)
                    )
                if candidate_data:
                    generate_and_save_prompt(
                        candidate_entity,
                        candidate_data,
                        candidate_condition,
                        sentence,
                        context,
                        model_id,
                        output_dir,
                        self.chat_model if self.chat_model else OpenAI(api_key=gpt_key, base_url=gpt_base)
                    )

    def extract_candidates(
        self, context: str, sentence: str, nlp: Language = None
    ) -> ():
        """Extract candidate entities, data from a sentence and conditions from its context."""
        candidate_conditions = ConditionHandler.recognize_as_lower_Condition(sentence)
        if not candidate_conditions:
            candidate_conditions = ConditionHandler.recognize_as_lower_Condition(
                context
            )
            if not candidate_conditions:
                candidate_conditions = {Condition.NO_COND}

        # if use nlp, we can get more entities
        candidate_entity: set[Entity] = EntityHandler.recognize_as_Entity(sentence)
        candidate_entity: set[str] = {e.value for e in candidate_entity}
        if nlp:
            sent = nlp(sentence)
            try:
                nlp_recognized: list[str] = [
                    ent.text for ent in sent.ents if ent.label_ in ["ORG", "GPE", "LOC"]
                ]
                if nlp_recognized:
                    candidate_entity.update(nlp_recognized)
            except Exception as e:
                logger.error(
                    f"Error processing {sentence} with spaCy: {e}", exc_info=True
                )
                pass

        candidate_data = DataHandler.recognize_as_Data(sentence)
        return candidate_entity, candidate_data, candidate_conditions

    def process_batch(self, paths: list, filter: Callable = None):
        """Process multiple policy files."""
        for policy_full_path in paths:
            name_piece = os.path.basename(os.path.dirname(policy_full_path))
            if filter and filter(name_piece):
                logger.info(f"Skipping {name_piece}")
                continue

            try:
                self.process_single(policy_full_path, self.model)
            except openai.APIConnectionError as apiError:
                logger.error("API connection error occurred. Please check your api_key, api_host, and network.", exc_info=True)
                logger.error(apiError)
            except Exception as e:
                logger.error(f"Error processing {policy_full_path}: {e}", exc_info=True)
