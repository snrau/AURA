import { writable } from "svelte/store";

// Store for the shift value of File B
export const shiftB = writable(0);

export const dtwmethod = writable("dtw_own");

export const dtwOption = ["dtw_mfcc", "dtw_own", "dtw_chroma", "dtw_mixed"];