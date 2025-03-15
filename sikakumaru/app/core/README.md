# LLM 問題生成エンジン

このモジュールは、LLM（大規模言語モデル）を活用して高品質な資格試験問題を生成するための機能を提供します。認知科学と心理測定学の原則に基づいた問題設計を実現します。

## 主な機能

- **テンプレートベース問題生成**: 様々な問題形式や認知レベルに対応したテンプレートを使用した問題生成
- **LLM 駆動問題生成**: OpenAI GPT などの LLM を活用した高品質な問題文生成
- **誤答選択肢生成**: 異なるタイプの誤答選択肢（一般的な誤解、類似概念など）を生成
- **詳細な解説生成**: 問題の解説と各選択肢の分析を含む詳細な解説
- **適応型問題生成**: 前の問題の結果に基づいて難易度や認知レベルを調整
- **分布に基づく問題セット生成**: 指定された分布に従った問題セットの生成

## アーキテクチャ

システムは以下のコンポーネントで構成されています：

1. **基本問題生成エンジン** (`question_generation_engine.py`):

   - テンプレートベースの問題生成機能
   - 問題の基本構造とメタデータ管理

2. **LLM 問題生成エンジン** (`llm_question_generator.py`):

   - LLM を使用した拡張問題生成機能
   - プロンプトエンジニアリングを活用した高品質な問題生成

3. **LLM クライアント** (`llm_client.py`):
   - 様々な LLM サービスとの通信を抽象化
   - エラーハンドリングとフォールバック機能

## 使用方法

### 基本的な問題生成

```python
from sikakumaru.app.core.llm_question_generator import LLMQuestionGenerationEngine
from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    QuestionFormat,
    DistractorType,
    Topic
)
from sikakumaru.app.core.question_generation_engine import QuestionDifficultyLevel

# トピックの作成
topic = Topic(
    id="topic-1",
    name="Pythonプログラミング",
    parent_id=None
)

# エンジンの作成
engine = LLMQuestionGenerationEngine()

# 単一の問題生成
question = engine.generate_question(
    topic=topic,
    bloom_level=BloomsTaxonomyLevel.UNDERSTAND,
    format_type=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
    difficulty=QuestionDifficultyLevel.MEDIUM,
    distractor_type=DistractorType.COMMON_MISCONCEPTION
)

# 問題の内容を表示
print(f"問題: {question.text}")
for i, choice in enumerate(question.choices):
    correct_mark = "✓" if choice.is_correct else " "
    print(f"  {chr(65+i)}. [{correct_mark}] {choice.text}")
```

### 問題セットの生成

```python
# 認知レベルの分布
bloom_distribution = {
    BloomsTaxonomyLevel.REMEMBER: 0.3,
    BloomsTaxonomyLevel.UNDERSTAND: 0.4,
    BloomsTaxonomyLevel.APPLY: 0.3
}

# 問題形式の分布
format_distribution = {
    QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER: 0.7,
    QuestionFormat.SCENARIO_BASED: 0.3
}

# 難易度の分布
difficulty_distribution = {
    QuestionDifficultyLevel.EASY: 0.3,
    QuestionDifficultyLevel.MEDIUM: 0.5,
    QuestionDifficultyLevel.HARD: 0.2
}

# 問題セットの生成
questions = engine.generate_question_set(
    topics=[topic],
    bloom_distribution=bloom_distribution,
    format_distribution=format_distribution,
    difficulty_distribution=difficulty_distribution,
    count=10  # 生成する問題数
)
```

### LLM 設定のカスタマイズ

```python
from sikakumaru.app.llm.llm_client import LLMConfig

# LLM設定
llm_config = LLMConfig(
    model="gpt-4-turbo",  # モデル指定
    temperature=0.7,      # 創造性の度合い（0.0-1.0）
    max_tokens=2000       # 最大トークン数
)

# エンジンにLLM設定を適用
engine.set_llm_config(llm_config)
```

## デモの実行

同梱のデモスクリプトを実行して、問題生成エンジンの機能を確認できます：

```bash
python -m sikakumaru.app.core.demo
```

## 依存パッケージ

必要なパッケージをインストールするには、requirements.txt を使用してください：

```bash
pip install -r sikakumaru/app/core/requirements.txt
```

## 環境変数

LLM 機能を使用するには、以下の環境変数を設定してください：

- `OPENAI_API_KEY`: OpenAI API キー

## 注意事項

- API キーはシステム外で安全に管理し、環境変数やシークレット管理サービスを通じて提供することをお勧めします。
- 生成された問題は、資格試験の公式問題としてそのまま使用するのではなく、専門家のレビューを経ることをお勧めします。
