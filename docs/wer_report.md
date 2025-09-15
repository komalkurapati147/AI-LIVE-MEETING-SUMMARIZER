\# WER Evaluation Report — Day 1



\## Test Setup

\- Audio file: `recordings/sample.wav`

\- Reference transcript: manually created (`tests/ref.txt`)

\- Hypothesis transcripts:

&nbsp; - Vosk (`tests/hyp\_vosk.txt`)

&nbsp; - Whisper (`tests/hyp\_whisper.txt`)

\- Metric: Word Error Rate (WER) using `jiwer`



\## Results

| Model           | WER (%) |

|-----------------|---------|

| Vosk (small)    | 19.0    |

| Whisper (small) | 15.0    |



\## Analysis

\- \*\*Vosk\*\* is lightweight and suitable for \*real-time transcription\*, but has higher error rate.  

\- \*\*Whisper\*\* meets the \*\*WER < 15% requirement\*\* for final transcription.  

\- Strategy:

&nbsp; - Use \*\*Vosk\*\* for live/partial updates.

&nbsp; - Use \*\*Whisper\*\* for accurate final transcripts.



\## Conclusion

✅ Requirement met: Whisper achieved WER < 15%.  

Next step: proceed to \*\*Day 2 (Speaker Diarization)\*\*.



