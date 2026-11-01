
// ==========================================
// LINGUAAI - SMART LANGUAGE TRANSLATOR
// Frontend JavaScript
// ==========================================


// ==========================================
// 1. GET HTML ELEMENTS
// ==========================================

const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");

const sourceLanguage = document.getElementById("sourceLanguage");
const targetLanguage = document.getElementById("targetLanguage");

const translateButton = document.getElementById("translateButton");
const buttonText = document.getElementById("buttonText");

const clearButton = document.getElementById("clearButton");
const copyButton = document.getElementById("copyButton");
const downloadButton = document.getElementById("downloadButton");
const swapButton = document.getElementById("swapButton");

const characterCount = document.getElementById("characterCount");
const outputCount = document.getElementById("outputCount");

const errorMessage = document.getElementById("errorMessage");

// Text-to-Speech elements
const speakButton = document.getElementById("speakButton");
const pauseButton = document.getElementById("pauseButton");
const resumeButton = document.getElementById("resumeButton");
const stopButton = document.getElementById("stopButton");

const MAX_CHARACTERS = 5000;


// ==========================================
// 2. CHARACTER COUNTER
// ==========================================

function updateCharacterCount() {

    characterCount.textContent =
        `${inputText.value.length} / ${MAX_CHARACTERS} characters`;

    outputCount.textContent =
        `${getTranslatedText().length} characters`;
}


inputText.addEventListener("input", function () {

    if (inputText.value.length > MAX_CHARACTERS) {

        inputText.value = inputText.value.substring(
            0,
            MAX_CHARACTERS
        );
    }

    updateCharacterCount();
});


// ==========================================
// 3. ERROR HANDLING
// ==========================================

function showError(message) {

    errorMessage.textContent = message;
    errorMessage.hidden = false;
}


function hideError() {

    errorMessage.textContent = "";
    errorMessage.hidden = true;
}


// ==========================================
// 4. FRIENDLY ERROR MESSAGES
// ==========================================

function getFriendlyErrorMessage(error) {

    const message = (error.message || "").toLowerCase();

    if (message.includes("invalid api key")) {
        return "API configuration error. Please contact support.";
    }

    if (
        message.includes("insufficient credits") ||
        message.includes("payment required")
    ) {
        return "Translation service requires credits. Please try again later.";
    }

    if (
        message.includes("rate limit") ||
        message.includes("too many requests")
    ) {
        return "Too many requests. Please wait and try again.";
    }

    if (
        message.includes("timed out") ||
        message.includes("timeout")
    ) {
        return "Translation is taking too long. Please try again.";
    }

    if (
        message.includes("unable to connect") ||
        message.includes("failed to fetch") ||
        message.includes("network")
    ) {
        return "Connection lost. Please check your internet.";
    }

    if (
        message.includes("temporarily unavailable") ||
        message.includes("service unavailable")
    ) {
        return "Translation service is temporarily unavailable.";
    }

    return error.message || "Something went wrong. Please try again.";
}


// ==========================================
// 5. GET TRANSLATED TEXT
// ==========================================

function getTranslatedText() {

    const placeholder =
        outputText.querySelector(".placeholder-text");

    if (placeholder) {
        return "";
    }

    return outputText.textContent.trim();
}


// ==========================================
// 6. TEXT-TO-SPEECH INITIALIZATION
// ==========================================

const speechSupported =
    "speechSynthesis" in window &&
    "SpeechSynthesisUtterance" in window;

let currentUtterance = null;

let speechState = "idle";

let speechSessionId = 0;


// ==========================================
// 7. UPDATE BUTTON STATES
// ==========================================

function updateSpeechButtons() {

    const hasText = Boolean(getTranslatedText());

    // Download works independently of speech support
    downloadButton.disabled = !hasText;

    if (!speechSupported) {

        speakButton.disabled = true;
        pauseButton.disabled = true;
        resumeButton.disabled = true;
        stopButton.disabled = true;

        return;
    }

    speakButton.disabled = !hasText;

    pauseButton.disabled =
        speechState !== "speaking";

    resumeButton.disabled =
        speechState !== "paused";

    stopButton.disabled =
        speechState === "idle";
}


// ==========================================
// 8. LANGUAGE CODE MAPPING - 25 LANGUAGES
// ==========================================

const speechLanguageCodes = {

    "English": "en-US",
    "Hindi": "hi-IN",
    "French": "fr-FR",
    "Spanish": "es-ES",
    "German": "de-DE",
    "Italian": "it-IT",
    "Portuguese": "pt-PT",
    "Russian": "ru-RU",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Chinese": "zh-CN",
    "Arabic": "ar-SA",
    "Bengali": "bn-IN",
    "Urdu": "ur-PK",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN",
    "Dutch": "nl-NL",
    "Turkish": "tr-TR",
    "Polish": "pl-PL",
    "Ukrainian": "uk-UA",
    "Vietnamese": "vi-VN",
    "Thai": "th-TH"

};


