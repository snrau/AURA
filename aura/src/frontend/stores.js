import { writable } from "svelte/store";

// Store for the shift value of File B
export const shiftB = writable(0);

export const dtwmethod = writable("dtw_own");

export const dtwOption = ["dtw_mfcc", "dtw_own", "dtw_chroma", "dtw_mixed"];


function createShiftStore() {
    const { subscribe, update, set } = writable({});

    return {
        subscribe,
        // Get shift for one pair
        getShift: (pairKey) => {
            let val;
            update((s) => {
                val = s[pairKey] ?? 0;
                return s;
            });
            return val;
        },
        // Set shift for one pair
        setShift: (pairKey, value) =>
            update((s) => {
                return { ...s, [pairKey]: value };
            }),
        // Reset shift for one pair
        resetShift: (pairKey) =>
            update((s) => {
                return { ...s, [pairKey]: 0 };
            })
    };
}

export const shiftStore = createShiftStore();