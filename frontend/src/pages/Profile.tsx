import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api, clearTokens } from "../api/client";

interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export function ProfilePage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Form states
  const [fullName, setFullName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [deletePassword, setDeletePassword] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const p = await api.getProfile();
      setProfile(p);
      setFullName(p.full_name || "");
    } catch {
      setMessage({ type: "error", text: "Failed to load profile" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      await api.updateProfile({ full_name: fullName });
      setIsEditing(false);
      setMessage({ type: "success", text: "Profile updated" });
      loadProfile();
    } catch {
      setMessage({ type: "error", text: "Failed to update profile" });
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      setMessage({ type: "error", text: "Passwords do not match" });
      return;
    }
    if (newPassword.length < 8) {
      setMessage({ type: "error", text: "Password must be at least 8 characters" });
      return;
    }
    try {
      await api.changePassword(currentPassword, newPassword);
      setIsChangingPassword(false);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setMessage({ type: "success", text: "Password changed successfully" });
    } catch {
      setMessage({ type: "error", text: "Failed to change password. Current password may be incorrect." });
    }
  };

  const handleDeleteAccount = async () => {
    try {
      await api.deleteAccount(deletePassword);
      clearTokens();
      navigate("/login");
    } catch {
      setMessage({ type: "error", text: "Failed to delete account. Password may be incorrect." });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Profile Settings</h1>
          <button
            onClick={() => navigate("/chat")}
            className="px-4 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80"
          >
            Back to Chat
          </button>
        </div>

        {message && (
          <div
            className={`p-3 rounded ${
              message.type === "success" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Profile Section */}
        <div className="bg-card border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Profile Information</h2>
          {isEditing ? (
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input
                  type="email"
                  value={profile?.email || ""}
                  disabled
                  className="w-full px-3 py-2 bg-muted rounded border opacity-60"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3 py-2 rounded border"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleSaveProfile}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setFullName(profile?.full_name || "");
                  }}
                  className="px-4 py-2 bg-secondary rounded hover:bg-secondary/80"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <p>
                <span className="font-medium">Email:</span> {profile?.email}
              </p>
              <p>
                <span className="font-medium">Name:</span> {profile?.full_name || "Not set"}
              </p>
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-secondary rounded hover:bg-secondary/80"
              >
                Edit Profile
              </button>
            </div>
          )}
        </div>

        {/* Change Password Section */}
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Change Password</h2>
          {isChangingPassword ? (
            <div className="space-y-3">
              <input
                type="password"
                placeholder="Current password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full px-3 py-2 rounded border"
              />
              <input
                type="password"
                placeholder="New password (min 8 characters)"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-3 py-2 rounded border"
              />
              <input
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2 rounded border"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleChangePassword}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
                >
                  Change Password
                </button>
                <button
                  onClick={() => {
                    setIsChangingPassword(false);
                    setCurrentPassword("");
                    setNewPassword("");
                    setConfirmPassword("");
                  }}
                  className="px-4 py-2 bg-secondary rounded hover:bg-secondary/80"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsChangingPassword(true)}
              className="px-4 py-2 bg-secondary rounded hover:bg-secondary/80"
            >
              Change Password
            </button>
          )}
        </div>

        {/* Delete Account Section */}
        <div className="bg-card border border-destructive/50 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-destructive mb-4">Delete Account</h2>
          <p className="text-sm text-muted-foreground mb-4">
            This will permanently delete your account and all conversations.
          </p>
          {isDeleting ? (
            <div className="space-y-3">
              <input
                type="password"
                placeholder="Enter password to confirm"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                className="w-full px-3 py-2 rounded border"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleDeleteAccount}
                  className="px-4 py-2 bg-destructive text-destructive-foreground rounded hover:bg-destructive/90"
                >
                  Confirm Delete
                </button>
                <button
                  onClick={() => {
                    setIsDeleting(false);
                    setDeletePassword("");
                  }}
                  className="px-4 py-2 bg-secondary rounded hover:bg-secondary/80"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsDeleting(true)}
              className="px-4 py-2 bg-destructive text-destructive-foreground rounded hover:bg-destructive/90"
            >
              Delete Account
            </button>
          )}
        </div>
      </div>
    </div>
  );
}