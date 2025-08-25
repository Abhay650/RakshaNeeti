
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

app = FastAPI()

# ---------------- Load and Train Model ----------------

df = pd.read_csv("merged_scheme2.csv", encoding='ISO-8859-1', skiprows=1)
df.columns = df.columns.str.strip()
df.rename(columns={'Scheme Name (English)': 'Scheme Name'}, inplace=True)

def extract_income_level(text: str) -> str:
    if pd.isnull(text) or not text.strip():
        return 'Unknown'
    text = text.lower()
    if any(word in text for word in ['bpl', 'low-income', '< ₹21,000', 'below poverty line', 'ews']):
        return 'Low'
    if any(word in text for word in ['middle', 'senior citizen', 'pensioner']):
        return 'Middle'
    if any(word in text for word in ['all', 'any']):
        return 'All'
    return 'Unknown'

df['Income_Level'] = df['Eligibility'].apply(extract_income_level)

X = df[['State/National', 'Income_Level']].copy()
y = df['Scheme Name']

state_encoder = LabelEncoder().fit(X['State/National'])
income_encoder = LabelEncoder().fit(X['Income_Level'])
scheme_encoder = LabelEncoder().fit(y)

X_encoded = pd.DataFrame({
    'State': state_encoder.transform(X['State/National']),
    'Income': income_encoder.transform(X['Income_Level'])
})

y_encoded = scheme_encoder.transform(y)

X_train, X_test, y_train, y_test = train_test_split(X_encoded, y_encoded, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

# ---------------- API Input Model ----------------

class UserInput(BaseModel):
    state: str
    income_text: str

# ---------------- API Endpoints ----------------

@app.post("/predict")
def predict_scheme(user_input: UserInput):
    try:
        income_level = extract_income_level(user_input.income_text)
        s = state_encoder.transform([user_input.state])[0]
        i = income_encoder.transform([income_level])[0]
        prediction = model.predict([[s, i]])
        scheme_name = scheme_encoder.inverse_transform(prediction)[0]

        return {
            "recommended_scheme": scheme_name,
            "state": user_input.state,
            "income_level": income_level
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
