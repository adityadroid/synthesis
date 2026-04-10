import { useState, useCallback } from "react";

interface SystemPromptEditorProps {
  initialValue?: string;
  onSave: (prompt: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

const PRESET_PROMPTS = [
  {
    name: "Assistant",
    prompt: "You are a helpful AI assistant. Provide clear, accurate, and concise responses.",
  },
  {
    name: "Code Reviewer",
    prompt: "You are an expert code reviewer. Analyze code for bugs, performance issues, security vulnerabilities, and best practices. Provide specific suggestions with code examples when helpful.",
  },
  {
    name: "Teacher",
    prompt: "You are a patient and knowledgeable teacher. Explain concepts step by step, use analogies, and check for understanding before moving forward.",
  },
  {
    name: "Creative Writer",
    prompt: "You are a creative writer. Help with storytelling, creative writing, brainstorming ideas, and providing literary feedback.",
  },
  {
    name: "Technical Writer",
    prompt: "You are a technical writer. Create clear, well-structured documentation with proper formatting, examples, and explanations suitable for developers.",
  },
];

export function SystemPromptEditor({
  initialValue = "",
  onSave,
  isOpen,
  onClose,
}: SystemPromptEditorProps) {
  const [prompt, setPrompt] = useState(initialValue);
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = useCallback(() => {
    onSave(prompt);
    setIsEditing(false);
  }, [prompt, onSave]);

  const handlePresetSelect = useCallback((presetPrompt: string) => {
    setPrompt(presetPrompt);
    setIsEditing(true);
  }, []);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40 overflow-hidden">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />

      {/* Panel */}
      <div className="absolute left-0 top-0 bottom-0 w-full max-w-lg bg-card border-r border-border shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-semibold text-foreground">System Prompt</h2>
          <button
            onClick={onClose}
            className="p-1 text-muted-foreground hover:text-foreground hover:bg-secondary rounded transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <p className="text-sm text-muted-foreground mb-4">
            Set a custom system prompt to define the AI&apos;s personality and behavior for this conversation.
          </p>

          {/* Presets */}
          <div className="mb-4">
            <label className="text-sm font-medium text-foreground mb-2 block">
              Quick Presets
            </label>
            <div className="flex flex-wrap gap-2">
              {PRESET_PROMPTS.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => handlePresetSelect(preset.prompt)}
                  className="px-3 py-1.5 text-sm bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Editor */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              Custom Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => {
                setPrompt(e.target.value);
                setIsEditing(true);
              }}
              placeholder="Enter a system prompt..."
              className="w-full h-48 px-3 py-2 bg-background border border-input rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            />
            <p className="text-xs text-muted-foreground">
              The system prompt guides how the AI responds. Be specific about the tone, style, and any constraints.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              setPrompt("");
              setIsEditing(true);
            }}
            className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear
          </button>
          <button
            onClick={handleSave}
            disabled={!prompt.trim() && !isEditing}
            className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
