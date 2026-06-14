import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

const SPLIT_LABELS = {
  equal: "Split equally",
  unequal: "Split by amount",
  percentage: "Split by %",
  shares: "Split by shares",
};

export default function ExpenseCard({ expense, onDelete }) {
  const navigate = useNavigate();
  const { user } = useAuth();

  const myShare = expense.splits?.find((s) => s.user.id === user?.id);
  const iAmPayer = expense.paid_by?.id === user?.id;

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-2">
        <div
          className="flex-1 cursor-pointer"
          onClick={() => navigate(`/expenses/${expense.id}`)}
        >
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0">
              <span className="text-indigo-600 text-lg">🧾</span>
            </div>
            <div>
              <p className="font-medium text-gray-900">{expense.title}</p>
              <p className="text-xs text-gray-400">
                {new Date(expense.created_at).toLocaleDateString()} ·{" "}
                {SPLIT_LABELS[expense.split_type]}
              </p>
            </div>
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="font-semibold text-gray-900">₹{parseFloat(expense.amount).toFixed(2)}</p>
          {iAmPayer ? (
            <p className="text-xs text-green-600 font-medium">You paid</p>
          ) : myShare ? (
            <p className="text-xs text-red-500">You owe ₹{parseFloat(myShare.amount).toFixed(2)}</p>
          ) : null}
        </div>
      </div>

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-50">
        <p className="text-xs text-gray-500">
          Paid by <span className="font-medium">{expense.paid_by?.name}</span>
        </p>
        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(expense.id);
            }}
            className="text-xs text-red-400 hover:text-red-600 transition-colors"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}
