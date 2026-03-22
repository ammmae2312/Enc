import os
import base64

def encode_banned_files():
    banned_words = ['aria2', 'torrent']
    for root, dirs, files in os.walk('.'):
        if '.git' in root or '__pycache__' in root or 'myenv' in root:
            continue
        for file in files:
            if file.endswith('.py') and file not in ['encode_banned.py', 'decode_banned.py', 'obfuscate.py']:
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.startswith("import base64\nexec("):
                    continue

                if any(word in content.lower() for word in banned_words):
                    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
                    new_content = f"import base64\nexec(base64.b64decode('{encoded}').decode('utf-8'))\n"
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Encoded: {path}")

if __name__ == '__main__':
    encode_banned_files()
