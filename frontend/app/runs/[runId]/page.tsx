'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getRunDetail, processRunSSE } from '../../../lib/api';

type ProgressEvent = { phase: string; post?: string; slide?: number; progress: number; message: string };

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.runId as string;
  const [run, setRun] = useState<any>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [processing, setProcessing] = useState(false);
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [progress, setProgress] = useState(0);

  const loadRun = () => getRunDetail(runId).then(setRun).catch(() => {});

  useEffect(() => { loadRun(); }, [runId]);

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const selectAll = () => {
    if (!run) return;
    const allIds = new Set<string>(run.posts.map((p: any) => p.id));
    setSelected(selected.size === allIds.size ? new Set<string>() : allIds);
  };

  const startProcess = (mode: string) => {
    setProcessing(true);
    setEvents([]);
    setProgress(0);

    const selectStr = mode === 'auto' ? 'auto' : Array.from(selected).join(',');

    processRunSSE(
      runId,
      { select: selectStr, skip_images: false },
      (event) => {
        setEvents((prev) => [...prev, event]);
        setProgress(event.progress);
      },
      () => { setProcessing(false); loadRun(); },
      (err) => { setProcessing(false); setEvents((prev) => [...prev, { phase: 'error', progress: 0, message: err }]); },
    );
  };

  if (!run) return <p className="text-gray-400">Loading...</p>;

  const platformIcon: Record<string, string> = { reddit: '🔴', tiktok: '🎵', instagram: '📸' };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{run.query}</h1>
        <p className="text-sm text-gray-500 mt-1">{run.created_at?.slice(0, 19)} · {run.posts.length}건</p>
      </div>

      {/* Post Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-left text-gray-500">
              <th className="py-2 px-2 w-8">
                <input type="checkbox" onChange={selectAll} checked={selected.size === run.posts.length && run.posts.length > 0} className="accent-yellow-400" />
              </th>
              <th className="py-2 px-2">ID</th>
              <th className="py-2 px-2">플랫폼</th>
              <th className="py-2 px-2">제목</th>
              <th className="py-2 px-2">지표</th>
              <th className="py-2 px-2">상태</th>
            </tr>
          </thead>
          <tbody>
            {run.posts.map((post: any) => (
              <tr key={post.id} className="border-b border-gray-800/50 hover:bg-gray-900/50">
                <td className="py-2 px-2">
                  <input type="checkbox" checked={selected.has(post.id)} onChange={() => toggleSelect(post.id)} className="accent-yellow-400" />
                </td>
                <td className="py-2 px-2 font-mono text-yellow-400">{post.id}</td>
                <td className="py-2 px-2">{platformIcon[post.platform] || ''} {post.platform}</td>
                <td className="py-2 px-2 max-w-xs truncate">
                  {post.has_output ? (
                    <a href={`/runs/${encodeURIComponent(runId)}/posts/${post.id}`} className="text-blue-400 hover:underline">{post.title}</a>
                  ) : post.title}
                </td>
                <td className="py-2 px-2 text-gray-400 text-xs">
                  {post.engagement.views && `조회 ${post.engagement.views}`}
                  {post.engagement.likes && ` · 좋아요 ${post.engagement.likes}`}
                </td>
                <td className="py-2 px-2">
                  {post.has_output ? (
                    <span className="text-green-400 text-xs">완료</span>
                  ) : (
                    <span className="text-gray-600 text-xs">대기</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mt-6">
        <button
          onClick={() => startProcess('auto')}
          disabled={processing}
          className="px-5 py-2.5 bg-yellow-400 text-gray-900 font-semibold rounded-lg hover:bg-yellow-300 disabled:opacity-50 transition"
        >
          Auto Select & Process
        </button>
        <button
          onClick={() => startProcess('manual')}
          disabled={processing || selected.size === 0}
          className="px-5 py-2.5 border border-yellow-400 text-yellow-400 rounded-lg hover:bg-yellow-400/10 disabled:opacity-50 transition"
        >
          선택 처리 ({selected.size}건)
        </button>
      </div>

      {/* Progress */}
      {(processing || events.length > 0) && (
        <div className="mt-8 p-4 bg-gray-900 border border-gray-800 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold">
              {processing ? '처리 중...' : events.some(e => e.phase === 'error') ? '오류 발생' : '완료'}
            </h3>
            <span className="text-yellow-400 font-mono">{progress}%</span>
          </div>
          <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden mb-4">
            <div className="h-full bg-yellow-400 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>
          <div className="max-h-48 overflow-y-auto space-y-1 text-xs font-mono text-gray-400">
            {events.map((e, i) => (
              <div key={i} className={e.phase === 'error' ? 'text-red-400' : e.phase === 'done' || e.phase === 'all_done' ? 'text-green-400' : ''}>
                {e.message}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
