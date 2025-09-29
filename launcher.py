import argparse
import asyncio
import time

from config import *
from pipeline.async_prompt_pipeline import AsyncPromptPipeline
from pipeline.prompt_pipeline import PromptPipeline


async def main_async(
        mode: InputMode,
        model_id: str,
        policy_dir: str = None,
        file_path: str = None,
        filter_function=None,
        save_dir: str = None,
        api_key: str = None,
        api_base_url: str = None
):
    """
    Main function to execute the pipeline in batch or single mode asynchronously.

    Args:
        mode (str): Processing mode, either 'batch' or 'single'.
        model_id (str): The model ID to use for processing.
        policy_dir (str, optional): Directory containing policy files. Required for batch mode.
        file_path (str, optional): Path to a single policy file. Required for single mode.
        filter_function (callable, optional): Function to filter files in batch mode.
        save_dir: The path to save the LLM's outputs.
    """
    if mode not in {InputMode.BATCH, InputMode.SINGLE,'single','batch'}:
        raise ValueError("Mode must be either 'batch' (InputMode.BATCH) or 'single'(InputMode.SINGLE) .")
    if mode=='single': mode= InputMode.SINGLE
    elif mode=='batch': mode=InputMode.BATCH

    if mode == InputMode.BATCH:
        if not policy_dir:
            raise ValueError("policy_dir must be provided for batch mode.")
        if not filter_function:
            filter_function = lambda x: x.endswith(
                ".html"
            )  # Default filter for HTML files

        paths = [
            os.path.join(root, file)
            for root, _, files in os.walk(policy_dir)
            for file in files
            if filter_function(os.path.join(root, file))
        ]

    else:  # Single mode
        if not file_path:
            raise ValueError("file_path must be provided for single mode.")
        paths = [file_path]

    pipeline = AsyncPromptPipeline(
        policy_dir=policy_dir,
        save_dir=save_dir,
        model=model_id,
        mode=mode,
        api_key=api_key,
        api_base_url=api_base_url,
    )

    start_time = time.time()
    await pipeline.process_batch_async(paths)
    running_time = time.time() - start_time

    logger.info(f"Overall running time: {running_time:.2f} seconds.")


def main(
        mode: InputMode,
        model_id: str,
        policy_dir: str = None,
        file_path: str = None,
        filter_function=None,
        save_dir: str = None,
        api_key: str = None,
        api_base_url: str = None
):
    """
    Main function to execute the pipeline in batch or single mode.

    Args:
        mode (str): Processing mode, either 'batch' or 'single'.
        policy_dir (str, optional): Directory containing policy files. Required for batch mode.
        file_path (str, optional): Path to a single policy file. Required for single mode.
        filter_function (callable, optional): Function to filter files in batch mode.
        save_dir: The path to save the LLM's outputs.
    """
    if mode not in {InputMode.BATCH, InputMode.SINGLE}:
        raise ValueError("Mode must be either 'batch' (InputMode.BATCH) or 'single'(InputMode.SINGLE) .")

    if mode == InputMode.BATCH:
        if not policy_dir:
            raise ValueError("policy_dir must be provided for batch mode.")
        if not filter_function:
            filter_function = lambda x: x.endswith(
                ".html"
            )  # Default filter for HTML files

        # Collect all files matching the filter
        paths = [
            os.path.join(root, file)
            for root, _, files in os.walk(policy_dir)
            for file in files
            if filter_function(os.path.join(root, file))
        ]
        save_dir = policy_dir if not save_dir else save_dir

    else:  # Single mode
        if not file_path:
            raise ValueError("file_path must be provided for single mode.")
        paths = [file_path]
        save_dir = os.path.dirname(file_path) if not save_dir else save_dir

    # Initialize pipeline
    pipeline = PromptPipeline(
        policy_dir=policy_dir,
        save_dir=save_dir,
        model=model_id,
        mode=mode,
        api_key=api_key,
        api_base_url=api_base_url,
    )

    # Run pipeline
    start_time = time.time()
    pipeline.process_batch(paths)
    running_time = time.time() - start_time

    logger.info(f"Overall running time: {running_time:.2f} seconds.")


def run_batch(
        model_id: str,
        policy_dir: str,
        filter_function=None,
        exec_type: ExecutionType = ExecutionType.ASYNC,
        api_key=gpt_key,
        api_base_url=gpt_base
):
    if exec_type == ExecutionType.ASYNC:
        asyncio.run(
            main_async(InputMode.BATCH, model_id, policy_dir, filter_function, api_key=api_key, api_base_url=api_base_url )
        )
    else:
        main(InputMode.BATCH, model_id, policy_dir, filter_function, )


