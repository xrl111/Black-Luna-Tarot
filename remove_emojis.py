import os
import sys
import subprocess

try:
    import emoji
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "emoji"])
    import emoji

def strip_emojis(text):
    return emoji.replace_emoji(text, replace='')

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return False
    
    new_content = strip_emojis(content)
    
    # In case there are some specific characters like '—' that aren't emojis but we want to be safe,
    # wait, they only asked for icons/emojis. The 'emoji' library should handle , , , etc.
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    skip_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.next', 'dist', 'build'}
    exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.yml', '.yaml', '.sh', '.css', '.env', '.md', '.json', '.txt'}
    
    count = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in exts):
                filepath = os.path.join(root, file)
                if process_file(filepath):
                    print(f"Removed emojis from: {filepath}")
                    count += 1
    print(f"Total files updated: {count}")

if __name__ == "__main__":
    main()
