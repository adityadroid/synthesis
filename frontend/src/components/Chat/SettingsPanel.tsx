import { useState } from "react";
import { AccentColorPicker } from "./AccentColorPicker";
import { FontSizeSlider } from "./FontSizeSlider";

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  const [activeTab, setActiveTab] = useState<"appearance" | "about">("appearance");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40 overflow-hidden">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />

      {/* Panel */}
      <div className="absolute right-0 top-0 bottom-0 w-full max-w-md bg-card border-l border-border shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">Settings</h2>
          <button
            onClick={onClose}
            className="p-1 text-muted-foreground hover:text-foreground hover:bg-secondary rounded transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border">
          <button
            onClick={() => setActiveTab("appearance")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "appearance"
                ? "text-foreground border-b-2 border-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Appearance
          </button>
          <button
            onClick={() => setActiveTab("about")}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === "about"
                ? "text-foreground border-b-2 border-primary"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            About
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === "appearance" && (
            <div className="space-y-6">
              <AccentColorPicker />
              <div className="border-t border-border pt-6">
                <FontSizeSlider />
              </div>
            </div>
          )}

          {activeTab === "about" && (
            <div className="space-y-4 text-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-lg bg-primary flex items-center justify-center">
                  <svg className="w-6 h-6 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Synthesis</h3>
                  <p className="text-muted-foreground">Version 1.1.0</p>
                </div>
              </div>
              
              <p className="text-muted-foreground">
                A modern, scalable AI chat application with support for multiple LLM providers,
                real-time streaming, and enterprise-grade features.
              </p>

              <div className="border-t border-border pt-4 mt-4">
                <h4 className="font-medium text-foreground mb-2">Features</h4>
                <ul className="space-y-1 text-muted-foreground">
                  <li>• Multiple AI model support</li>
                  <li>• Real-time streaming responses</li>
                  <li>• Conversation management</li>
                  <li>• Export to Markdown, JSON, PDF</li>
                  <li>• Customizable themes</li>
                  <li>• Local model support (Ollama, LM Studio)</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
