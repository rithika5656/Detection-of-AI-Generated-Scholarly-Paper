
import pandas as pd
import os

# Create a simple DataFrame
df = pd.DataFrame({'Data': ['This is a test sentence.', 'Another sentence with AI content likely.']})
os.makedirs('data/uploads', exist_ok=True)
# Save as Excel
try:
    df.to_excel('data/uploads/debug_test.xlsx', index=False)
    print("Created debug_test.xlsx")
except Exception as e:
    print(f"Failed to create xlsx: {e}")
