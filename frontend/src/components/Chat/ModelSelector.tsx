import { useState, useCallback } from "react";

interface Model {
  id: string;
  name: string;
  provider: string;
}

interface ModelSelectorProps {
  currentModel: string | null;
  onModelChange: (model: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

const COMMON_MODELS = [
  // OpenAI
  { id: "gpt-4o", name: "GPT-4o", provider: "openai" },
  { id: "gpt-4o-mini", name: "GPT-4o Mini", provider: "openai" },
  { id: "gpt-4-turbo", name: "GPT-4 Turbo", provider: "openai" },
  // Anthropic
  { id: "claude-3-5-sonnet-latest", name: "Claude 3.5 Sonnet", provider: "anthropic" },
  { id: "claude-3-5-haiku-latest", name: "Claude 3.5 Haiku", provider: "anthropic" },
];

export function ModelSelector({
  currentModel,
  onModelChange,
  isOpen,
  onClose,
}: ModelSelectorProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredModels = COMMON_MODELS.filter(
    (m) =>
      m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelect = useCallback(
    (modelId: string) => {
      onModelChange(modelId);
      onClose();
    },
    [onModelChange, onClose]
  );

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case "openai":
        return (
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08-4.778 2.758a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z" />
          </svg>
        );
      case "anthropic":
        return (
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        );
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-40 overflow-hidden">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      
      <div className="absolute top-[15%] left-1/2 -translate-x-1/2 w-full max-w-md">
        <div className="bg-card border border-border rounded-lg shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="p-4 border-b border-border">
            <h3 className="text-lg font-semibold text-foreground">Select Model</h3>
          </div>

          {/* Search */}
          <div className="p-4 border-b border-border">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search models..."
              className="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Models list */}
          <div className="max-h-80 overflow-y-auto p-2">
            {filteredModels.map((model) => (
              <button
                key={model.id}
                onClick={() => handleSelect(model.id)}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-md transition-colors ${
                  currentModel === model.id
                    ? "bg-secondary text-foreground"
                    : "text-muted-foreground hover:bg-secondary/50"
                }`}
              >
                <span className="text-muted-foreground">
                  {getProviderIcon(model.provider)}
                </span>
                <div className="flex-1 text-left">
                  <div className="font-medium">{model.name}</div>
                  <div className="text-xs text-muted-foreground">{model.provider}</div>
                </div>
                {currentModel === model.id && (
                  <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            ))}

            {filteredModels.length === 0 && (
              <div className="px-4 py-8 text-center text-muted-foreground">
                No models found
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-border text-xs text-muted-foreground text-center">
            Local models (Ollama, LM Studio) available in settings
          </div>
        </div>
      </div>
    </div>
  );
}
