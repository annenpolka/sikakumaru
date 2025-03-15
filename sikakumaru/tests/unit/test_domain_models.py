from __future__ import annotations

import unittest
import uuid
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    Choice,
    Difficulty,
    DistractorType,
    Question,
    QuestionFormat,
    QuestionMetadata,
)


class TestQuestion(unittest.TestCase):
    """問題（Question）ドメインモデルのテスト"""

    def test_create_question(self):
        """問題を正しく作成できることを確認"""
        metadata = QuestionMetadata(
            difficulty=Difficulty.MEDIUM,
            topics=["コンピュータネットワーク", "TCP/IP"],
            certification="ネットワークスペシャリスト",
            source=None,
            cognitive_level=BloomsTaxonomyLevel.UNDERSTAND
        )

        # 選択肢を作成
        choices = [
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="SYN→SYN+ACK→ACK",
                is_correct=True
            ),
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="ACK→SYN→SYN+ACK",
                is_correct=False,
                distractor_type=DistractorType.COMMON_MISCONCEPTION
            )
        ]

        question = Question(
            id=f"question-{uuid.uuid4()}",
            text="TCP/IPのコネクション確立時に行われる3ウェイハンドシェイクの順序として正しいものはどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=choices,
            metadata=metadata
        )

        # エンティティとして正しく作成されていることを確認
        self.assertEqual(question.text, "TCP/IPのコネクション確立時に行われる3ウェイハンドシェイクの順序として正しいものはどれか。")
        self.assertEqual(question.metadata.difficulty, Difficulty.MEDIUM)
        self.assertEqual(question.metadata.certification, "ネットワークスペシャリスト")
        self.assertEqual(question.metadata.topics, ["コンピュータネットワーク", "TCP/IP"])
        self.assertEqual(question.metadata.cognitive_level, BloomsTaxonomyLevel.UNDERSTAND)
        self.assertIsNone(question.metadata.source)
        self.assertEqual(len(question.choices), 2)
        self.assertEqual(len(question.correct_answers), 1)
        self.assertEqual(question.correct_answers[0].text, "SYN→SYN+ACK→ACK")

    def test_to_dict(self):
        """問題を辞書形式に変換できることを確認"""
        metadata = QuestionMetadata(
            difficulty=Difficulty.EASY,
            topics=["データベース", "SQL"],
            certification="データベーススペシャリスト",
            source="公式問題集",
            cognitive_level=BloomsTaxonomyLevel.APPLY
        )

        # 選択肢を作成
        choices = [
            Choice(
                id="choice-1",
                text="テーブル内のレコードを一意に識別する",
                is_correct=True
            ),
            Choice(
                id="choice-2",
                text="テーブル間の関係を示す",
                is_correct=False,
                distractor_type=DistractorType.PARTIAL_TRUTH
            )
        ]

        question = Question(
            id="q-123",
            text="主キーの役割として適切なものはどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=choices,
            metadata=metadata
        )

        question_dict = question.to_dict()

        # 辞書形式に正しく変換されていることを確認
        self.assertEqual(question_dict["text"], "主キーの役割として適切なものはどれか。")
        self.assertEqual(question_dict["metadata"]["difficulty"], "EASY")
        self.assertEqual(question_dict["metadata"]["certification"], "データベーススペシャリスト")
        self.assertEqual(question_dict["metadata"]["topics"], ["データベース", "SQL"])
        self.assertEqual(question_dict["metadata"]["source"], "公式問題集")
        self.assertEqual(question_dict["metadata"]["cognitive_level"], "APPLY")
        self.assertEqual(len(question_dict["choices"]), 2)
        self.assertEqual(question_dict["choices"][0]["text"], "テーブル内のレコードを一意に識別する")
        self.assertTrue(question_dict["choices"][0]["is_correct"])

    def test_from_dict(self):
        """辞書形式から問題を作成できることを確認"""
        question_dict = {
            "id": "q-456",
            "text": "OSI参照モデルのアプリケーション層の役割として適切なものはどれか。",
            "question_format": "MULTIPLE_CHOICE_SINGLE_ANSWER",
            "choices": [
                {
                    "id": "choice-1",
                    "text": "利用者向けのサービスを提供する",
                    "is_correct": True
                },
                {
                    "id": "choice-2",
                    "text": "データの転送制御を行う",
                    "is_correct": False,
                    "distractor_type": "COMMON_MISCONCEPTION"
                }
            ],
            "metadata": {
                "difficulty": "HARD",
                "topics": ["ネットワーク", "OSI参照モデル"],
                "certification": "ネットワークスペシャリスト",
                "source": None,
                "cognitive_level": "ANALYZE"
            }
        }

        question = Question.from_dict(question_dict)

        # 辞書形式から正しく問題が作成されていることを確認
        self.assertEqual(question.text, "OSI参照モデルのアプリケーション層の役割として適切なものはどれか。")
        self.assertEqual(question.metadata.difficulty, Difficulty.HARD)
        self.assertEqual(question.metadata.certification, "ネットワークスペシャリスト")
        self.assertEqual(question.metadata.topics, ["ネットワーク", "OSI参照モデル"])
        self.assertEqual(question.metadata.cognitive_level, BloomsTaxonomyLevel.ANALYZE)
        self.assertIsNone(question.metadata.source)
        self.assertEqual(len(question.choices), 2)
        self.assertEqual(question.correct_answers[0].text, "利用者向けのサービスを提供する")


if __name__ == '__main__':
    unittest.main()