// ==========================================
// 9. SELECT LANGUAGE VOICE
// ==========================================

function getLanguageVoice(languageCode) {

    const voices = window.speechSynthesis.getVoices();

    if (!voices.length) {
        return null;
    }

    let voice = voices.find(item =>
        item.lang.toLowerCase() === languageCode.toLowerCase()
    );

    if (!voice) {

        const mainLanguage =
            languageCode.split("-")[0].toLowerCase();

        voice = voices.find(item =>
            item.lang.toLowerCase().split("-")[0] === mainLanguage
        );
    }

    return voice || null;
}


// ==========================================
// 10. RESET / STOP SPEECH
// ==========================================

function stopSpeech() {

    if (!speechSupported) {
        return;
    }

    speechSessionId++;

    speechState = "idle";

    currentUtterance = null;

    window.speechSynthesis.cancel();

    updateSpeechButtons();
}


// ==========================================
// 11. LISTEN TO TRANSLATED TEXT
// ==========================================

speakButton.addEventListener("click", function () {

    if (!speechSupported) {

        showError(
            "Your browser does not support text-to-speech."
        );

        return;
    }

    const translatedText = getTranslatedText();

    if (!translatedText) {

        showError(
            "Please translate some text before listening."
        );

        return;
    }

    stopSpeech();

    const thisSession = speechSessionId;

    const selectedLanguage = targetLanguage.value;

    const languageCode =
        speechLanguageCodes[selectedLanguage] || "en-US";

    const utterance =
        new SpeechSynthesisUtterance(translatedText);

    currentUtterance = utterance;

    utterance.lang = languageCode;
    utterance.rate = 1;
    utterance.pitch = 1;

    const selectedVoice = getLanguageVoice(languageCode);

    if (selectedVoice) {
        utterance.voice = selectedVoice;
    }

    utterance.onstart = function () {

        if (thisSession !== speechSessionId) return;

        speechState = "speaking";

        updateSpeechButtons();
    };

    utterance.onpause = function () {

        if (thisSession !== speechSessionId) return;

        speechState = "paused";

        updateSpeechButtons();
    };

    utterance.onresume = function () {

        if (thisSession !== speechSessionId) return;

        speechState = "speaking";

        updateSpeechButtons();
    };

    utterance.onend = function () {

        if (thisSession !== speechSessionId) return;

        speechState = "idle";

        currentUtterance = null;

        updateSpeechButtons();
    };

    utterance.onerror = function (event) {

        if (thisSession !== speechSessionId) return;

        speechState = "idle";

        currentUtterance = null;

        updateSpeechButtons();

        if (
            event.error !== "canceled" &&
            event.error !== "interrupted"
        ) {

            showError(
                "Unable to play audio. Please try again."
            );
        }
    };

    hideError();

    speechState = "speaking";

    updateSpeechButtons();

    try {

        window.speechSynthesis.speak(utterance);

    } catch (error) {

        stopSpeech();

        showError(
            "Unable to start speech. Please try again."
        );
    }

});


// ==========================================
// 12. PAUSE SPEECH
// ==========================================

pauseButton.addEventListener("click", function () {

    if (
        !speechSupported ||
        speechState !== "speaking"
    ) {
        return;
    }

    window.speechSynthesis.pause();

    speechState = "paused";

    updateSpeechButtons();
});


// ==========================================
// 13. RESUME SPEECH
// ==========================================

resumeButton.addEventListener("click", function () {

    if (
        !speechSupported ||
        speechState !== "paused"
    ) {
        return;
    }

    window.speechSynthesis.resume();

    speechState = "speaking";

    updateSpeechButtons();
});


// ==========================================
// 14. STOP SPEECH BUTTON
// ==========================================

stopButton.addEventListener("click", function () {

    stopSpeech();

});


// ==========================================
// 15. CLEAR INPUT AND OUTPUT
// ==========================================

clearButton.addEventListener("click", function () {

    stopSpeech();

    stopVoiceInput();

    inputText.value = "";

    outputText.textContent = "";

    const detectedLanguageElement =
        document.getElementById("detectedLanguage");

    if (detectedLanguageElement) {
        detectedLanguageElement.hidden = true;
    }

    updateCharacterCount();

    hideError();

    updateSpeechButtons();
});


// ==========================================
// 16. COPY TRANSLATED TEXT
// ==========================================

