Synchronization of film subtitles, using computer vision and an algorithm that predicts the conformity of the transcription to the displayed subtitles. 
Character detection was achieved using VisionAPI (https://cloud.google.com/vision), but can be changed for Tesseract OCR (https://pypi.org/project/pytesseract/). 
The algorithm detects the phrases displayed in the video and processes them, to match the provided transcript and adjust the timestamps of each phrase. 
The output is a standard .srt file.
Considering unexpected errors, the package provides a recovery function, that skips already parsed data, cutting down on processing time.
