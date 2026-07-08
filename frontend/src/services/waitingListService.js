import api from "./api";


export async function getWaitingList() {
  const response = await api.get("/waiting-list");

  return response.data;
}