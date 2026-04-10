import { useState, useCallback } from "react";

interface ModelSettingsProps {
  conversationId?: string;
  isOpen: boolean;
  onClose: () => void;
  onSettingsChange?: (settings: AISettings) => void;
}

export interface AISettings {
  temperature: number;
  maxTokens: number;
  topP: number;
  presencePenalty: number;
  frequencyPenalty: number;
}

const DEFAULT_SETTINGS: AISettings = {
  temperature: 0.7,
  maxTokens: 2048,
  topP: 1.0,
  presencePenalty: 0,
  frequencyPenalty: 0,
};

const STORAGE_KEY = "synthesis-ai-settings";

function getStoredSettings(): AISettings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? { ...DEFAULT_SETTINGS, ...JSON.parse(stored) } : DEFAULT_SETTINGS;
}

function Slider({
  label,
  value,
  min,
  max,
  step = 0.1,
  onChange,
  tooltip,
  unit = "",
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
  tooltip?: string;
  unit?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground flex items-center gap-2">
          {label}
          {tooltip && (
            <span className="group relative">
              <svg
                className="w-4 h-4 text-muted-foreground cursor-help"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="absolute left-0 bottom-full mb-1 hidden group-hover:block w-48 p-2 text-xs bg-popover border border-border rounded shadow-lg z-10">
                {tooltip}
              </span>
            </span>
          )}
        </label>
        <span className="text-sm text-muted-foreground font-mono">
          {value.toFixed(step < 1 ? 1 : 0)}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
      />
    </div>
  );
}

export function ModelSettings({
  isOpen,
  onClose,
  onSettingsChange,
}: ModelSettingsProps) {
  const [settings, setSettings] = useState<AISettings>(getStoredSettings);
  const [showReset, setShowReset] = useState(false);

  const updateSetting = useCallback(
    <K extends keyof AISettings>(key: K, value: AISettings[K]) => {
      const newSettings = { ...settings, [key]: value };
      setSettings(newSettings);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newSettings));
      onSettingsChange?.(newSettings);
    },
    [settings, onSettingsChange]
  );

  const resetToDefaults = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_SETTINGS));
    onSettingsChange?.(DEFAULT_SETTINGS);
    setShowReset(false);
  }, [onSettingsChange]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/30"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="absolute right-0 top-0 bottom-0 w-full max-w-sm bg-card border-l border-border shadow-2xl overflow-y-auto">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">AI Settings</h2>
          <button
            onClick={onClose}
            className="p-1 text-muted-foreground hover:text-foreground hover:bg-secondary rounded"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Temperature */}
          <Slider
            label="Temperature"
            value={settings.temperature}
            min={0}
            max={2}
            step={0.1}
            onChange={(v) => updateSetting("temperature", v)}
            tooltip="Controls randomness. Lower = more focused, higher = more creative."
          />

          {/* Max Tokens */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-foreground">Max Tokens</label>
              <span className="text-sm text-muted-foreground font-mono">
                {settings.maxTokens}
              </span>
            </div>
            <input
              type="number"
              min={256}
              max={32000}
              step={256}
              value={settings.maxTokens}
              onChange={(e) => updateSetting("maxTokens", parseInt(e.target.value) || 2048)}
              className="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Top P */}
          <Slider
            label="Top P"
            value={settings.topP}
            min={0}
            max={1}
            step={0.05}
            onChange={(v) => updateSetting("topP", v)}
            tooltip="Nucleus sampling. Controls diversity of token selection."
          />

          {/* Presence Penalty */}
          <Slider
            label="Presence Penalty"
            value={settings.presencePenalty}
            min={-2}
            max={2}
            step={0.1}
            onChange={(v) => updateSetting("presencePenalty", v)}
            tooltip="Penalizes tokens that have already appeared. Higher = more diverse topics."
          />

          {/* Frequency Penalty */}
          <Slider
            label="Frequency Penalty"
            value={settings.frequencyPenalty}
            min={-2}
            max={2}
            step={0.1}
            onChange={(v) => updateSetting("frequencyPenalty", v)}
            tooltip="Penalizes token frequency. Higher = less repetition."
          />

          {/* Reset */}
          <div className="pt-4 border-t border-border">
            {showReset ? (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Reset to defaults?</span>
                <button
                  onClick={resetToDefaults}
                  className="px-3 py-1 text-sm bg-destructive text-destructive-foreground rounded hover:bg-destructive/90"
                >
                  Yes
                </button>
                <button
                  onClick={() => setShowReset(false)}
                  className="px-3 py-1 text-sm bg-secondary text-foreground rounded hover:bg-secondary/80"
                >
                  No
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowReset(true)}
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                Reset to defaults
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export { DEFAULT_SETTINGS };
