import { useState, useEffect, useCallback } from "react";

interface KeyboardShortcut {
  key: string;
  modifiers?: ("ctrl" | "alt" | "shift" | "meta")[];
  description: string;
  action: () => void;
}

interface UseKeyboardShortcutsReturn {
  isCommandPaletteOpen: boolean;
  openCommandPalette: () => void;
  closeCommandPalette: () => void;
  toggleCommandPalette: () => void;
  shortcuts: KeyboardShortcut[];
}

export function useKeyboardShortcuts(
  shortcuts: KeyboardShortcut[]
): UseKeyboardShortcutsReturn {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  const openCommandPalette = useCallback(() => {
    setIsCommandPaletteOpen(true);
  }, []);

  const closeCommandPalette = useCallback(() => {
    setIsCommandPaletteOpen(false);
  }, []);

  const toggleCommandPalette = useCallback(() => {
    setIsCommandPaletteOpen((prev) => !prev);
  }, []);

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K to open command palette
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        toggleCommandPalette();
        return;
      }

      // Escape to close command palette
      if (e.key === "Escape" && isCommandPaletteOpen) {
        e.preventDefault();
        closeCommandPalette();
        return;
      }

      // Don't process other shortcuts if command palette is open
      if (isCommandPaletteOpen) {
        return;
      }

      // Escape to close modals/panels (general)
      if (e.key === "Escape") {
        e.preventDefault();
        closeCommandPalette();
        return;
      }

      // Check custom shortcuts
      for (const shortcut of shortcuts) {
        const modifiers = shortcut.modifiers || [];
        
        const ctrlMatch =
          modifiers.includes("ctrl") === (e.ctrlKey || e.metaKey);
        const altMatch = modifiers.includes("alt") === e.altKey;
        const shiftMatch = modifiers.includes("shift") === e.shiftKey;
        const metaMatch = modifiers.includes("meta") === e.metaKey;

        if (
          e.key.toLowerCase() === shortcut.key.toLowerCase() &&
          ctrlMatch &&
          altMatch &&
          shiftMatch &&
          metaMatch
        ) {
          e.preventDefault();
          shortcut.action();
          return;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [shortcuts, isCommandPaletteOpen, toggleCommandPalette, closeCommandPalette]);

  return {
    isCommandPaletteOpen,
    openCommandPalette,
    closeCommandPalette,
    toggleCommandPalette,
    shortcuts,
  };
}

// Default shortcuts
export const DEFAULT_SHORTCUTS: KeyboardShortcut[] = [
  {
    key: "k",
    modifiers: ["meta"],
    description: "Open command palette",
    action: () => {},
  },
  {
    key: "n",
    modifiers: ["meta"],
    description: "New conversation",
    action: () => {},
  },
  {
    key: "w",
    modifiers: ["meta"],
    description: "Close sidebar",
    action: () => {},
  },
  {
    key: "/",
    modifiers: ["meta"],
    description: "Focus search",
    action: () => {},
  },
  {
    key: "?",
    modifiers: ["shift"],
    description: "Show shortcuts",
    action: () => {},
  },
];
