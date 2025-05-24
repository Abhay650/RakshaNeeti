import streamlit as st
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# App Config
st.set_page_config(page_title="रक्षाNeeti - Scheme Finder", layout="wide")
st.title("\ud83c\udf10 \u0930\u0915\u094d\u0937\u093eNeeti - Your Government Scheme Advisor")

# Load and Prepare Data
@st.cache_data

def load_data():
    df = pd.read_csv("/mnt/data/merged_scheme2.csv")
    df.columns = df.columns.str.strip()

    if 'Eligibility' not in df.columns or 'State/National' not in df.columns:
        st.error("Required columns like 'Eligibility' or 'State/National' are missing from the data.")
        st.stop()

    df['Income_Level'] = df['Eligibility'].apply(categorize_income)
    return df

def categorize_income(text):
    text = str(text).lower()
    if any(keyword in text for keyword in ['bpl', 'low income', '< ₹21,000']):
        return 'Low'
    elif any(keyword in text for keyword in ['middle', 'pensioner', 'senior citizen']):
        return 'Middle'
    elif any(keyword in text for keyword in ['all', 'any']):
        return 'All'
    else:
        return 'Unknown'

# Language dictionary for translation
translations = {
    "English": {
        "title": "Recommended Schemes",
        "select_state": "Select your state:",
        "select_lang": "Choose Language:",
        "elig_text": "Paste Eligibility Text (Optional):",
        "find_btn": "Find Schemes",
        "income": "What's your income category?",
    },
    "Hindi": {
        "title": "\u0916\u093e\u0938 \u092f\u094b\u0917\u094d\u092f \u092f\u094b\u091c\u0928\u093e\u090f\u0902",
        "select_state": "\u0905\u092a\u0928\u0940 \u0930\u093e\u091c\u094d\u092f \u091a\u0941\u0928\u0947\u0902:",
        "select_lang": "\u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902:",
        "elig_text": "\u092f\u094b\u0917\u094d\u092f\u0924\u093e \u091f\u0947\u0915\u094d\u0938\u094d\u091f \u091a\u093f\u092a\u0915\u093e\u090f\0902 (\u0911\u092a\u094d\u0936\u0928\u093e):",
        "find_btn": "\u092f\u094b\u091c\u0928\u093e\u090f\u0902 \u0922\u0942\u0902\u0922\u0947\u0902",
        "income": "\u0906\u092a\u0915\u0940 \u0906\u092f \u0915\u094d\u092f\u093e \u0936\u094d\u0930\u0947\u0923\u0940 \u0936\u094d\u0930\u0947\u0923\u0940 \u0915\u094d\u092f\u093e \u0939\u0948?",
    }
}

# Load data
schemes_df = load_data()

# Sidebar
with st.sidebar:
    lang = st.selectbox("Choose Language / \u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902", ["English", "Hindi"])
    t = translations[lang]
    st.header(t["title"])
    state = st.selectbox(t["select_state"], sorted(schemes_df['State/National'].dropna().unique()))
    income = st.selectbox(t["income"], ['Low', 'Middle', 'All', 'Unknown'])
    elig_text = st.text_area(t["elig_text"], height=100)
    if elig_text.strip():
        income = categorize_income(elig_text)
        st.markdown(f"Detected Income Level: **{income}**")

# Filter and Predict
st.subheader(t["title"])
if st.button(t["find_btn"]):
    matched = schemes_df[(schemes_df['State/National'] == state) &
                         ((schemes_df['Income_Level'] == income) | (schemes_df['Income_Level'] == 'All'))]
    if matched.empty:
        st.warning("No matching schemes found for your criteria.")
    else:
        for _, row in matched.iterrows():
            st.markdown(f"### 📄 {row['Scheme Name']}")
            st.markdown(f"**Eligibility:** {row.get('Eligibility', 'N/A')}")
            st.markdown(f"**Description:** {row.get('Description', 'N/A')}")
            st.markdown("---")

# Footer
st.caption("Made with ❤️ by RakshaNeeti to simplify access to healthcare schemes across India.")
