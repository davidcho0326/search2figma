const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

export async function checkHealth() {
  return fetchApi<{ status: string; version: string; runs_count: number }>('/api/health');
}

export async function searchPosts(query: string, depth: string = 'quick') {
  return fetchApi<{ run_id: string; counts: Record<string, number> }>('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query, depth }),
  });
}

export async function listRuns() {
  return fetchApi<Array<{
    run_id: string; query: string; created_at: string; depth: string; stages: Record<string, any>;
  }>>('/api/runs');
}

export async function getRunDetail(runId: string) {
  return fetchApi<{
    run_id: string; query: string; created_at: string; stages: Record<string, any>;
    posts: Array<{
      id: string; platform: string; title: string; url: string;
      engagement: Record<string, any>; has_output: boolean;
    }>;
  }>(`/api/runs/${encodeURIComponent(runId)}`);
}

export async function getPostDetail(runId: string, postId: string) {
  return fetchApi<{
    id: string; platform: string; title: string; url: string;
    analysis: Record<string, any> | null;
    content: Record<string, any> | null;
    cards: Array<{ role: string; index: number; image_url: string; html_url: string }>;
    gallery_url: string | null;
  }>(`/api/runs/${encodeURIComponent(runId)}/posts/${postId}`);
}

export function imageUrl(path: string) {
  return `${BASE_URL}${path}`;
}

export function processRunSSE(
  runId: string,
  body: { select: string; skip_images: boolean },
  onEvent: (event: {
    phase: string; post?: string; slide?: number; progress: number; message: string;
  }) => void,
  onDone: () => void,
  onError: (err: string) => void,
) {
  fetch(`${BASE_URL}/api/process/${encodeURIComponent(runId)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    },
    body: JSON.stringify(body),
  }).then(async (res) => {
    if (!res.ok) {
      onError(`HTTP ${res.status}`);
      return;
    }
    const reader = res.body?.getReader();
    if (!reader) { onError('No response body'); return; }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6));
            onEvent(event);
            if (event.phase === 'all_done') onDone();
            if (event.phase === 'error') onError(event.message);
          } catch {}
        }
      }
    }
  }).catch((err) => onError(err.message));
}
