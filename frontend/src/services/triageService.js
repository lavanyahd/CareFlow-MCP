import api from "./api";


export async function predictTriage(referralId) {
  const response = await api.post(
    `/triage/predict/${referralId}`
  );

  return response.data;
}


export async function getTriageResults(referralId) {
  const response = await api.get(
    `/triage/results/${referralId}`
  );

  return response.data;
}