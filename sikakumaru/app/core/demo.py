"""
問題生成エンジンのデモンストレーション

このスクリプトは、LLMを使用した問題生成エンジンの基本的な使用方法を示します。
"""

import os
import uuid
from typing import Any, Dict

from sikakumaru.app.core.llm_question_generator import LLMQuestionGenerationEngine
from sikakumaru.app.core.question_generation_engine import QuestionDifficultyLevel
from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    DistractorType,
    Domain,
    QuestionFormat,
    Topic,
)
from sikakumaru.app.llm.llm_client import LLMConfig


def setup_env() -> None:
    """環境変数の設定"""
    # このサンプルでは環境変数を直接設定していますが、
    # 実際のアプリケーションでは.envファイルや設定ファイルを使用することをお勧めします

    # APIキーが設定されていない場合はダミー値を設定（実際の利用時は適切なキーを設定してください）
    if not os.environ.get("OPENAI_API_KEY"):
        print("警告: OPENAI_API_KEYが設定されていません。デモのために一時的な値を設定します。")
        os.environ["OPENAI_API_KEY"] = "your-api-key-here"


def create_sample_topic() -> Topic:
    """サンプルのトピックを作成"""
    # 実際のアプリケーションでは、データベースからトピックを取得することが多いです
    topic_id = str(uuid.uuid4())
    domain_id = str(uuid.uuid4())

    domain = Domain(
        id=domain_id,
        name="プログラミング基礎",
        weight=1.0,
        certification_id="dummy-cert"
    )

    return Topic(
        id=topic_id,
        name="Pythonプログラミング",
        parent_id=None
    )


def demo_question_generation() -> None:
    """LLM問題生成エンジンのデモ"""
    # 環境設定
    setup_env()

    # サンプルトピックの作成
    topic = create_sample_topic()

    # LLM設定
    llm_config = LLMConfig(
        model="gpt-4-turbo",  # または利用可能な最新モデル
        temperature=0.7
    )

    # エンジンの作成
    engine = LLMQuestionGenerationEngine()
    engine.set_llm_config(llm_config)

    print("=" * 80)
    print("LLM問題生成エンジンデモ")
    print("=" * 80)
    print(f"トピック: {topic.name}")
    print("-" * 80)

    # 1. 基本的な問題生成
    print("\n[1] 基本的な問題生成")
    question = engine.generate_question(
        topic=topic,
        bloom_level=BloomsTaxonomyLevel.UNDERSTAND,
        format_type=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
        difficulty=QuestionDifficultyLevel.MEDIUM,
        distractor_type=DistractorType.COMMON_MISCONCEPTION
    )

    print_question(question)

    # 2. 異なる認知レベルの問題生成
    print("\n[2] 高度な認知レベル（ANALYZE）の問題")
    question = engine.generate_question(
        topic=topic,
        bloom_level=BloomsTaxonomyLevel.ANALYZE,
        format_type=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
        difficulty=QuestionDifficultyLevel.HARD,
        distractor_type=DistractorType.SIMILAR_CONCEPT
    )

    print_question(question)

    # 3. シナリオベースの問題生成
    print("\n[3] シナリオベースの問題")
    question = engine.generate_question(
        topic=topic,
        bloom_level=BloomsTaxonomyLevel.APPLY,
        format_type=QuestionFormat.SCENARIO_BASED,
        difficulty=QuestionDifficultyLevel.MEDIUM,
        distractor_type=DistractorType.PARTIAL_TRUTH
    )

    print_question(question)

    # 4. 問題セットの生成
    print("\n[4] 問題セットの生成（3問）")

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

    questions = engine.generate_question_set(
        topics=[topic],
        bloom_distribution=bloom_distribution,
        format_distribution=format_distribution,
        difficulty_distribution=difficulty_distribution,
        count=3
    )

    for i, q in enumerate(questions):
        print(f"\n問題 {i+1}:")
        print_question(q, detailed=False)

    print("\n=" * 80)
    print("デモ完了")
    print("=" * 80)


def print_question(question, detailed=True) -> None:
    """問題を整形して表示"""
    print(f"\n問題: {question.text}")

    # 選択肢の表示
    print("\n選択肢:")
    for i, choice in enumerate(question.choices):
        correct_mark = "✓" if choice.is_correct else " "
        print(f"  {chr(65+i)}. [{correct_mark}] {choice.text}")

    # 正解の表示
    correct_choices = [choice for choice in question.choices if choice.is_correct]
    correct_indices = [i for i, choice in enumerate(question.choices) if choice.is_correct]
    correct_letters = [chr(65+i) for i in correct_indices]

    print(f"\n正解: {', '.join(correct_letters)}")

    # 詳細表示モードの場合は追加情報を表示
    if detailed and question.explanation:
        print("\n解説:")
        print(f"  {question.explanation.text}")

        print("\n誤答選択肢の分析:")
        for key, value in question.explanation.distractor_analysis.items():
            print(f"  - {value}")

        if hasattr(question.explanation, 'related_concepts') and question.explanation.related_concepts:
            print("\n関連概念:")
            for concept in question.explanation.related_concepts:
                print(f"  - {concept}")

        if question.explanation.learning_resources:
            print("\n学習リソース:")
            for resource in question.explanation.learning_resources:
                print(f"  - {resource}")

    print("\n" + "-" * 40)


if __name__ == "__main__":
    demo_question_generation()