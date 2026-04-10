import { useAccentColor } from "../../hooks/useAccentColor";

interface AccentColorPickerProps {
  className?: string;
}

export function AccentColorPicker({ className = "" }: AccentColorPickerProps) {
  const { accentColor, setAccentColor, presetColors } = useAccentColor();

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="text-sm font-medium text-foreground">Accent Color</div>
      
      {/* Preset colors */}
      <div className="grid grid-cols-6 gap-2">
        {presetColors.map((color) => (
          <button
            key={color}
            onClick={() => setAccentColor(color)}
            className={`w-8 h-8 rounded-full transition-transform hover:scale-110 ${
              accentColor === color ? "ring-2 ring-offset-2 ring-offset-card ring-primary" : ""
            }`}
            style={{ backgroundColor: color }}
            title={color}
          />
        ))}
      </div>

      {/* Custom color picker */}
      <div className="flex items-center gap-2">
        <label className="text-sm text-muted-foreground">Custom:</label>
        <input
          type="color"
          value={accentColor}
          onChange={(e) => setAccentColor(e.target.value)}
          className="w-8 h-8 rounded cursor-pointer border-0"
        />
        <input
          type="text"
          value={accentColor}
          onChange={(e) => {
            if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value)) {
              setAccentColor(e.target.value);
            }
          }}
          className="flex-1 px-2 py-1 text-sm bg-background border border-input rounded focus:outline-none focus:ring-1 focus:ring-ring text-foreground font-mono"
          placeholder="#6366f1"
        />
      </div>
    </div>
  );
}
