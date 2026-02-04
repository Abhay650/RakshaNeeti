🛡️ रक्षाNeeti – Health Scheme Finder

An AI-powered tool that helps citizens discover the right government health schemes based on their state, eligibility criteria, and income level.
Supports voice input, multi-language translation, and an interactive Streamlit web app.

✨ Features

🎙️ Voice Input – Speak your eligibility criteria (uses speechrecognition + sounddevice).

📊 Machine Learning Recommendation – Decision Tree model suggests best schemes.

🌐 Multi-Language Support – Auto-translates scheme details into Hindi, Bengali, Tamil, Kannada, Marathi, etc.

🏛️ State-wise Filtering – Fetches schemes relevant to your state.

📋 Eligibility Detection – Extracts income level from eligibility text automatically.

🖥️ Streamlit Web App – User-friendly interface for non-technical users.

📦 Requirements

You need Python 3.8+ installed.

Install dependencies
pip install -r requirements.txt

requirements.txt
pandas
deep-translator
speechrecognition
sounddevice
wavio
streamlit
scikit-learn
audio-recorder-streamlit

▶️ Usage
🔹 CLI Mode (Voice/Text Input)
python main.py


Prompts you to speak or type your eligibility.

Asks for state and preferred language.

Recommends schemes with descriptions translated into your language.

🔹 Streamlit Web App
streamlit run app.py


Opens an interactive browser app.

Select state, income level, language.

Optionally record your voice eligibility input.

Displays the recommended scheme with translations.

📂 Project Structure
raksha_neeti/
│── app.py                 # Streamlit web app
│── main.py                # CLI script with voice input
│── merged_scheme2.csv     # Dataset of health schemes
│── requirements.txt       # Dependencies
│── README.md              # Project documentation

📊 Dataset

File: merged_scheme2.csv

Contains government health scheme details.

Important columns:

Scheme Name

Eligibility

State/National

Language-specific descriptions (optional)

🧠 Machine Learning Model

Uses Decision Tree Classifier trained on:

State/National

Income Level (Low, Middle, High, Unknown – derived from eligibility text).

Predicts most suitable health scheme.

Achieves ~85% accuracy on test data.

🌐 Supported Languages

English (en)

Hindi (hi)

Bengali (bn)

Kannada (kn)

Marathi (mr)

Tamil (ta)

❤️ Contributing

Contributions are welcome!

Fork the repo