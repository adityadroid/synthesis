import { useState, useRef, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { useChat } from "../hooks/useChat";
import { useTheme } from "../hooks/useTheme";
import { useKeyboardShortcuts, DEFAULT_SHORTCUTS } from "../hooks/useKeyboardShortcuts";
import { useConversationSearch } from "../hooks/useSearch";
import { useMessageReactions, ReactionPicker } from "../hooks/useMessageReactions.tsx";
import { CommandPalette } from "../components/ui/CommandPalette";
import { ThemeToggle } from "../components/Chat/ThemeToggle";
import { SettingsPanel } from "../components/Chat/SettingsPanel";
import { ModelSettings } from "../components/Chat/ModelSettings";
import { ModelSelector } from "../components/Chat/ModelSelector";
import { SystemPromptEditor } from "../components/Chat/SystemPromptEditor";
import { ExportMenu } from "../components/Chat/ExportMenu";
import { JumpToMessage } from "../components/Chat/JumpToMessage";
import { MessageContent } from "../components/Chat/MessageContent";
import { VoiceInput } from "../components/Chat/VoiceInput";
import { TemplateBrowser } from "../components/Chat/TemplateBrowser";
import { api, Message, Conversation } from "../api/client";

function MessageBubble({
  message,
  onEdit,
  isHighlighted,
  onRetry,
  onRegenerate,
  isLastAssistant,
  isRetrying,
}: {
  message: Message;
  onEdit?: (messageId: string, content: string) => void;
  isHighlighted?: boolean;
  onRetry?: (messageId: string) => void;
  onRegenerate?: (messageId: string) => void;
  isLastAssistant?: boolean;
  isRetrying?: boolean;
}) {
  const isUser = message.role === "user";
  const [showActions, setShowActions] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [_isSaving, setIsSaving] = useState(false);
  const { getReactions, toggleReaction } = useMessageReactions();
  const [showReactionPicker, setShowReactionPicker] = useState(false);
  const reactions = getReactions(message.id);

  const handleSaveEdit = async () => {
    if (!editContent.trim() || editContent === message.content) {
      setIsEditing(false);
      return;
    }
    
    setIsSaving(true);
    try {
      const updated = await api.updateMessage(message.id, editContent);
      onEdit?.(message.id, updated.content);
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to update message:", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} ${
        isHighlighted ? "ring-2 ring-ring ring-offset-2 ring-offset-background rounded-lg" : ""
      }`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => {
        setShowActions(false);
        setShowReactionPicker(false);
      }}
    >
      <div
        className={`max-w-[80%] px-4 py-3 rounded-lg relative group ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-secondary text-secondary-foreground"
        }`}
      >
        {isEditing ? (
          <div className="space-y-2">
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="w-full min-h-[60px] px-2 py-1 bg-background text-foreground rounded border focus:outline-none focus:ring-2 focus:ring-ring resize-none"
              autoFocus
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setIsEditing(false)}
                className="px-2 py-1 text-xs bg-muted rounded hover:bg-muted/80"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-2 py-1 text-xs bg-primary text-primary-foreground rounded hover:bg-primary/90"
              >
                Save
              </button>
            </div>
          </div>
        ) : (
          <>
            {/* Render images if present */}
            {message.images && message.images.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-2">
                {message.images.map((img, idx) => (
                  <img
                    key={idx}
                    src={img.url}
                    alt={img.alt_text || "Uploaded image"}
                    className="max-w-[200px] max-h-[200px] rounded-lg object-cover"
                  />
                ))}
              </div>
            )}
            <MessageContent content={message.content} />
            <div className={`flex items-center gap-2 mt-1 ${isUser ? "justify-end" : ""}`}>
              {reactions.length > 0 && (
                <div className="flex gap-1">
                  {reactions.map((r) => (
                    <button
                      key={r.emoji}
                      onClick={() => toggleReaction(message.id, r.emoji)}
                      className={`flex items-center gap-0.5 px-1 py-0.5 text-xs rounded ${
                        r.hasReacted ? "bg-accent/20" : "bg-muted/50"
                      }`}
                    >
                      <span>{r.emoji}</span>
                      <span>{r.count}</span>
                    </button>
                  ))}
                </div>
              )}
              <span className={`text-xs ${isUser ? "text-primary-foreground/50" : "text-muted-foreground"}`}>
                {new Date(message.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </>
        )}

        {/* Action buttons */}
        {showActions && !isEditing && (
          <div className={`absolute ${isUser ? "-left-16" : "-right-16"} top-0 flex gap-1`}>
            {isUser && (
              <button
                onClick={() => setIsEditing(true)}
                className="p-1.5 bg-muted rounded hover:bg-muted/80 text-xs"
                title="Edit message"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            )}
            {/* Retry button for failed messages */}
            {onRetry && !isUser && (
              <button
                onClick={() => onRetry(message.id)}
                className="p-1.5 bg-muted rounded hover:bg-muted/80 text-xs"
                title="Retry"
                disabled={isRetrying}
              >
                {isRetrying ? (
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                )}
              </button>
            )}
            {/* Regenerate button for last assistant message */}
            {onRegenerate && !isUser && isLastAssistant && (
              <button
                onClick={() => onRegenerate(message.id)}
                className="p-1.5 bg-muted rounded hover:bg-muted/80 text-xs"
                title="Regenerate"
                disabled={isRetrying}
              >
                {isRetrying ? (
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                )}
              </button>
            )}
            <button
              onClick={() => navigator.clipboard.writeText(message.content)}
              className="p-1.5 bg-muted rounded hover:bg-muted/80 text-xs"
              title="Copy message"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
            <button
              onClick={() => setShowReactionPicker(true)}
              className="p-1.5 bg-muted rounded hover:bg-muted/80 text-xs"
              title="Add reaction"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
        )}

        {/* Reaction picker */}
        <div className="relative">
          <ReactionPicker
            messageId={message.id}
            isOpen={showReactionPicker}
            onClose={() => setShowReactionPicker(false)}
            onSelect={(emoji) => {
              toggleReaction(message.id, emoji);
              setShowReactionPicker(false);
            }}
          />
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-secondary px-4 py-3 rounded-lg border border-border">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
          <span className="text-xs text-muted-foreground ml-2">Thinking...</span>
        </div>
      </div>
    </div>
  );
}

function ConversationItem({
  conversation,
  isActive,
  onClick,
  onRename,
  onDelete,
  onClear,
}: {
  conversation: { id: string; title: string | null; created_at: string; updated_at?: string };
  isActive: boolean;
  onClick: () => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string) => void;
  onClear: (id: string) => void;
}) {
  const [showActions, setShowActions] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title || "");

  const handleRename = () => {
    if (editTitle.trim() && editTitle !== conversation.title) {
      onRename(conversation.id, editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowMenu(true);
  };

  if (isEditing) {
    return (
      <div className="w-full">
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleRename();
            if (e.key === "Escape") {
              setIsEditing(false);
              setEditTitle(conversation.title || "");
            }
          }}
          onBlur={handleRename}
          className="w-full px-3 py-2 bg-background border border-ring text-sm text-foreground rounded-md focus:outline-none"
          autoFocus
        />
      </div>
    );
  }

  return (
    <div
      className={`relative w-full text-left px-3 py-2 rounded-md text-sm transition-colors group ${
        isActive
          ? "bg-secondary text-foreground"
          : "text-muted-foreground hover:bg-secondary hover:text-foreground"
      }`}
      onClick={onClick}
      onContextMenu={handleContextMenu}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => {
        setShowActions(false);
        setShowMenu(false);
      }}
    >
      <span className="truncate block">{conversation.title || "New Chat"}</span>

      {/* Hover actions */}
      {showActions && !isActive && (
        <div className="absolute right-1 top-1/2 -translate-y-1/2 flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
              setEditTitle(conversation.title || "");
            }}
            className="p-1 hover:bg-accent rounded"
            title="Rename"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClear(conversation.id);
            }}
            className="p-1 hover:bg-accent rounded"
            title="Clear messages"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(conversation.id);
            }}
            className="p-1 hover:bg-destructive/20 hover:text-destructive rounded"
            title="Delete"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      )}

      {/* Context menu */}
      {showMenu && (
        <div className="absolute left-full ml-1 top-0 z-50 bg-popover border rounded-md shadow-lg py-1 min-w-[140px]">
          <button
            onClick={() => {
              setIsEditing(true);
              setEditTitle(conversation.title || "");
              setShowMenu(false);
            }}
            className="w-full px-3 py-1.5 text-left text-sm hover:bg-accent"
          >
            Rename
          </button>
          <button
            onClick={() => {
              onClear(conversation.id);
              setShowMenu(false);
            }}
            className="w-full px-3 py-1.5 text-left text-sm hover:bg-accent"
          >
            Clear Messages
          </button>
          <button
            onClick={() => {
              onDelete(conversation.id);
              setShowMenu(false);
            }}
            className="w-full px-3 py-1.5 text-left text-sm hover:bg-destructive/20 text-destructive"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
}

export function ChatPage() {
  const { user, logout } = useAuth();
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    conversations,
    loadConversations,
    currentConversation,
    setCurrentConversation,
    createNewConversation,
    renameConversation,
    deleteConversation,
    clearConversation,
    searchConversations,
  } = useChat();
  useTheme(); // Initialize theme hook

  // UI state
  const [input, setInput] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [showModelSettings, setShowModelSettings] = useState(false);
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showJumpToMessage, setShowJumpToMessage] = useState(false);
  const [showVoiceInput, setShowVoiceInput] = useState(false);
  const [showTemplateBrowser, setShowTemplateBrowser] = useState(false);
  const [currentModel, setCurrentModel] = useState<string | null>(null);
  const [highlightedMessageIndex, setHighlightedMessageIndex] = useState<number | null>(null);
  const [retryingMessageId, setRetryingMessageId] = useState<string | null>(null);
  const [regeneratingMessageId, setRegeneratingMessageId] = useState<string | null>(null);
  
  // Sidebar state
  const [conversationSearch, setConversationSearch] = useState("");
  const [filteredConversations, setFilteredConversations] = useState<Conversation[]>([]);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messageRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Search
  const { query: searchQuery, setQuery: setSearchQuery, matches, currentMatch } = useConversationSearch(messages);

  // Keyboard shortcuts
  const shortcuts = [
    ...DEFAULT_SHORTCUTS,
    {
      key: "n",
      modifiers: ["meta"] as ("meta" | "ctrl" | "alt" | "shift")[],
      description: "New conversation",
      action: () => {
        createNewConversation();
        inputRef.current?.focus();
      },
    },
    {
      key: "s",
      modifiers: ["meta"] as ("meta" | "ctrl" | "alt" | "shift")[],
      description: "Toggle settings",
      action: () => setShowSettings((v) => !v),
    },
  ];
  const { isCommandPaletteOpen, openCommandPalette, closeCommandPalette } = useKeyboardShortcuts(shortcuts);

  // Command palette items
  const commandItems = [
    {
      id: "new-chat",
      label: "New Chat",
      action: () => {
        createNewConversation();
        inputRef.current?.focus();
      },
    },
    {
      id: "templates",
      label: "Browse Templates",
      action: () => setShowTemplateBrowser(true),
    },
    {
      id: "settings",
      label: "Settings",
      action: () => setShowSettings(true),
    },
    {
      id: "model-settings",
      label: "AI Settings",
      action: () => setShowModelSettings(true),
    },
    {
      id: "export",
      label: "Export Conversation",
      action: () => setShowExportMenu(true),
    },
    {
      id: "jump",
      label: "Jump to Message",
      action: () => setShowJumpToMessage(true),
    },
    {
      id: "theme",
      label: "Toggle Theme",
      action: () => document.documentElement.classList.toggle("dark"),
    },
  ];

  // Effects
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (messages.length === 0 && currentConversation) {
      inputRef.current?.focus();
    }
  }, [currentConversation, messages.length]);

  // Filter conversations based on search
  useEffect(() => {
    if (conversationSearch.trim()) {
      searchConversations(conversationSearch).then(setFilteredConversations);
    } else {
      setFilteredConversations(conversations);
    }
  }, [conversationSearch, conversations, searchConversations]);

  // Handlers
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    await sendMessage(input);
    setInput("");
  };

  const handleRetry = async (assistantMessageId: string) => {
    const msgIndex = messages.findIndex((m) => m.id === assistantMessageId);
    if (msgIndex === -1) return;
    
    // Find the user message before this assistant message
    const userMsgIndex = messages.slice(0, msgIndex).reverse().findIndex((m) => m.role === "user");
    if (userMsgIndex === -1) return;
    
    const userMessage = messages[msgIndex - 1 - userMsgIndex];
    if (!userMessage) return;
    
    setRetryingMessageId(assistantMessageId);
    try {
      // Re-send the user message to get a new response
      // Note: This adds a duplicate user message and new response
      await sendMessage(userMessage.content);
    } catch (error) {
      console.error("Retry failed:", error);
    } finally {
      setRetryingMessageId(null);
    }
  };

  const handleRegenerate = async (assistantMessageId: string) => {
    const msgIndex = messages.findIndex((m) => m.id === assistantMessageId);
    if (msgIndex === -1) return;
    
    // Find the user message that prompted this response
    const userMsgIndex = messages.slice(0, msgIndex).reverse().findIndex((m) => m.role === "user");
    if (userMsgIndex === -1) return;
    
    const userMessage = messages[msgIndex - 1 - userMsgIndex];
    if (!userMessage) return;
    
    setRegeneratingMessageId(assistantMessageId);
    try {
      // Re-send the user message to regenerate the response
      await sendMessage(userMessage.content);
    } catch (error) {
      console.error("Regenerate failed:", error);
    } finally {
      setRegeneratingMessageId(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
    // Search navigation
    if (searchQuery && matches.length > 0) {
      if (e.key === "Enter" && e.shiftKey) {
        e.preventDefault();
        setHighlightedMessageIndex(matches[currentMatch]);
        messageRefs.current[matches[currentMatch]]?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      }
    }
  };

  const handleNewChat = () => {
    createNewConversation();
    setInput("");
    inputRef.current?.focus();
  };

  const handleJumpToMessage = (index: number) => {
    setHighlightedMessageIndex(index);
    messageRefs.current[index]?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
    // Clear highlight after 2 seconds
    setTimeout(() => setHighlightedMessageIndex(null), 2000);
  };

  const displayName = user?.email?.split("@")[0] || "User";

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-card border-r border-border flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-md bg-secondary flex items-center justify-center">
              <svg className="w-4 h-4 text-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-sm font-semibold text-foreground">Synthesis</h2>
              <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
            </div>
          </div>

          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 font-medium rounded-md transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New Chat</span>
          </button>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto p-2">
          {/* Search conversations */}
          <div className="px-2 mb-2">
            <div className="relative">
              <input
                type="text"
                value={conversationSearch}
                onChange={(e) => setConversationSearch(e.target.value)}
                placeholder="Search conversations..."
                className="w-full px-3 py-1.5 bg-background border border-input rounded-md text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
              {conversationSearch && (
                <button
                  onClick={() => setConversationSearch("")}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
          
          <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Conversations
          </div>

          {filteredConversations.length === 0 ? (
            <div className="text-center py-8 px-4">
              <p className="text-muted-foreground text-sm">
                {conversationSearch ? "No matching conversations" : "No conversations"}
              </p>
            </div>
          ) : (
            filteredConversations.map((conv) => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                isActive={currentConversation?.id === conv.id}
                onClick={() => setCurrentConversation(conv)}
                onRename={renameConversation}
                onDelete={deleteConversation}
                onClear={clearConversation}
              />
            ))
          )}
        </div>

        {/* User section */}
        <div className="p-3 border-t border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-7 h-7 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-medium text-foreground">
                  {displayName.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-sm text-muted-foreground truncate">{displayName}</span>
            </div>
            <button
              onClick={logout}
              className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
              title="Logout"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </aside>

      {/* Main chat area */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="px-4 py-3 border-b border-border bg-card flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowModelSelector(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-secondary rounded-md hover:bg-secondary/80 transition-colors"
            >
              <span className="text-sm font-medium">{currentModel || "Select Model"}</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Search */}
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search messages..."
                className="w-48 px-3 py-1.5 bg-background border border-input rounded-md text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
              {matches.length > 0 && (
                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                  {currentMatch + 1}/{matches.length}
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSystemPrompt(true)}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
              title="System Prompt"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </button>

            <button
              onClick={() => setShowModelSettings(true)}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
              title="AI Settings"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>

            <ThemeToggle />

            <div className="relative">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
                title="Export"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </button>
              {currentConversation && showExportMenu && (
                <ExportMenu
                  conversation={currentConversation}
                  onClose={() => setShowExportMenu(false)}
                  onClear={() => clearConversation(currentConversation.id)}
                />
              )}
            </div>

            <button
              onClick={() => setShowSettings(true)}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
              title="Settings"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <button
              onClick={openCommandPalette}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
              title="Command Palette (Cmd+K)"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </header>

        {/* Messages container */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="w-16 h-16 rounded-lg bg-secondary flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>

              <h3 className="text-lg font-semibold text-foreground mb-2">
                Start a conversation
              </h3>
              <p className="text-muted-foreground text-sm max-w-md">
                Send a message to begin chatting with AI.
              </p>

              {/* Quick prompts */}
              <div className="mt-6 grid grid-cols-2 gap-2 max-w-md w-full">
                {[
                  "Help me write code",
                  "Explain a concept",
                  "Review my code",
                  "Brainstorm ideas",
                ].map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(prompt)}
                    className="p-3 bg-secondary text-muted-foreground hover:text-foreground text-sm rounded-md transition-colors text-left"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4 max-w-3xl mx-auto">
              {messages.map((msg, index) => {
                const isLastAssistant = msg.role === "assistant" && index === messages.length - 1;
                return (
                  <div
                    key={msg.id}
                    ref={(el) => { messageRefs.current[index] = el; }}
                  >
                    <MessageBubble
                      message={msg}
                      isHighlighted={highlightedMessageIndex === index}
                      onRetry={error ? handleRetry : undefined}
                      onRegenerate={isLastAssistant && !isLoading && !error ? handleRegenerate : undefined}
                      isLastAssistant={isLastAssistant}
                      isRetrying={retryingMessageId === msg.id || regeneratingMessageId === msg.id}
                    />
                  </div>
                );
              })}
            </div>
          )}

          {isLoading && <TypingIndicator />}

          {error && (
            <div className="max-w-3xl mx-auto">
              <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-destructive text-sm">
                {error}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="px-4 py-4 border-t border-border">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="relative flex items-end gap-2">
              {/* Voice Input */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowVoiceInput(!showVoiceInput)}
                  className="p-3 rounded-lg bg-secondary text-muted-foreground hover:text-foreground hover:bg-secondary/80 transition-colors"
                  title="Voice input"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>
                {showVoiceInput && (
                  <VoiceInput
                    onTranscript={(text) => {
                      setInput((prev) => prev + (prev ? " " : "") + text);
                      setShowVoiceInput(false);
                    }}
                    disabled={isLoading}
                  />
                )}
              </div>

              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                className="w-full px-4 py-3 bg-background border border-input text-foreground text-sm rounded-lg focus:outline-none focus:ring-2 focus:ring-ring resize-none min-h-[60px] max-h-40 placeholder:text-muted-foreground"
                rows={1}
                disabled={isLoading}
              />

              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className={`p-3 rounded-lg transition-colors ${
                  input.trim() && !isLoading
                    ? "bg-primary text-primary-foreground hover:bg-primary/90"
                    : "bg-secondary text-muted-foreground cursor-not-allowed"
                }`}
              >
                {isLoading ? (
                  <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                )}
              </button>
            </div>
          </form>

          <p className="text-center text-xs text-muted-foreground mt-3">
            AI can make mistakes. Consider checking important information.
          </p>
        </div>
      </main>

      {/* Modals & Panels */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={closeCommandPalette}
        items={commandItems.map((item) => ({
          ...item,
          icon: (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          ),
        }))}
      />

      <SettingsPanel isOpen={showSettings} onClose={() => setShowSettings(false)} />

      <ModelSettings
        isOpen={showModelSettings}
        onClose={() => setShowModelSettings(false)}
        onSettingsChange={() => {}}
        conversationId={currentConversation?.id}
      />

      <ModelSelector
        currentModel={currentModel}
        onModelChange={setCurrentModel}
        isOpen={showModelSelector}
        onClose={() => setShowModelSelector(false)}
      />

      <SystemPromptEditor
        initialValue=""
        onSave={(prompt) => console.log("System prompt:", prompt)}
        isOpen={showSystemPrompt}
        onClose={() => setShowSystemPrompt(false)}
      />

      <JumpToMessage
        totalMessages={messages.length}
        onJump={handleJumpToMessage}
        isOpen={showJumpToMessage}
        onClose={() => setShowJumpToMessage(false)}
      />

      {showTemplateBrowser && (
        <TemplateBrowser
          onSelect={(prompt) => {
            setInput(prompt);
            setShowTemplateBrowser(false);
            inputRef.current?.focus();
          }}
          onClose={() => setShowTemplateBrowser(false)}
        />
      )}
    </div>
  );
}
