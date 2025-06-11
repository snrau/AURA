import librosa
import numpy as np
import json
import os
from scipy.spatial.distance import cdist
from scipy.signal import get_window
from scipy.fft import fft, fftfreq

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

hop_length = 512
hop_length_dtw = 1 * hop_length

def detect_vibrato(f0, sr, hop_length, frame_sec=0.5, vibrato_range=(4, 8)):
    frame_length = int((sr / hop_length) * frame_sec)
    vibrato_strength = []

    # Pad f0 to avoid boundary issues
    padded_f0 = np.pad(f0, (frame_length//2, frame_length//2), mode='constant', constant_values=0)

    for i in range(len(f0)):
        # Extract frame centered at i
        start = i
        end = i + frame_length
        frame = padded_f0[start:end]

        if np.all(frame == 0):
            vibrato_strength.append(0)
            continue

        detrended = frame - np.mean(frame)
        windowed = detrended * get_window('hann', frame.shape[0])
        spectrum = np.abs(fft(windowed))
        freqs = fftfreq(frame_length, d=hop_length / sr)

        # Only positive freqs
        pos_mask = freqs > 0
        freqs = freqs[pos_mask]
        spectrum = spectrum[pos_mask]

        # Energy in vibrato band
        idx = np.where((freqs >= vibrato_range[0]) & (freqs <= vibrato_range[1]))[0]
        vib_energy = np.sum(spectrum[idx]**2) if idx.size > 0 else 0

        vibrato_strength.append(vib_energy)

    # Normalize vibrato strength for convenience
    vib_array = np.array(vibrato_strength)
    vib_array = vib_array / (np.max(vib_array) + 1e-9)  # avoid div by zero

    # Downsample to frame length (frame_sec)
    step = frame_length
    vib_frames = []
    for i in range(0, len(vib_array), step):
        vib_frames.append(float(np.mean(vib_array[i:i+step])))

    return vib_frames

def extract_features(audio_path, frame_duration=0.25):
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)

    frame_length = int((frame_duration * sr) / hop_length)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=1000)
    #onsets = librosa.onset.onset_detect(y=y, sr=sr)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    onsets = librosa.onset.onset_detect(
    y=y, sr=sr, onset_envelope=onset_env, delta=0.1, hop_length=hop_length
)
    onset_times = librosa.frames_to_time(onsets, sr=sr, hop_length=hop_length).tolist()
    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    chroma_cens = librosa.feature.chroma_cens(y=y, sr=sr, hop_length=hop_length)

    f0_frames = []
    for i in range(0, len(f0), frame_length):
        frame = np.array(f0[i:i+frame_length])
        valid_frame = frame[~np.isnan(frame)]
        f0_mean = float(np.mean(valid_frame)) if len(valid_frame) > 0 else 0
        f0_frames.append(f0_mean)

    # Clean f0 array for output (replace NaNs with 0.0)
    f0_clean = [float(f) if not (np.isnan(f) or np.isinf(f)) else 0.0 for f in f0]

    # Compute vibrato (uses cleaned f0)
    vibrato_raw = detect_vibrato(np.array(f0_clean), sr, hop_length, frame_sec=frame_duration)

    # Clean vibrato for JSON
    vibrato = [float(v) if not (np.isnan(v) or np.isinf(v)) else 0.0 for v in vibrato_raw]

    return {
        "waveform": y.tolist(),
        "rms": rms.tolist(),
        "f0": f0_clean,
        "f0_framewise": f0_frames,
        "vibrato": vibrato,
        "onsets": onset_times,
        "onsets_strength": onset_env.tolist(),
        "spectral_centroid": spec_centroid.tolist(),
        "mfcc": mfcc.tolist(),
        "duration": duration,
        "chroma_cens": chroma_cens.tolist()
    }


def compute_dtw_mixed(feat1, feat2, hop_length):
    x = np.array(feat1["chroma_cens"])
    y = np.array(feat2["chroma_cens"])

    x1 = np.array(feat1["mfcc"])
    y1 = np.array(feat2["mfcc"])

    feat_a = np.vstack([x, x1])
    feat_b = np.vstack([y, y1])

    dist = cdist(feat_a.T, feat_b.T, metric='cosine')

    D, wp = librosa.sequence.dtw(C=dist)

    wp = wp[::-1]  # Time warp path

    # Convert frame indices to sample indices by multiplying by hop_length
    path = [{"x": int(i * hop_length), "y": int(j * hop_length)} for i, j in wp]
    return path

def compute_dtw_cens(feat1, feat2, hop_length):
    # We assume MFCCs are used for alignment (13 x N)
    x = np.array(feat1["chroma_cens"])
    y = np.array(feat2["chroma_cens"])
    dist = cdist(x.T, y.T, metric='cosine')
    D, wp = librosa.sequence.dtw(C=dist)

    wp = wp[::-1]  # Time warp path

    # Convert frame indices to sample indices by multiplying by hop_length
    path = [{"x": int(i * hop_length), "y": int(j * hop_length)} for i, j in wp]
    return path

def compute_dtw_mfcc(feat1, feat2, hop_length):
    # We assume MFCCs are used for alignment (13 x N)
    x = np.array(feat1["mfcc"])
    y = np.array(feat2["mfcc"])
    dist = cdist(x.T, y.T, metric='euclidean')
    D, wp = librosa.sequence.dtw(C=dist)

    wp = wp[::-1]  # Time warp path

    # Convert frame indices to sample indices by multiplying by hop_length
    path = [{"x": int(i * hop_length), "y": int(j * hop_length)} for i, j in wp]
    return path



