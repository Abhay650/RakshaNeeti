import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from deep_translator import GoogleTranslator

# --- Step 1: Clean column names and ensure required columns exist ---
def normalize_columns(df):
    df.columns = df.columns.str.strip()
    if 'Eligibility' not in df.columns:
        matches = [col for col in df.columns if 'eligib' in col.lower()]
        if matches:
            df.rename(columns={matches[0]: 'Eligibility'}, inplace=True)
        else:
            st.error("We couldn't find an 'Eligibility' column in your file.")
    return df

# --- Step 2: Extract income level from eligibility text ---
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

# --- Step 3: Load and prepare the scheme data ---
@st.cache_data
def load_data(path='merged_scheme2.csv'):
    df = pd.read_csv(path, encoding='ISO-8859-1', skiprows=1)
    df = normalize_columns(df)
    df['Income_Level'] = df['Eligibility'].apply(extract_income_level)
    df.rename(columns={'Scheme Name (English)': 'Scheme Name'}, inplace=True)
    return df

# --- Step 4: Train model ---
@st.cache_resource
def train_model(df: pd.DataFrame):
    X = df[['State/National', 'Income_Level']].copy()
    y = df['Scheme Name']

    state_encoder = LabelEncoder().fit(X['State/National'])
    income_encoder = LabelEncoder().fit(X['Income_Level'])

    X_encoded = pd.DataFrame({
        'State': state_encoder.transform(X['State/National']),
        'Income': income_encoder.transform(X['Income_Level'])
    })

    scheme_encoder = LabelEncoder().fit(y)
    y_encoded = scheme_encoder.transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y_encoded, test_size=0.2, random_state=42)

    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    return model, state_encoder, income_encoder, scheme_encoder, accuracy

# --- Step 5: Translate text using GoogleTranslator ---
def translate_text(text, target_lang_code):
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(text)
    except Exception as e:
        return f"[Translation error: {e}]"

# --- Step 6: Build Streamlit UI ---
st.set_page_config(page_title="Health Scheme Finder", layout="wide")
st.title("🛡️ रक्षाNeeti")
st.subheader("📋 Find the right government schemes for you")

st.markdown("""
This tool helps you identify a suitable **health scheme** based on your **state** and **family income**.
""")

# Load data and model
df = load_data()
model, state_encoder, income_encoder, scheme_encoder, model_accuracy = train_model(df)

# --- Sidebar for user input ---
with st.sidebar:
    st.header("📝 Tell us about yourself")

    language = st.selectbox("🌐 Select Language", ['English', 'Hindi', 'Bengali', 'Kannada', 'Marathi', 'Tamil'])
    state = st.selectbox("📍 Which state are you from?", sorted(df['State/National'].unique()))
    income_level = st.selectbox("💰 What's your family's income category?", ['Low', 'Middle', 'High', 'Unknown'])

    st.caption("Optional: Paste eligibility text from a government form or record your voice")

    # --- Voice Recorder Widget ---
    import io
    import speech_recognition as sr
    from audio_recorder_streamlit import audio_recorder as voice_input_recorder

    audio_bytes = voice_input_recorder("🎙️ Record your eligibility criteria here",  energy_threshold=4000, pause_threshold=1.0, sample_rate=16000)

    elig_text = ""

    if audio_bytes is not None:
        recognizer = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes)

        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        try:
            elig_text = recognizer.recognize_google(audio_data)
            st.success(f"🎉 Recognized eligibility text: {elig_text}")
            detected_level = extract_income_level(elig_text)
            st.markdown(f"🔍 Detected income level: **{detected_level}**")
            income_level = detected_level
        except sr.UnknownValueError:
            st.warning("⚠️ Sorry, could not understand the audio.")
        except sr.RequestError as e:
            st.warning(f"⚠️ Could not request results; {e}")

    # Text area (prefilled if voice recognized)
    elig_text = st.text_area("📋 Paste or edit eligibility text", value=elig_text, height=100)

    # Update income level if user edits text manually
    if elig_text.strip():
        detected_level = extract_income_level(elig_text)
        st.markdown(f"🔍 Detected income level: **{detected_level}**")
        income_level = detected_level

# --- Prediction Section ---
st.markdown("## 🎯 Your Recommended Scheme")
if st.button("🔎 Find My Scheme"):
    try:
        s = state_encoder.transform([state])[0]
        i = income_encoder.transform([income_level])[0]
        prediction = model.predict([[s, i]])
        scheme_name = scheme_encoder.inverse_transform(prediction)[0]

        st.success(f"✅ We recommend: **{scheme_name}**")

        scheme_info = df[df['Scheme Name'] == scheme_name].iloc[0]
        original_name = scheme_info.get('Scheme Name', '')
        original_elig = scheme_info.get('Eligibility', '')

        # Language codes for Google Translator
        lang_codes = {
            'English': 'en',
            'Hindi': 'hi',
            'Bengali': 'bn',
            'Kannada': 'kn',
            'Marathi': 'mr',
            'Tamil': 'ta'
        }

        target_lang = lang_codes.get(language, 'en')

        # Translate
        translated_name = translate_text(original_name, target_lang)
        translated_elig = translate_text(original_elig, target_lang)

        st.markdown(f"**Scheme Name ({language}):** {translated_name}")
        st.markdown(f"**Eligibility ({language}):** {translated_elig}")

    except Exception as e:
        st.error(f"Oops! Something went wrong: {e}")

# --- Data & Model Info ---
with st.expander("📊 Model and Scheme Data", expanded=False):
    st.metric("🔍 Model Accuracy", f"{model_accuracy:.2f}")
    st.dataframe(df[['Scheme Name', 'State/National', 'Income_Level', 'Eligibility']])

# --- Footer ---
st.caption("Made with ❤️ to help every citizen find the help they deserve.")
