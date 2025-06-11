from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
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
    #file = sorted(glob.glob("outputs/audio_analysis.json"))
    files = sorted(glob.glob("outputs/*.json"))
    if not files:
        return {"results": []}
    filenames = [os.path.basename(f) for f in files]
    #filenames = [os.path.basename(file[0])]
    return {"results": filenames}

@app.get("/results/{filename}")
def list_results(filename: str):
    file_path = os.path.join("outputs", filename)
    if os.path.exists(file_path):
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        return FileResponse(file_path, media_type='application/json',  headers=headers)
    else:
        return {"error": "File not found"}