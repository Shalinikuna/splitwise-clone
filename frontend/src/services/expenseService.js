import api from "./api";

export const expenseService = {
  list: (groupId) => api.get(`/groups/${groupId}/expenses/`),
  get: (expenseId) => api.get(`/expenses/${expenseId}/`),
  create: (groupId, data) => api.post(`/groups/${groupId}/expenses/`, data),
  delete: (expenseId) => api.delete(`/expenses/${expenseId}/`),
  groupBalances: (groupId) => api.get(`/groups/${groupId}/balances/`),
  myBalances: () => api.get("/balances/"),
  listComments: (expenseId) => api.get(`/expenses/${expenseId}/comments/`),
  postComment: (expenseId, text) => api.post(`/expenses/${expenseId}/comments/`, { text }),
};
