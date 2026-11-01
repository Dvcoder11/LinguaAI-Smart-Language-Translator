
import requests
from unittest.mock import patch

from services import openrouter_client as client


# ==========================================
# LINGUAAI - API ERROR HANDLING TEST SUITE
# ==========================================

TEST_MESSAGES = [
    {
        "role": "user",
        "content": "Translate Hello into Hindi."
    }
]


# ==========================================
# 1. CREATE MOCK HTTP RESPONSE
# ==========================================

def create_mock_response(status_code, message):

    response = requests.Response()

    response.status_code = status_code

    response.reason = message

    response._content = (
        '{"error":{"message":"' + message + '"}}'
    ).encode("utf-8")

    return response


# ==========================================
# 2. RUN HTTP ERROR TEST
# ==========================================

def test_http_error(status_code, message, expected_text):

    print(f"\nTesting HTTP {status_code}...")

    mock_response = create_mock_response(
        status_code,
        message
    )

    # Ensure tests do not depend on real API keys.
    with patch.object(
        client,
        "OPENROUTER_API_KEY",
        "test-openrouter-key"
    ), patch.object(
        client,
        "GROQ_API_KEY",
        "test-groq-key"
    ), patch(
        "services.openrouter_client.requests.post",
        side_effect=[
            create_mock_response(status_code, message),
            create_mock_response(status_code, message)
        ]
    ) as mock_post:

        try:

            client.send_chat_request(TEST_MESSAGES)

            print("FAIL: Expected an error but request succeeded.")

        except RuntimeError as error:

            error_message = str(error)

            print("RESULT:", error_message)

            assert expected_text.lower() in error_message.lower(), (
                f"Expected '{expected_text}' in error message."
            )

            assert "OpenRouter" in error_message

            assert "Groq" in error_message

            assert mock_post.call_count == 2

            print(f"PASS: HTTP {status_code} handled correctly.")


# ==========================================
# 3. RUN TIMEOUT TEST
# ==========================================

def test_timeout():

    print("\nTesting API timeout...")

    with patch.object(
        client,
        "OPENROUTER_API_KEY",
        "test-openrouter-key"
    ), patch.object(
        client,
        "GROQ_API_KEY",
        "test-groq-key"
    ), patch(
        "services.openrouter_client.requests.post",
        side_effect=[
            requests.exceptions.Timeout("Request timed out"),
            requests.exceptions.Timeout("Request timed out")
        ]
    ) as mock_post:

        try:

            client.send_chat_request(TEST_MESSAGES)

            print("FAIL: Expected timeout error.")

        except RuntimeError as error:

            print("RESULT:", error)

            assert "timed out" in str(error).lower()

            assert mock_post.call_count == 2

            print("PASS: Timeout handled correctly.")


# ==========================================
# 4. RUN CONNECTION ERROR TEST
# ==========================================

def test_connection_error():

    print("\nTesting connection failure...")

    with patch.object(
        client,
        "OPENROUTER_API_KEY",
        "test-openrouter-key"
    ), patch.object(
        client,
        "GROQ_API_KEY",
        "test-groq-key"
    ), patch(
        "services.openrouter_client.requests.post",
        side_effect=[
            requests.exceptions.ConnectionError("Network unavailable"),
            requests.exceptions.ConnectionError("Network unavailable")
        ]
    ) as mock_post:

        try:

            client.send_chat_request(TEST_MESSAGES)

            print("FAIL: Expected connection error.")

        except RuntimeError as error:

            print("RESULT:", error)

            assert "connection failed" in str(error).lower()

            assert mock_post.call_count == 2

            print("PASS: Connection error handled correctly.")


# ==========================================
# 5. MAIN TEST EXECUTION
# ==========================================

if __name__ == "__main__":

    passed = 0

    total = 5

    tests = [

        lambda: test_http_error(
            401,
            "Unauthorized",
            "Invalid API key"
        ),

        lambda: test_http_error(
            429,
            "Too many requests",
            "Rate limit exceeded"
        ),

        lambda: test_http_error(
            503,
            "Service unavailable",
            "temporarily unavailable"
        ),

        test_timeout,

        test_connection_error

    ]

    print("=" * 55)

    print("LINGUAAI API ERROR HANDLING TESTS")

    print("=" * 55)

    for test in tests:

        try:

            test()

            passed += 1

        except Exception as error:

            print("\nFAIL:", error)

    print("\n" + "=" * 55)

    print(f"FINAL RESULT: {passed}/{total} TESTS PASSED")

    print("=" * 55)

    if passed == total:

        print("ALL API ERROR TESTS PASSED SUCCESSFULLY!")

    else:

        print("SOME TESTS FAILED. CHECK THE ERROR DETAILS.")
