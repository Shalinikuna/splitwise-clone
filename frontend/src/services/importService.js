import api from "./api";

export const importService = {
  uploadCsv: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/import/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  listSessions: () => api.get("/import/sessions/"),
  getReport: (sessionId) => api.get(`/import/sessions/${sessionId}/`),
};
