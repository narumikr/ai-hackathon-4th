/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router使用
  reactStrictMode: true,

  // 本番環境ではAPIルート（プロキシ）を利用するため、静的エクスポートは行わない

  // 画像最適化（静的エクスポート時は無効化）
  images: {
    unoptimized: process.env.NODE_ENV === 'production',
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
        pathname: '/**',
      },
    ],
  },

  // 開発環境でのAPIプロキシ設定（CORS回避）
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*', // /api プレフィックスを除去してプロキシ
      },
    ];
  },
};

module.exports = nextConfig;
