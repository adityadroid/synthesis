import { useState, ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface MessageContentProps {
  content: string;
}

interface CodeBlockProps {
  inline?: boolean;
  className?: string;
  children?: ReactNode;
}

function CopyButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="absolute top-2 right-2 p-1.5 rounded bg-muted/80 hover:bg-muted text-xs text-muted-foreground hover:text-foreground transition-colors opacity-0 group-hover:opacity-100"
      title="Copy code"
    >
      {copied ? (
        <svg className="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      )}
    </button>
  );
}

function CodeBlock({ inline, className, children, ...props }: CodeBlockProps) {
  const match = /language-(\w+)/.exec(className || "");
  const language = match ? match[1] : "";
  const code = String(children).replace(/\n$/, "");

  if (!inline && match) {
    return (
      <div className="relative group">
        <CopyButton code={code} />
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={language || "text"}
          PreTag="div"
          customStyle={{
            margin: 0,
            borderRadius: "6px",
            padding: "1rem",
            backgroundColor: "#1e1e1e",
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    );
  }

  return (
    <code
      {...props}
      className={className}
      style={{
        backgroundColor: !inline ? "#1e1e1e" : undefined,
        borderRadius: !inline ? "4px" : undefined,
        padding: !inline ? "0.25rem 0.5rem" : undefined,
        fontSize: "0.875em",
      }}
    >
      {children}
    </code>
  );
}

export function MessageContent({ content }: MessageContentProps) {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code: CodeBlock,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}