def run_single(
        model_id: str, file_path: str, exec_type: ExecutionType = ExecutionType.ASYNC
):
    if exec_type == ExecutionType.ASYNC:
        asyncio.run(
            main_async(mode=InputMode.SINGLE, model_id=model_id, file_path=file_path)
        )
    else:
        main(mode=InputMode.SINGLE, model_id=model_id, file_path=file_path)


def example_usage_batch():
    # Example usage
    run_batch(
        model_id=deepseek_model,
        policy_dir=r"PATH_TO_DATASET\datasets\policies",
        #filter_function=lambda x: x.endswith(".html") and "cleaned" in x,
        filter_function=lambda x: x.endswith(".html"),
        exec_type=ExecutionType.ASYNC,
        api_key=gpt_key,
        api_base_url=gpt_base
    )


def example_usage_single():
    # Example usage
    run_single(
        model_id=deepseek_model,
        file_path=r".\datasets\apps\htmls\138_AI Chat・Ask Chatbot Assistant\cleaned.html",
        exec_type=ExecutionType.ASYNC,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Privacy Policy Analysis Tool",
        epilog="Examples:\n"
               "  python launcher.py file1.txt file2.txt --key [key] --url [url] --model[model name]; \t\t"
               "  python launcher.py ./policies/ --model [model-str] --sync --save-dir [path_to_save_dir]; \t\t"
    )

    parser.add_argument(
        "inputs",
        nargs="*",
        help="Input file(s) or directory path(s)"
    )
    parser.add_argument(
        "--key",
        default=None,
        help="API key for the model provider (default: None)"
    )

    parser.add_argument(
        "--url",
        default=None,
        help="Base URL for the model provider (default: None)"
    )

    parser.add_argument(
        "--model",
        default=deepseek_model,
        help="Model to use for processing (default: %(default)s)"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        default=False,
        help="Run in synchronous mode (default: asynchronous)"
    )
    parser.add_argument(
        "--save-dir",
        help="Directory to save results (default: same as input directory)"
    )

    return parser.parse_args()


def determine_input_mode(inputs):
    """Determine input mode based on provided paths"""
    if len(inputs) == 1:
        path = inputs[0]
        if os.path.isfile(path):
            # Check if it's a supported file type
            _, ext = os.path.splitext(path.lower())
            if ext in ['.htm', '.html', '.txt', '.md']:
                return InputMode.SINGLE
        # If it's not a supported single file, or it's a directory, it's batch
        return InputMode.BATCH
    elif len(inputs) > 1:
        # Multiple paths mean batch mode
        return InputMode.BATCH
    else:
        # No inputs provided
        return None


def run_from_args():
    args = parse_args()

    # Determine execution type
    exec_type = ExecutionType.SYNC if args.sync else ExecutionType.ASYNC

    # Determine input mode
    input_mode = determine_input_mode(args.inputs)

    if input_mode is None:
        # Run example usage if no inputs provided
        print("Please provide at least one valid input file or directory.")
        return
    api_key = args.key if hasattr(args, 'key') else gpt_key
    api_base_url = args.url if hasattr(args, 'url') else gpt_base
    if input_mode == InputMode.SINGLE:
        file_path = args.inputs[0]
        save_dir = args.save_dir if args.save_dir else None

        # Create pipeline with single file settings
        if exec_type == ExecutionType.ASYNC:
            asyncio.run(
                main_async(
                    mode=InputMode.SINGLE,
                    model_id=args.model,
                    file_path=file_path,
                    save_dir=save_dir,
                    api_key=api_key,
                    api_base_url=api_base_url
                )
            )
        else:
            main(
                mode=InputMode.SINGLE,
                model_id=args.model,
                file_path=file_path,
                save_dir=save_dir,
                api_key=api_key,
                api_base_url=api_base_url
            )
    else:  # BATCH mode
        # For batch mode, we treat all inputs as directories or files to include
        save_dir = args.save_dir if args.save_dir else None

        # We'll use the first directory as the policy_dir for filtering
        policy_dir = None
        for path in args.inputs:
            if os.path.isdir(path):
                policy_dir = path
                break

        if policy_dir is None and args.inputs:
            policy_dir = os.path.dirname(args.inputs[0])

        if exec_type == ExecutionType.ASYNC:
            asyncio.run(
                main_async(
                    mode=InputMode.BATCH,
                    model_id=args.model,
                    policy_dir=policy_dir,
                    save_dir=save_dir,
                    api_key=api_key,
                    api_base_url=api_base_url
                )
            )
        else:
            main(
                mode=InputMode.BATCH,
                model_id=args.model,
                policy_dir=policy_dir,
                save_dir=save_dir,
                api_key=api_key,
                api_base_url=api_base_url
            )


if __name__ == "__main__":
    example_usage_batch()
    # example_usage_single()
    # run_from_args()
