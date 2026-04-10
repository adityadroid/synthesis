import { useState, useEffect, useCallback } from "react";

interface UseAccentColorReturn {
  accentColor: string;
  setAccentColor: (color: string) => void;
  presetColors: string[];
  isCustom: boolean;
}

const STORAGE_KEY = "synthesis-accent-color";
const PRESET_COLORS = [
  { name: "Zinc", value: "#71717a" },
  { name: "Red", value: "#ef4444" },
  { name: "Orange", value: "#f97316" },
  { name: "Amber", value: "#f59e0b" },
  { name: "Yellow", value: "#eab308" },
  { name: "Lime", value: "#84cc16" },
  { name: "Green", value: "#22c55e" },
  { name: "Emerald", value: "#10b981" },
  { name: "Teal", value: "#14b8a6" },
  { name: "Cyan", value: "#06b6d4" },
  { name: "Sky", value: "#0ea5e9" },
  { name: "Blue", value: "#3b82f6" },
  { name: "Indigo", value: "#6366f1" },
  { name: "Violet", value: "#8b5cf6" },
  { name: "Purple", value: "#a855f7" },
  { name: "Fuchsia", value: "#d946ef" },
  { name: "Pink", value: "#ec4899" },
  { name: "Rose", value: "#f43f5e" },
];

export function useAccentColor(): UseAccentColorReturn {
  const [accentColor, setAccentColorState] = useState<string>(() => {
    if (typeof window === "undefined") return PRESET_COLORS[13].value;
    return localStorage.getItem(STORAGE_KEY) || PRESET_COLORS[13].value;
  });

  // Apply accent color to CSS variables
  useEffect(() => {
    document.documentElement.style.setProperty("--accent", accentColor);
    document.documentElement.style.setProperty("--ring", accentColor);
    // Calculate hover/focus variants
    const hoverColor = adjustBrightness(accentColor, 0.9);
    document.documentElement.style.setProperty("--accent-hover", hoverColor);
  }, [accentColor]);

  const setAccentColor = useCallback((color: string) => {
    setAccentColorState(color);
    localStorage.setItem(STORAGE_KEY, color);
  }, []);

  const presetNames = PRESET_COLORS.map((c) => c.value);
  const isCustom = !presetNames.includes(accentColor);

  return {
    accentColor,
    setAccentColor,
    presetColors: PRESET_COLORS.map((c) => c.value),
    isCustom,
  };
}

// Helper to adjust color brightness
function adjustBrightness(hex: string, factor: number): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  const adjusted = {
    r: Math.round(rgb.r * factor),
    g: Math.round(rgb.g * factor),
    b: Math.round(rgb.b * factor),
  };
  return rgbToHex(adjusted.r, adjusted.g, adjusted.b);
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

function rgbToHex(r: number, g: number, b: number): string {
  return "#" + [r, g, b].map((x) => x.toString(16).padStart(2, "0")).join("");
}
