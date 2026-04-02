'use client';

import { useState } from 'react';
import { Send, Trash2 } from 'lucide-react';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
  hasError?: boolean;
}

export function PromptInput({
  onSubmit,
  isLoading,
  hasError = false,
}: PromptInputProps) {
  const [prompt, setPrompt] = useState('');
  const [charCount, setCharCount] = useState(0);

  const maxChars = 1000;
  const minChars = 10;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    if (text.length <= maxChars) {
      setPrompt(text);
      setCharCount(text.length);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim().length >= minChars && !isLoading) {
      onSubmit(prompt.trim());
    }
  };

  const handleClear = () => {
    setPrompt('');
    setCharCount(0);
  };

  const isValid = prompt.trim().length >= minChars;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className={`relative rounded-xl border transition-colors ${
        hasError
          ? 'border-red-500 bg-red-500/10'
          : 'border-border bg-background focus-within:border-foreground/50'
      }`}>
        <textarea
          value={prompt}
          onChange={handleChange}
          placeholder="Write your presentation topic or idea here... E.g., 'Create a presentation about climate change and its impact on ecosystems'"
          disabled={isLoading}
          className={`w-full px-6 py-4 bg-transparent text-foreground placeholder:text-muted-foreground rounded-xl outline-none resize-none disabled:opacity-50 transition-colors ${
            isLoading ? 'cursor-not-allowed' : 'cursor-text'
          }`}
          rows={8}
        />

        {/* Character count */}
        <div className="absolute bottom-3 right-4 text-xs text-muted-foreground font-medium bg-background px-2 py-1 rounded-md border border-border/50">
          {charCount}/{maxChars}
        </div>
      </div>

      {/* Info text */}
      <div className="text-sm text-muted-foreground flex justify-between items-center px-1">
        <p>
          Minimum {minChars} characters • Maximum {maxChars} characters
        </p>
        {charCount < minChars && charCount > 0 && (
          <p className="text-amber-500 mt-1">
            Add {minChars - charCount} more characters
          </p>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-3 justify-between">
        <button
          type="button"
          onClick={handleClear}
          disabled={isLoading || charCount === 0}
          className="flex items-center gap-2 px-4 py-2 text-foreground bg-secondary hover:bg-secondary/80 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Trash2 size={18} />
          Clear
        </button>

        <button
          type="submit"
          disabled={!isValid || isLoading}
          className="flex items-center gap-2 px-8 py-2 bg-foreground text-background rounded-lg font-medium hover:bg-foreground/90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          {isLoading ? (
            <>
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Send size={18} />
              Generate
            </>
          )}
        </button>
      </div>
    </form>
  );
}
