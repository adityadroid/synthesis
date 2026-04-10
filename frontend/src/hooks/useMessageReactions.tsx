import { useState, useCallback, useEffect } from "react";
import { getAccessToken } from "../api/client";

interface MessageReaction {
  emoji: string;
  count: number;
  hasReacted: boolean;
}

interface UseMessageReactionsReturn {
  getReactions: (messageId: string) => MessageReaction[];
  addReaction: (messageId: string, emoji: string) => void;
  removeReaction: (messageId: string, emoji: string) => void;
  toggleReaction: (messageId: string, emoji: string) => void;
}

const QUICK_REACTIONS = ["👍", "👎", "❤️", "😂", "😮", "😢", "🙏"];
const STORAGE_KEY = "synthesis-reactions";
const USER_ID_KEY = "synthesis-user-id";

type ReactionsMap = Record<string, Record<string, { count: number; users: string[] }>>;

function loadReactions(): ReactionsMap {
  if (typeof window === "undefined") return {};
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : {};
}

function saveReactions(reactions: ReactionsMap) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reactions));
}

function getCurrentUserId(): string {
  if (typeof window === "undefined") return "anonymous";
  // Try to get from stored user, fallback to token hash
  let userId = localStorage.getItem(USER_ID_KEY);
  if (!userId) {
    const token = getAccessToken();
    if (token) {
      // Create a hash-like ID from token (first 16 chars)
      userId = `user-${token.substring(0, 16)}`;
      localStorage.setItem(USER_ID_KEY, userId);
    } else {
      userId = "anonymous";
    }
  }
  return userId;
}

export function useMessageReactions(): UseMessageReactionsReturn {
  const [reactions, setReactions] = useState<ReactionsMap>(loadReactions);
  const [userId, setUserId] = useState<string>("anonymous");

  // Get user ID on mount
  useEffect(() => {
    setUserId(getCurrentUserId());
  }, []);

  const getReactions = useCallback(
    (messageId: string): MessageReaction[] => {
      const messageReactions = reactions[messageId] || {};

      return QUICK_REACTIONS.map((emoji) => {
        const reaction = messageReactions[emoji] || { count: 0, users: [] };
        return {
          emoji,
          count: reaction.count,
          hasReacted: reaction.users.includes(userId),
        };
      }).filter((r) => r.count > 0);
    },
    [reactions, userId]
  );

  const updateReactions = useCallback(
    (messageId: string, updater: (prev: ReactionsMap[string]) => ReactionsMap[string]) => {
      setReactions((prev) => {
        const updated = {
          ...prev,
          [messageId]: updater(prev[messageId] || {}),
        };
        saveReactions(updated);
        return updated;
      });
    },
    []
  );

  const addReaction = useCallback(
    (messageId: string, emoji: string) => {
      updateReactions(messageId, (prev) => {
        const existing = prev[emoji] || { count: 0, users: [] };
        if (existing.users.includes(userId)) return prev;
        return {
          ...prev,
          [emoji]: {
            count: existing.count + 1,
            users: [...existing.users, userId],
          },
        };
      });
    },
    [updateReactions, userId]
  );

  const removeReaction = useCallback(
    (messageId: string, emoji: string) => {
      updateReactions(messageId, (prev) => {
        const existing = prev[emoji] || { count: 0, users: [] };
        if (!existing.users.includes(userId)) return prev;
        return {
          ...prev,
          [emoji]: {
            count: Math.max(0, existing.count - 1),
            users: existing.users.filter((u) => u !== userId),
          },
        };
      });
    },
    [updateReactions, userId]
  );

  const toggleReaction = useCallback(
    (messageId: string, emoji: string) => {
      const messageReactions = reactions[messageId] || {};
      const existing = messageReactions[emoji] || { count: 0, users: [] };

      if (existing.users.includes(userId)) {
        removeReaction(messageId, emoji);
      } else {
        addReaction(messageId, emoji);
      }
    },
    [reactions, addReaction, removeReaction, userId]
  );

  return {
    getReactions,
    addReaction,
    removeReaction,
    toggleReaction,
  };
}

interface ReactionPickerProps {
  messageId: string;
  onSelect: (emoji: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function ReactionPicker({
  messageId: _messageId,
  onSelect,
  isOpen,
  onClose,
}: ReactionPickerProps) {
  if (!isOpen) return null;

  return (
    <div className="absolute -top-2 right-0 transform -translate-y-full z-10">
      <div className="bg-popover border border-border rounded-lg shadow-lg p-1 flex gap-1">
        {QUICK_REACTIONS.map((emoji) => (
          <button
            key={emoji}
            onClick={() => {
              onSelect(emoji);
              onClose();
            }}
            className="p-1.5 hover:bg-secondary rounded transition-colors text-lg"
          >
            {emoji}
          </button>
        ))}
      </div>
    </div>
  );
}
