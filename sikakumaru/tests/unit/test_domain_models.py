from __future__ import annotations

import unittest
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from sikakumaru.app.domain.models import Question, QuestionMetadata, Difficulty


class TestQuestion(unittest.TestCase):
    """問題（Question）ドメインモデルのテスト"""

    def test_create_question(self):
        """問題を正しく作成できることを確認"""
        metadata = QuestionMetadata(
            difficulty=Difficulty.MEDIUM,
            topics=["コンピュータネットワーク", "TCP/IP"],
            certification="ネットワークスペシャリスト",
            source=None
        )

        question = Question(
            text="TCP/IPのコネクション確立時に行われる3ウェイハンドシェイクの順序として正しいものはどれか。",
            answer="SYN→SYN+ACK→ACK",
            metadata=metadata
        )

        # エンティティとして正しく作成されていることを確認
        self.assertEqual(question.text, "TCP/IPのコネクション確立時に行われる3ウェイハンドシェイクの順序として正しいものはどれか。")
        self.assertEqual(question.answer, "SYN→SYN+ACK→ACK")
        self.assertEqual(question.metadata.difficulty, Difficulty.MEDIUM)
        self.assertEqual(question.metadata.certification, "ネットワークスペシャリスト")
        self.assertEqual(question.metadata.topics, ["コンピュータネットワーク", "TCP/IP"])
        self.assertIsNone(question.metadata.source)

    def test_to_dict(self):
        """問題を辞書形式に変換できることを確認"""
        metadata = QuestionMetadata(
            difficulty=Difficulty.EASY,
            topics=["データベース", "SQL"],
            certification="データベーススペシャリスト",
            source="公式問題集"
        )

        question = Question(
            text="主キーの役割として適切なものはどれか。",
            answer="テーブル内のレコードを一意に識別する",
            metadata=metadata
        )

        question_dict = question.to_dict()

        # 辞書形式に正しく変換されていることを確認
        self.assertEqual(question_dict["text"], "主キーの役割として適切なものはどれか。")
        self.assertEqual(question_dict["answer"], "テーブル内のレコードを一意に識別する")
        self.assertEqual(question_dict["metadata"]["difficulty"], "EASY")
        self.assertEqual(question_dict["metadata"]["certification"], "データベーススペシャリスト")
        self.assertEqual(question_dict["metadata"]["topics"], ["データベース", "SQL"])
        self.assertEqual(question_dict["metadata"]["source"], "公式問題集")

    def test_from_dict(self):
        """辞書形式から問題を作成できることを確認"""
        question_dict = {
            "text": "OSI参照モデルのアプリケーション層の役割として適切なものはどれか。",
            "answer": "利用者向けのサービスを提供する",
            "metadata": {
                "difficulty": "HARD",
                "topics": ["ネットワーク", "OSI参照モデル"],
                "certification": "ネットワークスペシャリスト",
                "source": None
            }
        }

        question = Question.from_dict(question_dict)

        # 辞書形式から正しく問題が作成されていることを確認
        self.assertEqual(question.text, "OSI参照モデルのアプリケーション層の役割として適切なものはどれか。")
        self.assertEqual(question.answer, "利用者向けのサービスを提供する")
        self.assertEqual(question.metadata.difficulty, Difficulty.HARD)
        self.assertEqual(question.metadata.certification, "ネットワークスペシャリスト")
        self.assertEqual(question.metadata.topics, ["ネットワーク", "OSI参照モデル"])
        self.assertIsNone(question.metadata.source)


if __name__ == '__main__':
    unittest.main()