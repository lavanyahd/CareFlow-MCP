import api from "./api";


export async function getAuditLogs(referralId = null) {
  const params = {};

  if (referralId !== null) {
    params.referral_id = referralId;
  }

  const response = await api.get(
    "/audit-logs",
    { params }
  );

  return response.data;
}