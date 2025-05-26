import pandas as pd
import os

# Input and output paths
input_path = os.path.join('docs', 'NEWAdultstotheDatabaseinlastMonth.xlsx')
output_path = os.path.join('data', 'extracted_names_v1.csv')

# Read the Excel file
# Assume first row is header, columns B and D are index 1 and 3 (0-based)
df = pd.read_excel(input_path, engine='openpyxl')

# Extract columns B and D (first and last names)
first_names = df.iloc[:, 1]
last_names = df.iloc[:, 3]

# Combine into a new DataFrame
names_df = pd.DataFrame({'First Name': first_names, 'Last Name': last_names})

# Ensure output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save to CSV
names_df.to_csv(output_path, index=False)

print(f"Extracted {len(names_df)} names to {output_path}") 