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
        <h1 className="text-3xl font-serif font-bold text-foreground tracking-tight mb-2">
          Create Presentation
        </h1>
        <p className="text-lg text-muted-foreground">
          Write your presentation topic and let AI create a beautiful PowerPoint presentation in seconds.
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-2 gap-8 items-start">
        {/* Left: Input Section */}
        <div className="space-y-4">
          <div className="bg-card rounded-2xl p-8 border border-border/50 shadow-sm">
            <h2 className="text-xl font-semibold text-foreground mb-6 font-serif tracking-tight">
              Your Presentation Topic
            </h2>
            <PromptInput
              onSubmit={handleGeneratePPT}
              isLoading={isGenerating}
              hasError={status === 'error'}
            />
          </div>

          {/* Tips */}
          <div className="bg-secondary/40 rounded-xl p-6 border border-border/40">
            <h3 className="font-medium flex items-center gap-2 text-foreground mb-3">
              💡 Tips for better results
            </h3>
            <ul className="text-sm text-muted-foreground space-y-2">
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
              <div className="bg-card rounded-2xl p-8 border border-border/50 shadow-sm text-center">
                <div className="w-16 h-16 bg-background border border-border rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">✨</span>
                </div>
                <h3 className="font-semibold text-lg text-foreground mb-2">
                  Ready to Create?
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Enter your presentation topic on the left and click Generate to create a beautiful PowerPoint presentation powered by AI.
                </p>
                <div className="mt-6 pt-6 border-t border-border/40">
                  <p className="text-xs text-muted-foreground">
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
