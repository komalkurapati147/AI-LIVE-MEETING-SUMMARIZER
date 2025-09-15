\# AI Live Meeting Summarizer



This project captures live meeting audio, transcribes it in real time, diarizes speakers, and produces structured summaries (decisions, action items, key points).



\## ✅ Current Progress (Zero Day)

\- Environment set up (venv, pip upgraded)

\- Git repo initialized correctly

\- FFmpeg installed

\- Base Python dependencies installed

\- `.env` created \& ignored in git

\- Microphone recording tested (`backend/record\_wav.py`)

\- Streamlit stub app created (`app/app.py`)

\- Architecture doc drafted (`docs/architecture.md`)



\## 📅 Next Steps

\- \*\*Day 1\*\* — Add STT engine (Vosk / Whisper)

\- \*\*Day 2\*\* — Evaluate STT performance (WER)

\- \*\*Day 3\*\* — Add diarization

\- \*\*Day 4\*\* — Summarization pipeline

\- \*\*Day 5+\*\* — Integrate backend, UI, exports, evaluation



\## Project Structure



meeting-summarizer/

├─ app/ # Streamlit UI

├─ backend/ # Audio + NLP pipeline

├─ docs/ # Documentation

├─ models/ # AI models (ignored in git)

├─ recordings/ # Recorded WAVs

├─ sessions/ # Session outputs (ignored in git)

├─ tests/ # Unit tests

├─ .env # Secrets (ignored in git)

├─ .gitignore

├─ README.md

└─ requirements.txt

