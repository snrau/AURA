import DynamicTimeWarping from 'dynamic-time-warping';
import { euclidean } from 'ml-distance-euclidean';

export function alignSequences(seq1, seq2) {
    const dtw = new DynamicTimeWarping(seq1, seq2, euclidean);
    const cost = dtw.getDistance();
    const path = dtw.getPath(); // array of [i, j]
    return { cost, path };
}

/**
 * Aligns a list of feature objects (from multiple takes) to a reference (first item).
 * Returns a new aligned feature list.
 */
export function alignAllTakes(featuresList) {
    const ref = featuresList[0];
    const alignedList = [];

    alignedList.push(ref); // first is reference, no need to align

    for (let i = 1; i < featuresList.length; i++) {
        const target = featuresList[i];

        const pitchPath = getDTWPath(ref.pitch.map(p => [p]), target.pitch.map(p => [p]));
        const aligned = {
            pitch: pitchPath.map(([, j]) => target.pitch[j] ?? 0),
            rms: pitchPath.map(([, j]) => target.rms[j] ?? 0),
            mfcc: pitchPath.map(([, j]) => target.mfcc[j] ?? Array(13).fill(0))
        };

        alignedList.push(aligned);
    }

    return alignedList;
}

function getDTWPath(seqA, seqB) {
    const dtw = new DynamicTimeWarping(seqA, seqB, euclidean);
    return dtw.getPath(); // array of [i, j]
}