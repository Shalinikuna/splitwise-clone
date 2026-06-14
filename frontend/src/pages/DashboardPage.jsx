import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/layout/Navbar";
import GroupCard from "../components/groups/GroupCard";
import CreateGroupModal from "../components/groups/CreateGroupModal";
import { useGroups } from "../hooks/useGroups";
import { useMyBalances } from "../hooks/useBalances";

export default function DashboardPage() {
  const navigate = useNavigate();
  const { groups, loading, createGroup, deleteGroup } = useGroups();
  const { balances, loading: balLoading } = useMyBalances();
  const [showCreate, setShowCreate] = useState(false);

  const handleCreate = async (data) => {
    const group = await createGroup(data);
    setShowCreate(false);
    navigate(`/groups/${group.id}`);
  };

  const totalOwed = balances
    .filter((b) => b.direction === "owed")
    .reduce((s, b) => s + b.amount, 0);
  const totalOwe = balances
    .filter((b) => b.direction === "owe")
    .reduce((s, b) => s + b.amount, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">

        {/* Overall Balance Summary */}
        {!balLoading && (
          <div className="grid grid-cols-2 gap-4">
            <div className="card text-center">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">You are owed</p>
              <p className="text-2xl font-bold text-green-600">₹{totalOwed.toFixed(2)}</p>
            </div>
            <div className="card text-center">
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">You owe</p>
              <p className="text-2xl font-bold text-red-500">₹{totalOwe.toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* Per-person balance list */}
        {!balLoading && balances.length > 0 && (
          <div className="card">
            <h2 className="font-semibold text-gray-700 mb-3 text-sm uppercase tracking-wide">
              Overall Balances
            </h2>
            <ul className="divide-y divide-gray-100">
              {balances.map((b, i) => (
                <li key={i} className="py-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center text-xs font-semibold text-gray-600">
                      {b.user.name[0].toUpperCase()}
                    </div>
                    <span className="text-sm text-gray-800">{b.user.name}</span>
                  </div>
                  <span
                    className={`text-sm font-semibold ${
                      b.direction === "owed" ? "text-green-600" : "text-red-500"
                    }`}
                  >
                    {b.direction === "owed" ? "owes you" : "you owe"} ₹{b.amount.toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Groups section */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900">My Groups</h2>
            <button onClick={() => setShowCreate(true)} className="btn-primary text-sm px-3 py-1.5">
              + New Group
            </button>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-brand-600" />
            </div>
          ) : groups.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-400 text-sm">No groups yet.</p>
              <button
                onClick={() => setShowCreate(true)}
                className="btn-primary mt-3 text-sm"
              >
                Create your first group
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {groups.map((g) => (
                <GroupCard key={g.id} group={g} onDelete={deleteGroup} />
              ))}
            </div>
          )}
        </div>
      </main>

      {showCreate && (
        <CreateGroupModal onClose={() => setShowCreate(false)} onCreate={handleCreate} />
      )}
    </div>
  );
}
