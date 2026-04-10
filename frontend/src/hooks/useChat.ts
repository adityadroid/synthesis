import { useState, useCallback, useEffect } from "react";
import { api, Message, Conversation, ImageContent } from "../api/client";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string, model?: string, images?: ImageContent[]) => Promise<void>;
  conversations: Conversation[];
  loadConversations: () => Promise<void>;
  currentConversation: Conversation | null;
  setCurrentConversation: (conv: Conversation | null) => void;
  createNewConversation: () => void;
  renameConversation: (conversationId: string, newTitle: string) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  clearConversation: (conversationId: string) => Promise<void>;
  searchConversations: (query: string) => Promise<Conversation[]>;
  currentModel: string | null;
  setCurrentModel: (model: string | null) => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [currentModel, setCurrentModel] = useState<string | null>(null);

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

  const sendMessage = useCallback(async (content: string, model?: string, images?: ImageContent[]) => {
    if (!content.trim()) return;
    
    setIsLoading(true);
    setError(null);

    // Use provided model or fall back to currentModel (from conversation)
    const selectedModel = model || currentModel || currentConversation?.model || undefined;

    // Optimistic add user message
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content,
      token_count: null,
      created_at: new Date().toISOString(),
      model: selectedModel || null,
      images: images || null,
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      // If we have a conversation, use streaming
      if (currentConversation?.id) {
        const assistantMessageId = `temp-assistant-${Date.now()}`;
        let assistantContent = "";

        // Add placeholder for assistant message
        const assistantMessage: Message = {
          id: assistantMessageId,
          role: "assistant",
          content: "",
          token_count: null,
          created_at: new Date().toISOString(),
          model: selectedModel || null,
          images: null,
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Stream the response
        try {
          for await (const chunk of api.streamMessage(currentConversation.id, content, selectedModel, images)) {
            if (!chunk.done) {
              assistantContent += chunk.content;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMessageId
                    ? { ...m, content: assistantContent }
                    : m
                )
              );
            }
          }
        } catch (streamErr) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMessageId
                ? { ...m, content: "Error: Failed to get response" }
                : m
            )
          );
          setError(streamErr instanceof Error ? streamErr.message : "Stream failed");
        }
      } else {
        // No conversation yet, use send endpoint
        const response = await api.sendMessage(content, currentConversation?.id, selectedModel, images);
        
        // Update conversation if it's new
        if (response.conversation && !currentConversation) {
          setCurrentConversation(response.conversation);
          await loadConversations();
        }

        // Update model if set
        if (response.conversation?.model) {
          setCurrentModel(response.conversation.model);
        }

        // Replace optimistic message with real one and add assistant message
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== userMessage.id);
          return [...filtered, response.message];
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      // Remove optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  }, [currentConversation, currentModel, loadConversations]);

  const renameConversation = useCallback(async (conversationId: string, newTitle: string) => {
    try {
      const updated = await api.renameConversation(conversationId, newTitle);
      setConversations((prev) =>
        prev.map((c) => (c.id === conversationId ? updated : c))
      );
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(updated);
      }
    } catch (err) {
      console.error("Failed to rename conversation:", err);
      setError("Failed to rename conversation");
    }
  }, [currentConversation]);

  const deleteConversation = useCallback(async (conversationId: string) => {
    try {
      await api.deleteConversation(conversationId);
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
      setError("Failed to delete conversation");
    }
  }, [currentConversation]);

  const clearConversation = useCallback(async (conversationId: string) => {
    try {
      await api.clearConversation(conversationId);
      if (currentConversation?.id === conversationId) {
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to clear conversation:", err);
      setError("Failed to clear messages");
    }
  }, [currentConversation]);

  const searchConversations = useCallback(async (query: string): Promise<Conversation[]> => {
    try {
      return await api.searchConversations(query);
    } catch (err) {
      console.error("Failed to search conversations:", err);
      return [];
    }
  }, []);

  // Load messages and model when conversation changes
  useEffect(() => {
    if (currentConversation) {
      loadMessages(currentConversation.id);
      setCurrentModel(currentConversation.model);
    }
  }, [currentConversation, loadMessages]);

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
    renameConversation,
    deleteConversation,
    clearConversation,
    searchConversations,
    currentModel,
    setCurrentModel,
  };
}