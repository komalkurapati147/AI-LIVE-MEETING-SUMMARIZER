import streamlit as st
from dotenv import load_dotenv
import time
import os
import smtplib
import ssl
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import logging
import whisper
from groq import Groq
from st_audiorec import st_audiorec

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Page Configuration ---
st.set_page_config(
    page_title="Meeting Genie",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* --- Base & Layout --- */
    :root {
        --rainbow-1: #ff0000; --rainbow-2: #ff7f00; --rainbow-3: #ffff00;
        --rainbow-4: #00ff00; --rainbow-5: #0000ff; --rainbow-6: #4b0082;
        --rainbow-7: #9400d3;
        --button-grad-1: #00c6ff; --button-grad-2: #0072ff;
        --button-hover-1: #0072ff; --button-hover-2: #0050e0;
        --accent-color: #1abc9c; --accent-color-darker: #16a085;
        --text-color-light: #ffffff; --text-color-dark: #2c3e50;
        --bg-color-light: #f8f9fa; --bg-color-medium: #ffffff;
        --bg-color-darker: #e9ecef; --border-radius: 10px;
        --box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        --box-shadow-inset: inset 0 1px 3px rgba(0,0,0,0.06);
    }
    body { color: var(--text-color-dark); background-color: var(--bg-color-light); }
    .main .block-container {
        padding: 2rem 3rem 3rem 3rem; background-color: var(--bg-color-medium);
        border-radius: var(--border-radius); box-shadow: var(--box-shadow);
        max-width: 1200px; margin: 1rem auto;
    }
    h1 {
        background: linear-gradient(90deg, var(--rainbow-1), var(--rainbow-2), var(--rainbow-3), var(--rainbow-4), var(--rainbow-5), var(--rainbow-6), var(--rainbow-7));
        -webkit-background-clip: text; color: transparent; text-align: center;
        padding-bottom: 1.5rem; font-weight: 700; margin-top: 0; font-size: 2.8rem;
    }
    h2, h3, h4, h5 { color: #1e3a5f; margin-top: 1.8rem; margin-bottom: 0.8rem; font-weight: 600; }
    h3 { font-size: 1.6rem; } h4 { font-size: 1.3rem; } h5 { font-size: 1.1rem; color: #555; margin-top: 1.2rem;}
    .stButton > button {
        border: none; border-radius: 20px; padding: 0.7rem 1.6rem; color: var(--text-color-light);
        background: linear-gradient(45deg, var(--button-grad-1), var(--button-grad-2));
        box-shadow: 0 3px 8px rgba(0,0,0,0.15); transition: transform 0.2s ease, box-shadow 0.2s ease;
        font-weight: 500; font-size: 0.95rem;
    }
    .stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 5px 12px rgba(0,0,0,0.2); color: var(--text-color-light);
        background: linear-gradient(45deg, var(--button-hover-1), var(--button-hover-2));
    }
    .stButton > button:disabled { background: var(--bg-color-darker); color: #95a5a6; box-shadow: none; transform: none; cursor: not-allowed; }
    div[data-testid="stDownloadButton"] > button { background: linear-gradient(45deg, var(--accent-color), var(--accent-color-darker)); }
    div[data-testid="stDownloadButton"] > button:hover { background: linear-gradient(45deg, var(--accent-color-darker), var(--accent-color)); color: var(--text-color-light); }
    [data-baseweb="tab-list"] { gap: 1.5rem; border-bottom: 1px solid var(--bg-color-darker); padding-bottom: 0; margin-bottom: 1.5rem; }
    div[data-testid="stTabs"] > div:first-child > [data-baseweb="tab-list"] { justify-content: center; }
    [data-baseweb="tab"] {
        height: 45px; background-color: transparent; border-radius: 0; border-bottom: 3px solid transparent;
        padding: 0.4rem 1rem; color: #666; transition: color 0.3s ease, border-bottom-color 0.3s ease;
        font-weight: 500; font-size: 1.05rem;
    }
    [data-baseweb="tab"]:hover { color: var(--button-grad-2); }
    [aria-selected="true"] { color: var(--button-grad-2); border-bottom: 3px solid var(--button-grad-2); }
    div.stTabs [data-baseweb="tab-list"] { justify-content: flex-start; font-size: 1rem; color: #444; }
    div.stTabs [aria-selected="true"] { color: var(--button-grad-2); border-bottom-color: var(--button-grad-2); }
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="element-container"] { border-top: none; padding-top: 1.5rem; }
    .stAlert { border-radius: var(--border-radius); border: 1px solid var(--bg-color-darker); box-shadow: none; }
    .stAudioRec, [data-testid="stFileUploader"] {
        background-color: var(--bg-color-light); border-radius: var(--border-radius); padding: 1.5rem;
        box-shadow: var(--box-shadow-inset); border: 1px solid var(--bg-color-darker);
    }
    .stTextArea textarea, .stTextInput input { border-radius: var(--border-radius); border: 1px solid #ccc; background-color: #ffffff; }
    [data-testid="stSpinner"] > div { border-top-color: var(--button-grad-2); border-right-color: var(--button-grad-2); }
</style>
""", unsafe_allow_html=True)

# --- AI Model Loading ---
@st.cache_resource
def load_whisper_model():
    try:
        model = whisper.load_model("base")
        logging.info("Whisper model loaded.")
        return model
    except Exception as e:
        st.error(f"Error loading Whisper model: {e}. Ensure ffmpeg is installed.")
        logging.error(f"Whisper load error: {e}", exc_info=True)
        return None

# --- Core AI Functions ---
@st.cache_data
def transcribe_audio(_model, audio_path):
    if _model is None: return None
    if not os.path.exists(audio_path):
        st.error(f"Audio file not found: {audio_path}")
        return None
    try:
        logging.info(f"Starting English transcription for: {audio_path}")
        result = _model.transcribe(audio_path, language="en", fp16=False)
        logging.info(f"Transcription successful for: {audio_path}")
        return result["text"]
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        logging.error(f"Transcription error: {e}", exc_info=True)
        return None

@st.cache_data
def summarize_transcript(transcript_text):
    if not transcript_text or not transcript_text.strip(): return None
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            st.error("GROQ_API_KEY environment variable not found. Check .env file.")
            return None
        client = Groq(api_key=groq_api_key)
        logging.info("Sending transcript to Groq for summarization...")
        prompt = f"""
        **Objective:** Generate a clear, concise, and structured meeting summary from the provided transcript in Markdown format.
        Include these sections *only if* relevant information exists in the transcript:
        * **Key Discussion Points:** Bulleted list (max 5-7 points).
        * **Action Items:** Bulleted list (e.g., "- Task assigned to [Person Name]"). State "No specific action items noted." if none.
        * **Decisions Made:** Bulleted list. State "No key decisions noted." if none.
        * **Open Questions/Concerns:** Bulleted list. State "No major open questions or concerns noted." if none.

        **Transcript:**
        ---
        {transcript_text}
        ---
        **Summary:**
        """
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional meeting summarization assistant. Provide concise and accurate summaries based *only* on the transcript."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.1-8b-instant", temperature=0.2, max_tokens=512,
        )
        summary = chat_completion.choices[0].message.content
        logging.info("Summarization successful.")
        return summary
    except Exception as e:
        st.error(f"Error during summarization with Groq: {e}")
        logging.error(f"Summarization error: {e}", exc_info=True)
        return None

# --- Export Functions ---
def send_email(recipient_email, summary_text, transcript_text):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    if not EMAIL_USER or not EMAIL_PASS:
        st.error("Email credentials (EMAIL_USER, EMAIL_PASS) not found in .env.")
        return False
    SMTP_SERVER = "smtp.gmail.com"; SMTP_PORT = 465
    subject = f"Meeting Summary - {time.strftime('%Y-%m-%d')}"
    body_summary = summary_text.replace("### ", "## ").replace("**", "*").replace("  -", "-")
    body = f"Hello,\n\nSummary and transcript from the meeting:\n\n--- SUMMARY ---\n{body_summary}\n\n--- FULL TRANSCRIPT ---\n{transcript_text}\n\nSent from Meeting Genie App"
    message = f"Subject: {subject}\n\n{body}".encode('utf-8')
    context = ssl.create_default_context()
    try:
        logging.info(f"Attempting to send email to {recipient_email}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, recipient_email, message)
        logging.info("Email sent successfully.")
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("Email Authentication Failed. Check EMAIL_USER and ensure EMAIL_PASS is the correct 16-digit Google App Password.")
        logging.error("SMTP Authentication Error.")
        return False
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        logging.error(f"Email sending error: {e}", exc_info=True)
        return False

@st.cache_data
def create_pdf(summary_text, transcript_text):
    pdf = FPDF()
    font_path_regular = "DejaVuSans.ttf"
    font_path_bold = "DejaVuSans-Bold.ttf"
    try:
        pdf.add_font("DejaVu", "", font_path_regular, uni=True)
        pdf.add_font("DejaVu", "B", font_path_bold, uni=True)
        font_family = "DejaVu"
    except FileNotFoundError:
        st.warning("DejaVu fonts not found. PDF using Arial. Place .ttf files in script directory for best results.")
        font_family = "Arial"
        logging.warning("DejaVu fonts not found, falling back to Arial for PDF.")

    # Summary Page
    pdf.add_page()
    pdf.set_font(font_family, "B", size=18)
    pdf.cell(0, 12, text="Meeting Summary", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    summary_lines = summary_text.replace("### ", "## ").split('\n')
    for line in summary_lines:
        line_stripped = line.strip()
        if line_stripped.startswith("## "):
            pdf.set_font(font_family, "B", size=13)
            pdf.multi_cell(0, 7, text=line_stripped.replace("## ", ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(1)
        elif line_stripped.startswith("* "):
            pdf.set_font(font_family, "", size=11)
            pdf.multi_cell(0, 6, text=f"  • {line_stripped[2:]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        elif line_stripped:
            pdf.set_font(font_family, "", size=11)
            pdf.multi_cell(0, 6, text=line_stripped, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else: pdf.ln(3)

    # Transcript Page
    pdf.add_page()
    pdf.set_font(font_family, "B", size=18)
    pdf.cell(0, 12, text="Full Transcript", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.set_font(font_family, "", size=9)
    pdf.multi_cell(0, 5, text=transcript_text)

    # Output as bytes
    try:
        pdf_bytes_output = pdf.output(dest='S')
        if isinstance(pdf_bytes_output, str):
             pdf_bytes_output = pdf_bytes_output.encode('latin-1')
        logging.info("PDF generated successfully.")
        return bytes(pdf_bytes_output) # Final conversion to bytes
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        logging.error(f"PDF generation error: {e}", exc_info=True)
        return None

# --- Main Audio Processing Logic ---
def process_audio_input(audio_input, input_type="bytes"):
    temp_audio_path = None
    st.session_state.transcript = None
    st.session_state.summary = None
    status_placeholder = st.empty()
    try:
        status_placeholder.info("Preparing audio...")
        if input_type == "bytes":
            if not audio_input: raise ValueError("No audio data from recording.")
            temp_audio_path = f"temp_recording_{int(time.time())}.wav"
            with open(temp_audio_path, "wb") as f: f.write(audio_input)
            audio_source_path = temp_audio_path
            logging.info(f"Saved recording to temp: {audio_source_path}")
        elif input_type == "filepath":
            if not audio_input or not os.path.exists(audio_input):
                 raise FileNotFoundError(f"Uploaded file path invalid: {audio_input}")
            audio_source_path = audio_input
            logging.info(f"Processing upload: {audio_source_path}")
        else: raise ValueError("Invalid input type for processing.")

        st.markdown("---"); st.subheader("Processing Status")

        status_placeholder.info("Loading Whisper model...")
        whisper_model = load_whisper_model()
        if not whisper_model: raise RuntimeError("Failed to load Whisper model.")

        status_placeholder.info("Transcribing audio...")
        transcript_result = transcribe_audio(whisper_model, audio_source_path)

        if transcript_result and transcript_result.strip():
            st.session_state.transcript = transcript_result
            status_placeholder.success("Transcription Complete!")
            logging.info("Transcription successful.")

            status_placeholder.info("Summarizing transcript...")
            summary_result = summarize_transcript(transcript_result)

            if summary_result:
                st.session_state.summary = summary_result
                status_placeholder.success("Summarization Complete!")
                logging.info("Summarization successful.")
                time.sleep(2.0); status_placeholder.empty()
            else:
                st.error("Summarization failed. Transcript is available below.")
                status_placeholder.warning("Summarization Failed. Displaying transcript only.")
        else:
            st.error("Transcription failed or audio was silent.")
            status_placeholder.error("Transcription Failed.")
            logging.warning(f"Transcription failed/empty for {audio_source_path}")

    except (FileNotFoundError, ValueError, RuntimeError) as known_error:
        st.error(str(known_error))
        logging.error(str(known_error))
        if 'status_placeholder' in locals(): status_placeholder.error("Processing error occurred.")
    except Exception as e:
         st.error(f"An unexpected error occurred: {e}")
         logging.error(f"General processing error: {e}", exc_info=True)
         st.session_state.transcript = None; st.session_state.summary = None
         if 'status_placeholder' in locals(): status_placeholder.error("Processing Failed Unexpectedly.")
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try: os.remove(temp_audio_path); logging.info(f"Removed temp file: {temp_audio_path}")
            except Exception as e: st.warning(f"Could not remove temp file {temp_audio_path}: {e}")

# --- Session State ---
if "summary" not in st.session_state: st.session_state.summary = None
if "transcript" not in st.session_state: st.session_state.transcript = None
if "current_audio_source" not in st.session_state: st.session_state.current_audio_source = None
if "temp_upload_path" not in st.session_state: st.session_state.temp_upload_path = None

# --- ==================== UI LAYOUT ==================== ---
st.title("AI LIVE MEETING SUMMARIZER")
st.caption("Record live, upload audio, get transcripts & summaries powered by Whisper and Groq.")
st.markdown("---")

tab_record, tab_upload = st.tabs(["Record Live Meeting", "Upload Meeting File"])

# --- Recording Tab ---
with tab_record:
    st.subheader("Record Directly")
    st.caption("Click the microphone icon to start, click the stop icon when finished.")
    wav_audio_data = st_audiorec()

    if wav_audio_data:
        st.audio(wav_audio_data, format='audio/wav')
        st.success("Recording ready!")
        col_dl_rec, col_proc_rec = st.columns([1, 2])
        with col_dl_rec:
            st.download_button(
                label="Download WAV", data=wav_audio_data,
                file_name=f"recording_{time.strftime('%Y%m%d_%H%M%S')}.wav",
                mime="audio/wav", key="download_rec_button"
            )
        with col_proc_rec:
            if st.button("Process Recording", key="process_recording_button"):
                st.session_state.current_audio_source = 'record'
                if st.session_state.temp_upload_path and os.path.exists(st.session_state.temp_upload_path):
                     try: os.remove(st.session_state.temp_upload_path); st.session_state.temp_upload_path = None
                     except Exception as e: logging.warning(f"Could not remove previous upload temp file: {e}")
                process_audio_input(wav_audio_data, input_type="bytes")

# --- Upload Tab ---
with tab_upload:
    st.subheader("Upload Existing Audio File")
    st.caption("Supports WAV, MP3, M4A, OGG formats.")
    uploaded_file = st.file_uploader(
        "Select your audio file:", type=["wav", "mp3", "m4a", "ogg"],
        key="file_uploader", label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Clean up previous temp file before saving new one
        if st.session_state.temp_upload_path and os.path.exists(st.session_state.temp_upload_path):
            try: os.remove(st.session_state.temp_upload_path); logging.info(f"Removed previous temp upload: {st.session_state.temp_upload_path}")
            except Exception as e: logging.warning(f"Could not remove previous temp upload: {e}")
            st.session_state.temp_upload_path = None # Clear state path regardless

        # Save new file
        temp_dir = "."
        unique_suffix = f"{int(time.time())}_{uploaded_file.name}"
        temp_path = os.path.join(temp_dir, f"uploaded_{unique_suffix}")
        try:
            with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
            st.session_state.temp_upload_path = temp_path # Store new path
            logging.info(f"Saved new upload temp: {temp_path}")

            st.audio(temp_path)
            if st.button("Process Uploaded File", key="process_upload_button"):
                st.session_state.current_audio_source = 'upload'
                process_audio_input(st.session_state.temp_upload_path, input_type="filepath")
                # Attempt cleanup after triggering process (will happen on next rerun if successful)

        except Exception as e:
             st.error(f"Error handling upload: {e}"); logging.error(f"File upload error: {e}", exc_info=True)
             if 'temp_path' in locals() and os.path.exists(temp_path): # Cleanup on error
                 try: os.remove(temp_path); logging.info(f"Cleaned temp upload on error: {temp_path}")
                 except: pass
             st.session_state.temp_upload_path = None


# --- Results Section ---
if st.session_state.summary and st.session_state.transcript:
    st.markdown("---"); st.header("Results")
    res_tab_summary, res_tab_transcript, res_tab_export = st.tabs(["Summary", "Transcript", "Export"])

    with res_tab_summary: st.markdown(st.session_state.summary)
    with res_tab_transcript: st.text_area("Full Transcript:", value=st.session_state.transcript, height=400, key="transcript_display_area")
    with res_tab_export:
        st.subheader("Export Options")
        col_dl_txt_res, col_dl_pdf_res = st.columns(2)
        with col_dl_txt_res:
            try:
                transcript_str = st.session_state.transcript or ""; summary_str = st.session_state.summary or ""
                clean_summary = summary_str.replace("### ", "").replace("**", "").replace("*", "  -")
                full_text_export = f"--- MEETING SUMMARY ---\n\n{clean_summary}\n\n\n--- FULL TRANSCRIPT ---\n\n{transcript_str}"
                st.download_button(
                    label="Download .txt File", data=full_text_export.encode('utf-8'),
                    file_name=f"Meeting_Summary_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain", use_container_width=True, key="download_txt_button"
                )
            except Exception as e: st.error(f"Error preparing .txt download: {e}"); logging.error(f".txt download error: {e}", exc_info=True)
        with col_dl_pdf_res:
            try:
                pdf_data = create_pdf(st.session_state.summary or "N/A", st.session_state.transcript or "N/A")
                if pdf_data:
                    st.download_button(
                        label="Download PDF File", data=pdf_data,
                        file_name=f"Meeting_Summary_{time.strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf", use_container_width=True, key="download_pdf_button"
                    )
                else: st.button("Download PDF File", disabled=True, use_container_width=True)
            except Exception as e: st.error(f"Error preparing PDF download: {e}"); logging.error(f"PDF download error: {e}", exc_info=True)

        st.markdown("---"); st.subheader("Email Results")
        recipient_email = st.text_input("Recipient's Email Address:", key="email_recipient_input_export")
        if st.button("Send Email", key="send_email_button_export"):
            if recipient_email:
                with st.spinner("Sending email..."):
                    success = send_email(recipient_email, st.session_state.summary or "N/A", st.session_state.transcript or "N/A")
                if success: st.toast("Email sent successfully!")
            else: st.warning("Please enter a recipient email address.")

elif not st.session_state.current_audio_source:
     st.info("Welcome! Use the tabs above to record live audio or upload an audio file to start.")

# --- Attempt Final Cleanup (e.g., if user leaves page after upload without processing) ---
if st.session_state.temp_upload_path and os.path.exists(st.session_state.temp_upload_path):
    # Check if this path was processed THIS run; if not, maybe clean it.
    # This is still tricky, might delete file needed for display if user interacts elsewhere.
    # Consider a more robust cleanup strategy if temp files accumulate.
    pass # Leaving this less aggressive for now.

logging.info("Streamlit script run complete.")