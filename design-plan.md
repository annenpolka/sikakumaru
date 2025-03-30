# Deno CLI アプリケーション「Comprehensive Exam Generator」要件定義・設計計画

## 1. 概要

本アプリケーションは、指定されたプロンプトテンプレート (`comprehensive-exam-generator-prompt.md` 等) とユーザーからの入力に基づき、LLM (Large Language Model) を利用して資格試験問題を生成し、その結果を構造化された JSON 形式でファイルに出力する Deno 製 CLI ツールよ。

## 2. 要件定義

### 2.1. 機能要件

* **設定ファイル読み込み:** YAML または JSON 形式の設定ファイルを読み込み、試験の基本構成（ドメイン分布、難易度分布など）を取得する。
* **インタラクティブな入力:** CLI 実行時に、ユーザーに対して対話形式で必須パラメータ（資格名、分野、問題数、出力ファイルパスなど）を要求し、取得する。
* **プロンプトテンプレート読み込み:** 指定された Markdown 形式のプロンプトテンプレートファイルを読み込む。
* **プロンプト生成:** 設定ファイルとインタラクティブ入力で得られた情報、およびプロンプトテンプレートを基に、LLM に送信する最終的なプロンプト文字列を構築する。
* **LLM API 連携:** 構築したプロンプトを、設定された LLM API (OpenAI, Anthropic, Google AI 等、選択可能) に送信し、問題生成結果（Markdown 形式テキスト想定）を取得する。
* **レスポンス解析:** LLM から返却された Markdown テキストを解析し、個々の問題（問題文、選択肢、正解、解説、参照など）を抽出・構造化する。
* **JSON スキーマに基づいた整形:** 抽出・構造化されたデータを、定義された JSON スキーマに従って整形する。
* **JSON ファイル出力:** 整形された JSON データを、指定されたファイルパスに出力する。
* **進捗表示:** LLM API 通信中など、時間がかかる処理について、ユーザーに進捗状況を表示する（例: スピナー表示）。

### 2.2. 非機能要件

* **拡張性:** 将来的に異なる LLM API やプロンプトテンプレートに対応できるよう、関連モジュールは疎結合に設計する。LLM クライアント部分は特に抽象化を意識する。
* **保守性:** Deno のベストプラクティスに従い、型定義 (TypeScript) を活用し、可読性の高いコードを記述する。機能ごとにモジュールを分割する。
* **エラーハンドリング:** ファイル I/O エラー、設定ファイル形式エラー、API 通信エラー、レスポンス解析エラー、ユーザー入力エラーなどを適切にハンドリングし、ユーザーに分かりやすいエラーメッセージを表示する。Result 型などの活用を検討する。
* **設定可能性:** API キー、利用モデル、設定ファイルパス、プロンプトテンプレートパスなどを柔軟に設定・変更可能にする。

### 2.3. 入力

* **設定ファイル:** YAML または JSON 形式。以下の情報を含む想定。
  * 出題範囲ドメインと比率
  * 難易度分布
  * 認知レベル分布
  * 問題形式分布
  * 参照資料リスト (任意)
  * 利用する LLM API の種類 (例: "openai", "anthropic")
  * LLM モデル名 (例: "gpt-4o", "claude-3-opus-20240229")
  * LLM API キー (環境変数での指定も可能とし、優先度を設定)
* **インタラクティブ CLI 入力:**
  * 資格名
  * 分野 (複数指定可能)
  * 総問題数
  * 出力 JSON ファイルパス
  * 設定ファイルパス (デフォルトパスを設定)
  * プロンプトテンプレートファイルパス (デフォルトパスを設定)
* **プロンプトテンプレートファイル:** Markdown 形式。`comprehensive-exam-generator-prompt.md` がデフォルト。

### 2.4. 出力

* **JSON ファイル:** 指定されたパスに、生成された問題セットを後述のスキーマに従って出力する。
* **標準出力/標準エラー出力:** 実行中の進捗、完了メッセージ、エラーメッセージなどを表示する。

## 3. LLM 連携設計

* **API アクセス:** 特定の LLM API に依存しないよう、汎用的なインターフェース (`LLMClient`のような) を定義し、その実装として各 API (OpenAI, Anthropic 等) へのアダプターを作成する。これにより、設定ファイルで利用する API を切り替え可能にする。
* **ライブラリ候補:**
  * Deno のエコシステムで、複数の LLM を抽象化するライブラリがあれば活用を検討する (例: `langchain` の Deno 移植版などがあれば理想的だが、現状有力なものが見当たらない可能性もあるわ)。
  * 見つからない場合は、`fetch` API を用いて各 API のエンドポイントに直接リクエストを送信するシンプルなアダプターを自作する。主要な API (OpenAI, Anthropic) から対応するのが現実的でしょう。
