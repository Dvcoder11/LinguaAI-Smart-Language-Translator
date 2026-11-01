
# ==========================================
# LINGUAAI - TRANSLATION SERVICE
# Language Detection + Translation Cache
# ==========================================

import re
import time
import threading
from collections import OrderedDict

from langdetect import detect_langs, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

from services.openrouter_client import send_chat_request

DetectorFactory.seed = 0


# ==========================================
# 1. LANGUAGE CODE MAPPING
# ==========================================

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese",
    "ar": "Arabic",
    "bn": "Bengali",
    "ur": "Urdu",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "nl": "Dutch",
    "tr": "Turkish",
    "pl": "Polish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
    "th": "Thai",
}


# ==========================================
# 2. TRANSLATION CACHE CONFIGURATION
# ==========================================

CACHE_MAX_SIZE = 500
CACHE_TTL = 60 * 60

translation_cache = OrderedDict()
cache_lock = threading.RLock()

cache_hits = 0
cache_misses = 0


# ==========================================
# 3. CACHE KEY GENERATION
# ==========================================

def generate_cache_key(text, source_language, target_language):

    normalized_text = text.strip()
    normalized_source = source_language.strip().lower()
    normalized_target = target_language.strip().lower()

    return (
        normalized_text,
        normalized_source,
        normalized_target
    )


# ==========================================
# 4. GET TRANSLATION FROM CACHE
# ==========================================

def get_cached_translation(cache_key):

    global cache_hits, cache_misses

    with cache_lock:

        cached_item = translation_cache.get(cache_key)

        if cached_item is None:
            cache_misses += 1
            return None

        cached_result, created_at = cached_item

        if time.monotonic() - created_at > CACHE_TTL:
            del translation_cache[cache_key]
            cache_misses += 1
            return None

        translation_cache.move_to_end(cache_key)

        cache_hits += 1

        result = cached_result.copy()
        result["cache_hit"] = True

        return result


# ==========================================
# 5. SAVE TRANSLATION TO CACHE
# ==========================================

def save_translation_to_cache(cache_key, result):

    with cache_lock:

        result_to_store = result.copy()
        result_to_store.pop("cache_hit", None)

        translation_cache[cache_key] = (
            result_to_store,
            time.monotonic()
        )

        translation_cache.move_to_end(cache_key)

        current_time = time.monotonic()

        expired_keys = [
            key
            for key, (_, created_at) in translation_cache.items()
            if current_time - created_at > CACHE_TTL
        ]

        for key in expired_keys:
            translation_cache.pop(key, None)

        while len(translation_cache) > CACHE_MAX_SIZE:
            translation_cache.popitem(last=False)


# ==========================================
# 6. CACHE STATISTICS
# ==========================================

def get_cache_stats():

    with cache_lock:

        total_requests = cache_hits + cache_misses

        hit_rate = (
            (cache_hits / total_requests) * 100
            if total_requests > 0
            else 0
        )

        return {
            "cache_size": len(translation_cache),
            "maximum_size": CACHE_MAX_SIZE,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "hit_rate": round(hit_rate, 2),
            "cache_ttl_seconds": CACHE_TTL
        }


# ==========================================
# 7. CLEAR TRANSLATION CACHE
# ==========================================

def clear_translation_cache():

    global cache_hits, cache_misses

    with cache_lock:

        translation_cache.clear()
        cache_hits = 0
        cache_misses = 0

    return True


# ==========================================
# 8. VALIDATE INPUT
# ==========================================

def validate_translation_input(text, source_language, target_language):

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter some text to translate.")

    if len(text) > 5000:
        raise ValueError("Text cannot exceed 5000 characters.")

    if not isinstance(source_language, str) or not source_language.strip():
        raise ValueError("Please select a source language.")

    if not isinstance(target_language, str) or not target_language.strip():
        raise ValueError("Please select a target language.")

    if (
        source_language.strip().lower() != "auto"
        and source_language.strip().lower()
        == target_language.strip().lower()
    ):
        raise ValueError(
            "Source and target languages must be different."
        )

    return True


# ==========================================
# 9. SCRIPT-BASED LANGUAGE DETECTION
# ==========================================

