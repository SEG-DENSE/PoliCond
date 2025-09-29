import argparse
import os

from analyzer.analyzer import process_single_file,process_batch


def example_usage_single():
    jsonl_path = r'PATH_TO_TEST\test\test\analysis.jsonl'
    yaml_path = r'PATH_TO_TEST\test\test\analysis.yaml'
    policy_path = r'PATH_TO_TEST\test\test.html'
    process_single_file(jsonl_path, yaml_path, policy_path)


def example_usage_batch():
    """Example usage for batch processing"""
    jsonl_dir = r'PATH_TO_DATASET\datasets\policies'
    yaml_dir = jsonl_dir
    policy_dir = jsonl_dir
    process_batch(jsonl_dir, yaml_dir, policy_dir,
                  filter_func=lambda x: x.endswith('.jsonl') and 'analysis' in x)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process JSONL files and generate YAML reports.",
        epilog="Examples:\n"
               "  python analyzer.py --single --jsonl path/to/file.jsonl --output path/to/output.yaml --policy path/to/content.html\n"
               "  python analyzer.py --batch --jsonl path/to/jsonl_dir --output path/to/yaml_dir --policy path/to/content_dir"
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--single', action='store_true', help='Process a single file')
    mode_group.add_argument('--batch', action='store_true', help='Process multiple files in batch mode')

    # Core arguments
    parser.add_argument('--jsonl', required=True, help='Path to the input JSONL file or directory')
    parser.add_argument('--output', required=True, help='Path to the output YAML file or directory')
    parser.add_argument('--policy', required=True, help='Path to the policy file or directory')
    parser.add_argument('--name',  help='Policy name for the report')

    return parser.parse_args()


def run_from_args():
    args = parse_args()
    jsonl_path, yaml_path, policy_content_path = args.jsonl, args.output, args.policy
    if not os.path.exists(jsonl_path):
        print(f"Error: The specified JSONL path '{jsonl_path}' does not exist.")
        return
    if not os.path.exists(policy_content_path):
        print(f"Error: The specified policy path '{policy_content_path}' does not exist.")
        return
    if args.single:
        # Validate that all paths are files for single mode
        if not all([os.path.isfile(args.jsonl), os.path.isfile(args.output) or args.output.endswith('.yaml'),
                    os.path.isfile(args.policy)]):
            print("Error: For single mode, --jsonl, --output, and --policy should be files")
            return
        name = args.name if args.name else os.path.basename(args.jsonl)[:-len('.jsonl')]
        process_single_file(args.jsonl, args.output, args.policy, name)
    elif args.batch:
        # Check if paths are directories or files to determine actual mode
        jsonl_is_dir = os.path.isdir(args.jsonl)
        output_is_dir = os.path.isdir(args.output)
        policy_is_dir = os.path.isdir(args.policy)
        # Validate that all paths are directories for batch mode
        if not all([jsonl_is_dir, output_is_dir, policy_is_dir]):
            print("Error: For batch mode, --jsonl, --output, and --policy should be directories")
            return

        process_batch(args.jsonl, args.output, args.policy,
                      filter_func=lambda x: x.endswith('.jsonl') and 'analysis' in x)
    else:
        print("Error: You must specify either --single or --batch mode")
        return


if __name__ == '__main__':
    # If no command line arguments provided, run example usage
    example_usage_batch()
