
const historyList = document.getElementById("historyList");
const historyStatus = document.getElementById("historyStatus");
const deleteButton = document.getElementById("deleteHistoryButton");

// Remove unwanted tags from old translation records.
function cleanText(text) {
    return String(text || "")
        .replace(/<\/?text\s*>/gi, "")
        .trim();
}

// Load translation history.
async function loadHistory() {
    try {
        const response = await fetch("/history");

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to load history.");
        }

        historyList.innerHTML = "";

        if (data.history.length === 0) {
            historyStatus.textContent = "No translation history found.";
            return;
        }

        historyStatus.textContent =
            `Total translations: ${data.total_records}`;

        data.history.forEach((item) => {
            const card = document.createElement("div");
            card.className = "history-card";

            const heading = document.createElement("h3");
            heading.textContent =
                `${item.source_language} → ${item.target_language}`;

            const original = document.createElement("p");
            original.textContent =
                `Original: ${cleanText(item.original_text)}`;

            const translated = document.createElement("p");
            translated.textContent =
                `Translation: ${cleanText(item.translated_text)}`;

            const date = document.createElement("small");
            date.textContent = `Date: ${item.created_at}`;

            card.append(heading, original, translated, date);
            historyList.appendChild(card);
        });

    } catch (error) {
        historyStatus.textContent = error.message;
    }
}

// Delete history only after user confirmation.
deleteButton.addEventListener("click", async () => {
    const confirmed = confirm(
        "Are you sure you want to delete all your translation history?"
    );

    if (!confirmed) return;

    try {
        const response = await fetch("/history/delete", {
            method: "POST"
        });

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to delete history.");
        }

        alert(data.message);
        loadHistory();

    } catch (error) {
        alert(error.message);
    }
});

// Load history when the page opens.
loadHistory();