copyButton.addEventListener("click", async function () {

    const translatedText = getTranslatedText();

    if (!translatedText) {

        showError("There is no translated text to copy.");

        return;
    }

    try {

        await navigator.clipboard.writeText(translatedText);

        hideError();

    } catch (error) {

        showError(
            "Unable to copy text. Please copy it manually."
        );
    }

});


// ==========================================
// 17. DOWNLOAD TRANSLATED TEXT
// ==========================================

downloadButton.addEventListener("click", function () {

    const translatedText = getTranslatedText();

    if (!translatedText) {

        showError(
            "There is no translated text to download."
        );

        return;
    }

    const selectedLanguage = targetLanguage.value;

    const fileContent =
        `LinguaAI - Translation\n\n` +
        `Target Language: ${selectedLanguage}\n\n` +
        `Translated Text:\n${translatedText}`;

    const blob = new Blob(
        [fileContent],
        { type: "text/plain;charset=utf-8" }
    );

    const downloadURL = URL.createObjectURL(blob);

    const downloadLink = document.createElement("a");

    downloadLink.href = downloadURL;

    downloadLink.download =
        `LinguaAI_Translation_${selectedLanguage}.txt`;

    document.body.appendChild(downloadLink);

    downloadLink.click();

    document.body.removeChild(downloadLink);

    setTimeout(function () {
        URL.revokeObjectURL(downloadURL);
    }, 1000);

    hideError();

});


// ==========================================
// 18. SWAP LANGUAGES
// ==========================================

swapButton.addEventListener("click", function () {

    const source = sourceLanguage.value;

    const target = targetLanguage.value;

    if (source.toLowerCase() === "auto") {

        showError(
            "Please select a source language before swapping."
        );

        return;
    }

    stopSpeech();

    stopVoiceInput();

    sourceLanguage.value = target;

    targetLanguage.value = source;

    const originalText = inputText.value;

    inputText.value = getTranslatedText();

    outputText.textContent = originalText;

    const detectedLanguageElement =
        document.getElementById("detectedLanguage");

    if (detectedLanguageElement) {
        detectedLanguageElement.hidden = true;
    }

    updateCharacterCount();

    updateSpeechButtons();

    hideError();
});


// ==========================================
// 19. LOADING STATE
// ==========================================

function startLoading() {

    translateButton.disabled = true;

    buttonText.textContent = "Translating...";
}


function stopLoading() {

    translateButton.disabled = false;

    buttonText.textContent = "Translate Now";
}


// ==========================================
// 20. TRANSLATION FUNCTION
// ==========================================

translateButton.addEventListener("click", async function () {

    const text = inputText.value.trim();

    const source = sourceLanguage.value;

    const target = targetLanguage.value;

    // Empty input validation
    if (!text) {

        showError("Please enter some text to translate.");

        outputText.textContent = "";

        stopSpeech();

        updateCharacterCount();

        return;
    }

    // Character limit validation
    if (inputText.value.length > MAX_CHARACTERS) {

        showError("Text cannot exceed 5000 characters.");

        return;
    }

    // Language validation
    if (!source || !target) {

        showError("Please select both languages.");

        return;
    }

    // Same language validation
    if (
        source.toLowerCase() !== "auto" &&
        source.toLowerCase() === target.toLowerCase()
    ) {

        showError(
            "Source and target languages must be different."
        );

        return;
    }

    hideError();

    stopSpeech();

    startLoading();

    try {

        const response = await fetch("/translate", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                text: text,

                source_language: source,

                target_language: target

            })

        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.error || "Translation request failed."
            );
        }

        if (
            !data.translated_text ||
            typeof data.translated_text !== "string"
        ) {

            throw new Error(
                "The translation service returned an empty response."
            );
        }

        // Display translated text
        outputText.textContent = data.translated_text;

        // Display detected language
        let detectedLanguageElement =
            document.getElementById("detectedLanguage");

        if (!detectedLanguageElement) {

            detectedLanguageElement =
                document.createElement("p");

            detectedLanguageElement.id = "detectedLanguage";

            detectedLanguageElement.className = "detected-language";

            outputText.parentElement.insertBefore(
                detectedLanguageElement,
                outputText
            );
        }

        if (source === "auto") {

            detectedLanguageElement.textContent =
                `Language detected: ${data.detected_language}`;

            detectedLanguageElement.hidden = false;

        } else {

            detectedLanguageElement.hidden = true;
        }

        updateCharacterCount();

        updateSpeechButtons();

        hideError();

    } catch (error) {

        outputText.textContent = "";

        updateCharacterCount();

        stopSpeech();

        showError(getFriendlyErrorMessage(error));

    } finally {

        stopLoading();
    }

});


// ==========================================
// 21. SPEECH-TO-TEXT (VOICE INPUT)
// ==========================================

