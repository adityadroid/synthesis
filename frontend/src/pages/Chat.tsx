import { useState, useRef, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";
import { useChat } from "../hooks/useChat";
import { Message } from "../api/client";

function MessageBubble({ message, isNew }: { message: Message; isNew: boolean }) {
  const isUser = message.role === "user";
  
  return (
    <div 
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 animate-fade-in-up ${isNew ? 'animate-pulse' : ''}`}
      style={{ animationDelay: isNew ? '0ms' : '0ms' }}
    >
      <div
        className={`max-w-[70%] px-5 py-3 rounded-2xl transition-all duration-300 ${
          isUser
            ? "bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40"
            : "glass-card text-zinc-100 border border-zinc-800/50 hover:border-zinc-700/50"
        }`}
      >
        <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{message.content}</p>
        <div className={`flex items-center gap-2 mt-2 ${isUser ? "justify-end" : ""}`}>
          <span className={`text-xs ${isUser ? "text-white/50" : "text-zinc-500"}`}>
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="glass-card px-5 py-3 rounded-2xl border border-zinc-800/50">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span className="text-zinc-500 text-xs ml-2">Thinking...</span>
        </div>
      </div>
    </div>
  );
}

function ConversationItem({ 
  conversation, 
  isActive, 
  onClick 
}: { 
  conversation: { id: string; title: string | null; created_at: string };
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-3 rounded-xl text-sm transition-all duration-200 group ${
        isActive
          ? "bg-zinc-800/80 text-white border border-zinc-700/50"
          : "text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-300 border border-transparent"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors ${
          isActive 
            ? "bg-indigo-500/20 text-indigo-400" 
            : "bg-zinc-800/50 text-zinc-500 group-hover:text-zinc-400"
        }`}>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <span className="truncate block font-medium">
            {conversation.title || "New Chat"}
          </span>
          <span className="text-xs text-zinc-600 group-hover:text-zinc-500">
            {new Date(conversation.created_at).toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric'
            })}
          </span>
        </div>
      </div>
    </button>
  );
}

function NewChatButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white font-medium rounded-xl transition-all duration-200 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 hover:scale-[1.01] active:scale-[0.99]"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
      </svg>
      <span>New Chat</span>
    </button>
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
  } = useChat();
  
  const [input, setInput] = useState("");
  const [isInputFocused, setIsInputFocused] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const prevMessagesLength = useRef(messages.length);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    // Focus input when starting a new conversation
    if (messages.length === 0 && currentConversation) {
      inputRef.current?.focus();
    }
  }, [currentConversation, messages.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    await sendMessage(input);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleNewChat = () => {
    createNewConversation();
    setInput("");
    inputRef.current?.focus();
  };

  const displayName = user?.email?.split('@')[0] || 'User';
  const isNewMessage = messages.length > prevMessagesLength.current;
  
  useEffect(() => {
    prevMessagesLength.current = messages.length;
  }, [messages.length]);

  return (
    <div className="flex h-screen bg-zinc-950 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-72 bg-zinc-900/40 border-r border-zinc-800/50 flex flex-col backdrop-blur-sm hidden md:flex">
        {/* Header */}
        <div className="p-5 border-b border-zinc-800/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-lg font-bold text-white">Synthesis</h2>
              <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
            </div>
          </div>
          
          {/* New Chat Button */}
          <NewChatButton onClick={handleNewChat} />
        </div>
        
        {/* Conversations */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2 no-scrollbar">
          <div className="px-3 py-2 text-xs font-medium text-zinc-500 uppercase tracking-wider">
            Conversations
          </div>
          
          {conversations.length === 0 ? (
            <div className="text-center py-8 px-4">
              <div className="w-12 h-12 rounded-xl bg-zinc-800/50 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-zinc-600 text-sm">No conversations yet</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <ConversationItem
                key={conv.id}
                conversation={conv}
                isActive={currentConversation?.id === conv.id}
                onClick={() => setCurrentConversation(conv)}
              />
            ))
          )}
        </div>

        {/* User section */}
        <div className="p-4 border-t border-zinc-800/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-600 flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-semibold text-zinc-300">
                  {displayName.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-sm text-zinc-400 truncate">{displayName}</span>
            </div>
            <button
              onClick={logout}
              className="p-1.5 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-200"
              title="Logout"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </aside>

      {/* Main chat area */}
      <main className="flex-1 flex flex-col bg-zinc-950 relative">
        {/* Ambient background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-zinc-900 via-zinc-950 to-zinc-950 pointer-events-none" />
        
        {/* Mobile header */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 border-b border-zinc-800/30 bg-zinc-900/40 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="font-bold text-white">Synthesis</span>
          </div>
          <button
            onClick={handleNewChat}
            className="p-2 bg-zinc-800/60 hover:bg-zinc-700 text-zinc-400 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </header>

        {/* Messages container */}
        <div className="flex-1 overflow-y-auto p-6 relative">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              {/* Empty state icon */}
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-zinc-800/50 to-zinc-900/50 border border-zinc-700/30 flex items-center justify-center mb-6 animate-fade-in-scale">
                <svg className="w-10 h-10 text-zinc-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              
              <h3 className="text-xl font-medium text-white mb-2 animate-fade-in-up delay-100">
                Start a conversation
              </h3>
              <p className="text-zinc-500 text-sm max-w-sm animate-fade-in-up delay-200">
                Send a message below to begin chatting with AI. I can help you with coding, writing, analysis, and more.
              </p>
              
              {/* Quick prompts */}
              <div className="mt-8 grid gap-3 animate-fade-in-up delay-300 max-w-md w-full">
                {[
                  "Help me write a function",
                  "Explain a concept",
                  "Review my code",
                  "Brainstorm ideas"
                ].map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(prompt)}
                    className="p-4 bg-zinc-900/60 hover:bg-zinc-800/60 border border-zinc-800/50 hover:border-zinc-700/50 rounded-xl text-left transition-all duration-200 group"
                  >
                    <span className="text-zinc-400 group-hover:text-zinc-300 text-sm">{prompt}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto">
              {messages.map((msg, index) => (
                <MessageBubble 
                  key={msg.id} 
                  message={msg} 
                  isNew={index === messages.length - 1 && isNewMessage}
                />
              ))}
            </div>
          )}
          
          {isLoading && <TypingIndicator />}
          
          {error && (
            <div className="max-w-4xl mx-auto">
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm flex items-start gap-3 animate-fade-in">
                <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>{error}</p>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="p-4 border-t border-zinc-800/30 relative">
          <div className="max-w-4xl mx-auto">
            <form 
              onSubmit={handleSubmit} 
              className={`relative transition-all duration-200 ${isInputFocused ? 'scale-[1.01]' : ''}`}
            >
              <div className="relative flex items-end gap-3">
                {/* Input field */}
                <div className="flex-1 relative">
                  <textarea
                    ref={(el) => {
                      // Maintain ref for focus
                      if (el) inputRef.current = el;
                    }}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onFocus={() => setIsInputFocused(true)}
                    onBlur={() => setIsInputFocused(false)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    className="w-full px-5 py-3.5 bg-zinc-900/80 text-white text-sm rounded-xl border border-zinc-800/50 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:outline-none transition-all duration-200 placeholder-zinc-500 resize-none min-h-[52px] max-h-48 scrollbar-hide"
                    rows={1}
                    disabled={isLoading}
                  />
                  
                  {/* Send button */}
                  <button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className={`absolute right-2 bottom-2 p-2 rounded-xl transition-all duration-200 ${
                      input.trim() && !isLoading
                        ? "bg-gradient-to-r from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-105 active:scale-95"
                        : "bg-zinc-800 text-zinc-500 cursor-not-allowed"
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
              </div>
            </form>
            
            <p className="text-center text-xs text-zinc-600 mt-3">
              AI can make mistakes. Consider checking important information.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
