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
    <div className="bg-blue-50 dark:bg-blue-950/30 rounded-xl border border-blue-200 dark:border-blue-800 p-6 space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Loader2 className="text-blue-600 dark:text-blue-400 animate-spin" size={20} />
          <h3 className="font-semibold text-blue-900 dark:text-blue-300">
            Generating Presentation
          </h3>
        </div>
        <p className="text-blue-700 dark:text-blue-400 text-sm">
          {message || 'Preparing your presentation...'}
        </p>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
            Progress
          </span>
          <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
            {progress}%
          </span>
        </div>
        <div className="w-full h-2 bg-blue-200 dark:bg-blue-900 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Phase Steps */}
      <div>
        <p className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-3">
          Generation Steps
        </p>
        <div className="space-y-2">
          {PHASES.map((phase, idx) => {
            const phaseIndex = PHASES.findIndex(p => p.key === currentPhase?.toLowerCase());
            const isActive = phaseIndex === idx;
            const isCompleted = phaseIndex > idx;

            return (
              <div
                key={phase.key}
                className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                  isCompleted
                    ? 'bg-blue-100 dark:bg-blue-900/50'
                    : isActive
                    ? 'bg-blue-100 dark:bg-blue-900/50 ring-2 ring-blue-400'
                    : 'bg-white dark:bg-gray-800'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                    isCompleted
                      ? 'bg-green-500 text-white'
                      : isActive
                      ? 'bg-blue-600 text-white animate-pulse'
                      : 'bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {isCompleted ? '✓' : idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {phase.label}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {phase.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Estimated time */}
      <div className="text-sm text-blue-600 dark:text-blue-400">
        <p>Estimated time: 30-60 seconds</p>
      </div>
    </div>
  );
}
