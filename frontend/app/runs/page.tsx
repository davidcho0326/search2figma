'use client';
import { useEffect, useState } from 'react';
import { listRuns } from '../../lib/api';

export default function RunsPage() {
  const [runs, setRuns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listRuns().then(setRuns).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-400">Loading...</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">검색 기록</h1>
      {runs.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <p>아직 검색 기록이 없습니다.</p>
          <a href="/search" className="text-yellow-400 hover:underline mt-2 inline-block">첫 검색 시작하기</a>
        </div>
      ) : (
        <div className="grid gap-4">
          {runs.map((run) => {
            const counts = run.stages?.search?.counts || {};
            const total = (counts.reddit || 0) + (counts.tiktok || 0) + (counts.instagram || 0);
            const processed = run.stages?.process?.selected?.length || 0;
            return (
              <a
                key={run.run_id}
                href={`/runs/${encodeURIComponent(run.run_id)}`}
                className="block p-4 bg-gray-900 border border-gray-800 rounded-lg hover:border-yellow-400/50 transition"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{run.query}</h3>
                    <p className="text-sm text-gray-500 mt-1">{run.created_at?.slice(0, 19)}</p>
                  </div>
                  <div className="text-right text-sm">
                    <p className="text-gray-400">{total}건 검색됨</p>
                    {processed > 0 && <p className="text-yellow-400">{processed}건 처리 완료</p>}
                  </div>
                </div>
                <div className="flex gap-4 mt-3 text-xs text-gray-500">
                  {counts.reddit > 0 && <span>Reddit {counts.reddit}</span>}
                  {counts.tiktok > 0 && <span>TikTok {counts.tiktok}</span>}
                  {counts.instagram > 0 && <span>Instagram {counts.instagram}</span>}
                </div>
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}
