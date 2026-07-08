import api from "./api";


export async function getModelMonitoring() {
  const response = await api.get("/monitoring/models");

  return response.data;
}
