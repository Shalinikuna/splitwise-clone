import api from "./api";

export const settlementService = {
  list: (groupId) => api.get(`/groups/${groupId}/settlements/`),
  create: (groupId, data) => api.post(`/groups/${groupId}/settlements/`, data),
};
