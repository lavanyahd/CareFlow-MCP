import api from "./api";

export async function createReferral(referralData) {
  const response = await api.post(
    "/referrals",
    referralData
  );

  return response.data;
}

export async function getReferrals() {
  const response = await api.get("/referrals");

  return response.data;
}

export async function getReferral(referralId) {
  const response = await api.get(
    `/referrals/${referralId}`
  );

  return response.data;
}