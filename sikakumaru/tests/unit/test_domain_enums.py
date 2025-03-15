import unittest

from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    Difficulty,
    DistractorType,
    QuestionFormat,
)


class TestBloomsTaxonomyLevel(unittest.TestCase):
    """BloomsTaxonomyLevel列挙型のテスト"""

    def test_all_levels(self):
        """全ての認知レベルが正しく定義されていることを確認"""
        self.assertEqual(BloomsTaxonomyLevel.REMEMBER.value, "REMEMBER")
        self.assertEqual(BloomsTaxonomyLevel.UNDERSTAND.value, "UNDERSTAND")
        self.assertEqual(BloomsTaxonomyLevel.APPLY.value, "APPLY")
        self.assertEqual(BloomsTaxonomyLevel.ANALYZE.value, "ANALYZE")
        self.assertEqual(BloomsTaxonomyLevel.EVALUATE.value, "EVALUATE")
        self.assertEqual(BloomsTaxonomyLevel.CREATE.value, "CREATE")

    def test_from_str_valid(self):
        """from_strメソッドが有効な文字列から正しく列挙型を生成することを確認"""
        self.assertEqual(BloomsTaxonomyLevel.from_str("REMEMBER"), BloomsTaxonomyLevel.REMEMBER)
        self.assertEqual(BloomsTaxonomyLevel.from_str("UNDERSTAND"), BloomsTaxonomyLevel.UNDERSTAND)
        self.assertEqual(BloomsTaxonomyLevel.from_str("APPLY"), BloomsTaxonomyLevel.APPLY)
        self.assertEqual(BloomsTaxonomyLevel.from_str("ANALYZE"), BloomsTaxonomyLevel.ANALYZE)
        self.assertEqual(BloomsTaxonomyLevel.from_str("EVALUATE"), BloomsTaxonomyLevel.EVALUATE)
        self.assertEqual(BloomsTaxonomyLevel.from_str("CREATE"), BloomsTaxonomyLevel.CREATE)

    def test_from_str_invalid(self):
        """from_strメソッドが無効な文字列に対して適切に例外を発生させることを確認"""
        with self.assertRaises(ValueError):
            BloomsTaxonomyLevel.from_str("INVALID_LEVEL")

        with self.assertRaises(ValueError):
            BloomsTaxonomyLevel.from_str("remember")  # 小文字は無効

        with self.assertRaises(ValueError):
            BloomsTaxonomyLevel.from_str("")


class TestDifficulty(unittest.TestCase):
    """Difficulty列挙型のテスト"""

    def test_all_difficulties(self):
        """全ての難易度が正しく定義されていることを確認"""
        self.assertEqual(Difficulty.EASY.value, "EASY")
        self.assertEqual(Difficulty.MEDIUM.value, "MEDIUM")
        self.assertEqual(Difficulty.HARD.value, "HARD")

    def test_from_str_valid(self):
        """from_strメソッドが有効な文字列から正しく列挙型を生成することを確認"""
        self.assertEqual(Difficulty.from_str("EASY"), Difficulty.EASY)
        self.assertEqual(Difficulty.from_str("MEDIUM"), Difficulty.MEDIUM)
        self.assertEqual(Difficulty.from_str("HARD"), Difficulty.HARD)

    def test_from_str_invalid(self):
        """from_strメソッドが無効な文字列に対して適切に例外を発生させることを確認"""
        with self.assertRaises(ValueError):
            Difficulty.from_str("INVALID_DIFFICULTY")

        with self.assertRaises(ValueError):
            Difficulty.from_str("easy")  # 小文字は無効

        with self.assertRaises(ValueError):
            Difficulty.from_str("")


