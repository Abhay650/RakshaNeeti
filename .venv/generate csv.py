import pandas as pd

# Sample data
data = {
    'Scheme Name': [
        'Ayushman Bharat', 'Central Government Health Scheme',
        'Rashtriya Swasthya Bima Yojana', 'Employees State Insurance Scheme',
        'Senior Citizen Health Insurance Scheme'
    ],
    'Eligibility': [
        'All BPL families and low-income groups',
        'Central government employees earning < ₹21,000',
        'BPL families in unorganized sector',
        'Employees earning < ₹21,000',
        'Senior citizens and pensioners'
    ],
    'State/National': [
        'National', 'National', 'State', 'State', 'National'
    ]
}

# Save it in the current working directory
df = pd.DataFrame(data)
df.to_csv('schemes.csv', index=False)

print("CSV file created successfully.")