def compute_dtw_own(feat1, feat2, hop_length, energy_thresh, weights):

    # Feature extraction
    def extract_features(feat, weights):
        mfcc = np.array(feat['mfcc'])
        chroma = np.array(feat['chroma_cens'])
        f0 = np.array(feat['f0'])[None, :]  # make it 2D

        # Normalize features (optional but helpful)
        mfcc = (mfcc - np.mean(mfcc, axis=1, keepdims=True)) / (np.std(mfcc, axis=1, keepdims=True) + 1e-6)
        chroma = (chroma - np.mean(chroma, axis=1, keepdims=True)) / (np.std(chroma, axis=1, keepdims=True) + 1e-6)
        f0 = (f0 - np.mean(f0)) / (np.std(f0) + 1e-6)

        # Apply weights
        w_mfcc, w_chroma, w_f0 = weights
        mfcc *= w_mfcc
        chroma *= w_chroma
        f0 *= w_f0
        return np.vstack([mfcc, chroma, f0])
    

    # Get MFCCs
    x = extract_features(feat1, weights)
    y = extract_features(feat2, weights)

    # Get RMS energy
    rmsA = np.array(feat1["rms"]).flatten()
    rmsB = np.array(feat2["rms"]).flatten()

    # Normalize RMS
    rmsA /= np.max(rmsA) or 1
    rmsB /= np.max(rmsB) or 1

    # Silence masks
    maskA = rmsA > energy_thresh
    maskB = rmsB > energy_thresh

    # Compute base distance matrix
    dist = cdist(x.T, y.T, metric='euclidean')

    # Create weight matrix: penalize silence
    weight_matrix = np.outer(rmsA, rmsB)

    # Optional: further penalize very low energy areas
    # Encourage silence-to-silence, discourage silence-to-sound
    S1 = maskA.astype(float)  # 1 for sound, 0 for silence
    S2 = maskB.astype(float)

    # Weighting matrix:
    # - 0.1 cost if both are silent (prefer aligning silence)
    # - 1.0 if both are sound
    # - >1.0 penalty if mismatch
    weight_matrix = np.ones_like(dist)
    for i in range(len(S1)):
        for j in range(len(S2)):
            if S1[i] == 0 and S2[j] == 0:
                weight_matrix[i, j] = 0.1  # both silent
            elif S1[i] != S2[j]:
                weight_matrix[i, j] = 2.0  # mismatch: silence vs sound
            # else: default 1.0

    weighted_dist = dist * weight_matrix

    # Apply DTW
    D, wp = librosa.sequence.dtw(C=weighted_dist, metric='euclidean')

    wp = wp[::-1]  # Time warp path (reversed)

    # Convert to sample indices
    path = [{"x": int(i * hop_length), "y": int(j * hop_length)} for i, j in wp]
    return path



def analyze_audio_files(file_paths):
    features = [extract_features(file) for file in file_paths]
    dtw_mfcc = compute_dtw_mfcc(features[0], features[1], hop_length_dtw)
    dtw_chroma = compute_dtw_cens(features[0], features[1], hop_length_dtw)
    dtw_mixed = compute_dtw_mixed(features[0], features[1], hop_length_dtw)
    dtw_own = compute_dtw_own(features[0], features[1], hop_length_dtw, 0.5, (0.2, 0.1, 1.0))  #rms threshhold, (mfcc, chroma, f0)

    result = {
        "files": [os.path.basename(p) for p in file_paths],
        "features": {
            "waveform": {
                "fileA": features[0]['waveform'],
                "fileB": features[1]['waveform']
            },
            "rms": {
                "fileA": features[0]['rms'],
                "fileB": features[1]['rms']
            },
            "f0": {
                "fileA": features[0]['f0'],
                "fileB": features[1]['f0']
            },
            "f0_framewise": {
                "fileA": features[0]['f0_framewise'],
                "fileB": features[1]['f0_framewise']
            },
            "vibrato": {
                "fileA": features[0]['vibrato'],
                "fileB": features[1]['vibrato']
            },
            "spectral_centroid": {
                "fileA": features[0]['spectral_centroid'],
                "fileB": features[1]['spectral_centroid']
            },
            "onsets": {
                "fileA": features[0]['onsets'],
                "fileB": features[1]['onsets']
            },
            "onsets_strength": {
                "fileA": features[0]['onsets_strength'],
                "fileB": features[1]['onsets_strength']
            },
            "duration": {
                "fileA": features[0]['duration'],
                "fileB": features[1]['duration']
            },
            "chroma_cens": {
                "fileA": features[0]['chroma_cens'],
                "fileB": features[1]['chroma_cens']
            },
        },
        "dtw": {
            "dtw_mfcc": dtw_mfcc,
            "dtw_own": dtw_own,
            "dtw_chroma": dtw_chroma,
            "dtw_mixed": dtw_mixed
        }
    }


    base_names = [os.path.splitext(os.path.basename(p))[0] for p in file_paths]
    output_filename = f"audio_analysis_{base_names[0]}_vs_{base_names[1]}.json"
    #output_filename = f"audio_analysis.json"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[INFO] Analysis saved to {output_path}")

    return result