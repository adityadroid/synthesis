import { useState, useCallback, useRef, useEffect } from "react";
import { api, Message } from "../api/client";

interface SearchResult {
  message_id: string;
  conversation_id: string;
  conversation_title: string;
  content: string;
  role: string;
  created_at: string;
  snippet: string;
}

interface UseGlobalSearchReturn {
  query: string;
  setQuery: (query: string) => void;
  results: SearchResult[];
  isSearching: boolean;
  search: () => Promise<void>;
  clearSearch: () => void;
}

export function useGlobalSearch(): UseGlobalSearchReturn {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const abortController = useRef<AbortController | null>(null);

  const search = useCallback(async () => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    // Cancel previous request
    if (abortController.current) {
      abortController.current.abort();
    }
    abortController.current = new AbortController();

    setIsSearching(true);
    try {
      // For now, we'll search locally in messages
      // In a full implementation, this would call the backend API
      const conversations = await api.getConversations();
      const allResults: SearchResult[] = [];

      for (const conv of conversations.slice(0, 10)) {
        // Limit to recent conversations
        try {
          const messages = await api.getMessages(conv.id);
          const matchingMessages = messages.filter((msg) =>
            msg.content.toLowerCase().includes(query.toLowerCase())
          );

          for (const msg of matchingMessages) {
            // Create snippet with context
            const index = msg.content.toLowerCase().indexOf(query.toLowerCase());
            const start = Math.max(0, index - 30);
            const end = Math.min(msg.content.length, index + query.length + 30);
            let snippet = msg.content.slice(start, end);
            if (start > 0) snippet = "..." + snippet;
            if (end < msg.content.length) snippet = snippet + "...";

            allResults.push({
              message_id: msg.id,
              conversation_id: conv.id,
              conversation_title: conv.title || "Untitled",
              content: msg.content,
              role: msg.role,
              created_at: msg.created_at,
              snippet,
            });
          }
        } catch {
          // Skip conversations we can't access
        }
      }

      setResults(allResults);
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        console.error("Search failed:", error);
      }
    } finally {
      setIsSearching(false);
    }
  }, [query]);

  const clearSearch = useCallback(() => {
    setQuery("");
    setResults([]);
  }, []);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim()) {
        search();
      } else {
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, search]);

  return {
    query,
    setQuery,
    results,
    isSearching,
    search,
    clearSearch,
  };
}

interface UseConversationSearchReturn {
  query: string;
  setQuery: (query: string) => void;
  matches: number[];
  currentMatch: number;
  nextMatch: () => void;
  prevMatch: () => void;
  highlightMessage: (messageId: string, content: string) => boolean;
}

export function useConversationSearch(messages: Message[]): UseConversationSearchReturn {
  const [query, setQuery] = useState("");
  const [matches, setMatches] = useState<number[]>([]);
  const [currentMatch, setCurrentMatch] = useState(0);

  // Find matching message indices
  useEffect(() => {
    if (!query.trim()) {
      setMatches([]);
      return;
    }

    const indices: number[] = [];
    messages.forEach((msg, index) => {
      if (msg.content.toLowerCase().includes(query.toLowerCase())) {
        indices.push(index);
      }
    });
    setMatches(indices);
    setCurrentMatch(0);
  }, [query, messages]);

  const nextMatch = useCallback(() => {
    setCurrentMatch((prev) => (prev < matches.length - 1 ? prev + 1 : 0));
  }, [matches.length]);

  const prevMatch = useCallback(() => {
    setCurrentMatch((prev) => (prev > 0 ? prev - 1 : matches.length - 1));
  }, [matches.length]);

  const highlightMessage = useCallback(
    (messageId: string, _content: string): boolean => {
      if (!query.trim() || matches.length === 0) return false;
      const messageIndex = messages.findIndex((m) => m.id === messageId);
      return matches[currentMatch] === messageIndex;
    },
    [query, matches, currentMatch, messages]
  );

  return {
    query,
    setQuery,
    matches,
    currentMatch,
    nextMatch,
    prevMatch,
    highlightMessage,
  };
}
