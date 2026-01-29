# Node.js 22のスリムイメージを使用
FROM node:22-slim AS base

# pnpmのインストール
RUN corepack enable && corepack prepare pnpm@latest --activate

# 依存関係のインストール
FROM base AS deps
WORKDIR /app

# 依存関係ファイルをコピー
COPY package.json pnpm-lock.yaml ./

# 依存関係のインストール
RUN pnpm install --frozen-lockfile

# ビルド
FROM base AS builder
WORKDIR /app

# 依存関係をコピー
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 環境変数（ビルド時）
ENV NEXT_TELEMETRY_DISABLED=1

# Next.jsアプリケーションをビルド
RUN pnpm run build

# 本番環境
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# 非rootユーザーを作成
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 必要なファイルをコピー
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# Cloud Runのポート（環境変数PORTから取得、デフォルトは3000）
ENV PORT=3000
EXPOSE 3000

# Next.jsサーバーを起動
CMD ["node", "server.js"]
