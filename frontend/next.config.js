/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router使用
  reactStrictMode: true,

  // Standalone出力（Docker用）
  output: 'standalone',

  // 画像最適化
  images: {
    unoptimized: process.env.NODE_ENV !== 'production',
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'storage.googleapis.com',
        pathname: '/**',
      },
    ],
  },
};

module.exports = nextConfig;
