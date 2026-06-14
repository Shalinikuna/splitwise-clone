import api from "./api";

export const groupService = {
  list: () => api.get("/groups/"),
  get: (id) => api.get(`/groups/${id}/`),
  create: (data) => api.post("/groups/", data),
  update: (id, data) => api.patch(`/groups/${id}/`, data),
  delete: (id) => api.delete(`/groups/${id}/`),
  invite: (id, email) => api.post(`/groups/${id}/invite/`, { email }),
  removeMember: (groupId, userId) => api.delete(`/groups/${groupId}/members/${userId}/`),
};
