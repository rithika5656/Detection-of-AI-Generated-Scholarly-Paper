import requests
import json
import os
import random

def get_real_data_direct():
    print("Fetching authentic dataset samples directly from HC3 repository...")
    
    # Target: Finance subset of HC3 (Human ChatGPT Comparison Corpus)
    # It contains pairs of human answers and chatgpt answers
    url = "https://huggingface.co/datasets/hello-simpleai/HC3/resolve/main/finance/finance.jsonl"
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    samples_dir = os.path.join(base_dir, "data", "samples")
    os.makedirs(samples_dir, exist_ok=True)
    
    try:
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        human_text = ""
        ai_text = ""
        
        # Read line by line until we find good samples
        count = 0
        for line in response.iter_lines():
            if not line: continue
            if count > 10: break # Just need a few to find a good one
            
            data = json.loads(line)
            
            # HC3 structure: "human_answers": [...], "chatgpt_answers": [...]
            if data.get('human_answers') and data.get('chatgpt_answers'):
                h = data['human_answers'][0]
                a = data['chatgpt_answers'][0]
                
                # Check for reasonable length
                if len(h) > 500 and len(a) > 500:
                    human_text = h
                    ai_text = a
                    break # Found a good pair
            count += 1
            
        if human_text and ai_text:
            # Save Human Sample
            h_path = os.path.join(samples_dir, "real_human_finance.txt")
            with open(h_path, 'w', encoding='utf-8') as f:
                f.write(human_text)
            print(f"Saved real human sample: {h_path}")
            
            # Save AI Sample
            a_path = os.path.join(samples_dir, "real_ai_finance.txt")
            with open(a_path, 'w', encoding='utf-8') as f:
                f.write(ai_text)
            print(f"Saved real AI sample: {a_path}")
            
            print("Success! Real authentic samples acquired.")
        else:
            print("Could not find suitable samples in the download stream.")
            
    except Exception as e:
        print(f"Failed to download: {e}")

if __name__ == "__main__":
    get_real_data_direct()
