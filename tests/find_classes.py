import os
import re


def find_class_in_files(directory, class_name):
    """
    Search for a class definition in all .py files in the given directory (recursively).

    Args:
        directory (str): The root directory to search in.
        class_name (str): The name of the class to search for.

    Returns:
        list: A list of file paths and line numbers where the class is defined.
    """
    results = []
    class_pattern = re.compile(rf"class\s+{class_name}\b")  # Regex: matches "class <class_name>"

    # Walk through all files in the directory and subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Only look at Python files
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line_number, line in enumerate(f, start=1):
                            if class_pattern.search(line):  # Match the class pattern
                                results.append((file_path, line_number, line.strip()))
                except Exception as e:
                    print(f"Could not open {file_path}: {e}")

    return results


# Example usage
if __name__ == "__main__":
    directory = "../../../"  # Change this to your target directory
    class_name = "HookKeyframeGroup"
    matches = find_class_in_files(directory, class_name)

    if matches:
        print(f"Class '{class_name}' found in the following locations:")
        for file_path, line_number, line in matches:
            print(f"  - {file_path}, line {line_number}: {line}")
    else:
        print(f"Class '{class_name}' not found in any .py file under {directory}.")
