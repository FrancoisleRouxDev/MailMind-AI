const BACKEND_URL = "http://127.0.0.1:5000";

// --- 1. Main Inbox Fetching & AI Analysis ---
document.getElementById("btnFetch").addEventListener("click", async () => {
    const email = document.getElementById("emailUser").value;
    const app_password = document.getElementById("appPass").value;
    const imap_server = document.getElementById("imapServer").value;
    const provider = document.getElementById("aiProvider").value;
    const redact_pii = document.getElementById("togglePII").checked;

    const statusEl = document.getElementById("statusIndicator");
    const feedEl = document.getElementById("resultsFeed");

    if (!email || !app_password) {
        alert("Please provide both email address and app password.");
        return;
    }

    statusEl.innerText = "Fetching emails...";
    feedEl.innerHTML = "<div class='empty-state'>Connecting to mailbox...</div>";

    try {
        // Fetch Emails
        const fetchRes = await fetch(`${BACKEND_URL}/api/emails/fetch`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, app_password, imap_server, limit: 3 })
        });
        const fetchResult = await fetchRes.json();

        if (!fetchRes.ok || !fetchResult.success) {
            statusEl.innerText = "Error fetching emails";
            feedEl.innerHTML = `<div class='empty-state'>Error: ${fetchResult.error || 'Failed to fetch emails.'}</div>`;
            return;
        }

        feedEl.innerHTML = "";
        statusEl.innerText = "Analyzing emails with AI...";

        // Process each email
        for (const msg of fetchResult.emails) {
            const aiRes = await fetch(`${BACKEND_URL}/api/ai/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: msg, provider, redact_pii })
            });
            const aiResult = await aiRes.json();

            const contentHtml = aiRes.ok && aiResult.success
                ? aiResult.analysis
                : `<span style="color: #f87171; font-weight: 500;">⚠️ ${aiResult.error || 'Error processing email.'}</span>`;

            const card = document.createElement("div");
            card.className = "email-card";
            card.innerHTML = `
                <h3>${msg.subject}</h3>
                <div class="sender">From: ${msg.sender}</div>
                <div class="ai-body">${contentHtml}</div>
            `;
            feedEl.appendChild(card);
        }

        statusEl.innerText = "Complete";
    } catch (err) {
        statusEl.innerText = "Connection Failed";
        feedEl.innerHTML = `<div class='empty-state'>Could not connect to backend server. Make sure Python backend is running at ${BACKEND_URL}</div>`;
    }
});

// --- 2. App Password Helper Modal Logic ---
const modal = document.getElementById("appPassModal");
const btnHelp = document.getElementById("btnHelpAppPass");
const btnClose = document.getElementById("btnCloseModal");

btnHelp.addEventListener("click", () => modal.classList.remove("hidden"));
btnClose.addEventListener("click", () => modal.classList.add("hidden"));
window.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.add("hidden");
});