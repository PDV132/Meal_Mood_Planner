from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.speech_to_text import transcribe_audio
import tempfile
import os

router = APIRouter()

@router.post("/analyze-voice")
async def analyze_voice(audio: UploadFile = File(...)):
    """
    Analyzes voice recording and returns the transcribed text
    """
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Transcribe the audio using our speech to text service
            text = transcribe_audio(tmp_path)
            
            if text == "Could not process the audio file.":
                raise HTTPException(status_code=400, detail="Could not process the audio file")
                
            return {"text": text}
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
