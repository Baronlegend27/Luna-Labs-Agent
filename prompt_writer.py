import re
from pathlib import Path
from datetime import datetime



#For Export
def fill_dict_with_list(data_dict: dict, values: list):
    """
    Fill a dictionary's keys with values from a list, matching by order.

    If there are more keys than values, remaining keys are left unchanged (or None).
    If there are more values than keys, extra values are ignored.
    """
    for key, value in zip(data_dict.keys(), values):
        data_dict[key] = value
    return data_dict

#For Export
def fill_template_with_dict(
    template_path: Path, 
    data: dict, 
    output_folder: Path = None,
    name_prefix: str = None
):
    """
    Fill placeholders in a text file (e.g. {key}) with values from a dictionary,
    and write the result to a new file in the specified folder with a unique name.
    
    Args:
        template_path: Path to the input template file.
        data: Dictionary of key/value pairs.
        output_folder: Folder where the filled file will be saved. 
                       If None, uses "filled_templates" in the same directory as template.
        name_prefix: Optional prefix for the output filename. 
                     If None, uses the template filename.
    
    Returns:
        A tuple (filled_text, missing_keys, output_path)
    """
    # Set default output folder if not provided
    if output_folder is None:
        output_folder = template_path.parent / "filled_templates"
    
    # Create the output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    if name_prefix is None:
        name_prefix = template_path.stem
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{name_prefix}_{timestamp}{template_path.suffix}"
    output_path = output_folder / output_filename
    
    # Read the template file
    template_text = template_path.read_text(encoding="utf-8")
    
    # Find all placeholders like {key}
    placeholders = re.findall(r"\{(.*?)\}", template_text)
    
    filled_text = template_text
    missing_keys = []
    
    # Replace placeholders with actual data
    for key in placeholders:
        if key in data:
            filled_text = filled_text.replace(f"{{{key}}}", str(data[key]))
        else:
            filled_text = filled_text.replace(f"{{{key}}}", f"[MISSING: {key}]")
            missing_keys.append(key)
    
    # Write the filled text to the new output file
    output_path.write_text(filled_text, encoding="utf-8")
    
    print(f"✅ Template filled and saved to → {output_path}")
    
    if missing_keys:
        print("\n⚠️ Missing keys:")
        for k in missing_keys:
            print(f" - {k}")
    
    return filled_text, missing_keys, output_path


def get_most_recent_txt(
    folder: Path,
    pattern: str = "*"
) -> Path:
    """
    Get the most recent .txt file from a folder based on modification time.
    
    Args:
        folder: Path to the folder to search.
        pattern: Glob pattern to match files (e.g., "template_*", "invoice_*").
                 Default "*" matches all .txt files.
    
    Returns:
        Path to the most recent .txt file.
        
    Raises:
        FileNotFoundError: If no matching .txt files are found.
        NotADirectoryError: If the folder doesn't exist.
    """
    # Check if folder exists
    if not folder.exists():
        raise NotADirectoryError(f"Folder not found: {folder}")
    
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")
    
    # Get all matching .txt files
    search_pattern = f"{pattern}.txt"
    files = list(folder.glob(search_pattern))
    
    # Filter out directories, keep only files
    files = [f for f in files if f.is_file()]
    
    if not files:
        raise FileNotFoundError(f"No .txt files matching '{search_pattern}' found in {folder}")
    
    # Find the most recent file by modification time
    most_recent = max(files, key=lambda f: f.stat().st_mtime)
    

    return most_recent




