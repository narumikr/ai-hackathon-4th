/**
 * 歴史的イベントの型定義
 */
export interface HistoricalEvent {
  year: number;
  event: string;
}

/**
 * 観光スポットの型定義
 */
export interface TouristSpot {
  id: string;
  name: string;
  description: string;
  historicalContext: string;
  checkpoints: string[];
}

/**
 * 旅行ガイドの型定義
 */
export interface SampleGuide {
  id: string;
  title: string;
  destination: string;
  spots: TouristSpot[];
  timeline: HistoricalEvent[];
}

/**
 * サンプル旅行ガイドデータ
 */
export const sampleGuide: SampleGuide = {
  id: '1',
  title: '京都 歴史探訪の旅',
  destination: '京都府',
  spots: [
    {
      id: 's1',
      name: '金閣寺（鹿苑寺）',
      description: '室町時代の北山文化を代表する寺院',
      historicalContext:
        '1397年、足利義満により建立された山荘を起源とし、義満の死後に禅寺となった。金箔で覆われた舎利殿「金閣」は、北山文化の象徴として知られる。',
      checkpoints: [
        '金閣（舎利殿）の建築様式を観察',
        '鏡湖池に映る金閣の美しさを鑑賞',
        '庭園の回遊式構造を体験',
      ],
    },
    {
      id: 's2',
      name: '清水寺',
      description: '京都を代表する古刹、清水の舞台で有名',
      historicalContext:
        '778年（奈良時代）に開山された古刹。現在の本堂は1633年の再建。「清水の舞台から飛び降りる」の語源となった舞台は、釘を一本も使わない懸造り（かけづくり）で建てられている。',
      checkpoints: [
        '本堂の懸造り構造を観察',
        '音羽の滝で三筋の水の意味を学ぶ',
        '仁王門から二寧坂へ続く歴史的景観を楽しむ',
      ],
    },
    {
      id: 's3',
      name: '伏見稲荷大社',
      description: '千本鳥居で有名な稲荷神社の総本宮',
      historicalContext:
        '711年（和銅4年）に創建された日本全国に約3万社ある稲荷神社の総本宮。商売繁盛・五穀豊穣の神として信仰を集め、江戸時代以降、商人たちによって奉納された朱色の鳥居が山全体に立ち並ぶ。',
      checkpoints: [
        '千本鳥居のトンネルを歩く',
        '稲荷山への参道を登る',
        '各時代の鳥居の奉納銘を観察',
      ],
    },
  ],
  timeline: [
    { year: 711, event: '伏見稲荷大社創建' },
    { year: 778, event: '清水寺開山' },
    { year: 1397, event: '金閣寺（北山殿）建立' },
    { year: 1633, event: '清水寺本堂再建' },
  ],
};