class TestQuestionFormat(unittest.TestCase):
    """QuestionFormat列挙型のテスト"""

    def test_all_formats(self):
        """全ての問題形式が正しく定義されていることを確認"""
        self.assertEqual(QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER.value, "MULTIPLE_CHOICE_SINGLE_ANSWER")
        self.assertEqual(QuestionFormat.MULTIPLE_CHOICE_MULTIPLE_ANSWER.value, "MULTIPLE_CHOICE_MULTIPLE_ANSWER")
        self.assertEqual(QuestionFormat.SCENARIO_BASED.value, "SCENARIO_BASED")
        self.assertEqual(QuestionFormat.ORDERING.value, "ORDERING")
        self.assertEqual(QuestionFormat.MATCHING.value, "MATCHING")
        self.assertEqual(QuestionFormat.HOTSPOT.value, "HOTSPOT")
        self.assertEqual(QuestionFormat.CASE_STUDY.value, "CASE_STUDY")

    def test_from_str_valid(self):
        """from_strメソッドが有効な文字列から正しく列挙型を生成することを確認"""
        self.assertEqual(QuestionFormat.from_str("MULTIPLE_CHOICE_SINGLE_ANSWER"), QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER)
        self.assertEqual(QuestionFormat.from_str("MULTIPLE_CHOICE_MULTIPLE_ANSWER"), QuestionFormat.MULTIPLE_CHOICE_MULTIPLE_ANSWER)
        self.assertEqual(QuestionFormat.from_str("SCENARIO_BASED"), QuestionFormat.SCENARIO_BASED)
        self.assertEqual(QuestionFormat.from_str("ORDERING"), QuestionFormat.ORDERING)
        self.assertEqual(QuestionFormat.from_str("MATCHING"), QuestionFormat.MATCHING)
        self.assertEqual(QuestionFormat.from_str("HOTSPOT"), QuestionFormat.HOTSPOT)
        self.assertEqual(QuestionFormat.from_str("CASE_STUDY"), QuestionFormat.CASE_STUDY)

    def test_from_str_invalid(self):
        """from_strメソッドが無効な文字列に対して適切に例外を発生させることを確認"""
        with self.assertRaises(ValueError):
            QuestionFormat.from_str("INVALID_FORMAT")

        with self.assertRaises(ValueError):
            QuestionFormat.from_str("multiple_choice_single_answer")  # 小文字は無効

        with self.assertRaises(ValueError):
            QuestionFormat.from_str("")


class TestDistractorType(unittest.TestCase):
    """DistractorType列挙型のテスト"""

    def test_all_types(self):
        """全ての誤答選択肢タイプが正しく定義されていることを確認"""
        self.assertEqual(DistractorType.COMMON_MISCONCEPTION.value, "COMMON_MISCONCEPTION")
        self.assertEqual(DistractorType.PARTIAL_TRUTH.value, "PARTIAL_TRUTH")
        self.assertEqual(DistractorType.SIMILAR_CONCEPT.value, "SIMILAR_CONCEPT")
        self.assertEqual(DistractorType.RELATED_BUT_IRRELEVANT.value, "RELATED_BUT_IRRELEVANT")
        self.assertEqual(DistractorType.EXTREME_STATEMENT.value, "EXTREME_STATEMENT")

    def test_from_str_valid(self):
        """from_strメソッドが有効な文字列から正しく列挙型を生成することを確認"""
        self.assertEqual(DistractorType.from_str("COMMON_MISCONCEPTION"), DistractorType.COMMON_MISCONCEPTION)
        self.assertEqual(DistractorType.from_str("PARTIAL_TRUTH"), DistractorType.PARTIAL_TRUTH)
        self.assertEqual(DistractorType.from_str("SIMILAR_CONCEPT"), DistractorType.SIMILAR_CONCEPT)
        self.assertEqual(DistractorType.from_str("RELATED_BUT_IRRELEVANT"), DistractorType.RELATED_BUT_IRRELEVANT)
        self.assertEqual(DistractorType.from_str("EXTREME_STATEMENT"), DistractorType.EXTREME_STATEMENT)

    def test_from_str_invalid(self):
        """from_strメソッドが無効な文字列に対して適切に例外を発生させることを確認"""
        with self.assertRaises(ValueError):
            DistractorType.from_str("INVALID_TYPE")

        with self.assertRaises(ValueError):
            DistractorType.from_str("common_misconception")  # 小文字は無効

        with self.assertRaises(ValueError):
            DistractorType.from_str("")


if __name__ == "__main__":
    unittest.main()