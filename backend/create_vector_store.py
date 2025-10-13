from rag_main import RagPipeline

rag_pipeline = RagPipeline('vector_store_builder')

import os

def get_all_file_paths(directory):
    """
    Retrieves the absolute paths of all files within a given directory
    and its subdirectories.

    Args:
        directory (str): The path to the target directory.

    Returns:
        list: A list containing the absolute paths of all files found.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

# Example usage:
target_folder = "/home/yslcoat/data/text_documents/"  # Replace with your actual target folder path
all_files = get_all_file_paths(target_folder)

for file_path in all_files:
    print(file_path)

rag_pipeline.build_vector_store(all_files)