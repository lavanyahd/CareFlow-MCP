import api from "./api";


export async function getFhirBundle(referralId) {
  const response = await api.get(
    `/fhir/referral/${referralId}`
  );

  return response.data;
}