import pandas as pd
from deep_translator import GoogleTranslator
import speech_recognition as sr
import sounddevice as sd
import wavio
import tempfile
import os

# Voice input function using sounddevice (avoids PyAudio issues)
def get_voice_input(prompt="Please speak your eligibility criteria after the beep. Recording for 5 seconds..."):
    print(prompt)
    duration = 5  # seconds
    fs = 16000  # sample rate

    print("🎙️ Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print("Recording complete.")

    temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavio.write(temp_wav.name, recording, fs, sampwidth=2)
    temp_wav.close()

    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_wav.name) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"✅ Recognized Text: {text}")
    except sr.UnknownValueError:
        print("⚠️ Could not understand audio, please try typing instead.")
        text = input("Enter eligibility text manually: ").strip()
    except sr.RequestError as e:
        print(f"⚠️ Could not request results from Google Speech Recognition service; {e}")
        text = input("Enter eligibility text manually: ").strip()

    os.remove(temp_wav.name)
    return text

# Load dataset
def load_scheme_data(csv_path='merged_scheme2.csv'):
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()

# Recommend schemes based on eligibility and state
def recommend_schemes(eligibility_text, state, language, df):
    print(f"\n🔍 Searching for schemes in {state} for eligibility: \"{eligibility_text}\"...")

    # Filter by state
    state_filtered = df[df['state'].str.lower() == state.lower()]
    if state_filtered.empty:
        print("❌ No data found for the selected state.")
        return

    # Match eligibility text with fuzzy keyword search
    matched = state_filtered[state_filtered['eligibility'].str.contains(eligibility_text, case=False, na=False)]

    if matched.empty:
        print("⚠️ No direct eligibility match found. Showing all state schemes.")
        matched = state_filtered

    # Display matched results
    for _, row in matched.iterrows():
        name = row.get('scheme_name', 'N/A')
        eligibility = row.get('eligibility', 'N/A')
        translated = row.get(language.lower(), None)

        # Translate if column is missing or blank
        if pd.isna(translated) or not translated.strip():
            try:
                translated = GoogleTranslator(source='auto', target=language).translate(eligibility)
            except Exception:
                translated = eligibility

        print(f"\n📌 Scheme Name: {name}")
        print(f"🌐 Description ({language}): {translated}")

# Main execution
def main():
    print("🗂️ Loading scheme data...")
    df = load_scheme_data()

    if df.empty:
        return

    # Voice input for eligibility text (fallback to typing if voice fails)
    eligibility_text = get_voice_input()

    # Other inputs remain typed
    state = input("Enter your state (e.g., Karnataka, Maharashtra): ").strip()
    language = input("Enter preferred language (e.g., hindi, tamil, bengali): ").strip().lower()

    recommend_schemes(eligibility_text, state, language, df)

if __name__ == "__main__":
    main()
