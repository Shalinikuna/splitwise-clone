import { useState } from "react";
import { groupService } from "../../services/groupService";

export default function InviteMemberModal({ groupId, onClose, onInvited }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await groupService.invite(groupId, email.trim());
      setSuccess(`${email} has been invited!`);
      setEmail("");
      onInvited && onInvited();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to invite user.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Invite Member</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <p className="text-sm text-gray-500">
            The user must already have an account. Enter their registered email.
          </p>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2">
              {error}
            </div>
          )}
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 text-sm rounded-lg px-3 py-2">
              {success}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              placeholder="friend@example.com"
              required
            />
          </div>
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Done
            </button>
            <button type="submit" disabled={loading} className="btn-primary flex-1">
              {loading ? "Inviting..." : "Invite"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
