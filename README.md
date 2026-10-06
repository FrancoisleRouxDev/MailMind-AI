# MailMind AI

MailMind AI is an intelligent, privacy-focused email management assistant available as a web application and cross-platform Electron desktop app. It connects to your inbox over secure IMAP, sanitizes sensitive Personal Identifiable Information (PII) on the client side, summarizes incoming threads, and drafts context-aware responses using high-performance inference APIs.

## Key Features

- **Multi-Provider LLM Engine**: Switch between Groq, NVIDIA NIM, and Google Gemini endpoints using OpenAI-compatible API standards.
- **Client-Side PII Redaction**: Regex sanitization strips email addresses, phone numbers, credit card numbers, and social security numbers before sending prompts to external APIs.
- **Automated Summarization**: Categorizes emails into Recruiting, Personal, or General buckets and provides concise two-sentence summaries.
- **Dual Response Drafting**: Generates both accepting/positive and polite declining/rescheduling options tailored to recruiters or personal contacts.
- **Data Persistence & Auth**: Secure account management using Firebase Authentication and encrypted draft storage via Firebase Firestore.
- **Hybrid Architecture**: Runs in standard web browsers or packages into a native desktop window via Electron.

## Tech Stack

- **Desktop Runtime**: Electron
- **Frontend**: Modern JavaScript (ES6+), HTML5, Tailwind CSS / Custom Components
- **Backend Service**: Python 3.10+ (using `imaplib`, `email`, `openai` SDK)
- **Database & Auth**: Firebase Auth, Google Cloud Firestore
- **AI Models Supported**: Llama 3.3 70B (Groq), Llama 3.1 70B (NVIDIA NIM), Gemini 2.5/3 Flash

## Architecture Overview

1. **Client Layer**: Electron / Web UI captures user preferences and manages API keys securely in local application context.
2. **Sanitization Engine**: Raw email payloads pass through local PII scrubbing prior to LLM submission.
3. **Inference Pipeline**: Cleaned text is submitted via HTTPS to the selected provider (Groq/NVIDIA/Gemini).
4. **Data Sync**: Generated drafts and custom options persist strictly to the authenticated user's Firestore path (`/users/{uid}/drafts`).

## Getting Started

### Prerequisites

- Node.js (v18.0.0 or higher)
- Python 3.10 or higher
- An email provider account with IMAP enabled and an App Password generated (e.g., Gmail 2FA App Password)
- Free API Key from Groq Console, NVIDIA NIM, or Google AI Studio

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/mailmind-ai.git](https://github.com/your-username/mailmind-ai.git)
   cd mailmind-ai

    Install Node.js dependencies for Electron:
    Bash

    npm install

    Install Python dependencies for the backend engine:
    Bash

    pip install -r requirements.txt

    Environment Configuration:
    Create a .env file in the root directory and add your credentials:
    Code snippet

    GROQ_API_KEY=your_groq_api_key_here
    NVIDIA_API_KEY=your_nvidia_api_key_here
    GEMINI_API_KEY=your_gemini_api_key_here
    FIREBASE_API_KEY=your_firebase_key
    FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
    FIREBASE_PROJECT_ID=your_project_id

Development Execution
Web Mode

To start the application server locally in a web browser:
Bash

python app.py

Electron Desktop Mode

To execute the application as a desktop app:
Bash

npm start

Packaging Desktop Releases

To build executable binaries for Windows, macOS, or Linux using Electron Builder:
Bash

# Build for current platform
npm run dist

# Target specific platforms
npm run dist -- --win
npm run dist -- --mac
npm run dist -- --linux

Output binaries will be compiled in the dist/ folder.
Security & Privacy Standards

    Zero-Trust Token Transmission: Credentials and app passwords are held in session memory or system keychains; raw email credentials are never saved to cloud databases.

    Data Minimization: The application truncates message bodies to limits required for analysis, minimizing exposure.

    Data Erasure: Users can trigger full database purges directly from the embedded Privacy Center.

Contributing

Contributions are welcome. Please open an issue to discuss proposed changes or features before submitting pull requests.

    Fork the Project

    Create your Feature Branch (git checkout -b feature/NewFeature)

    Commit your Changes (git commit -m 'Add NewFeature')

    Push to the Branch (git push origin feature/NewFeature)

    Open a Pull Request

License

Distributed under the MIT License. See LICENSE for more information.
