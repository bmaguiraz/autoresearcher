import pandas as pd

cleaned = pd.read_csv('data/cleaned.csv', dtype=str)
truth = pd.read_csv('data/ground_truth.csv', dtype=str)

print('Cleaned shape:', cleaned.shape)
print('Truth shape:', truth.shape)
print()

# Check for any differences in empty strings
for col in cleaned.columns:
    cleaned_empties = (cleaned[col] == '') | cleaned[col].isna()
    truth_empties = (truth[col] == '') | truth[col].isna()

    if cleaned_empties.sum() != truth_empties.sum():
        print(f'{col}: cleaned has {cleaned_empties.sum()} empties, truth has {truth_empties.sum()}')
