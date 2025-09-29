import yaml

from analyzer.post_analysis import (
    load_yaml_content,
    add_missing_tuples_from_candidates,
    process_post_analysis_results,
)
from config import *

POST_PREFIX = "post_"
# WE_PRONOUNS = ['we', 'our', 'us', 'ourselves', 'ours', 'myself', 'my']
# third_party_alias = [entity.value for entity in Entity if entity != Entity.UNSPECIFIED and entity != Entity.WE]


def process_single_yaml(filepath: str):
    """
    Process a single YAML file to resolve unspecified entities and add missing tuples from candidates.
    :param filepath:
    :return:
    """
    post_yaml = os.path.join(
        os.path.dirname(filepath), POST_PREFIX + os.path.basename(filepath)
    )
    content = load_yaml_content(filepath)
    # Resolve unspecified entities
    new_nodes_from_unspecified_entity: dict = process_post_analysis_results(content)
    # Add missing tuples
    new_nodes_from_candidate_combination: list[dict] = (
        add_missing_tuples_from_candidates(content)
    )
    with open(post_yaml, "w", encoding="utf-8") as f:
        yaml.dump(content, f, allow_unicode=True, default_flow_style=False, width=1024)
    print(
        f"{filepath} resolved Unspecified nodes: {len(new_nodes_from_unspecified_entity)} unspecified_entity nodes"
    )
    print(
        f"{filepath} infer nodes: {len(new_nodes_from_candidate_combination)} complementary nodes"
    )


def process_directory(directory_path: str):
    """
    Process all YAML files in the given directory, resolving unspecified entities and
    adding missing tuples from candidates.
    Like:
    BaseDir
    |-- 01_App1
    |-- |-- app1.yaml
    |-- |-- app1.html
    |-- 02_App2
    |-- |-- app2.yaml
    |-- |-- app2.html
    The method take the [path to BaseDir] as input, and process all the yaml files in the subdirectories.
    Args:
        directory_path (str): Path to the directory containing YAML files to process
    """
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".yaml"):
                fullpath = os.path.join(root, file)
                process_single_yaml(fullpath)


def example_usage():
    path = os.path.join(PROJECT_ROOT, r"test\Bluesky\Bluesky.yaml")
    if os.path.exists(path):
        print(f"Processing {path}")
    else:
        print(f"{path} does not exist")
        return
    process_single_yaml(path)


def example_usage_batch():
    DIR = r"PATH_TO_POLICIES\datasets\policies"
    process_directory(DIR)


if __name__ == "__main__":
    example_usage()
