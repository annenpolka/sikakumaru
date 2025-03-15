# しかくまるシステムアーキテクチャ設計書

## 1. システム概要

「しかくまる」は、認知科学と心理測定学の原則に基づいた高品質な資格試験問題を自動生成するシステムです。このシステムは、様々な資格試験に対応し、Bloom's Taxonomy の認知レベル階層や問題難易度の心理測定学的分類などの理論を取り入れ、効果的な学習と評価を促進する問題を生成します。

## 2. アーキテクチャの基本原則

- **ドメイン駆動設計（DDD）**: 問題生成という複雑なドメインを適切にモデル化
- **マイクロサービスアーキテクチャ**: 問題生成、評価、解説生成などの機能を独立したサービスとして実装
- **イベント駆動**: 非同期処理による効率的な問題生成と更新
- **AI/LLM 統合**: 最新の大規模言語モデルを活用した高品質な問題と解説の生成
- **拡張性**: 新しい資格タイプや問題形式に容易に対応できる柔軟な設計

## 3. システムレイヤー構成

### 3.1 プレゼンテーション層

- Web インターフェース（React/Next.js）
- REST API（FastAPI）
- CLI（Command Line Interface）

### 3.2 アプリケーション層

- 問題生成サービス
- 問題評価サービス
- 解説生成サービス
- ユーザープロファイリングサービス
- 学習分析サービス

### 3.3 ドメイン層

- 問題モデル（Question, QuestionMetadata）
- 認知レベル分類（BloomsTaxonomyLevel）
- 難易度モデル（Difficulty）
- 問題形式モデル（QuestionFormat）
- 解説モデル（Explanation）
- 資格モデル（Certification）

### 3.4 インフラストラクチャ層

- データベース（PostgreSQL）
- LLM サービス連携（OpenAI, Anthropic）
- キャッシュ（Redis）
- 検索エンジン（Elasticsearch）
- バックグラウンドジョブ（Celery）

## 4. コアコンポーネント詳細設計

### 4.1 問題生成エンジン（QuestionGenerationEngine）

#### 4.1.1 責務

- 資格試験に適した問題の自動生成
- Bloom's Taxonomy に基づく認知レベルの調整
- 難易度レベルの調整と評価
- 異なる問題形式（MCQ、シナリオベース、複数選択など）の生成

#### 4.1.2 主要クラス

- `QuestionGenerator`: 問題生成の中心クラス
- `BloomsTaxonomyClassifier`: 認知レベル分類機能
- `DifficultyEvaluator`: 問題難易度の評価
- `DistractorGenerator`: 効果的な不正解選択肢の生成
- `ScenarioGenerator`: シナリオベースの問題生成

#### 4.1.3 LLM プロンプト戦略

- 段階的生成アプローチ（問題文 → 選択肢 → 解説）
- 資格特化型プロンプトテンプレートの活用
- Few-shot プロンプティングによる質の向上
- 制約付きプロンプトによる形式の一貫性確保

### 4.2 心理測定学評価エンジン（PsychometricEvaluationEngine）

#### 4.2.1 責務

- 問題の妥当性（Validity）評価
- 問題の信頼性（Reliability）評価
- 項目差別力（Item Discrimination）分析
- 項目応答理論（IRT）の適用

#### 4.2.2 主要クラス

- `ValidityEvaluator`: 内容的妥当性、構成概念妥当性、予測的妥当性の評価
- `ReliabilityAnalyzer`: 内的一貫性の分析
- `ItemDiscriminationCalculator`: 問題の識別力計算
- `IRTModelApplicator`: 項目応答理論モデルの適用

### 4.3 解説生成エンジン（ExplanationGenerationEngine）

#### 4.3.1 責務

- 詳細で教育的な解説の生成
- 不正解選択肢の分析と説明
- メタ認知強化のための思考プロセス解説
- 知識の関連性と構造の強調

#### 4.3.2 主要クラス

- `ExplanationGenerator`: 解説生成の中心クラス
- `AnswerJustifier`: 正解の根拠説明
- `DistractorAnalyzer`: 不正解選択肢の詳細分析
- `MetaCognitionEnhancer`: 思考プロセスの説明
- `KnowledgeConnector`: 関連知識との結合点を提示

### 4.4 資格特化型プロンプト管理エンジン（CertificationPromptEngine）

#### 4.4.1 責務

- 資格特有の要件に基づくプロンプトテンプレート管理
- 資格ごとのドメイン、サブドメイン、トピックの体系化
- 資格特有の問題形式とスタイルの適用
- 資格の更新や変更に対する適応

#### 4.4.2 主要クラス

- `PromptTemplateManager`: テンプレート管理の中心クラス
- `CertificationDomainMapper`: 資格のドメイン構造マッピング
- `PromptCustomizer`: 資格要件に合わせたプロンプトカスタマイズ
- `VersionTracker`: 資格バージョン変更の追跡と適応

### 4.5 学習分析エンジン（LearningAnalyticsEngine）

#### 4.5.1 責務

- ユーザーの学習進捗と理解度の分析
- 知識ギャップと弱点領域の特定
- パーソナライズされた学習パスの提案
- メタ認知スキルの発達支援

#### 4.5.2 主要クラス

- `ProgressAnalyzer`: 学習進捗の分析
- `KnowledgeGapIdentifier`: 知識ギャップの特定
- `PersonalizedPathRecommender`: カスタム学習パスの推奨
- `MetaCognitionCoach`: メタ認知スキル向上のためのガイダンス

## 5. データモデル

### 5.1 コアエンティティ

