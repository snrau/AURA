import librosa
import numpy as np
import json
import os
from scipy.spatial.distance import cdist

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_features(y, sr):
    # Extract MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).tolist()

    # RMS
    rms = librosa.feature.rms(y=y).flatten().tolist()

    # Pitch estimation using autocorrelation
    pitches, _ = librosa.piptrack(y=y, sr=sr)
    pitch = [float(np.max(p)) if np.max(p) > 0 else 0.0 for p in pitches.T]

    # Spectral centroid
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr).flatten().tolist()

    # Spectral bandwidth
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr).flatten().tolist()

    # Raw waveform
    waveform = y.tolist()

    return {
        "mfcc": mfcc,
        "rms": rms,
        "pitch": pitch,
        "centroid": centroid,
        "bandwidth": bandwidth,
        "waveform": waveform,
        "sr": sr,
    }

def compute_dtw_features(feat1, feat2):
    # We assume MFCCs are used for alignment (13 x N)
    x = np.array(feat1["mfcc"])
    y = np.array(feat2["mfcc"])
    dist = cdist(x.T, y.T, metric='euclidean')
    D, wp = librosa.sequence.dtw(D=dist)

    wp = wp[::-1]  # Time warp path
    path = [{"x": int(i), "y": int(j)} for i, j in wp]
    return path

def analyze_audio_files(filepaths):
    if len(filepaths) != 2:
        raise ValueError("Only pairwise comparison is supported. Provide exactly 2 audio files.")

    features = []
    for path in filepaths:
        y, sr = librosa.load(path, sr=None)
        feat = extract_features(y, sr)
        feat["filename"] = os.path.basename(path)
        features.append(feat)

    dtw_path = compute_dtw_features(features[0], features[1])

    result = {
        "audio_1": features[0],
        "audio_2": features[1],
        "dtw_path": dtw_path
    }


    output_filename = f"audio_analysis.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[INFO] Analysis saved to {output_path}")

    return result