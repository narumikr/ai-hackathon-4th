import { renderMermaid, THEMES } from 'beautiful-mermaid'
import { writeFileSync, mkdirSync } from 'node:fs'

const theme = { ...THEMES['github-light'], transparent: true }

const diagrams = [
  {
    name: 'user-journey',
    source: `graph LR
    A[事前学習] --> B[現地体験]
    B --> C[振り返り]
    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#e8f5e9`,
  },
  {
    name: 'architecture',
    source: `graph LR
    User([ユーザー]) --> Frontend[Frontend / Next.js 16]
    Frontend --> Backend[Backend / FastAPI]

    Backend --> Gemini[Vertex AI / gemini-3-preview]
    Backend --> ImageGen[Vertex AI / gemini-2.5-flash-image]
    Gemini --> GoogleSearch[Google Search / Grounding]

    Backend --> CloudSQL[(Cloud SQL / PostgreSQL)]
    Backend --> CloudStorage[(Cloud Storage)]
    Backend --> CloudTasks[Cloud Tasks]
    Backend --> SecretManager[Secret Manager]

    CloudTasks --> Worker[Spot Image Worker]
    Worker --> ImageGen
    Worker --> CloudStorage
    Worker --> CloudSQL`,
  },
  {
    name: 'feature-flow',
    source: `graph LR
    Plan[計画作成] --> Guide[ガイド生成]
    Guide --> SpotImage[画像生成]
    Guide --> Maps[Maps連携]
    Guide --> Visit[現地体験]
    Visit --> Photo[写真分析]
    Photo --> Pamphlet[振り返り生成]
    style Plan fill:#e3f2fd
    style Guide fill:#e3f2fd
    style SpotImage fill:#e3f2fd
    style Maps fill:#e3f2fd
    style Visit fill:#fff3e0
    style Photo fill:#e8f5e9
    style Pamphlet fill:#e8f5e9`,
  },
  {
    name: 'agent-guide',
    source: `graph LR
    In([目的地・スポット]) --> A[Step A: 情報収集・検証]
    A --> B[Step B: ガイド生成]
    B --> C[画像生成job起動]
    C --> Out([旅行ガイド])`,
  },
  {
    name: 'agent-photo',
    source: `graph LR
    In([画像]) --> A[画像分析]
    A --> Out([画像分析結果])`,
  },
  {
    name: 'agent-image',
    source: `graph LR
    In([スポット情報]) --> A[プロンプト生成]
    A --> B[画像生成]
    B --> Out([画像])`,
  },
  {
    name: 'agent-reflection',
    source: `graph LR
    In([目的地・スポット・感想・画像分析結果]) --> A[振り返り生成]
    A --> Out([振り返り結果])`,
  },
]

const outDir = 'docs/images'
mkdirSync(outDir, { recursive: true })

for (const d of diagrams) {
  const svg = await renderMermaid(d.source, theme)
  const outPath = `${outDir}/${d.name}.svg`
  writeFileSync(outPath, svg)
  console.log(`Generated: ${outPath}`)
}
