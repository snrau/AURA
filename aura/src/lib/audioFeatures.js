import Meyda from 'meyda';
import * as Pitchfinder from 'pitchfinder';

export async function extractFeaturesFromBuffer(audioCtx, audioBuffer) {
    const signal = audioBuffer.getChannelData(0);
    const sampleRate = audioBuffer.sampleRate;
    const frameSize = 2048;
    const hopSize = 512;

    const pitchDetector = new Pitchfinder.YIN(); // or use Pitchfinder.YIN

    const features = {
        rms: [],
        mfcc: [],
        pitch: []
    };

    for (let i = 0; i < signal.length - frameSize; i += hopSize) {
        const frame = signal.slice(i, i + frameSize);

        const meydaFeatures = Meyda.extract(['rms', 'mfcc'], frame);
        const pitch = pitchDetector(frame, sampleRate);

        features.rms.push(meydaFeatures?.rms ?? 0);
        features.mfcc.push(meydaFeatures?.mfcc ?? Array(13).fill(0));
        features.pitch.push(pitch ?? 0); // `null` means no pitch detected
    }

    return features;
}