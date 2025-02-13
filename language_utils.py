from deep_translator import GoogleTranslator
from langdetect import detect


def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        print(f"Language not detected : {str(e)}")
        return "en"


def translate_to_english(text):
    detected_lang = detect_language(text)
    if detected_lang == "en":
        return text
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)
        print("translated")
        return translated_text
    except Exception as e:
        return f"Translation Error: {e}"

