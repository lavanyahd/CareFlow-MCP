import api from "./api";


export async function predictDNA(referralId) {
  const response = await api.post(
    `/dna/predict/${referralId}`
  );

  return response.data;
}


export async function getDNAResults(referralId) {
  const response = await api.get(
    `/dna/results/${referralId}`
  );

  return response.data;
}