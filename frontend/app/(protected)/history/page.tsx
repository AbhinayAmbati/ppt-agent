'use client';

import { useEffect, useState } from 'react';
import { pptAPI } from '@/lib/api';
import { Download, Trash2, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { PPTJob } from '@/lib/types';

export default function HistoryPage() {
  const [jobs, setJobs] = useState<PPTJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await pptAPI.getJobs();
      setJobs(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || 'Failed to load history'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (job: PPTJob) => {
    try {
      if (job.file_path) {
        const filename = job.file_path.split('/').pop() || 'presentation.pptx';
        const blob = await pptAPI.downloadFile(filename);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await pptAPI.deleteJob(id);
      const updated = jobs.filter((job: PPTJob) => job.id !== id);
      setJobs(updated);
    } catch (err) {
      console.error('Failed to delete job', err);
      // Optional: you could set a toast or error state here if requested
    }
  };

  const getStatusIcon = (status: string) => {
    if (status.toLowerCase() === 'completed') {
      return <CheckCircle2 className="text-green-600 dark:text-green-400" size={20} />;
    } else if (status.toLowerCase() === 'failed') {
      return <AlertCircle className="text-red-600 dark:text-red-400" size={20} />;
    } else {
      return <Clock className="text-yellow-600 dark:text-yellow-400" size={20} />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-serif font-bold text-foreground tracking-tight mb-2">
            Presentation History
          </h1>
          <p className="text-lg text-muted-foreground">
            View and download all your generated presentations.
          </p>
        </div>

        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-card rounded-xl border border-border/50 p-4 animate-pulse"
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-secondary rounded w-3/4" />
                  <div className="h-3 bg-secondary rounded w-1/2" />
                </div>
                <div className="h-10 bg-secondary rounded w-24" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-serif font-bold text-foreground tracking-tight mb-2">
          Presentation History
        </h1>
        <p className="text-lg text-muted-foreground">
          View and download all your generated presentations.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-700 dark:text-red-400">{error}</p>
          <button
            onClick={loadJobs}
            className="mt-3 text-sm font-medium text-red-600 dark:text-red-400 hover:underline"
          >
            Try again
          </button>
        </div>
      )}

      {!error && jobs.length === 0 && (
        <div className="bg-card rounded-2xl border border-border/50 p-12 text-center shadow-sm">
          <div className="w-16 h-16 bg-background border border-border rounded-full flex items-center justify-center mx-auto mb-4">
            <Clock className="text-muted-foreground" size={24} />
          </div>
          <h3 className="text-xl font-semibold text-foreground mb-2">
            No presentations yet
          </h3>
          <p className="text-muted-foreground mb-6">
            Start creating presentations to see your history here.
          </p>
          <a
            href="/dashboard"
            className="inline-block px-6 py-2 bg-foreground text-background rounded-lg hover:bg-foreground/90 font-medium transition-colors shadow-sm"
          >
            Create First Presentation
          </a>
        </div>
      )}

      {!error && jobs.length > 0 && (
        <div className="bg-card rounded-2xl border border-border/50 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-secondary/40 border-b border-border/50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Prompt
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {jobs.map((job) => (
                  <tr
                    key={job.id}
                    className="hover:bg-secondary/20 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(job.status)}
                        <span className="text-sm font-medium text-foreground capitalize">
                          {job.status.toLowerCase()}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-foreground line-clamp-2">
                        {job.prompt}
                      </p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="text-sm text-muted-foreground">
                        {formatDate(job.created_at)}
                      </p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end gap-2">
                        {job.status.toLowerCase() === 'completed' && (
                          <button
                            onClick={() => handleDownload(job)}
                            className="p-2 text-foreground bg-secondary hover:bg-secondary/80 rounded-lg transition-colors border border-border/20"
                            title="Download"
                          >
                            <Download size={16} />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(job.id)}
                          className="p-2 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