* **認証:** API キーは、まず環境変数を確認し、設定されていなければ設定ファイルから読み込む方式とする。キーの取り扱いには十分注意が必要よ。
* **リクエスト:** プロンプト生成モジュールが作成したプロンプト文字列を、選択された LLM API の仕様に合わせてリクエストボディに含める。
* **レスポンス:** LLM から返されるテキスト（Markdown 形式想定）を取得する。ストリーミング応答に対応するかは初期段階では必須としないが、将来的な改善点として考慮する価値はあるわね。

## 4. アプリケーション設計 (Deno/TypeScript)

### 4.1. アーキテクチャとモジュール分割

主要な関心事を分離するため、以下のモジュール構成を提案するわ。

```mermaid
graph TD
    A[main.ts (エントリーポイント)] --> B{CLI処理};
    B --> C[設定読み込み];
    B --> D[インタラクティブ入力];
    C --> E[プロンプト生成];
    D --> E;
    F[テンプレート読み込み] --> E;
    E --> G{LLMクライアント};
    G --> H[LLM API (外部)];
    H --> G;
    G --> I[レスポンス解析];
    I --> J[JSON整形/出力];

    subgraph Core Logic
        E
        G
        I
        J
    end

    subgraph Input Handling
        B
        C
        D
        F
    end

    style Core Logic fill:#f9f,stroke:#333,stroke-width:2px
    style Input Handling fill:#ccf,stroke:#333,stroke-width:2px
```

* **`main.ts`:** アプリケーションのエントリーポイント。全体の処理フローを制御する。
* **`src/cli.ts`:** CLI 引数の解析とインタラクティブなユーザー入力の処理を担当。
* **`src/config.ts`:** 設定ファイル (YAML/JSON) の読み込みと検証を担当。
* **`src/template.ts`:** プロンプトテンプレートファイルの読み込みを担当。
* **`src/prompt_builder.ts`:** テンプレート、設定、ユーザー入力から最終的な LLM プロンプトを構築する。
* **`src/llm/`:** LLM 連携関連モジュール。
  * **`client.ts`:** `LLMClient` インターフェース定義。
  * **`openai_adapter.ts`:** OpenAI API 用アダプター実装。
  * **`anthropic_adapter.ts`:** Anthropic API 用アダプター実装 (必要に応じて)。
* **`src/parser.ts`:** LLM のレスポンス (Markdown) を解析し、構造化データに変換する。正規表現や簡単なパーサーロジックが必要になるでしょう。
* **`src/output.ts`:** 構造化データを指定された JSON スキーマに整形し、ファイルに出力する。
* **`src/types.ts`:** アプリケーション全体で使用する型定義 (設定、問題データ構造など)。
* **`src/error.ts`:** カスタムエラー型やエラーハンドリング関連のユーティリティ。

### 4.2. 利用ライブラリ候補

* **CLI 引数/インタラクション:**
  * `deno.land/std/flags` (標準ライブラリ): シンプルな引数解析に。
  * `deno.land/x/cliffy`: より高機能な CLI フレームワーク。インタラクティブプロンプトもサポートしているため、有力候補ね。
* **設定ファイル:**
  * `deno.land/std/jsonc` または `deno.land/std/json`: JSON/JSONC ファイルのパースに。
  * `deno.land/std/yaml`: YAML ファイルのパースに。
* **ファイル操作:**
  * `deno.land/std/fs`: ファイルの読み書きに。
  * `deno.land/std/path`: パス操作に。
* **HTTP クライアント:**
  * `fetch` (Deno グローバル): LLM API との通信に標準で利用可能。
* **その他:**
  * 進捗表示: `deno.land/x/spinner` のようなライブラリ。

### 4.3. エラーハンドリング方針

* 各処理（ファイル読み込み、設定解析、API 通信、レスポンス解析など）で発生しうるエラーを想定し、`try...catch` や Result パターン (`Ok`/`Err`) を用いて適切に捕捉する。
* ユーザーに起因するエラー（ファイルが見つからない、設定形式が不正など）は、分かりやすいメッセージと共に終了コードを返す。
* API 通信エラー（ネットワークエラー、認証エラー、レートリミットなど）は、リトライ処理（接続エラー等）を検討しつつ、最終的にはエラーメッセージを表示して終了する。`.clinerules` の再試行ポリシーに従うこと。
* レスポンス解析エラー（LLM の出力形式が予期したものと異なる場合）は、可能な限り堅牢なパーサーを実装するが、完全に防ぐのは難しいわね。エラー発生時は、どの部分で解析に失敗したかを示す情報をログに出力し、ユーザーには解析失敗のメッセージを表示する。

