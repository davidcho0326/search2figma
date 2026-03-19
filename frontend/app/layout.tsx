import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SNS Card News Factory',
  description: 'SNS 콘텐츠 → AI 카드뉴스 자동 생성',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css"
        />
      </head>
      <body className="bg-gray-950 text-white font-[Pretendard] min-h-screen">
        <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
          <a href="/" className="text-xl font-bold text-yellow-400">SNS Card News Factory</a>
          <div className="flex gap-4 text-sm text-gray-400">
            <a href="/search" className="hover:text-white">Search</a>
            <a href="/runs" className="hover:text-white">Runs</a>
          </div>
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
