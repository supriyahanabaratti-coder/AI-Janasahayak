
SUPPORTED_LANGUAGES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Bengali": "bn-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN",
    "Urdu": "ur-IN",
    "Odia": "or-IN",
    "Assamese": "as-IN"
}


def get_supported_languages():
    return list(SUPPORTED_LANGUAGES.keys())


def validate_language(language):
    if language not in SUPPORTED_LANGUAGES:
        return "English"

    return language


def get_speech_code(language):
    language = validate_language(language)
    return SUPPORTED_LANGUAGES[language]