```
Question
- id: UUID
- text: Text
- question_format: QuestionFormat
- cognitive_level: BloomsTaxonomyLevel
- difficulty: Difficulty
- metadata: QuestionMetadata
- choices: List[Choice]
- correct_answer: Choice
- explanation: Explanation
- tags: List[Tag]
- created_at: DateTime
- updated_at: DateTime

QuestionMetadata
- certification: Certification
- domains: List[Domain]
- topics: List[Topic]
- source: String
- version: String

Choice
- id: UUID
- text: Text
- is_correct: Boolean
- distractor_type: DistractorType (nullable)
- explanation: Text

Explanation
- id: UUID
- text: Text
- correct_answer_justification: Text
- distractor_analysis: Dict[UUID, Text]
- related_concepts: List[Concept]
- learning_resources: List[Resource]

Certification
- id: UUID
- name: String
- provider: String
- version: String
- domains: List[Domain]
- active: Boolean

Domain
- id: UUID
- name: String
- weight: Float
- topics: List[Topic]
- certification_id: UUID

Topic
- id: UUID
- name: String
- domain_id: UUID
- subtopics: List[Subtopic]
```

### 5.2 列挙型とバリューオブジェクト

```
enum QuestionFormat {
  MULTIPLE_CHOICE_SINGLE_ANSWER,
  MULTIPLE_CHOICE_MULTIPLE_ANSWER,
  SCENARIO_BASED,
  ORDERING,
  MATCHING,
  HOTSPOT,
  CASE_STUDY
}

enum BloomsTaxonomyLevel {
  REMEMBER,
  UNDERSTAND,
  APPLY,
  ANALYZE,
  EVALUATE,
  CREATE
}

enum Difficulty {
  EASY,    // P-値 > 0.7
  MEDIUM,  // P-値 0.4〜0.7
  HARD     // P-値 < 0.4
}

enum DistractorType {
  COMMON_MISCONCEPTION,
  PARTIAL_TRUTH,
  SIMILAR_CONCEPT,
  RELATED_BUT_IRRELEVANT,
  EXTREME_STATEMENT
}
```

## 6. API 設計

### 6.1 問題生成 API

```
POST /api/questions/generate
{
  "certification_id": "uuid",
  "domains": ["domain_id1", "domain_id2"],
  "topics": ["topic_id1", "topic_id2"],
  "cognitive_levels": ["UNDERSTAND", "APPLY", "ANALYZE"],
  "difficulty": "MEDIUM",
  "question_formats": ["MULTIPLE_CHOICE_SINGLE_ANSWER", "SCENARIO_BASED"],
  "count": 5
}
```

### 6.2 問題取得 API

```
GET /api/questions?certification_id=uuid&domain=domain_id&difficulty=MEDIUM&limit=10&offset=0
```

### 6.3 解説生成 API

```
POST /api/explanations/generate
{
  "question_id": "uuid",
  "detail_level": "COMPREHENSIVE"  // BASIC, STANDARD, COMPREHENSIVE
}
```

### 6.4 学習分析 API

```
GET /api/analytics/user/{user_id}/progress?certification_id=uuid
```

## 7. 統合フロー

### 7.1 問題生成フロー

1. ユーザーが問題生成パラメータを指定
2. 問題生成リクエストがキューに追加
3. 資格特化型プロンプトテンプレートが選択
4. LLM を使用して問題文を生成
5. 選択肢と正解を生成
6. 心理測定学評価エンジンが問題の品質を評価
7. 必要に応じて問題を調整
8. 解説生成エンジンが詳細な解説を生成
9. 生成された問題がデータベースに保存
10. ユーザーに完成した問題が提供

### 7.2 パーソナライズされた学習パスフロー

1. ユーザーの過去の回答データを分析
2. 知識ギャップと弱点領域を特定
3. 資格の出題範囲との関連付け
4. 認知レベルと難易度をユーザーに合わせて調整
5. 最適な問題セットを推奨
6. 学習効果を継続的に測定
7. 推奨内容を適宜更新

## 8. 展開アーキテクチャ

### 8.1 コンテナ構成

- Web アプリケーション（Frontend）
- API サーバー（Backend）
- 問題生成ワーカー
- 解説生成ワーカー
- 評価ワーカー
- データベース
- キャッシュサーバー
- ジョブキュー

### 8.2 スケーリング戦略

- 問題生成ワーカーの水平スケーリング
- 読み取り専用レプリカによるクエリパフォーマンス最適化
- キャッシュ戦略による LLM API 呼び出しの最小化
- バッチ処理による効率的な問題生成

## 9. セキュリティ考慮事項

- 問題ライブラリへのアクセス制御
- ユーザーデータの暗号化
- LLM プロンプトインジェクション対策
- API 認証と認可
- 監査ログ記録

## 10. 将来拡張計画

- マルチモーダル問題対応（画像、音声、動画）
- 適応型テスト（Computerized Adaptive Testing）
- 協調学習機能
- モバイルアプリケーション
- オフライン学習モード
- API エコシステム（サードパーティ統合）

## 11. 実装ロードマップ

### フェーズ 1: 基盤構築（1-2 ヶ月）

- コアドメインモデルの実装
- 基本的な LLM 統合
- 最小限の Web UI

### フェーズ 2: コア機能実装（2-3 ヶ月）

- 問題生成エンジンの完成
- 解説生成エンジンの実装
- 基本的な心理測定学評価機能

### フェーズ 3: 拡張機能実装（2-3 ヶ月）

- 高度な問題形式対応
- 学習分析エンジン
- パーソナライゼーション機能

### フェーズ 4: 最適化と拡張（2-3 ヶ月）

- パフォーマンス最適化
- 追加資格対応
- API 拡張とサードパーティ統合
