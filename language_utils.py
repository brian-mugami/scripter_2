from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Fixes inconsistent language detection issues
DetectorFactory.seed = 0


def detect_language(in_text):
    text = in_text.strip()
    try:
        return detect(text)
    except Exception as e:
        print(str(e))
        return "auto"


def translate_to_english(intext):
    detected_lang = detect_language(intext)

    if detected_lang == "en":
        return intext

    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(intext)
        return translated_text
    except Exception as e:
        print(f"Translation Error: {e}")
        return intext
