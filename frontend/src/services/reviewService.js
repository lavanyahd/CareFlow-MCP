import api from "./api";


export async function createClinicianReview(referralId, reviewData) {
  const response = await api.post(
    `/reviews/${referralId}`,
    reviewData
  );

  return response.data;
}


export async function getClinicianReviews(referralId) {
  const response = await api.get(
    `/reviews/${referralId}`
  );

  return response.data;
}