import { useState, useEffect } from "react";

export default function SplitEditor({ members, splitType, totalAmount, onChange }) {
  const [splits, setSplits] = useState({});

  // Initialize equal splits when members or splitType changes
  useEffect(() => {
    if (!members.length) return;
    const initial = {};
    members.forEach((m) => {
      initial[m.user.id] = {
        user_id: m.user.id,
        amount: 0,
        percentage: parseFloat((100 / members.length).toFixed(2)),
        shares: 1,
      };
    });
    setSplits(initial);
    onChange(Object.values(initial));
  }, [members, splitType]);

  const updateField = (userId, field, value) => {
    const updated = { ...splits, [userId]: { ...splits[userId], [field]: parseFloat(value) || 0 } };
    setSplits(updated);
    onChange(Object.values(updated));
  };

  const total = parseFloat(totalAmount) || 0;

  const pctSum = Object.values(splits).reduce((s, x) => s + (x.percentage || 0), 0);
  const amtSum = Object.values(splits).reduce((s, x) => s + (x.amount || 0), 0);

  if (splitType === "equal") {
    const share = members.length ? (total / members.length).toFixed(2) : "0.00";
    return (
      <div className="space-y-2">
        <p className="text-xs text-gray-500 mb-2">Split equally among all members.</p>
        {members.map((m) => (
          <div key={m.user.id} className="flex justify-between items-center text-sm py-1.5 border-b border-gray-50">
            <span className="text-gray-700">{m.user.name}</span>
            <span className="font-medium text-gray-900">₹{share}</span>
          </div>
        ))}
      </div>
    );
  }

  if (splitType === "unequal") {
    return (
      <div className="space-y-2">
        <p className="text-xs text-gray-500 mb-2">
          Enter exact amount each person owes. Sum must equal ₹{total.toFixed(2)}.
          <span className={Math.abs(amtSum - total) > 0.02 ? " text-red-500 font-medium" : " text-green-600 font-medium"}>
            {" "}Current sum: ₹{amtSum.toFixed(2)}
          </span>
        </p>
        {members.map((m) => (
          <div key={m.user.id} className="flex items-center gap-3">
            <span className="text-sm text-gray-700 flex-1">{m.user.name}</span>
            <div className="flex items-center gap-1">
              <span className="text-gray-400 text-sm">₹</span>
              <input
                type="number"
                min="0"
                step="0.01"
                value={splits[m.user.id]?.amount || ""}
                onChange={(e) => updateField(m.user.id, "amount", e.target.value)}
                className="input w-28 text-right"
                placeholder="0.00"
              />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (splitType === "percentage") {
    return (
      <div className="space-y-2">
        <p className="text-xs text-gray-500 mb-2">
          Enter percentage for each member. Must sum to 100%.
          <span className={Math.abs(pctSum - 100) > 0.01 ? " text-red-500 font-medium" : " text-green-600 font-medium"}>
            {" "}Current: {pctSum.toFixed(1)}%
          </span>
        </p>
        {members.map((m) => {
          const pct = splits[m.user.id]?.percentage || 0;
          const amt = ((pct / 100) * total).toFixed(2);
          return (
            <div key={m.user.id} className="flex items-center gap-3">
              <span className="text-sm text-gray-700 flex-1">{m.user.name}</span>
              <span className="text-xs text-gray-400 w-16 text-right">₹{amt}</span>
              <div className="flex items-center gap-1">
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={splits[m.user.id]?.percentage || ""}
                  onChange={(e) => updateField(m.user.id, "percentage", e.target.value)}
                  className="input w-20 text-right"
                  placeholder="0"
                />
                <span className="text-gray-400 text-sm">%</span>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  if (splitType === "shares") {
    const totalShares = Object.values(splits).reduce((s, x) => s + (x.shares || 0), 0);
    return (
      <div className="space-y-2">
        <p className="text-xs text-gray-500 mb-2">
          Assign share weights. Total shares: {totalShares}
        </p>
        {members.map((m) => {
          const s = splits[m.user.id]?.shares || 1;
          const amt = totalShares > 0 ? ((s / totalShares) * total).toFixed(2) : "0.00";
          return (
            <div key={m.user.id} className="flex items-center gap-3">
              <span className="text-sm text-gray-700 flex-1">{m.user.name}</span>
              <span className="text-xs text-gray-400 w-16 text-right">₹{amt}</span>
              <input
                type="number"
                min="0"
                step="1"
                value={splits[m.user.id]?.shares || ""}
                onChange={(e) => updateField(m.user.id, "shares", e.target.value)}
                className="input w-20 text-right"
                placeholder="1"
              />
            </div>
          );
        })}
      </div>
    );
  }

  return null;
}
