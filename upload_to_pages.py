import os
import subprocess
import shutil
from datetime import datetime

def upload_response_files():
    """
    Automatically upload files from ResponseFiles/ to gh-pages branch
    """
    
    response_files_dir = "ResponseFiles"
    
    # Check if ResponseFiles directory exists
    if not os.path.exists(response_files_dir):
        print(f"Error: {response_files_dir} directory not found")
        return
    
    # Get list of .txt files
    txt_files = [f for f in os.listdir(response_files_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print("No .txt files found in ResponseFiles/")
        return
    
    print(f"Found {len(txt_files)} files to upload")
    
    # Save current branch
    current_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True
    ).stdout.strip()
    
    try:
        # Switch to gh-pages branch
        print("Switching to gh-pages branch...")
        subprocess.run(["git", "checkout", "gh-pages"], check=True)
        
        # Create ResponseFiles directory if it doesn't exist
        if not os.path.exists("ResponseFiles"):
            os.makedirs("ResponseFiles")
        
        # Copy all txt files
        print("Copying files...")
        for file in txt_files:
            src = os.path.join("..", response_files_dir, file) if current_branch != "gh-pages" else os.path.join(response_files_dir, file)
            # Since we're on gh-pages, copy from main branch location
            main_src = os.path.join(f"../{response_files_dir}", file)
            
            # We need to get files from main branch
            subprocess.run(["git", "checkout", current_branch, "--", f"{response_files_dir}/{file}"], check=True)
        
        # Generate index.html with file list
        print("Generating index.html...")
        generate_index_html(txt_files)
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Update response files - {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push to GitHub
        print("Pushing to GitHub...")
        subprocess.run(["git", "push", "origin", "gh-pages"], check=True)
        
        print("✅ Successfully uploaded files to GitHub Pages!")
        print(f"View at: https://baronlegend27.github.io/Luna-Labs-Agent/")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    
    finally:
        # Switch back to original branch
        print(f"Switching back to {current_branch}...")
        subprocess.run(["git", "checkout", current_branch])

def generate_index_html(files):
    """
    Generate an index.html that lists all response files
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Response Files</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        .file-list {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .file-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.2s;
        }
        .file-item:hover {
            background-color: #f8f9fa;
        }
        .file-item:last-child {
            border-bottom: none;
        }
        .file-link {
            color: #007bff;
            text-decoration: none;
            font-size: 18px;
            font-weight: 500;
        }
        .file-link:hover {
            text-decoration: underline;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .count {
            color: #666;
            font-size: 16px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>Claude Response Files</h1>
    <p class="count">Total files: """ + str(len(files)) + """</p>
    <div class="file-list">
"""
    
    # Sort files by name (most recent first if they have timestamps)
    files.sort(reverse=True)
    
    for file in files:
        html += f"""
        <div class="file-item">
            <a href="ResponseFiles/{file}" class="file-link" target="_blank">{file}</a>
            <div class="timestamp">Click to view file contents</div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    upload_response_files()