def detect_script_language(text):

    script_patterns = [

        (r"[\u0900-\u097F]", "hi", "Hindi"),
        (r"[\u0980-\u09FF]", "bn", "Bengali"),
        (r"[\u0A00-\u0A7F]", "pa", "Punjabi"),
        (r"[\u0A80-\u0AFF]", "gu", "Gujarati"),
        (r"[\u0B80-\u0BFF]", "ta", "Tamil"),
        (r"[\u0C00-\u0C7F]", "te", "Telugu"),
        (r"[\u0600-\u06FF]", "ar", "Arabic"),
        (r"[\u0590-\u05FF]", "he", "Hebrew"),
        (r"[\u0E00-\u0E7F]", "th", "Thai"),
        (r"[\uAC00-\uD7AF]", "ko", "Korean"),
        (r"[\u3040-\u30FF]", "ja", "Japanese"),
        (r"[\u4E00-\u9FFF]", "zh-cn", "Chinese"),
        (r"[\u0400-\u04FF]", "ru", "Russian"),

    ]

    for pattern, code, name in script_patterns:

        if re.search(pattern, text):

            return {
                "language_code": code,
                "language_name": name,
                "confidence": 1.0
            }

    return None


# ==========================================
# 10. SHORT ENGLISH TEXT DETECTION
# ==========================================

def detect_short_english(text):

    words = re.findall(r"[a-z]+", text.lower())

    if not words:
        return None

    # Avoid applying this rule to text containing
    # non-Latin letters.
    if not re.fullmatch(r"[\x00-\x7F]+", text):
        return None

    common_english_phrases = {
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "good night",
        "how are you",
        "how are you today",
        "thank you",
        "thank you very much",
        "see you",
        "see you later",
        "goodbye",
        "i love you",
        "what is your name",
        "nice to meet you"
    }

    normalized_text = re.sub(
        r"[^a-z\s]",
        "",
        text.lower()
    ).strip()

    if normalized_text in common_english_phrases:

        return {
            "language_code": "en",
            "language_name": "English",
            "confidence": 0.90
        }

    english_common_words = {
        "the", "is", "are", "am", "was", "were",
        "you", "your", "how", "what", "where",
        "when", "why", "who", "this", "that",
        "these", "those", "and", "but", "with",
        "have", "has", "had", "hello", "please",
        "thank", "thanks", "good", "morning",
        "evening", "today", "tomorrow", "my",
        "me", "we", "they", "he", "she",
        "do", "does", "did", "can", "will",
        "would", "could", "should", "not"
    }

    matching_words = sum(
        1 for word in words
        if word in english_common_words
    )

    if matching_words >= 2:

        return {
            "language_code": "en",
            "language_name": "English",
            "confidence": 0.75
        }

    return None


# ==========================================
# 11. LOCAL LANGUAGE DETECTION
# ==========================================

def detect_language(text):

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            "Please enter text for language detection."
        )

    text = text.strip()

    # First: identify languages using their writing scripts.
    script_result = detect_script_language(text)

    if script_result:
        return script_result

    # Second: handle common short English phrases.
    english_result = detect_short_english(text)

    if english_result:
        return english_result

    # Third: use the langdetect library.
    try:

        predictions = detect_langs(text)

        if not predictions:
            return {
                "language_code": None,
                "language_name": "Uncertain",
                "confidence": 0.0
            }

        best_prediction = predictions[0]

        language_code = best_prediction.lang.lower()
        confidence = best_prediction.prob

        # Keep the original confidence threshold for
        # other Latin-script languages.
        if confidence < 0.85:

            return {
                "language_code": None,
                "language_name": "Uncertain",
                "confidence": confidence
            }

        language_name = LANGUAGE_NAMES.get(
            language_code,
            language_code
        )

        return {
            "language_code": language_code,
            "language_name": language_name,
            "confidence": confidence
        }

    except LangDetectException:

        return {
            "language_code": None,
            "language_name": "Uncertain",
            "confidence": 0.0
        }


# ==========================================
# 12. CREATE TRANSLATION PROMPT
# ==========================================

