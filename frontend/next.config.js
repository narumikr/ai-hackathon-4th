/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router使用
  reactStrictMode: true,

  // Standalone出力（Docker用）
  output: 'standalone',

  // 画像最適化
  images: {
<<<<<<< HEAD
    unoptimized: process.env.NODE_ENV === 'production',
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
        pathname: '/**',
      },
    ],
=======
    unoptimized: false,
>>>>>>> 953b3fb4b9ebaf4e6adb33b78d1acedb6cc5329d
  },

  // 開発環境でのAPIプロキシ設定（CORS回避）
  async rewrites() {
    // 本番環境ではCloud Run内部で動作するため、プロキシ不要
    if (process.env.NODE_ENV === 'production') {
      return [];
    }
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
