import api from "./api";


export async function askReferralAssistant(referralId, question) {
  const response = await api.post(
    `/rag/referral/${referralId}/ask`,
    {
      question: question,
    }
  );

  return response.data;
}