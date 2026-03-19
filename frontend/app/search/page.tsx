'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { searchPosts } from '../../lib/api';

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState('quick');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const result = await searchPosts(query, depth);
      router.push(`/runs/${encodeURIComponent(result.run_id)}`);
    } catch (e: any) {
      setError(e.message || 'Search failed');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-12">
      <h1 className="text-2xl font-bold mb-8">SNS 콘텐츠 검색</h1>

      <div className="space-y-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="검색어를 입력하세요 (예: Z세대 소비 트렌드)"
          className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-yellow-400"
          disabled={loading}
        />

        <div className="flex gap-3">
          {['quick', 'default', 'deep'].map((d) => (
            <button
              key={d}
              onClick={() => setDepth(d)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                depth === d ? 'bg-yellow-400 text-gray-900' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {d === 'quick' ? '빠른 검색' : d === 'default' ? '기본' : '심층 검색'}
            </button>
          ))}
        </div>

        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="w-full py-3 bg-yellow-400 text-gray-900 font-semibold rounded-lg hover:bg-yellow-300 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin h-4 w-4 border-2 border-gray-900 border-t-transparent rounded-full" />
              Reddit / TikTok / Instagram 검색 중... (30-90초)
            </span>
          ) : '검색 시작'}
        </button>

        {error && <p className="text-red-400 text-sm">{error}</p>}
      </div>

      <div className="mt-8 text-sm text-gray-500">
        <p>ScrapeCreators API로 Reddit, TikTok, Instagram을 동시 검색합니다.</p>
        <p className="mt-1">검색 후 게시물을 선택하면 AI 카드뉴스가 자동 생성됩니다.</p>
      </div>
    </div>
  );
}