def create_translation_messages(text, source_language, target_language):

    validate_translation_input(
        text,
        source_language,
        target_language
    )

    if source_language.strip().lower() == "auto":

        source_instruction = (
            "Automatically identify the source language "
            "from the input text."
        )

    else:

        source_instruction = f"Translate from {source_language}."

    system_prompt = """
You are LinguaAI, a professional multilingual translation assistant.

Rules:
1. Preserve the original meaning and context.
2. Maintain the original tone and intent.
3. Use natural and grammatically correct language.
4. Preserve names, numbers and important details.
5. Do not add unnecessary explanations.
6. Return only the translated text.
7. Translate questions instead of answering them.
8. Preserve formatting and line breaks where possible.
9. If the source language is not specified, identify it
   automatically before translating.
10. Never include XML, HTML or Markdown tags in the response.
"""

    user_prompt = f"""
Translate the following text.

Source language:
{source_instruction}

Target language:
{target_language}

Text to translate:
{text}

Return only the translated text without any XML or HTML tags.
"""

    return [
        {
            "role": "system",
            "content": system_prompt.strip()
        },
        {
            "role": "user",
            "content": user_prompt.strip()
        }
    ]


# ==========================================
# 13. CLEAN AI TRANSLATION RESPONSE
# ==========================================

def clean_translation_response(translated_text):

    if not isinstance(translated_text, str):
        return ""

    translated_text = translated_text.strip()

    translated_text = re.sub(
        r"</?text\s*>",
        "",
        translated_text,
        flags=re.IGNORECASE
    )

    translated_text = re.sub(
        r"^```(?:text)?\s*|\s*```$",
        "",
        translated_text,
        flags=re.IGNORECASE
    )

    return translated_text.strip()


# ==========================================
# 14. TRANSLATE WITH LANGUAGE DETECTION
# ==========================================

def translate_text_with_details(text, source_language, target_language):

    validate_translation_input(
        text,
        source_language,
        target_language
    )

    cache_key = generate_cache_key(
        text,
        source_language,
        target_language
    )

    # STEP 1: Check translation cache.

    cached_result = get_cached_translation(cache_key)

    if cached_result is not None:

        print("[LinguaAI Cache] Translation found in cache.")

        return cached_result

    print("[LinguaAI Cache] Cache miss. Calling AI provider.")

    # STEP 2: Detect source language.

    if source_language.strip().lower() == "auto":

        detection_result = detect_language(text)

        detected_language = detection_result["language_name"]
        detected_code = detection_result["language_code"]

        if (
            detected_code is not None
            and detected_language.lower()
            == target_language.strip().lower()
        ):

            raise ValueError(
                "The detected source language and target language "
                "are the same. Please select another target language."
            )

        if detected_language == "Uncertain":
            actual_source_language = "Auto"
        else:
            actual_source_language = detected_language

    else:

        detected_language = source_language.strip()
        detected_code = None
        actual_source_language = source_language.strip()

    # STEP 3: Create translation prompt.

    messages = create_translation_messages(
        text,
        actual_source_language,
        target_language
    )

    # STEP 4: Call configured AI providers.

    translated_text = send_chat_request(messages)

    # STEP 5: Clean AI response.

    translated_text = clean_translation_response(translated_text)

    if not translated_text:

        raise ValueError(
            "The translation provider returned an empty response."
        )

    # STEP 6: Prepare result.

    result = {
        "translated_text": translated_text,
        "detected_language": detected_language,
        "detected_language_code": detected_code,
        "source_language": actual_source_language,
        "target_language": target_language,
        "cache_hit": False
    }

    # STEP 7: Save successful translation to cache.

    save_translation_to_cache(cache_key, result)

    print("[LinguaAI Cache] Translation saved successfully.")

    return result


# ==========================================
# 15. BACKWARD-COMPATIBLE TRANSLATION
# ==========================================

def translate_text(text, source_language, target_language):

    result = translate_text_with_details(
        text,
        source_language,
        target_language
    )

    return result["translated_text"]


# ==========================================
# 16. SERVICE STATUS
# ==========================================

def get_service_status():

    return {
        "service": "LinguaAI Translation Service",
        "status": "initialized",
        "provider": "OpenRouter + Groq",
        "language_detection": (
            "Script detection + short English fallback + langdetect"
        ),
        "caching": "Enabled",
        "cache_statistics": get_cache_stats()
    }
