import { useState, useCallback } from "react";
import { api, Message, Conversation } from "../api/client";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  conversations: Conversation[];
  loadConversations: () => Promise<void>;
  currentConversation: Conversation | null;
  setCurrentConversation: (conv: Conversation | null) => void;
  createNewConversation: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);

  const createNewConversation = useCallback(() => {
    setCurrentConversation(null);
    setMessages([]);
  }, []);

  const loadConversations = useCallback(async () => {
    try {
      const convs = await api.getConversations();
      setConversations(convs);
      if (convs.length > 0 && !currentConversation) {
        setCurrentConversation(convs[0]);
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  }, [currentConversation]);

  const loadMessages = useCallback(async (conversationId: string) => {
    try {
      const msgs = await api.getMessages(conversationId);
      setMessages(msgs);
    } catch (err) {
      console.error("Failed to load messages:", err);
      setError("Failed to load messages");
    }
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;
    
    setIsLoading(true);
    setError(null);

    // Optimistic add user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      token_count: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await api.sendMessage(content, currentConversation?.id);
      
      // Update conversation if it's new
      if (response.conversation && !currentConversation) {
        setCurrentConversation(response.conversation);
        await loadConversations();
      }

      // Add assistant message
      setMessages((prev) => [...prev, response.message]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  }, [currentConversation, loadConversations]);

  // Load messages when conversation changes
  useState(() => {
    if (currentConversation) {
      loadMessages(currentConversation.id);
    }
  });

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    conversations,
    loadConversations,
    currentConversation,
    setCurrentConversation,
    createNewConversation,
  };
}