'use client';
import { useEffect, useState } from 'react';
import { checkHealth } from '../lib/api';

export default function Home() {
  const [status, setStatus] = useState<string>('checking...');
  const [runsCount, setRunsCount] = useState(0);

  useEffect(() => {
    checkHealth()
      .then((h) => { setStatus('connected'); setRunsCount(h.runs_count); })
      .catch(() => setStatus('disconnected'));
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-8">
      <h1 className="text-4xl font-bold">SNS Card News Factory</h1>
      <p className="text-gray-400 text-lg">SNS 콘텐츠를 AI로 분석하여 5장 카드뉴스를 자동 생성합니다</p>

      <div className="flex items-center gap-2 text-sm">
        <div className={`w-2.5 h-2.5 rounded-full ${status === 'connected' ? 'bg-green-500' : status === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'}`} />
        <span className="text-gray-400">
          Backend: {status === 'connected' ? `연결됨 (${runsCount} runs)` : status === 'disconnected' ? '연결 실패 — 로컬 백엔드를 실행하세요' : '확인 중...'}
        </span>
      </div>

      <div className="flex gap-4 mt-4">
        <a href="/search" className="px-6 py-3 bg-yellow-400 text-gray-900 font-semibold rounded-lg hover:bg-yellow-300 transition">
          새 검색 시작
        </a>
        <a href="/runs" className="px-6 py-3 border border-gray-700 rounded-lg hover:bg-gray-800 transition">
          기존 결과 보기
        </a>
      </div>
    </div>
  );
}
