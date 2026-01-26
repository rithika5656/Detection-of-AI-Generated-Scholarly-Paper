import os
import pandas as pd
from datasets import load_dataset

def download_datasets():
    print("Downloading authentic AI detection datasets...")
    
    # Target directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data", "real_datasets")
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # 1. Download "artem9k/ai-text-detection-pile" (A popular large dataset)
        # We will take a robust sample of 1000 rows to keep it manageable locally
        print("Fetching 'artem9k/ai-text-detection-pile' (Sample: 1000)...")
        dataset = load_dataset("artem9k/ai-text-detection-pile", split="train", streaming=True)
        
        # Take 500 human, 500 AI
        human_samples = []
        ai_samples = []
        
        for entry in dataset:
            if len(human_samples) >= 500 and len(ai_samples) >= 500:
                break
                
            label = entry.get('label') or entry.get('generated') # Adjust based on dataset structure
            text = entry.get('text')
            
            # The label is usually 0 (human) or 1 (AI) in many HF datasets, checking...
            # In this specific dataset 'ai-text-detection-pile', check typical structure
            # Usually: 'text', 'source', 'id'.
            # Correction: let's try a more standard one "hello-simpleai/HC3" which is very high quality
            pass 
            
        # Switch to "hello-simpleai/HC3" (Human ChatGPT Comparison Corpus) - Highly regarded
        print("Fetching 'hello-simpleai/HC3' (Finance/Medicine/Wiki)...")
        hc3 = load_dataset("hello-simpleai/HC3", "all", split="train", streaming=True)
        
        data = []
        count = 0
        for entry in hc3:
            if count >= 200: break
            
            # Human answer
            if entry['human_answers']:
                data.append({
                    'text': entry['human_answers'][0],
                    'label': 'human',
                    'source': 'HC3'
                })
            
            # ChatGPT answer
            if entry['chatgpt_answers']:
                data.append({
                    'text': entry['chatgpt_answers'][0],
                    'label': 'ai',
                    'source': 'HC3'
                })
            count += 1
            
        # Save results
        df = pd.DataFrame(data)
        out_path = os.path.join(data_dir, "hc3_sample.csv")
        df.to_csv(out_path, index=False)
        print(f"saved HC3 sample to {out_path}")
        
        # Create text file samples for UI testing from this real data
        if not df.empty:
            real_human_text = df[df['label'] == 'human'].iloc[0]['text']
            real_ai_text = df[df['label'] == 'ai'].iloc[0]['text']
            
            with open(os.path.join(base_dir, "data", "samples", "real_human_sample.txt"), "w", encoding='utf-8') as f:
                 f.write(real_human_text)
                 
            with open(os.path.join(base_dir, "data", "samples", "real_ai_sample.txt"), "w", encoding='utf-8') as f:
                 f.write(real_ai_text)
                 
            print("Extracted real .txt samples to /data/samples/")
            
    except Exception as e:
        print(f"Error downloading datasets: {e}")
        print("Please check internet connection or HuggingFace availability.")

if __name__ == "__main__":
    download_datasets()
