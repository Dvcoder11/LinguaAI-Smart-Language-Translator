
import os
import requests
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# 1. PROVIDER CONFIGURATION
# ==========================================

OPENROUTER_API_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)


GROQ_API_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

TIMEOUT = 60


# ==========================================
# 2. EXTRACT API ERROR DETAILS
# ==========================================

def get_api_error_message(response, provider_name):

    status_code = response.status_code

    try:
        error_data = response.json()

        error_details = error_data.get("error", {})

        if isinstance(error_details, dict):

            message = error_details.get("message")

            error_code = error_details.get("code")

        else:

            message = str(error_details)

            error_code = None

        if not message:
            message = error_data.get("message")

    except (ValueError, AttributeError):

        message = None

        error_code = None

    if not message:
        message = response.reason or "Unknown API error"

    status_messages = {

        400: "Bad request",

        401: "Invalid API key or unauthorized request",

        402: "Insufficient credits or payment required",

        403: "Access forbidden",

        404: "API endpoint or model not found",

        408: "Request timeout",

        429: "Rate limit exceeded or free quota exhausted",

        500: "Internal server error",

        502: "Bad gateway",

        503: "Translation service temporarily unavailable",

        504: "Gateway timeout"

    }

    friendly_message = status_messages.get(
        status_code,
        "API request failed"
    )

    if message and message.lower() != friendly_message.lower():

        friendly_message = f"{friendly_message}: {message}"

    return (
        f"{provider_name} API error "
        f"(HTTP {status_code}): {friendly_message}"
    )


# ==========================================
# 3. HANDLE HTTP REQUEST
# ==========================================

def make_api_request(url, headers, payload, provider_name):

    try:

        response = requests.post(

            url,

            headers=headers,

            json=payload,

            timeout=TIMEOUT

        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as error:

        response = error.response

        if response is not None:

            message = get_api_error_message(
                response,
                provider_name
            )

        else:

            message = (
                f"{provider_name} HTTP request failed: {error}"
            )

        raise RuntimeError(message) from error

    except requests.exceptions.Timeout as error:

        raise RuntimeError(
            f"{provider_name} request timed out after {TIMEOUT} seconds."
        ) from error

    except requests.exceptions.ConnectionError as error:

        raise RuntimeError(
            f"{provider_name} connection failed. Check your internet."
        ) from error

    except requests.exceptions.RequestException as error:

        raise RuntimeError(
            f"{provider_name} network request failed: {error}"
        ) from error

    except ValueError as error:

        raise RuntimeError(
            f"{provider_name} returned an invalid JSON response."
        ) from error


# ==========================================
# 4. EXTRACT TRANSLATION
# ==========================================

def extract_translation(data, provider_name):

    choices = data.get("choices", [])

    if not choices:

        raise RuntimeError(
            f"{provider_name} returned no translation choices."
        )

    content = choices[0].get(
        "message", {}
    ).get("content")

    if isinstance(content, list):

        content = "".join(

            part.get("text", "")

            for part in content

            if isinstance(part, dict)

        )

    if not isinstance(content, str) or not content.strip():

        raise RuntimeError(
            f"{provider_name} returned an empty translation."
        )

    return content.strip()


# ==========================================
# 5. OPENROUTER REQUEST
# ==========================================

def send_openrouter_request(messages):

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OpenRouter API key is missing."
        )

    headers = {

        "Authorization": f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type": "application/json",

        "HTTP-Referer": "http://localhost",

        "X-Title": "LinguaAI"

    }

    payload = {

        "model": OPENROUTER_MODEL,

        "messages": messages,

        "temperature": 0.2,

        "max_tokens": 1500

    }

    data = make_api_request(

        OPENROUTER_API_URL,

        headers,

        payload,

        "OpenRouter"

    )

    return extract_translation(data, "OpenRouter")


# ==========================================
# 6. GROQ REQUEST
# ==========================================

def send_groq_request(messages):

    if not GROQ_API_KEY:

        raise RuntimeError(
            "Groq API key is missing."
        )

    headers = {

        "Authorization": f"Bearer {GROQ_API_KEY}",

        "Content-Type": "application/json"

    }

    payload = {

        "model": GROQ_MODEL,

        "messages": messages,

        "temperature": 0.2,

        "max_tokens": 1500

    }

    data = make_api_request(

        GROQ_API_URL,

        headers,

        payload,

        "Groq"

    )

    return extract_translation(data, "Groq")


# ==========================================
# 7. AUTOMATIC PROVIDER FAILOVER
# ==========================================

def send_chat_request(messages):

    """
    Try OpenRouter first.

    If OpenRouter fails, try Groq.

    Every new request starts with OpenRouter again.
    """

    providers = [

        ("OpenRouter", send_openrouter_request),

        ("Groq", send_groq_request)

    ]

    errors = []

    for provider_name, provider_function in providers:

        try:

            result = provider_function(messages)

            print(
                f"[LinguaAI] Translation successful using {provider_name}."
            )

            return result

        except Exception as error:

            error_message = str(error).strip()

            if not error_message:

                error_message = type(error).__name__

            errors.append(
                f"{provider_name}: {error_message}"
            )

            print(
                f"[LinguaAI] {provider_name} failed: {error_message}"
            )

    raise RuntimeError(

        "All configured translation providers failed. "

        + " | ".join(errors)

    )


# ==========================================
# 8. CLIENT STATUS
# ==========================================

def get_client_status():

    return {

        "provider": "OpenRouter + Groq",

        "configured": bool(
            OPENROUTER_API_KEY or GROQ_API_KEY
        ),

        "openrouter_configured": bool(
            OPENROUTER_API_KEY
        ),

        "groq_configured": bool(
            GROQ_API_KEY
        ),

        "gemini_configured": bool(
            os.getenv("GEMINI_API_KEY")
        )

    }
