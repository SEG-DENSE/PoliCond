import argparse
import os
import time
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
    :param filepath: Path to the input YAML file
    :return: tuple (num_unspecified_resolved, num_tuples_inferred)
    """
    if not os.path.isfile(filepath):
        logger.warning(f"File not found: {filepath}")
        return 0, 0

    post_yaml = os.path.join(
        os.path.dirname(filepath), POST_PREFIX + os.path.basename(filepath)
    )

    try:
        content = load_yaml_content(filepath)
    except Exception as e:
        logger.error(f"Failed to load YAML {filepath}: {e}")
        return 0, 0

    # Resolve unspecified entities
    new_nodes_from_unspecified_entity = process_post_analysis_results(content)
    num_unspecified = len(new_nodes_from_unspecified_entity)

    # Add missing tuples from candidates
    new_nodes_from_candidate_combination = add_missing_tuples_from_candidates(content)
    num_tuples_inferred = len(new_nodes_from_candidate_combination)

    try:
        with open(post_yaml, "w", encoding="utf-8") as f:
            yaml.dump(content, f, allow_unicode=True, default_flow_style=False, width=1024)
    except Exception as e:
        logger.error(f"Failed to write post-processed YAML {post_yaml}: {e}")
        return num_unspecified, num_tuples_inferred

    logger.info(
        f"Processed {filepath} → {post_yaml} | "
        f"Unspecified resolved: {num_unspecified}, Candidates added: {num_tuples_inferred}"
    )
    return num_unspecified, num_tuples_inferred


def process_directory(directory_path: str):
    """
    Process all YAML files in the given directory, resolving unspecified entities and
    inferring tuples from candidates and other existing tuples.
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
    if not os.path.isdir(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return

    yaml_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".yaml") and not file.startswith(POST_PREFIX):
                yaml_files.append(os.path.join(root, file))

    if not yaml_files:
        logger.warning(f"No YAML files found in {directory_path}")
        return

    logger.info(f"Found {len(yaml_files)} YAML files to process in {directory_path}")

    total_unspecified = 0
    total_candidates = 0
    success_count = 0

    for filepath in yaml_files:
        try:
            u, c = process_single_yaml(filepath)
            total_unspecified += u
            total_candidates += c
            success_count += 1
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    logger.info(
        f"Batch processing complete. "
        f"Files processed: {success_count}/{len(yaml_files)}, "
        f"Total unspecified resolved: {total_unspecified}, "
        f"Total tuples inferred/added: {total_candidates}"
    )


# parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="Post-process YAML analysis files to resolve unspecified entities and add missing tuples.",
        epilog="Examples:\n"
               "  python post_launcher.py --single --input ./test/Bluesky.yaml\n"
               "  python post_launcher.py --batch --input ./datasets/policies"
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--single', action='store_true', help='Process a single YAML file')
    mode_group.add_argument('--batch', action='store_true', help='Process all YAML files in a directory recursively')

    parser.add_argument(
        '--input',
        required=True,
        help='Input YAML file path (for --single) or directory path (for --batch)'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    start_time = time.time()

    if args.single:
        if not os.path.isfile(args.input):
            logger.error(f"Input file does not exist: {args.input}")
            return
        logger.info(f"Running in SINGLE mode on file: {args.input}")
        process_single_yaml(args.input)

    elif args.batch:
        if not os.path.isdir(args.input):
            logger.error(f"Input directory does not exist: {args.input}")
            return
        logger.info(f"Running in BATCH mode on directory: {args.input}")
        process_directory(args.input)

    else:
        logger.error("Invalid mode specified.")
        return

    elapsed = time.time() - start_time
    logger.info(f"Total running time: {elapsed:.2f} seconds.")



# if no args, run example usage, which is an easy way to test the pipeline from IDEs.
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
    # If called with no args, run example
    import sys
    if len(sys.argv) == 1:
        example_usage()
    else:
        main()
