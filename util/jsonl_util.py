import json
import os

def create_jsonl_entry(prompt: str, input_content: str, output_content: str) -> {}:
    """
    Create a JSONL entry with the given prompt, input content, and output content.

    Args:
        prompt (str): The system prompt to include in the JSONL entry.
        input_content (str): The user input content to include in the JSONL entry.
        output_content (str): The assistant output content to include in the JSONL entry.

    Returns:
        dict: A dictionary representing a JSONL entry with the specified messages.
    """
    return {
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_content},
            {"role": "assistant", "content": output_content}
        ]
    }


def create_jsonl_file(save_file_path: str, data: [{}]):
    """
    Create a JSONL file at the specified json_path with the given data.

    Args:
        save_file_path (str): The file json_path where the JSONL file will be saved.
        data (list of dict): A list of dictionaries, each representing a JSONL entry.

    Raises:
        FileNotFoundError: If the directory for the save file json_path does not exist.
        IOError: If an error occurs while writing to the file.
    """
    if not os.path.exists(os.path.dirname(save_file_path)):
        raise FileNotFoundError(f"The directory {os.path.dirname(save_file_path)} does not exist.")

    try:
        with open(save_file_path, 'w', encoding='utf-8') as file:
            for item in data:
                file.write(json.dumps(item) + '\n')
    except Exception as e:
        raise IOError(f"An error occurred while writing to the file: {e}")