import { useState, useCallback } from "react";
import { Conversation } from "../../api/client";

interface ExportMenuProps {
  conversation: Conversation;
  onClose: () => void;
  onClear?: () => void;
}

type ExportFormat = "markdown" | "json" | "pdf";

export function ExportMenu({ conversation, onClose, onClear }: ExportMenuProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [showDropdown, setShowDropdown] = useState(true);

  const handleExport = useCallback(async (format: ExportFormat) => {
    setIsExporting(true);
    setShowDropdown(false);

    try {
      // For now, trigger download via browser
      const response = await fetch(
        `/api/conversations/${conversation.id}/export?format=${format}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        
        // Create and trigger download
        const blob = new Blob([data.content], { type: data.content_type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = data.filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Export failed:", error);
    } finally {
      setIsExporting(false);
      onClose();
    }
  }, [conversation.id, onClose]);

  if (!showDropdown) {
    return (
      <div className="absolute right-0 top-full mt-1 w-48 bg-popover border border-border rounded-lg shadow-lg p-2 z-20">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Exporting...
        </div>
      </div>
    );
  }

  return (
    <div className="absolute right-0 top-full mt-1 w-48 bg-popover border border-border rounded-lg shadow-lg py-1 z-20">
      <button
        onClick={() => handleExport("markdown")}
        disabled={isExporting}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-secondary transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Export as Markdown
      </button>
      <button
        onClick={() => handleExport("json")}
        disabled={isExporting}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-secondary transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
        Export as JSON
      </button>
      <button
        onClick={() => handleExport("pdf")}
        disabled={isExporting}
        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-secondary transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        Export as PDF
      </button>
      {onClear && (
        <button
          onClick={() => {
            onClose();
            onClear();
          }}
          disabled={isExporting}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear Messages
        </button>
      )}
    </div>
  );
}
