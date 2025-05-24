import pandas as pd
from deep_translator import GoogleTranslator

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

    # User input
    eligibility_text = input("Enter eligibility text (e.g., 'cancer', 'low income', etc.): ").strip()
    state = input("Enter your state (e.g., Karnataka, Maharashtra): ").strip()
    language = input("Enter preferred language (e.g., hindi, tamil, bengali): ").strip().lower()

    recommend_schemes(eligibility_text, state, language, df)

if __name__ == "__main__":
    main()
