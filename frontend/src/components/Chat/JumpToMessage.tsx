import { useState, useRef, useEffect } from "react";

interface JumpToMessageProps {
  totalMessages: number;
  onJump: (index: number) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function JumpToMessage({
  totalMessages,
  onJump,
  isOpen,
  onClose,
}: JumpToMessageProps) {
  const [inputValue, setInputValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setInputValue("");
    }
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const index = parseInt(inputValue, 10) - 1; // Convert to 0-based
    if (!isNaN(index) && index >= 0 && index < totalMessages) {
      onJump(index);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      
      <div className="absolute top-[30%] left-1/2 -translate-x-1/2 w-full max-w-xs">
        <form onSubmit={handleSubmit} className="bg-card border border-border rounded-lg shadow-2xl p-4">
          <h3 className="text-sm font-semibold text-foreground mb-3">
            Jump to Message
          </h3>
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="number"
              min={1}
              max={totalMessages}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={`1-${totalMessages}`}
              className="flex-1 px-3 py-2 bg-background border border-input rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              Go
            </button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Enter a number between 1 and {totalMessages}
          </p>
        </form>
      </div>
    </div>
  );
}
