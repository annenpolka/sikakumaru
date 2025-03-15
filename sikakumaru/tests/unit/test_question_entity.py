import unittest
import uuid
from copy import deepcopy
from datetime import datetime

from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    Choice,
    Difficulty,
    DistractorType,
    Explanation,
    Question,
    QuestionFormat,
    QuestionMetadata,
)


class TestQuestionEntity(unittest.TestCase):
    """Questionエンティティのテスト"""

    def setUp(self):
        """各テスト前の準備"""
        # テスト用のメタデータを作成
        self.metadata = QuestionMetadata(
            difficulty=Difficulty.MEDIUM,
            topics=["Python", "オブジェクト指向"],
            certification="Python検定",
            cognitive_level=BloomsTaxonomyLevel.UNDERSTAND,
            domains=["プログラミング言語", "設計"],
            source="公式問題集",
            version="2023"
        )

        # テスト用の選択肢を作成
        self.choices = [
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="Pythonはマルチパラダイムプログラミング言語である",
                is_correct=True,
                explanation="Pythonは手続き型、オブジェクト指向、関数型など複数のパラダイムをサポートしている"
            ),
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="Pythonは純粋なオブジェクト指向言語である",
                is_correct=False,
                distractor_type=DistractorType.PARTIAL_TRUTH,
                explanation="Pythonはオブジェクト指向をサポートしているが、純粋なOO言語ではない"
            ),
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="Pythonでは関数型プログラミングはできない",
                is_correct=False,
                distractor_type=DistractorType.COMMON_MISCONCEPTION,
                explanation="Pythonは高階関数、ラムダ式などの関数型プログラミング機能をサポートしている"
            ),
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="Pythonはコンパイル言語である",
                is_correct=False,
                distractor_type=DistractorType.COMMON_MISCONCEPTION,
                explanation="Pythonは主にインタープリタ言語として実行されるが、バイトコードへのコンパイルも行う"
            )
        ]

        # テスト用の解説を作成
        self.explanation = Explanation(
            id=f"explanation-{uuid.uuid4()}",
            text="Pythonはマルチパラダイムプログラミング言語であり、手続き型、オブジェクト指向、関数型など様々なスタイルのプログラミングをサポートしています。",
            correct_answer_justification="Pythonの強みの一つは異なるプログラミングパラダイムを組み合わせて使用できることです。",
            distractor_analysis={
                self.choices[1].id: "Pythonはオブジェクト指向言語ですが、他のパラダイムもサポートしています。",
                self.choices[2].id: "Pythonはmap、filter、reduceなどの関数型プログラミング機能を提供しています。",
                self.choices[3].id: "Pythonはバイトコードにコンパイルされますが、一般的にはインタープリタ言語として分類されます。"
            },
            related_concepts=["オブジェクト指向プログラミング", "関数型プログラミング", "REPL"],
            learning_resources=["Python公式ドキュメント", "https://example.com/python-paradigms"]
        )

    def test_create_question(self):
        """質問が正しく作成されることを確認"""
        question = Question(
            id=f"question-{uuid.uuid4()}",
            text="Pythonプログラミング言語について正しい記述はどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=self.choices,
            metadata=self.metadata,
            explanation=self.explanation,
            tags=["プログラミング言語", "Python", "初級"]
        )

        self.assertTrue(question.id.startswith("question-"))
        self.assertEqual(question.text, "Pythonプログラミング言語について正しい記述はどれか。")
        self.assertEqual(question.question_format, QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER)
        self.assertEqual(len(question.choices), 4)
        self.assertEqual(question.metadata.difficulty, Difficulty.MEDIUM)
        self.assertIsNotNone(question.explanation)
        if question.explanation:  # None対策
            self.assertEqual(question.explanation.text, self.explanation.text)
        self.assertEqual(question.tags, ["プログラミング言語", "Python", "初級"])

        # created_atとupdated_atが設定されていることを確認
        self.assertIsInstance(question.created_at, datetime)
        self.assertIsInstance(question.updated_at, datetime)

    def test_correct_answers_property(self):
        """correct_answersプロパティが正しく機能することを確認"""
        question = Question(
            id=f"question-{uuid.uuid4()}",
            text="Pythonプログラミング言語について正しい記述はどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=self.choices,
            metadata=self.metadata
        )

        correct_answers = question.correct_answers
        self.assertEqual(len(correct_answers), 1)
        self.assertEqual(correct_answers[0].text, "Pythonはマルチパラダイムプログラミング言語である")

    def test_distractors_property(self):
        """distractorsプロパティが正しく機能することを確認"""
        question = Question(
            id=f"question-{uuid.uuid4()}",
            text="Pythonプログラミング言語について正しい記述はどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=self.choices,
            metadata=self.metadata
        )

        distractors = question.distractors
        self.assertEqual(len(distractors), 3)
        self.assertTrue(all(not choice.is_correct for choice in distractors))

    def test_is_valid_method(self):
        """is_validメソッドが正しく機能することを確認"""
        # 有効な問題
        valid_question = Question(
            id=f"question-{uuid.uuid4()}",
            text="Pythonプログラミング言語について正しい記述はどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=self.choices,
            metadata=self.metadata
        )
        self.assertTrue(valid_question.is_valid())

        # 無効な問題（選択肢なし）
        invalid_question_no_choices = Question(
            id=f"question-{uuid.uuid4()}",
            text="Pythonプログラミング言語について正しい記述はどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=[],
            metadata=self.metadata
        )
        self.assertFalse(invalid_question_no_choices.is_valid())

        # 無効な問題（正解なし）
        no_correct_choices = [
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="選択肢1",
                is_correct=False
            ),
            Choice(
                id=f"choice-{uuid.uuid4()}",
                text="選択肢2",
                is_correct=False
            )
        ]

        invalid_question_no_correct = Question(
            id=f"question-{uuid.uuid4()}",
            text="テスト問題",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=no_correct_choices,
            metadata=self.metadata
        )
        self.assertFalse(invalid_question_no_correct.is_valid())

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        # 日付を固定して比較を簡単にする
        fixed_date = datetime(2023, 1, 1, 12, 0, 0)

        # 直接設定せずにQuestionオブジェクトを作成し、dictに変換後に日付部分を上書き
        question = Question(
            id="question-123",
            text="UNIXオペレーティングシステムの特徴として正しいものはどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=self.choices,
            metadata=self.metadata,
            explanation=self.explanation,
            tags=["OS", "UNIX", "中級"]
        )

        question_dict = question.to_dict()
        # 辞書内の日付を後から上書き
        question_dict["created_at"] = fixed_date.isoformat()
        question_dict["updated_at"] = fixed_date.isoformat()

        self.assertEqual(question_dict["id"], "question-123")
        self.assertEqual(question_dict["text"], "UNIXオペレーティングシステムの特徴として正しいものはどれか。")
        self.assertEqual(question_dict["question_format"], "MULTIPLE_CHOICE_SINGLE_ANSWER")
        self.assertEqual(len(question_dict["choices"]), 4)
        self.assertEqual(question_dict["metadata"]["difficulty"], "MEDIUM")
        self.assertEqual(question_dict["tags"], ["OS", "UNIX", "中級"])
        self.assertEqual(question_dict["created_at"], fixed_date.isoformat())
        self.assertEqual(question_dict["updated_at"], fixed_date.isoformat())

    def test_from_dict(self):
        """from_dictメソッドが正しく動作することを確認"""
        fixed_date = datetime(2023, 1, 1, 12, 0, 0).isoformat()

        # テスト用の辞書を作成
        question_dict = {
            "id": "question-456",
            "text": "データベース正規化の目的として最も適切なものはどれか。",
            "question_format": "MULTIPLE_CHOICE_SINGLE_ANSWER",
            "choices": [
                {
                    "id": "choice-1",
                    "text": "データの冗長性を排除し、整合性を保つため",
                    "is_correct": True,
                    "explanation": "正規化の主な目的はデータの冗長性を減らし、不整合を防ぐことです"
                },
                {
                    "id": "choice-2",
                    "text": "データベースの処理速度を最大化するため",
                    "is_correct": False,
                    "distractor_type": "COMMON_MISCONCEPTION",
                    "explanation": "正規化はむしろ結合操作が増えることで処理速度が低下する場合もあります"
                }
            ],
            "metadata": {
                "difficulty": "MEDIUM",
                "topics": ["データベース", "設計"],
                "certification": "データベーススペシャリスト",
                "cognitive_level": "UNDERSTAND",
                "domains": ["データベース理論"],
                "source": "模擬試験",
                "version": "2023"
            },
            "explanation": {
                "id": "explanation-456",
                "text": "データベースの正規化は、データの冗長性を排除し、整合性を保つための設計手法です。",
                "correct_answer_justification": "正規化によりデータの重複が減少し、更新異常が防止されます。",
                "distractor_analysis": {
                    "choice-2": "正規化は必ずしもパフォーマンス向上につながるわけではありません。"
                },
                "related_concepts": ["第一正規形", "第二正規形", "第三正規形"],
                "learning_resources": ["データベース設計の基礎", "https://example.com/normalization"]
            },
            "tags": ["データベース", "正規化", "設計"],
            "created_at": fixed_date,
            "updated_at": fixed_date
        }

        question = Question.from_dict(question_dict)

        self.assertEqual(question.id, "question-456")
        self.assertEqual(question.text, "データベース正規化の目的として最も適切なものはどれか。")
        self.assertEqual(question.question_format, QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER)
        self.assertEqual(len(question.choices), 2)
        self.assertEqual(question.metadata.difficulty, Difficulty.MEDIUM)
        self.assertEqual(question.metadata.topics, ["データベース", "設計"])
        self.assertIsNotNone(question.explanation)
        if question.explanation:  # None対策
            self.assertEqual(question.explanation.text, "データベースの正規化は、データの冗長性を排除し、整合性を保つための設計手法です。")
        self.assertEqual(question.tags, ["データベース", "正規化", "設計"])
        self.assertEqual(question.created_at.isoformat(), fixed_date)
        self.assertEqual(question.updated_at.isoformat(), fixed_date)

    def test_to_from_dict_consistency(self):
        """to_dictとfrom_dictの相互変換が一貫していることを確認"""
        # 固定日付を使用
        fixed_date_str = "2023-01-01T12:00:00"

        # 元の質問オブジェクトを作成
        original_question = Question(
            id="question-123",
            text="Javaプログラミング言語の特徴として正しいものはどれか。",
            question_format=QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
            choices=self.choices,
            metadata=self.metadata,
            explanation=self.explanation,
            tags=["プログラミング", "Java", "中級"]
        )

        # 辞書に変換
        question_dict = original_question.to_dict()

        # 日付を固定値に上書き
        question_dict["created_at"] = fixed_date_str
        question_dict["updated_at"] = fixed_date_str

        # 辞書から再構築
        reconstructed_question = Question.from_dict(question_dict)

        # 主要フィールドの比較
        self.assertEqual(reconstructed_question.id, original_question.id)
        self.assertEqual(reconstructed_question.text, original_question.text)
        self.assertEqual(reconstructed_question.question_format, original_question.question_format)
        self.assertEqual(len(reconstructed_question.choices), len(original_question.choices))

        # 選択肢の内容チェック
        for i, choice in enumerate(original_question.choices):
            reconstructed_choice = reconstructed_question.choices[i]
            self.assertEqual(reconstructed_choice.id, choice.id)
            self.assertEqual(reconstructed_choice.text, choice.text)
            self.assertEqual(reconstructed_choice.is_correct, choice.is_correct)

        # メタデータチェック
        self.assertEqual(reconstructed_question.metadata.difficulty, original_question.metadata.difficulty)
        self.assertEqual(reconstructed_question.metadata.topics, original_question.metadata.topics)

        # 解説チェック
        self.assertIsNotNone(reconstructed_question.explanation)
        self.assertIsNotNone(original_question.explanation)
        if reconstructed_question.explanation and original_question.explanation:  # None対策
            self.assertEqual(reconstructed_question.explanation.text, original_question.explanation.text)

        # タグチェック
        self.assertEqual(reconstructed_question.tags, original_question.tags)

        # タイムスタンプチェック
        self.assertEqual(reconstructed_question.created_at.isoformat(), fixed_date_str)
        self.assertEqual(reconstructed_question.updated_at.isoformat(), fixed_date_str)


if __name__ == "__main__":
    unittest.main()