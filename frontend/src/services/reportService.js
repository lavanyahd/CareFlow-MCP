import api from "./api";


export async function downloadReferralReport(referralId) {
  const response = await api.get(
    `/reports/referral/${referralId}`,
    {
      responseType: "blob",
    }
  );

  const pdfBlob = new Blob(
    [response.data],
    {
      type: "application/pdf",
    }
  );

  const fileUrl = window.URL.createObjectURL(pdfBlob);

  const downloadLink = document.createElement("a");
  downloadLink.href = fileUrl;
  downloadLink.download = `careflow_referral_${referralId}_report.pdf`;

  document.body.appendChild(downloadLink);
  downloadLink.click();

  downloadLink.remove();
  window.URL.revokeObjectURL(fileUrl);
}