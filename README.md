                            \# AI Live Meeting Summarizer

# AI Live Meeting Summarizer

This project integrates speech-to-text (using the Whisper model) with a large language model (Llama via Groq API) for abstractive summarization. It processes meeting audio to automatically generate both a full transcript and key meeting takeaways. The system is presented through a Streamlit web interface, handling audio input and displaying the AI-generated text outputs.

## What it Does

- Live Recording: Capture meeting audio directly from your browser using your microphone.
- File Upload: Process existing meeting recordings (supports .wav, .mp3, .m4a, .ogg).
- Accurate Transcription: Uses OpenAI's Whisper model (running locally) to convert speech to text.
- AI Summarization: Leverages the Groq API (running Llama 3.1) to create structured summaries highlighting key points, action items, and decisions.
- Multiple Export Options:
    - Download the full transcript and summary as a .txt file.
    - Download a formatted PDF report.
    - Send the summary and transcript directly via email (uses Gmail).

## Tech Stack

- Language: Python 3.9+
- Framework: Streamlit (for the web UI)
- Transcription: OpenAI Whisper (running locally)
- Summarization: Groq API (Llama 3.1 model)
- Audio Recording: streamlit-audiorec component
- PDF Generation: FPDF2
- Environment Management: python-dotenv

## Getting Started Locally

Want to run this on your own machine? Here’s how:

1.  Clone the Repo:
    ```bash
    git clone https://your-github-repo-url/ai-live-meeting-summarizer.git
    cd ai-live-meeting-summarizer
    ```
2.  Set up a Virtual Environment (Recommended):
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  Install Dependencies: Make sure you have Python 3.9+ and pip installed.
    ```bash
    pip install -r requirements.txt
    ```
4.  Install FFmpeg: Whisper needs FFmpeg. You'll need to install it separately on your system:
    - macOS (using Homebrew): `brew install ffmpeg`
    - Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
    - Windows: Download from the FFmpeg website, extract it, and add the `bin` folder to your system's PATH environment variable.
5.  Create .env File: Create a file named .env in the project root directory and add your secret keys:
    ```dotenv
    GROQ_API_KEY="your_groq_api_key_here"
    EMAIL_USER="your_gmail_address@gmail.com"
    EMAIL_PASS="your_16_digit_google_app_password"
    ```
    - Remember: Get the 16-digit App Password from your Google Account security settings (2-Step Verification must be enabled).
6.  (Optional) PDF Fonts: For the best-looking PDFs, download DejaVuSans.ttf and DejaVuSans-Bold.ttf and place them in the project root directory.
7.  Run the App:
    ```bash
    streamlit run streamlit_app.py
    ```
    The app should open automatically in your web browser!

## Project Journey & Milestones

This project evolved through several planned stages:

- Milestone 1: Getting Speech-to-Text Right
    - Initially explored different STT options like Vosk and Whisper.
    - Implemented and tested Whisper (running locally via `openai-whisper`) for robust transcription capabilities. This forms the core transcription engine in the current app.

- Milestone 2: Adding Summarization (and aiming for Diarization)
    - The plan was to integrate speaker diarization (identifying who spoke when) using tools like `pyannote.audio`. Note: Diarization is not yet implemented in this version – the transcript currently doesn't separate speakers automatically.
    - Focused on implementing the summarization engine. We evaluated option like Groq .
    - Integrated the Groq API with Llama 3.1 for fast and effective summarization, driven by custom prompts designed for meeting contexts.

- Milestone 3: Building the UI and Tying it Together
    - Developed the user interface using Streamlit, providing controls for recording and file uploads.
    - Integrated the Whisper transcription and Groq summarization steps into a processing pipeline triggered by user actions within the Streamlit app.
    - Ensured results (transcript, summary) are displayed clearly in tabs.

- Milestone 4: Finishing Touches - Exports & Polish
    - Added crucial export features: Download as .txt and formatted PDF.
    - Implemented the Email functionality using `smtplib` for sending results directly.
    - Refined the UI with custom styling for a better look and feel.

## How to Use the App

1.  Choose Your Input Method:
    - Record Live: Go to the "Record Live Meeting" tab, click the microphone icon to start, and click the stop icon when done.
    - Upload File: Go to the "Upload Meeting File" tab and select your pre-recorded audio file.
2.  Process: After recording or uploading, click the "Process Recording" or "Process Uploaded File" button.
3.  View Results: The app will transcribe and summarize the audio. The results will appear in the "Summary" and "Transcript" tabs below.
4.  Export: Go to the "Export" tab to download the results as a .txt or PDF file, or to email them.

## Future Ideas / Next Steps

Based on the original plan, here are some potential improvements:

- Speaker Diarization: Integrate `pyannote.audio` or a similar library to identify different speakers in the transcript.
- Real-time Streaming Transcription: Modify the app to show the transcript as you speak during live recording (this is significantly more complex and requires asynchronous processing).
- Improved Error Handling: Add more specific checks and user feedback for potential issues (e.g., long processing times, API errors).
- Model Selection: Allow users to choose different Whisper model sizes (trading speed for accuracy).
- Enhanced UI/UX: Further refine the visual design and user flow.

## Configuration

Remember to create a .env file in the root directory and add your GROQ_API_KEY, EMAIL_USER, and EMAIL_PASS (the 16-digit Google App Password) for the summarization and email features to work.

---

