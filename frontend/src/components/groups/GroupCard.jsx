import { useNavigate } from "react-router-dom";

export default function GroupCard({ group }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/groups/${group.id}`)}
      className="card cursor-pointer hover:shadow-md transition-shadow hover:border-brand-200"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-100 flex items-center justify-center flex-shrink-0">
            <span className="text-brand-700 font-semibold text-sm">
              {group.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{group.name}</h3>
            {group.description && (
              <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{group.description}</p>
            )}
          </div>
        </div>
        <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full">
          {group.member_count} member{group.member_count !== 1 ? "s" : ""}
        </span>
      </div>
    </div>
  );
}