## 5. 出力 JSON スキーマ (TypeScript 型定義)

```typescript
// src/types.ts

/** アプリケーション全体の設定 */
export interface AppConfig {
  llm: LLMConfig;
  exam: ExamConfig;
}

/** LLM関連設定 */
export interface LLMConfig {
  provider: "openai" | "anthropic" | string; // 利用するLLMプロバイダー
  model: string; // 利用するモデル名
  apiKey?: string; // APIキー (環境変数優先)
  // その他、temperatureなどのパラメータも追加可能
}

/** 試験構成設定 */
export interface ExamConfig {
  domains: DomainDistribution[]; // ドメインとその比率
  difficultyDistribution: DifficultyDistribution; // 難易度分布
  cognitiveLevelDistribution: CognitiveLevelDistribution; // 認知レベル分布
  questionTypeDistribution: QuestionTypeDistribution; // 問題形式分布
  referenceMaterials?: string[]; // 参照資料リスト
}

export interface DomainDistribution {
  name: string;
  percentage: number;
}

export interface DifficultyDistribution {
  basic: number; // 基礎レベル (%)
  intermediate: number; // 中級レベル (%)
  advanced: number; // 上級レベル (%)
}

export interface CognitiveLevelDistribution {
  remember: number;
  understand: number;
  apply: number;
  analyze: number;
  evaluate: number;
  create: number;
}

export interface QuestionTypeDistribution {
  mcq: number; // 標準MCQ (%)
  scenario: number; // シナリオベース (%)
  multipleSelect?: number; // 複数選択 (%)
  // 他の形式も追加可能
}

/** CLIでインタラクティブに取得するパラメータ */
export interface CLIOptions {
  qualification: string;
  field: string[];
  count: number;
  output: string;
  configPath: string;
  templatePath: string;
}

/** 出力JSONの全体構造 */
export interface ExamResultSet {
  metadata: ExamMetadata;
  questions: Question[];
}

/** 試験メタデータ */
export interface ExamMetadata {
  qualification: string;
  field: string[];
  total_questions_requested: number; // 要求された問題数
  total_questions_generated: number; // 実際に生成された問題数
  generated_at: string; // ISO 8601 形式
  llm_provider_used: string;
  llm_model_used: string;
  prompt_template_path: string;
  config_path: string;
  // 設定ファイルから読み込んだ分布情報なども含めるとより丁寧
  domain_distribution_config?: DomainDistribution[];
  difficulty_distribution_config?: DifficultyDistribution;
  // ... 他の分布設定
}

/** 個々の問題データ */
export interface Question {
  id: string; // UUIDなどで一意に
  question_number: number;
  domain?: string; // 該当ドメイン
  difficulty?: "basic" | "intermediate" | "advanced" | string; // 推定難易度
  cognitive_level?: "remember" | "understand" | "apply" | "analyze" | "evaluate" | "create" | string; // 推定認知レベル
  question_type?: "MCQ" | "Scenario" | "MultipleSelect" | string; // 問題形式
  stem: string; // 問題文 or シナリオ
  choices?: Record<string, string>; // 選択肢 (例: { "A": "...", "B": "..." })
  correct_answer: string | string[]; // 正解 (単一または複数)
  explanation: Explanation; // 解説
  reference?: string; // 参照情報
}

/** 解説データ */
export interface Explanation {
  correct_reason: string; // 正解の根拠
  incorrect_analysis?: Record<string, string>; // 不正解選択肢の分析 (例: { "A": "なぜAが違うか", "C": "..." })
  supplement?: string; // 補足情報
}
```

## 6. 今後のステップ

1. **計画レビューと承認:** この計画をあなたが確認し、承認または修正点を指示する。
2. **Markdown ファイル出力 (任意):** 承認後、この計画を Markdown ファイルとして保存するかどうか確認する。
3. **実装フェーズへの移行:** Code モードに切り替え、この設計計画に基づいて実装を開始する。
4. **テストフェーズ:** Debug モードに切り替え、実装された機能のテストとデバッグを行う。
5. **ドキュメント作成:** 最終的なアプリケーションの利用方法や設定方法に関するドキュメントを作成する。
