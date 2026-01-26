import os
import random
import csv

def create_dummy_dataset():
    """Generates a dummy dataset of 'Human' vs 'AI' texts for testing/training."""
    
    # Get absolute path to the project root (assuming src/learning/create_dataset.py)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data")
    
    output_dir = os.path.join(data_dir, "dataset")
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "scholarly_data.csv")
    
    print(f"Generating synthetic dataset at {csv_path}...")
    
    # Templates for synthetic generation
    human_phrases = [
        "In this study, we empirically demonstrate...",
        "The results suggest a significant correlation between...",
        "Contrary to previous findings by Smith et al. (2019)...",
        "Our methodology involves a rigorous cross-validation...",
        "Data was collected from three distinct sources...",
        "We argue that the implications of this theory are...",
        "Figure 3 illustrates the decay rate of...",
        "We utilized a double-blind experimental design...",
    ]
    
    ai_phrases = [
        "In conclusion, the importance of this topic cannot be overstated.",
        "There are many advantages and disadvantages to consider.",
        "Furthermore, it is important to note that...",
        "Artificial Intelligence has revolutionized various industries.",
        "This essay will discuss the key factors of...",
        "On the one hand, there are benefits; on the other hand, risks.",
        "In summary, the aforementioned points illustrate...",
        "To conclude, one must consider all aspects effectively.",
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"]) # Header
        
        # Generate 100 samples
        for _ in range(50):
            # Human sample: specific, variable length, cites
            text = " ".join(random.sample(human_phrases, k=random.randint(2, 4)))
            writer.writerow([text, "human"])
            
        for _ in range(50):
            # AI sample: generic, structured, connective words
            text = " ".join(random.sample(ai_phrases, k=random.randint(2, 4)))
            writer.writerow([text, "ai"])
            
    print("Dataset creation complete.")

    # Also create specific large sample files for UI testing
    samples_dir = os.path.join(data_dir, "samples")
    os.makedirs(samples_dir, exist_ok=True)
    
    with open(os.path.join(samples_dir, "human_sample.txt"), "w") as f:
        f.write("Title: Deep Learning in Genomics.\n\nAbstract: We present a novel architecture...\n\n" + 
                " ".join(human_phrases * 5))
                
    with open(os.path.join(samples_dir, "ai_sample.txt"), "w") as f:
        f.write("Title: The Future of AI.\n\nAbstract: AI is changing the world...\n\n" + 
                " ".join(ai_phrases * 5))
                
    print(f"Sample test files created in {samples_dir}")

if __name__ == "__main__":
    create_dummy_dataset()
