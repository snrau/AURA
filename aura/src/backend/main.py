from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil, os
from audio_analysis import analyze_audio_files
import glob

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    saved_paths = []
    for file in files:
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_paths.append(path)

    result_json = analyze_audio_files(saved_paths)
    return result_json

# List all JSON result files
@app.get("/results")
def list_results():
    file = sorted(glob.glob("outputs/audio_analysis.json"))
    filename = [os.path.basename(file) ]
    return {"results": filename}