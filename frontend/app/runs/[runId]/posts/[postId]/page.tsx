'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getPostDetail, imageUrl } from '../../../../../lib/api';

export default function PostDetailPage() {
  const params = useParams();
  const runId = params.runId as string;
  const postId = params.postId as string;
  const [post, setPost] = useState<any>(null);

  useEffect(() => {
    getPostDetail(runId, postId).then(setPost).catch(() => {});
  }, [runId, postId]);

  if (!post) return <p className="text-gray-400">Loading...</p>;

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <a href={`/runs/${encodeURIComponent(runId)}`} className="text-sm text-gray-500 hover:text-white">← 돌아가기</a>
        <h1 className="text-2xl font-bold mt-2">{post.id} — {post.platform}</h1>
        <a href={post.url} target="_blank" rel="noopener" className="text-sm text-blue-400 hover:underline">{post.url}</a>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Analysis Panel */}
        {post.analysis && (
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 text-yellow-400">AI 분석 결과</h2>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-500">핵심 주제:</span>
                <p className="mt-1 font-medium">{post.analysis.core_topic}</p>
              </div>
              <div>
                <span className="text-gray-500">감성 톤:</span>
                <span className="ml-2 px-2 py-0.5 bg-yellow-400/20 text-yellow-400 rounded text-xs">{post.analysis.emotional_tone}</span>
              </div>
              <div>
                <span className="text-gray-500">핵심 메시지:</span>
                <ul className="mt-1 list-disc list-inside text-gray-300 space-y-1">
                  {post.analysis.key_messages?.map((m: string, i: number) => (
                    <li key={i}>{m}</li>
                  ))}
                </ul>
              </div>
              <div>
                <span className="text-gray-500">타겟 오디언스:</span>
                <p className="mt-1 text-gray-300">{post.analysis.target_audience}</p>
              </div>
              <div>
                <span className="text-gray-500">바이럴 요소:</span>
                <p className="mt-1 text-gray-300">{post.analysis.viral_factor}</p>
              </div>
              <div>
                <span className="text-gray-500">카드뉴스 앵글:</span>
                <p className="mt-1 text-gray-300">{post.analysis.card_news_angle}</p>
              </div>
            </div>
          </div>
        )}

        {/* Content Slides */}
        {post.content && (
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4 text-yellow-400">5장 슬라이드 콘텐츠</h2>
            <div className="space-y-3">
              {post.content.slides?.map((slide: any, i: number) => (
                <div key={i} className="p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs px-2 py-0.5 bg-yellow-400/20 text-yellow-400 rounded">{slide.role}</span>
                    <span className="text-xs text-gray-500">Slide {i + 1}</span>
                  </div>
                  <p className="text-sm font-medium whitespace-pre-line">{slide.title}</p>
                  {slide.bottom_text && <p className="text-xs text-gray-400 mt-1">{slide.bottom_text}</p>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Card Gallery */}
      {post.cards.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4 text-yellow-400">생성된 카드뉴스</h2>
          <div className="flex gap-4 overflow-x-auto pb-4">
            {post.cards.map((card: any) => (
              <div key={card.index} className="flex-shrink-0">
                <p className="text-xs text-gray-500 mb-2 text-center">{card.index}. {card.role}</p>
                <img
                  src={imageUrl(card.image_url)}
                  alt={card.role}
                  className="w-48 h-60 object-cover rounded-lg border border-gray-800"
                  loading="lazy"
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
