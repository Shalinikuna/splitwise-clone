import { useState, useEffect, useCallback } from "react";
import { groupService } from "../services/groupService";

export function useGroups() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchGroups = useCallback(async () => {
    setLoading(true);
    try {
      const res = await groupService.list();
      setGroups(res.data);
      setError(null);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to load groups");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGroups();
  }, [fetchGroups]);

  const createGroup = async (data) => {
    const res = await groupService.create(data);
    setGroups((prev) => [res.data, ...prev]);
    return res.data;
  };

  const deleteGroup = async (id) => {
    await groupService.delete(id);
    setGroups((prev) => prev.filter((g) => g.id !== id));
  };

  return { groups, loading, error, fetchGroups, createGroup, deleteGroup };
}
