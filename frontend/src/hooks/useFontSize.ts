import { useState, useEffect, useCallback } from "react";

interface UseFontSizeReturn {
  fontSize: number;
  setFontSize: (size: number) => void;
  increaseFontSize: () => void;
  decreaseFontSize: () => void;
  resetFontSize: () => void;
}

const STORAGE_KEY = "synthesis-font-size";
const MIN_FONT_SIZE = 12;
const MAX_FONT_SIZE = 24;
const DEFAULT_FONT_SIZE = 14;
const FONT_SIZE_STEP = 1;

export function useFontSize(): UseFontSizeReturn {
  const [fontSize, setFontSizeState] = useState<number>(() => {
    if (typeof window === "undefined") return DEFAULT_FONT_SIZE;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? parseInt(stored, 10) : DEFAULT_FONT_SIZE;
  });

  // Apply font size to document
  useEffect(() => {
    document.documentElement.style.setProperty("--font-size-base", `${fontSize}px`);
  }, [fontSize]);

  const setFontSize = useCallback((size: number) => {
    const clampedSize = Math.min(MAX_FONT_SIZE, Math.max(MIN_FONT_SIZE, size));
    setFontSizeState(clampedSize);
    localStorage.setItem(STORAGE_KEY, clampedSize.toString());
  }, []);

  const increaseFontSize = useCallback(() => {
    setFontSize(fontSize + FONT_SIZE_STEP);
  }, [fontSize, setFontSize]);

  const decreaseFontSize = useCallback(() => {
    setFontSize(fontSize - FONT_SIZE_STEP);
  }, [fontSize, setFontSize]);

  const resetFontSize = useCallback(() => {
    setFontSize(DEFAULT_FONT_SIZE);
  }, [setFontSize]);

  return {
    fontSize,
    setFontSize,
    increaseFontSize,
    decreaseFontSize,
    resetFontSize,
  };
}
