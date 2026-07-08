import api from "./api";


export async function getSlmReferralSummary(referralId) {
  const response = await api.get(
    `/slm/referral/${referralId}/summary`
  );

  return response.data;
}