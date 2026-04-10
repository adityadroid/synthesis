import { useState, useCallback, useRef, useEffect } from 'react';

interface SpeechRecognitionEvent {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent {
  error: string;
  message: string;
}

// Check for browser support
const SpeechRecognitionAPI = typeof window !== 'undefined' 
  ? (window.SpeechRecognition || window.webkitSpeechRecognition)
  : null;

interface UseSpeechToTextOptions {
  onTranscript?: (transcript: string) => void;
  onError?: (error: string) => void;
  continuous?: boolean;
  lang?: string;
}

interface UseSpeechToTextReturn {
  transcript: string;
  isListening: boolean;
  isSupported: boolean;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
  error: string | null;
}

export function useSpeechToText({
  onTranscript,
  onError,
  continuous = false,
  lang = 'en-US',
}: UseSpeechToTextOptions = {}): UseSpeechToTextReturn {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const isSupported = SpeechRecognitionAPI !== null;

  useEffect(() => {
    if (!isSupported) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.lang = lang;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      const fullTranscript = finalTranscript;
      setTranscript(fullTranscript);
      
      if (onTranscript && (finalTranscript || interimTranscript)) {
        onTranscript(finalTranscript || interimTranscript);
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      const errorMessage = event.error;
      setError(errorMessage);
      setIsListening(false);
      
      if (onError) {
        onError(errorMessage);
      }

      // Handle specific errors
      if (errorMessage === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access.');
      } else if (errorMessage === 'no-speech') {
        setError('No speech detected. Please try again.');
      } else if (errorMessage === 'network') {
        setError('Network error. Check your connection.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
    };
  }, [continuous, lang, isSupported, onTranscript, onError]);

  const startListening = useCallback(() => {
    if (!isSupported || !recognitionRef.current) {
      setError('Speech recognition not supported in this browser.');
      return;
    }

    setError(null);
    setTranscript('');

    try {
      recognitionRef.current.start();
    } catch (err) {
      // Recognition might already be running
      if (err instanceof Error && err.message.includes('already started')) {
        return;
      }
      setError('Failed to start speech recognition.');
    }
  }, [isSupported]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  return {
    transcript,
    isListening,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
    error,
  };
}

// Type declarations for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}
