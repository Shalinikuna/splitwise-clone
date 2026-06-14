import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import ChatBox from "../components/chat/ChatBox";
import { expenseService } from "../services/expenseService";
import { useAuth } from "../context/AuthContext";

function SplitRow({ split, paidBy }) {
  const isCreditor = split.user.id === paidBy?.id;
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center text-xs font-semibold text-gray-600">
          {split.user.name[0].toUpperCase()}
        </div>
        <span className="text-sm text-gray-800">{split.user.name}</span>
        {isCreditor && (
          <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">paid</span>
        )}
      </div>
      <span className="text-sm font-semibold text-gray-700">₹{parseFloat(split.amount).toFixed(2)}</span>
    </div>
  );
}

const SPLIT_LABEL = {
  equal: "Split Equally",
  unequal: "Split by Amount",
  percentage: "Split by %",
  shares: "Split by Shares",
};

export default function ExpenseDetailPage() {
  const { expenseId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [expense, setExpense] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    expenseService
      .get(expenseId)
      .then((r) => setExpense(r.data))
      .catch(() => navigate("/"))
      .finally(() => setLoading(false));
  }, [expenseId, navigate]);

  const handleDelete = async () => {
    if (!window.confirm("Delete this expense? This cannot be undone.")) return;
    try {
      await expenseService.delete(expenseId);
      navigate(-1);
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to delete.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-brand-600" />
      </div>
    );
  }

  if (!expense) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-6 space-y-4">

        {/* Back */}
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
        >
          ← Back
        </button>

        {/* Expense header */}
        <div className="card space-y-3">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">{expense.title}</h1>
              <p className="text-3xl font-bold text-brand-600 mt-1">
                ₹{parseFloat(expense.amount).toFixed(2)}
              </p>
            </div>
            {expense.created_by?.id === user?.id && (
              <button
                onClick={handleDelete}
                className="btn-danger text-xs px-3 py-1.5"
              >
                Delete
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-gray-50 rounded-lg p-2">
              <p className="text-xs text-gray-400 mb-0.5">Paid by</p>
              <p className="font-medium text-gray-800">{expense.paid_by?.name}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-2">
              <p className="text-xs text-gray-400 mb-0.5">Split type</p>
              <p className="font-medium text-gray-800">{SPLIT_LABEL[expense.split_type] || expense.split_type}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-2 col-span-2">
              <p className="text-xs text-gray-400 mb-0.5">Added by</p>
              <p className="font-medium text-gray-800">
                {expense.created_by?.name} ·{" "}
                <span className="text-gray-400 text-xs">
                  {new Date(expense.created_at).toLocaleDateString("en-IN", {
                    day: "numeric", month: "short", year: "numeric",
                  })}
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Split breakdown */}
        <div className="card">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-400 mb-2">
            Split Breakdown
          </h2>
          <div className="divide-y divide-gray-100">
            {expense.splits?.map((split) => (
              <SplitRow key={split.id} split={split} paidBy={expense.paid_by} />
            ))}
          </div>
        </div>

        {/* Chat */}
        <div className="card">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-400 mb-3">
            Comments
          </h2>
          <ChatBox expenseId={expenseId} currentUser={user} />
        </div>
      </main>
    </div>
  );
}
