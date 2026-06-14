import { useState, useEffect, useCallback } from "react";
import { expenseService } from "../services/expenseService";

export function useGroupBalances(groupId) {
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchBalances = useCallback(async () => {
    if (!groupId) return;
    try {
      const res = await expenseService.groupBalances(groupId);
      setBalances(res.data);
    } catch {
      setBalances([]);
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    fetchBalances();
  }, [fetchBalances]);

  return { balances, loading, refetch: fetchBalances };
}

export function useMyBalances() {
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    expenseService
      .myBalances()
      .then((res) => setBalances(res.data))
      .catch(() => setBalances([]))
      .finally(() => setLoading(false));
  }, []);

  return { balances, loading };
}
