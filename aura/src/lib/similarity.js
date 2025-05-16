import { euclidean } from 'ml-distance-euclidean';
import DynamicTimeWarping from 'dynamic-time-warping';

export function computeDetailedDistanceMatrix(mfccList) {
    const n = mfccList.length;
    const matrix = Array(n).fill(null).map(() => Array(n).fill(null));

    for (let i = 0; i < n; i++) {
        for (let j = i; j < n; j++) {
            if (i === j) {
                matrix[i][j] = { euclidean: 0, dtwCost: 0, dtwCostPerStep: 0 };
                continue;
            }

            const seqA = mfccList[i];
            const seqB = mfccList[j];

            const minLength = Math.min(seqA.length, seqB.length);
            const trimmedA = seqA.slice(0, minLength);
            const trimmedB = seqB.slice(0, minLength);

            const euc = averageEuclidean(trimmedA, trimmedB);

            const dtw = new DynamicTimeWarping(
                seqA,
                seqB,
                euclidean
            );
            const cost = dtw.getDistance();
            const path = dtw.getPath();
            const costPerStep = cost / path.length;

            matrix[i][j] = matrix[j][i] = {
                euclidean: euc,
                dtwCost: cost,
                dtwCostPerStep: costPerStep
            };
        }
    }

    return matrix;
}

function averageEuclidean(seq1, seq2) {
    return seq1.reduce((sum, val, i) => sum + euclidean([val], [seq2[i]]), 0) / seq1.length;
}