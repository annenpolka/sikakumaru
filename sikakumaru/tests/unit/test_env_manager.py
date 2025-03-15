import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from sikakumaru.app.infrastructure.env_manager import (
    AppEnvVars,
    EnvManager,
    EnvVarNotFoundError,
    EnvVarValidationError,
    LLMEnvVars,
    get_env,
    load_env_file,
    validate_env,
)


class TestEnvManager(unittest.TestCase):
    """環境変数マネージャー（EnvManager）のユニットテスト"""

    def setUp(self):
        """各テスト前の準備"""
        # 環境変数のバックアップを作成
        self.env_backup = os.environ.copy()
        # テスト用の環境変数を設定
        os.environ["TEST_STRING"] = "test_value"
        os.environ["TEST_INT"] = "42"
        os.environ["TEST_FLOAT"] = "3.14"
        os.environ["TEST_BOOL"] = "true"
        os.environ["TEST_LIST"] = "one,two,three"

        # エンジンのキャッシュをリセット
        self.env_manager = EnvManager()
        self.env_manager.reset_cache()

    def tearDown(self):
        """各テスト後の後処理"""
        # 環境変数を元に戻す
        os.environ.clear()
        os.environ.update(self.env_backup)

    def test_get_string(self):
        """文字列の環境変数を取得できることを確認"""
        value = self.env_manager.get("TEST_STRING")
        self.assertEqual(value, "test_value")

    def test_get_with_default(self):
        """存在しない環境変数の場合、デフォルト値が返されることを確認"""
        value = self.env_manager.get("NON_EXISTENT_VAR", default="default_value")
        self.assertEqual(value, "default_value")

    def test_get_int(self):
        """整数型の環境変数を取得できることを確認"""
        value = self.env_manager.get_int("TEST_INT")
        self.assertEqual(value, 42)
        self.assertIsInstance(value, int)

    def test_get_float(self):
        """浮動小数点数型の環境変数を取得できることを確認"""
        value = self.env_manager.get_float("TEST_FLOAT")
        self.assertEqual(value, 3.14)
        self.assertIsInstance(value, float)

    def test_get_bool(self):
        """真偽値型の環境変数を取得できることを確認"""
        value = self.env_manager.get_bool("TEST_BOOL")
        self.assertEqual(value, True)
        self.assertIsInstance(value, bool)

        # falseの場合のテスト
        os.environ["TEST_BOOL_FALSE"] = "false"
        value = self.env_manager.get_bool("TEST_BOOL_FALSE")
        self.assertEqual(value, False)

    def test_get_list(self):
        """リスト型の環境変数を取得できることを確認"""
        value = self.env_manager.get_list("TEST_LIST")
        self.assertEqual(value, ["one", "two", "three"])
        self.assertIsInstance(value, list)

    def test_required_env_var_missing(self):
        """必須環境変数が欠けている場合、適切な例外が発生することを確認"""
        # モックされた環境変数の定義を作成（OPENAIのキーが必須）
        with self.assertRaises(EnvVarNotFoundError):
            # OPENAIのキーは必須設定なので、存在しない場合は例外が発生する
            os.environ.pop("OPENAI_API_KEY", None)  # 環境変数から削除
            self.env_manager.reset_cache()  # キャッシュをリセット
            self.env_manager.get("OPENAI_API_KEY")  # 例外が発生するはず

    @patch("sikakumaru.app.infrastructure.env_manager.dotenv_available", True)
    @patch("sikakumaru.app.infrastructure.env_manager.load_dotenv")
    def test_load_env_file(self, mock_load_dotenv):
        """環境変数ファイルが正しく読み込まれることを確認"""
        # 一時的な.envファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".env") as temp_env:
            temp_env.write(b"TEST_KEY=test_value\n")
            temp_env.flush()

            # .envファイルのパスを指定して読み込み
            result = self.env_manager.load_env_file(temp_env.name)

            # 結果と呼び出し履歴を確認
            self.assertTrue(result)
            mock_load_dotenv.assert_called_once()

    def test_validation(self):
        """環境変数の検証が正しく行われることを確認"""
        # 検証エラーが発生する環境変数を設定
        os.environ["LLM_TEMPERATURE"] = "2.0"  # 許容範囲は0.0-1.0

        # キャッシュをリセット
        self.env_manager.reset_cache()

        # 検証エラーが発生することを確認
        with self.assertRaises(EnvVarValidationError):
            self.env_manager.get("LLM_TEMPERATURE")

    def test_helper_functions(self):
        """ヘルパー関数が正しく動作することを確認"""
        # get_env関数のテスト
        value = get_env("TEST_STRING")
        self.assertEqual(value, "test_value")

        # APIキーが設定されている場合のLLMEnvVarsのテスト
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        os.environ["DEFAULT_LLM_MODEL"] = "gpt-4"
        os.environ["LLM_TEMPERATURE"] = "0.5"

        # キャッシュをリセット
        self.env_manager.reset_cache()

        self.assertEqual(LLMEnvVars.get_api_key(), "test_api_key")
        self.assertEqual(LLMEnvVars.get_default_model(), "gpt-4")
        self.assertEqual(LLMEnvVars.get_temperature(), 0.5)

        # AppEnvVarsのテスト
        os.environ["APP_ENV"] = "development"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["MAX_QUESTIONS_PER_REQUEST"] = "20"

        # キャッシュをリセット
        self.env_manager.reset_cache()

        self.assertTrue(AppEnvVars.is_development())
        self.assertEqual(AppEnvVars.get_log_level(), "DEBUG")
        self.assertEqual(AppEnvVars.get_max_questions_per_request(), 20)


if __name__ == "__main__":
    unittest.main()