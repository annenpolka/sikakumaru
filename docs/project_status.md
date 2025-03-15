# しかくまる プロジェクト状況

このドキュメントは、「しかくまる」プロジェクトの現在の状態を記録したものです。

## プロジェクト概要

「しかくまる」は資格試験対策のための自動問題生成システムです。DDDおよびTDDの手法に基づき開発され、関数型プログラミングのプラクティスを取り入れています。

## 開発環境

- Python 3.11+
- 依存関係管理: pyproject.toml + venv
- テストフレームワーク: pytest + hypothesis

## プロジェクト構造

```
/
├── .clinerules                   # Cline AIツール用のルール設定
├── .cursorrules                  # Cursor AIツール用のルール設定
├── .roomodes                     # Room モード設定
├── flowchart.md                  # システムのフロー図
├── pyproject.toml                # プロジェクト依存関係と設定
├── tech-stack.md                 # 技術スタック情報
├── sikakumaru/                   # メインパッケージ
│   ├── __init__.py               # パッケージ初期化ファイル
│   ├── app/                      # アプリケーションコード
│   │   ├── __init__.py           # アプリケーションパッケージ初期化
│   │   ├── application/          # アプリケーションサービス層（未実装）
│   │   ├── core/                 # コア機能（未実装）
│   │   ├── domain/               # ドメイン層
│   │   │   ├── __init__.py       # ドメインパッケージ初期化
│   │   │   ├── models.py         # ドメインモデル定義
│   │   │   └── exceptions/       # ドメイン例外（未実装）
│   │   ├── infrastructure/       # インフラストラクチャ層（未実装）
│   │   ├── llm/                  # LLM連携機能（未実装）
│   │   ├── output/               # 出力機能（未実装）
│   │   ├── presentation/         # プレゼンテーション層（未実装）
│   │   └── search/               # 検索機能（未実装）
│   └── tests/                    # テストコード
│       ├── __init__.py           # テストパッケージ初期化
│       ├── integration/          # 統合テスト（未実装）
│       └── unit/                 # 単体テスト
│           └── test_domain_models.py  # ドメインモデルのテスト
└── docs/                         # ドキュメント
    └── project_status.md         # このファイル
```

## 実装済みコンポーネント

### 1. ドメインモデル

`sikakumaru/app/domain/models.py` に実装されています。以下のクラスを含みます：

- **Difficulty (Enum)**: 問題の難易度を表現する列挙型
  - EASY, MEDIUM, HARD の3段階
  - from_str メソッドで文字列から Difficulty オブジェクトに変換

- **QuestionMetadata (dataclass)**: 問題のメタデータを表す値オブジェクト
  - difficulty: 問題の難易度
  - topics: 問題のトピックリスト
  - certification: 対  - source: 問題の出典（オプショナル）
  - to_dict/from_dict メソッドで辞書形式への相互変換をサポート

- **Question (dataclass)**: 問題エンティティ
  - text: 問題文
  - answer: 解答
  - metadata: QuestionMetadata オブジェクト
  - to_dict/from_dict メソッドで辞書形式への相互変換をサポート

これらはすべて不変（イミュータブル）として実装されており、関数型プログラミングの原則に従っています。

### 2. テスト

`sikakumaru/tests/unit/test_domain_models.py` に実装されています。以下のテストケースを含みます：

- **test_create_question**: 問題オブジェクトの正常な作成をテスト
- **test_to_dict**: 問題オブジェクトから辞書への変換をテスト
- **test_from_dict**: 辞書から問題オブジェクトへの変換をテスト

すべてのテストは成功しており、ドメインモデルの基本機能が正しく実装されていることを確認しています。

## 未実装コンポーネント

1. **アプリケーションサービス**
   - 資格試験対策問題生成のユースケース

2. **ドメインサービス**
   - 問題生成器（QuestionGenerator）
   - スコープ抽出器（ScopeExtractor）
   - トピック分析器（TopicAnalyzer）

3. **インフラストラクチャ**
   - LLM API クライアント
   - 検索 API クライアント
   - キャッシュメカニズム

4. **プレゼンテーションレイヤー**
   - API エンドポイント

## 次のステップ

次に実装すべきコンポーネントとして、以下の優先順位が考えられます：

1. LLM APIクライアントの抽象化レイヤー
2. ドメインサービスの実装（問題生成の中核機能）
3. 検索APIとキャッシュメカニズム
4. アプリケーションサービスとAPI