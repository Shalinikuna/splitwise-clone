import { useState, useEffect, useCallback } from "react";
import { expenseService } from "../services/expenseService";

export function useExpenses(groupId) {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchExpenses = useCallback(async () => {
    if (!groupId) return;
    setLoading(true);
    try {
      const res = await expenseService.list(groupId);
      setExpenses(res.data);
      setError(null);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load expenses");
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  const createExpense = async (data) => {
    const res = await expenseService.create(groupId, data);
    setExpenses((prev) => [res.data, ...prev]);
    return res.data;
  };

  const deleteExpense = async (expenseId) => {
    await expenseService.delete(expenseId);
    setExpenses((prev) => prev.filter((e) => e.id !== expenseId));
  };

  return { expenses, loading, error, fetchExpenses, createExpense, deleteExpense };
}
