'use client';

import { usePPT } from '@/hooks/usePPT';
import { PromptInput } from '@/components/ppt/PromptInput';
import { GenerationStatus } from '@/components/ppt/GenerationStatus';
import { useState } from 'react';

export default function DashboardPage() {
  const {
    status,
    progress,
    error,
    message,
    currentJob,
    generatePPT,
    downloadPPT,
    reset,
  } = usePPT();

  const [lastPrompt, setLastPrompt] = useState('');

  const handleGeneratePPT = async (prompt: string) => {
    setLastPrompt(prompt);
    try {
      await generatePPT(prompt);
    } catch (err) {
      console.error('Failed to generate PPT:', err);
    }
  };

  const handleDownload = async () => {
    if (currentJob?.file_path) {
      try {
        // Extract filename from file_path
        const filename = currentJob.file_path.split('/').pop() || 'presentation.pptx';
        await downloadPPT(filename);
      } catch (err) {
        console.error('Download failed:', err);
      }
    }
  };

  const isGenerating = status !== 'idle' && status !== 'completed' && status !== 'error';

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Create Presentation
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Write your presentation topic and let AI create a beautiful PowerPoint presentation in seconds.
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-2 gap-8 items-start">
        {/* Left: Input Section */}
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-900 rounded-xl p-8 border border-gray-200 dark:border-gray-800 shadow-sm">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              Your Presentation Topic
            </h2>
            <PromptInput
              onSubmit={handleGeneratePPT}
              isLoading={isGenerating}
              hasError={status === 'error'}
            />
          </div>

          {/* Tips */}
          <div className="bg-blue-50 dark:bg-blue-950/30 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
            <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
              💡 Tips for better results
            </h3>
            <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1">
              <li>• Be specific about your topic and keywords</li>
              <li>• Mention the target audience if relevant</li>
              <li>• Include any specific themes or styles you prefer</li>
            </ul>
          </div>
        </div>

        {/* Right: Status Section */}
        <div>
          <div className="sticky top-24">
            {isGenerating || error || currentJob?.status === 'completed' ? (
              <GenerationStatus
                isGenerating={isGenerating}
                progress={progress}
                currentPhase={status}
                error={error || (status === 'error' ? 'An error occurred' : null)}
                downloadUrl={currentJob?.file_path ? `/api/download/${currentJob.file_path}` : null}
                message={message}
                onDownload={handleDownload}
                onRetry={
                  status === 'error'
                    ? () => {
                        reset();
                        if (lastPrompt) {
                          handleGeneratePPT(lastPrompt);
                        }
                      }
                    : undefined
                }
                onReset={reset}
              />
            ) : (
              /* Empty State */
              <div className="bg-white dark:bg-gray-900 rounded-xl p-8 border border-gray-200 dark:border-gray-800 shadow-sm text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">✨</span>
                </div>
                <h3 className="font-semibold text-lg text-gray-900 dark:text-white mb-2">
                  Ready to Create?
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Enter your presentation topic on the left and click Generate to create a beautiful PowerPoint presentation powered by AI.
                </p>
                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-800">
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    ⏱️ Average generation time: 30-60 seconds
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
