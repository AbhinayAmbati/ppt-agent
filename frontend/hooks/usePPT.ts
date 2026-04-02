'use client';

import { useState, useCallback } from 'react';
import { pptAPI } from '@/lib/api';
import { PPTJob } from '@/lib/types';

export function usePPT() {
  const [status, setStatus] = useState<'idle' | 'planning' | 'creating' | 'building' | 'theming' | 'saving' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [currentJob, setCurrentJob] = useState<PPTJob | null>(null);

  const generatePPT = useCallback(async (prompt: string) => {
    setStatus('planning');
    setProgress(0);
    setError(null);
    setMessage('');

    try {
      // Plan phase
      setProgress(20);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMessage('Planning your slides...');

      // Creating phase
      setStatus('creating');
      setProgress(40);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMessage('Creating presentation...');

      // Building phase
      setStatus('building');
      setProgress(60);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMessage('Adding slide content...');

      // Theming phase
      setStatus('theming');
      setProgress(75);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setMessage('Applying theme...');

      // Call actual API
      setStatus('saving');
      setProgress(85);
      setMessage('Saving your presentation...');

      const response = await pptAPI.generate(prompt);

      setProgress(100);
      setStatus('completed');
      setMessage('Your presentation is ready!');
      setCurrentJob({
        id: Date.now().toString(),
        prompt,
        status: 'completed',
        file_path: response.file_path,
        created_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
      });

      return response;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate presentation';
      setStatus('error');
      setError(errorMessage);
      setMessage('Generation failed');
      throw err;
    }
  }, []);

  const downloadPPT = useCallback(async (filename: string) => {
    try {
      const blob = await pptAPI.downloadFile(filename);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || 'presentation.pptx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download failed:', err);
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setProgress(0);
    setError(null);
    setMessage('');
    setCurrentJob(null);
  }, []);

  return {
    status,
    progress,
    error,
    message,
    currentJob,
    generatePPT,
    downloadPPT,
    reset,
  };
}