const voiceInputButton = document.getElementById("voiceInputButton");
const voiceInputStatus = document.getElementById("voiceInputStatus");

const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

const voiceInputSupported = Boolean(SpeechRecognition);
let recognition = null;
let isVoiceInputActive = false;


// ==========================================
// 22. VOICE INPUT LANGUAGE CODES
// 25 LANGUAGES
// ==========================================

const recognitionLanguageCodes = {

    "English": "en-US",
    "Hindi": "hi-IN",
    "French": "fr-FR",
    "Spanish": "es-ES",
    "German": "de-DE",
    "Italian": "it-IT",
    "Portuguese": "pt-PT",
    "Russian": "ru-RU",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Chinese": "zh-CN",
    "Arabic": "ar-SA",
    "Bengali": "bn-IN",
    "Urdu": "ur-PK",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN",
    "Dutch": "nl-NL",
    "Turkish": "tr-TR",
    "Polish": "pl-PL",
    "Ukrainian": "uk-UA",
    "Vietnamese": "vi-VN",
    "Thai": "th-TH"

};


function setVoiceInputState(active, message) {

    isVoiceInputActive = active;

    voiceInputButton.textContent = active
        ? "⏹ Stop Voice Input"
        : "🎤 Start Voice Input";

    voiceInputButton.setAttribute(
        "aria-pressed",
        String(active)
    );

    voiceInputStatus.textContent = message || "";
}


function stopVoiceInput() {

    if (recognition && isVoiceInputActive) {

        recognition.stop();

    } else {

        setVoiceInputState(false, "");
    }
}


function startVoiceInput() {

    if (!voiceInputSupported) {

        showError(
            "Voice input is not supported in this browser. Please use the latest Google Chrome."
        );

        return;
    }

    if (!window.isSecureContext) {

        showError(
            "Microphone access requires a secure connection. Use localhost or HTTPS."
        );

        return;
    }

    hideError();

    recognition = new SpeechRecognition();

    recognition.continuous = false;

    recognition.interimResults = false;

    const selectedSourceLanguage = sourceLanguage.value;

    recognition.lang =
        recognitionLanguageCodes[selectedSourceLanguage] || "en-US";


    recognition.onstart = function () {

        setVoiceInputState(
            true,
            "Listening... Speak now."
        );
    };


    recognition.onresult = function (event) {

        const transcript =
            event.results[0][0].transcript.trim();

        if (!transcript) {

            setVoiceInputState(
                false,
                "No speech detected. Try again."
            );

            return;
        }

        const separator =
            inputText.value.trim() ? " " : "";

        inputText.value = (
            inputText.value +
            separator +
            transcript
        ).slice(0, MAX_CHARACTERS);

        updateCharacterCount();

        setVoiceInputState(
            false,
            "Voice input added."
        );
    };


    recognition.onerror = function (event) {

        setVoiceInputState(false, "");

        const messages = {

            "not-allowed":
                "Microphone permission was denied. Allow microphone access in your browser.",

            "audio-capture":
                "No microphone was found. Check your microphone connection.",

            "no-speech":
                "No speech detected. Please try speaking again.",

            "network":
                "Voice recognition needs an internet connection. Check your connection."

        };

        showError(
            messages[event.error] ||
            "Voice input failed. Please try again."
        );
    };


    recognition.onend = function () {

        if (isVoiceInputActive) {

            setVoiceInputState(
                false,
                "Voice input stopped."
            );
        }
    };


    try {

        recognition.start();

    } catch (error) {

        setVoiceInputState(false, "");

        showError(
            "Unable to start voice input. Please try again."
        );
    }
}


// ==========================================
// 23. VOICE INPUT BUTTON EVENT
// ==========================================

voiceInputButton.addEventListener("click", function () {

    if (!voiceInputSupported) {

        startVoiceInput();

        return;
    }

    if (isVoiceInputActive) {

        stopVoiceInput();

    } else {

        startVoiceInput();
    }
});


if (!voiceInputSupported) {

    voiceInputButton.title =
        "Voice input is not supported by this browser.";
}


// ==========================================
// 24. BROWSER VOICE INITIALIZATION
// ==========================================

if (speechSupported) {

    window.speechSynthesis.onvoiceschanged = function () {

        updateSpeechButtons();

    };
}


// ==========================================
// 25. INITIALIZE APPLICATION
// ==========================================

function initializeApp() {

    updateCharacterCount();

    hideError();

    stopLoading();

    updateSpeechButtons();

    if (!voiceInputSupported) {

        setVoiceInputState(
            false,
            "Voice input is unavailable in this browser."
        );

    } else {

        setVoiceInputState(false, "");
    }

    console.log(
        "LinguaAI frontend initialized successfully."
    );
}


initializeApp();
