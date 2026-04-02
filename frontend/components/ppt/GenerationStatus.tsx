'use client';

import { CheckCircle2, AlertCircle, Loader2, Download } from 'lucide-react';

interface GenerationStatusProps {
  isGenerating: boolean;
  progress: number;
  currentPhase: string | null;
  error: string | null;
  downloadUrl: string | null;
  message: string;
  onDownload?: () => void;
  onRetry?: () => void;
  onReset?: () => void;
}

const PHASES = [
  { key: 'plan', label: 'Plan', description: 'Planning slide structure' },
  { key: 'create', label: 'Create', description: 'Initializing presentation' },
  { key: 'build', label: 'Build', description: 'Adding slide content' },
  { key: 'theme', label: 'Theme', description: 'Applying design theme' },
  { key: 'save', label: 'Save', description: 'Saving presentation' },
];

export function GenerationStatus({
  isGenerating,
  progress,
  currentPhase,
  error,
  downloadUrl,
  message,
  onDownload,
  onRetry,
  onReset,
}: GenerationStatusProps) {
  // Show nothing if not generating and no error/success
  if (!isGenerating && !error && !downloadUrl) {
    return null;
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-950/30 rounded-xl border border-red-200 dark:border-red-800 p-6">
        <div className="flex items-start gap-4">
          <AlertCircle className="text-red-600 dark:text-red-400 flex-shrink-0" size={24} />
          <div className="flex-1">
            <h3 className="font-semibold text-red-900 dark:text-red-300 mb-1">
              Generation Failed
            </h3>
            <p className="text-red-700 dark:text-red-400 text-sm mb-4">
              {error}
            </p>
            <div className="flex gap-2">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors text-sm"
                >
                  Retry
                </button>
              )}
              {onReset && (
                <button
                  onClick={onReset}
                  className="px-4 py-2 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/50 font-medium transition-colors text-sm"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (downloadUrl) {
    return (
      <div className="bg-green-50 dark:bg-green-950/30 rounded-xl border border-green-200 dark:border-green-800 p-6">
        <div className="flex items-start gap-4">
          <CheckCircle2 className="text-green-600 dark:text-green-400 flex-shrink-0" size={24} />
          <div className="flex-1">
            <h3 className="font-semibold text-green-900 dark:text-green-300 mb-1">
              Presentation Ready!
            </h3>
            <p className="text-green-700 dark:text-green-400 text-sm mb-4">
              Your PowerPoint presentation has been generated successfully.
            </p>
            <div className="flex gap-2">
              <button
                onClick={onDownload}
                className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors text-sm"
              >
                <Download size={16} />
                Download
              </button>
              {onReset && (
                <button
                  onClick={onReset}
                  className="px-4 py-2 border border-green-300 dark:border-green-700 text-green-600 dark:text-green-400 rounded-lg hover:bg-green-50 dark:hover:bg-green-950/50 font-medium transition-colors text-sm"
                >
                  Create Another
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Generation in progress
  return (
    <div className="bg-card rounded-2xl border border-border/50 p-8 space-y-8 shadow-sm">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <Loader2 className="text-foreground animate-spin" size={22} />
          <h3 className="font-semibold text-lg text-foreground font-serif tracking-tight">
            Generating Presentation
          </h3>
        </div>
        <p className="text-muted-foreground text-sm ml-8">
          {message || 'Preparing your presentation...'}
        </p>
      </div>

      {/* Progress Bar */}
      <div className="ml-8">
        <div className="flex justify-between items-center mb-3">
          <span className="text-xs font-semibold text-foreground tracking-wide uppercase">
            Progress
          </span>
          <span className="text-xs font-semibold text-foreground">
            {progress}%
          </span>
        </div>
        <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-foreground transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Phase Steps */}
      <div className="ml-8">
        <div className="space-y-3">
          {PHASES.map((phase, idx) => {
            const phaseIndex = PHASES.findIndex(p => p.key === currentPhase?.toLowerCase());
            const isActive = phaseIndex === idx;
            const isCompleted = phaseIndex > idx;

            return (
              <div
                key={phase.key}
                className={`flex items-center gap-4 p-4 rounded-xl transition-all ${
                  isCompleted
                    ? 'bg-secondary/40'
                    : isActive
                    ? 'bg-background border border-border/80 shadow-sm'
                    : 'bg-transparent border border-border/20'
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 transition-colors ${
                    isCompleted
                      ? 'bg-foreground text-background'
                      : isActive
                      ? 'bg-foreground text-background animate-pulse'
                      : 'bg-secondary text-muted-foreground'
                  }`}
                >
                  {isCompleted ? '✓' : idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${isActive || isCompleted ? 'text-foreground' : 'text-muted-foreground'}`}>
                    {phase.label}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {phase.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Estimated time */}
      <div className="text-sm text-muted-foreground ml-8 pt-2">
        <p>⏱️ Estimated time: 30-60 seconds</p>
      </div>
    </div>
  );
}
