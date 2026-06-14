import { useState } from "react";
import SplitEditor from "./SplitEditor";

const SPLIT_TYPES = [
  { value: "equal", label: "Equal" },
  { value: "unequal", label: "Exact Amounts" },
  { value: "percentage", label: "Percentage" },
  { value: "shares", label: "Shares" },
];

export default function CreateExpenseModal({ groupId, members, currentUser, onCreate, onClose }) {
  const [form, setForm] = useState({
    title: "",
    amount: "",
    paid_by_id: currentUser?.id || members[0]?.user.id || "",
    split_type: "equal",
  });
  const [splits, setSplits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title.trim() || !form.amount || !form.paid_by_id) return;
    setError("");
    setLoading(true);

    const payload = {
      title: form.title.trim(),
      amount: parseFloat(form.amount),
      paid_by_id: form.paid_by_id,
      split_type: form.split_type,
      splits:
        form.split_type === "equal"
          ? members.map((m) => ({ user_id: m.user.id }))
          : splits,
    };

    try {
      await onCreate(payload);
    } catch (err) {
      const data = err.response?.data;
      setError(
        typeof data === "string"
          ? data
          : data?.detail || data?.non_field_errors?.[0] || "Failed to create expense."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Add Expense</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="input"
              placeholder="e.g. Dinner at Pizza Hut"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Total Amount (₹) *</label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
              className="input"
              placeholder="0.00"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Paid By *</label>
            <select
              value={form.paid_by_id}
              onChange={(e) => setForm({ ...form, paid_by_id: e.target.value })}
              className="input"
            >
              {members.map((m) => (
                <option key={m.user.id} value={m.user.id}>
                  {m.user.name} {m.user.id === currentUser?.id ? "(you)" : ""}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Split Type</label>
            <div className="flex gap-2 flex-wrap">
              {SPLIT_TYPES.map((st) => (
                <button
                  key={st.value}
                  type="button"
                  onClick={() => setForm({ ...form, split_type: st.value })}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                    form.split_type === st.value
                      ? "bg-brand-600 text-white border-brand-600"
                      : "bg-white text-gray-600 border-gray-300 hover:border-brand-400"
                  }`}
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>

          {form.split_type !== "equal" && (
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-sm font-medium text-gray-700 mb-3">Split Details</p>
              <SplitEditor
                members={members}
                splitType={form.split_type}
                totalAmount={parseFloat(form.amount) || 0}
                onChange={setSplits}
              />
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary flex-1">
              {loading ? "Adding..." : "Add Expense"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
