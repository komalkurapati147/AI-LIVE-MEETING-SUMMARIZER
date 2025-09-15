\# AI Live Meeting Summarizer — Zero Day Architecture



\*\*Overall Flow\*\*

Audio Capture → Speech-to-Text (STT) → Diarization → Summarization → UI → Export



\### Components

\- \*\*Audio Input:\*\* Mic recording (16 kHz mono WAV, Step 6 tested)

\- \*\*STT (Speech-to-Text):\*\* Vosk / Whisper (Day 1–2)

\- \*\*Diarization:\*\* Pyannote for speaker separation (Day 3)

\- \*\*Summarization:\*\* Transformer summarizer (Day 4)

\- \*\*UI:\*\* Streamlit app (already running, Step 7)

\- \*\*Exports:\*\* Markdown, PDF, Email (Day 7)



\### Data Flow

1\. Record audio from mic (backend/record\_wav.py)  

2\. Save to `recordings/`  

3\. Process through STT → transcript  

4\. Diarization → speaker-attributed transcript  

5\. Summarization → structured notes  

6\. Streamlit UI displays results, export to PDF/Markdown, optional email.  



\### Folder Roles

\- `backend/` → processing code (recording, stt, diarize, summarizer, pipeline)

\- `app/` → Streamlit UI

\- `docs/` → project documentation

\- `recordings/` → raw meeting WAV files

\- `models/` → downloaded AI models (ignored by git)

\- `sessions/` → processed outputs, logs (ignored by git)



