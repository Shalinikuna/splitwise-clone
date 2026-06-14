import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import ExpenseCard from "../components/expenses/ExpenseCard";
import CreateExpenseModal from "../components/expenses/CreateExpenseModal";
import InviteMemberModal from "../components/groups/InviteMemberModal";
import BalanceSummary from "../components/settlements/BalanceSummary";
import SettleForm from "../components/settlements/SettleForm";
import { useExpenses } from "../hooks/useExpenses";
import { useGroupBalances } from "../hooks/useBalances";
import { groupService } from "../services/groupService";
import { useAuth } from "../context/AuthContext";

export default function GroupDetailPage() {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [group, setGroup] = useState(null);
  const [loadingGroup, setLoadingGroup] = useState(true);
  const [tab, setTab] = useState("expenses"); // "expenses" | "balances"
  const [showCreateExpense, setShowCreateExpense] = useState(false);
  const [showInvite, setShowInvite] = useState(false);
  const [showSettle, setShowSettle] = useState(false);

  const { expenses, loading: expLoading, createExpense, deleteExpense } = useExpenses(groupId);
  const { balances, loading: balLoading, refetch: refetchBalances } = useGroupBalances(groupId);

  useEffect(() => {
    groupService
      .get(groupId)
      .then((r) => setGroup(r.data))
      .catch(() => navigate("/"))
      .finally(() => setLoadingGroup(false));
  }, [groupId, navigate]);

  if (loadingGroup) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-brand-600" />
      </div>
    );
  }

  const isAdmin = group?.members?.find((m) => m.user.id === user?.id)?.role === "admin";
  const members = group?.members || [];

  const handleCreateExpense = async (data) => {
    await createExpense(data);
    setShowCreateExpense(false);
    refetchBalances();
  };

  const handleDeleteExpense = async (id) => {
    if (!window.confirm("Delete this expense?")) return;
    await deleteExpense(id);
    refetchBalances();
  };

  const handleRemoveMember = async (memberId) => {
    if (!window.confirm("Remove this member?")) return;
    try {
      await groupService.removeMember(groupId, memberId);
      setGroup((g) => ({
        ...g,
        members: g.members.filter((m) => m.user.id !== memberId),
      }));
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to remove member.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 py-6 space-y-4">

        {/* Header */}
        <div className="card flex items-start justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-gray-900">{group.name}</h1>
            {group.description && (
              <p className="text-sm text-gray-500 mt-0.5">{group.description}</p>
            )}
            <p className="text-xs text-gray-400 mt-1">{members.length} members</p>
          </div>
          <div className="flex gap-2 flex-wrap">
            {isAdmin && (
              <button
                onClick={() => setShowInvite(true)}
                className="btn-secondary text-xs px-3 py-1.5"
              >
                + Invite
              </button>
            )}
            <button
              onClick={() => setShowCreateExpense(true)}
              className="btn-primary text-xs px-3 py-1.5"
            >
              + Expense
            </button>
          </div>
        </div>

        {/* Members strip */}
        <div className="card">
          <h2 className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">Members</h2>
          <div className="flex flex-wrap gap-2">
            {members.map((m) => (
              <div
                key={m.user.id}
                className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-full px-3 py-1"
              >
                <div className="w-5 h-5 rounded-full bg-brand-100 flex items-center justify-center">
                  <span className="text-brand-700 text-xs font-semibold">
                    {m.user.name[0].toUpperCase()}
                  </span>
                </div>
                <span className="text-xs text-gray-700">{m.user.name}</span>
                {m.role === "admin" && (
                  <span className="text-xs text-brand-600 font-medium">(admin)</span>
                )}
                {isAdmin && m.user.id !== user.id && (
                  <button
                    onClick={() => handleRemoveMember(m.user.id)}
                    className="text-gray-300 hover:text-red-400 ml-1 text-xs leading-none"
                    title="Remove"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 border-b border-gray-200">
          {["expenses", "balances"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
                tab === t
                  ? "border-b-2 border-brand-600 text-brand-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {tab === "expenses" && (
          <div className="space-y-2">
            {expLoading ? (
              <div className="flex justify-center py-10">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-brand-600" />
              </div>
            ) : expenses.length === 0 ? (
              <div className="card text-center py-10">
                <p className="text-gray-400 text-sm">No expenses yet.</p>
                <button
                  onClick={() => setShowCreateExpense(true)}
                  className="btn-primary mt-3 text-sm"
                >
                  Add first expense
                </button>
              </div>
            ) : (
              expenses.map((e) => (
                <ExpenseCard
                  key={e.id}
                  expense={e}
                  currentUser={user}
                  onDelete={handleDeleteExpense}
                />
              ))
            )}
          </div>
        )}

        {tab === "balances" && (
          <div className="space-y-3">
            {balLoading ? (
              <div className="flex justify-center py-10">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-brand-600" />
              </div>
            ) : (
              <>
                <BalanceSummary
                  balances={balances}
                  members={members}
                  onSettle={() => setShowSettle(true)}
                />
                <button
                  onClick={() => setShowSettle(true)}
                  className="btn-primary w-full"
                >
                  Record a Settlement
                </button>
              </>
            )}
          </div>
        )}
      </main>

      {showCreateExpense && (
        <CreateExpenseModal
          groupId={groupId}
          members={members}
          currentUser={user}
          onClose={() => setShowCreateExpense(false)}
          onCreate={handleCreateExpense}
        />
      )}

      {showInvite && (
        <InviteMemberModal
          groupId={groupId}
          onClose={() => setShowInvite(false)}
          onInvited={() => groupService.get(groupId).then((r) => setGroup(r.data))}
        />
      )}

      {showSettle && (
        <SettleForm
          groupId={groupId}
          members={members}
          currentUser={user}
          onClose={() => setShowSettle(false)}
          onSettled={() => {
            setShowSettle(false);
            refetchBalances();
          }}
        />
      )}
    </div>
  );
}
