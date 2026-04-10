import { useState, useCallback } from 'react';
import { useSpeechToText } from '../../hooks/useSpeechToText';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export function VoiceInput({ onTranscript, disabled }: VoiceInputProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const {
    transcript,
    isListening,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
    error,
  } = useSpeechToText({
    onTranscript: (text) => {
      setInputValue((prev) => prev + text);
    },
    onError: (err) => {
      console.error('Speech recognition error:', err);
    },
    continuous: false,
  });

  const handleStart = useCallback(() => {
    setIsExpanded(true);
    setInputValue('');
    startListening();
  }, [startListening]);

  const handleStop = useCallback(() => {
    stopListening();
  }, [stopListening]);

  const handleSend = useCallback(() => {
    if (inputValue.trim()) {
      onTranscript(inputValue.trim());
      setInputValue('');
      setIsExpanded(false);
      resetTranscript();
    }
  }, [inputValue, onTranscript, resetTranscript]);

  const handleCancel = useCallback(() => {
    stopListening();
    setInputValue('');
    setIsExpanded(false);
    resetTranscript();
  }, [stopListening, resetTranscript]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      } else if (e.key === 'Escape') {
        handleCancel();
      }
    },
    [handleSend, handleCancel]
  );

  if (!isSupported) {
    return null;
  }

  if (!isExpanded) {
    return (
      <button
        type="button"
        onClick={handleStart}
        disabled={disabled}
        className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        title="Voice input"
        aria-label="Start voice input"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="w-5 h-5 text-gray-600 dark:text-gray-400"
        >
          <path d="M8 11.5a1 1 0 100 2 1 1 0 000-2zm4 0a1 1 0 100 2 1 1 0 000-2zM12 2a4 4 0 00-4 4v6a4 4 0 008 0V6a4 4 0 00-4-4zm-6 4a6 6 0 0112 0v6a6 6 0 01-12 0V6z" />
          <path d="M12 18v4m-2 0h4" strokeWidth={2} stroke="currentColor" fill="none" />
        </svg>
      </button>
    );
  }

  return (
    <div className="absolute bottom-full left-0 mb-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-3">
      <div className="flex items-center gap-2 mb-2">
        <div
          className={`w-3 h-3 rounded-full ${
            isListening ? 'bg-red-500 animate-pulse' : 'bg-gray-400'
          }`}
        />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {isListening ? 'Listening...' : 'Voice Input'}
        </span>
      </div>

      {error && (
        <div className="mb-2 text-xs text-red-500 bg-red-50 dark:bg-red-900/20 p-2 rounded">
          {error}
        </div>
      )}

      <textarea
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Your speech will appear here..."
        className="w-full h-20 p-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
        autoFocus
      />

      <div className="flex justify-end gap-2 mt-2">
        <button
          type="button"
          onClick={handleCancel}
          className="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          Cancel
        </button>
        {isListening ? (
          <button
            type="button"
            onClick={handleStop}
            className="px-3 py-1.5 text-sm rounded-lg bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
          >
            Stop
          </button>
        ) : (
          <button
            type="button"
            onClick={handleStart}
            className="px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            Retry
          </button>
        )}
        <button
          type="button"
          onClick={handleSend}
          disabled={!inputValue.trim()}
          className="px-3 py-1.5 text-sm rounded-lg bg-blue-500 text-white hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </div>
    </div>
  );
}
