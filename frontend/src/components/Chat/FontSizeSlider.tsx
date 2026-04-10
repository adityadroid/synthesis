import { useFontSize } from "../../hooks/useFontSize";

interface FontSizeSliderProps {
  className?: string;
}

export function FontSizeSlider({ className = "" }: FontSizeSliderProps) {
  const { fontSize, setFontSize, increaseFontSize, decreaseFontSize } = useFontSize();

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-foreground">Font Size</span>
        <span className="text-sm text-muted-foreground font-mono">{fontSize}px</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={decreaseFontSize}
          disabled={fontSize <= 12}
          className="p-2 rounded-md bg-secondary text-foreground hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
          </svg>
        </button>

        <input
          type="range"
          min={12}
          max={24}
          step={1}
          value={fontSize}
          onChange={(e) => setFontSize(parseInt(e.target.value))}
          className="flex-1 h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
        />

        <button
          onClick={increaseFontSize}
          disabled={fontSize >= 24}
          className="p-2 rounded-md bg-secondary text-foreground hover:bg-secondary/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      {/* Preview */}
      <div
        className="p-3 bg-background border border-input rounded-md"
        style={{ fontSize: `${fontSize}px` }}
      >
        <span className="text-muted-foreground text-xs">Preview:</span> The quick brown fox jumps over the lazy dog.
      </div>
    </div>
  );
}
