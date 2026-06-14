export default function BalanceSummary({ balances, members, onSettle }) {
  if (!balances.length) {
    return (
      <div className="text-center py-8 text-gray-400 text-sm">
        🎉 All settled up! No outstanding balances.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {balances.map((b, i) => (
        <div
          key={i}
          className="flex items-center justify-between p-3 bg-orange-50 border border-orange-100 rounded-xl"
        >
          <div className="flex items-center gap-2 text-sm">
            <span className="font-medium text-gray-800">{b.from_user.name}</span>
            <span className="text-gray-400">owes</span>
            <span className="font-medium text-gray-800">{b.to_user.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-orange-700">₹{b.amount.toFixed(2)}</span>
            {onSettle && (
              <button
                onClick={() => onSettle(b)}
                className="text-xs bg-brand-600 hover:bg-brand-700 text-white px-2 py-1 rounded-lg transition-colors"
              >
                Settle
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
