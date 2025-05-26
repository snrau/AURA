import axios from "axios";

const BASE_URL = "http://localhost:8000";

export async function fetchResultsList() {
    const res = await axios.get(`${BASE_URL}/results`);
    return res.data.results;
}

export async function fetchResultData(filename) {
    const res = await axios.get(`${BASE_URL}/results/${filename}`);
    return res.data;
}