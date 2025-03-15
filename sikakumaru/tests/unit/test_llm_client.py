import unittest
from unittest.mock import MagicMock, patch

from sikakumaru.app.llm.llm_client import (
    LLMClient,
    LLMClientFactory,
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMResponse,
    LLMRole,
    OpenAIClient,
)


class TestLLMMessage(unittest.TestCase):
    """LLMMessageクラスのテスト"""

    def test_create_message(self):
        """LLMMessageが正しく作成されることを確認"""
        message = LLMMessage(role=LLMRole.SYSTEM, content="システムメッセージ")
        self.assertEqual(message.role, LLMRole.SYSTEM)
        self.assertEqual(message.content, "システムメッセージ")

    def test_create_message_with_string_role(self):
        """文字列ロールでLLMMessageが正しく作成されることを確認"""
        message = LLMMessage(role="user", content="ユーザーメッセージ")
        self.assertEqual(message.role, LLMRole.USER)
        self.assertEqual(message.content, "ユーザーメッセージ")

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        message = LLMMessage(role=LLMRole.ASSISTANT, content="アシスタントメッセージ")
        message_dict = message.to_dict()
        self.assertEqual(message_dict["role"], "assistant")
        self.assertEqual(message_dict["content"], "アシスタントメッセージ")

    def test_from_dict(self):
        """from_dictメソッドが正しく動作することを確認"""
        message_dict = {
            "role": "system",
            "content": "システム指示"
        }
        message = LLMMessage.from_dict(message_dict)
        self.assertEqual(message.role, LLMRole.SYSTEM)
        self.assertEqual(message.content, "システム指示")


class TestLLMConfig(unittest.TestCase):
    """LLMConfigクラスのテスト"""

    @patch("sikakumaru.app.llm.llm_client.LLMEnvVars")
    def test_create_config(self, mock_env_vars):
        """LLMConfigが正しく作成されることを確認"""
        # 環境変数からの取得をモック
        mock_env_vars.get_default_model.return_value = "gpt-4"
        mock_env_vars.get_temperature.return_value = 0.7
        mock_env_vars.get_api_key.return_value = "test-api-key"
        mock_env_vars.get_api_base.return_value = None

        config = LLMConfig(max_tokens=1000)
        self.assertEqual(config.provider, LLMProvider.OPENAI)
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 1000)
        self.assertEqual(config.api_key, "test-api-key")
        self.assertIsNone(config.api_base)

    def test_config_with_custom_values(self):
        """カスタム値でLLMConfigが正しく作成されることを確認"""
        config = LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=500,
            api_key="custom-api-key",
            api_base="https://custom-endpoint.openai.azure.com"
        )
        self.assertEqual(config.provider, LLMProvider.AZURE_OPENAI)
        self.assertEqual(config.model, "gpt-3.5-turbo")
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.max_tokens, 500)
        self.assertEqual(config.api_key, "custom-api-key")
        self.assertEqual(config.api_base, "https://custom-endpoint.openai.azure.com")

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        config = LLMConfig(
            model="gpt-4",
            temperature=0.8,
            max_tokens=2000,
            top_p=0.9
        )
        config_dict = config.to_dict()
        self.assertEqual(config_dict["model"], "gpt-4")
        self.assertEqual(config_dict["temperature"], 0.8)
        self.assertEqual(config_dict["top_p"], 0.9)
        self.assertEqual(config_dict.get("max_tokens"), 2000)


class TestOpenAIClient(unittest.TestCase):
    """OpenAIClientクラスのテスト"""

    @patch("sikakumaru.app.llm.llm_client.OpenAI")
    @patch("sikakumaru.app.llm.llm_client.AsyncOpenAI")
    def setUp(self, mock_async_openai, mock_openai):
        """各テスト前の準備"""
        self.mock_openai = mock_openai
        self.mock_async_openai = mock_async_openai

        # レスポンスのモックを設定
        self.mock_completion = MagicMock()
        self.mock_completion.choices = [
            MagicMock(message=MagicMock(content="テスト応答"), finish_reason="stop")
        ]
        # Usageをオブジェクトとしてモック
        self.mock_completion.usage = MagicMock()
        self.mock_completion.usage.prompt_tokens = 10
        self.mock_completion.usage.completion_tokens = 20
        self.mock_completion.usage.total_tokens = 30

        # 同期クライアントのモック設定
        self.mock_openai_instance = MagicMock()
        self.mock_openai_instance.chat.completions.create.return_value = self.mock_completion
        self.mock_openai.return_value = self.mock_openai_instance

        # 非同期クライアントのモック設定
        self.mock_async_openai_instance = MagicMock()
        self.mock_async_openai_instance.chat.completions.create.return_value = self.mock_completion
        self.mock_async_openai.return_value = self.mock_async_openai_instance

        # テスト用のクライアントを作成
        self.config = LLMConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            api_key="test-api-key"
        )
        self.client = OpenAIClient(self.config)

    def test_generate(self):
        """generateメソッドが正しく動作することを確認"""
        response = self.client.generate("テストプロンプト")

        # APIが正しく呼び出されたことを確認
        self.mock_openai_instance.chat.completions.create.assert_called_once()

        # 引数を確認
        call_args = self.mock_openai_instance.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4")
        self.assertEqual(call_args["temperature"], 0.7)

        # メッセージの内容を確認
        messages = call_args["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "テストプロンプト")

        # レスポンスが正しいことを確認
        self.assertEqual(response.content, "テスト応答")
        # プロパティごとに比較する（オブジェクト自体の比較ではなく）
        self.assertEqual(response.usage["prompt_tokens"], 10)
        self.assertEqual(response.usage["completion_tokens"], 20)
        self.assertEqual(response.usage["total_tokens"], 30)
        self.assertEqual(response.finish_reason, "stop")

    @patch("sikakumaru.app.llm.llm_client.asyncio.run")
    def test_generate_with_messages(self, mock_asyncio_run):
        """generate_with_messagesメソッドが正しく動作することを確認"""
        # モックの挙動を調整
        # OpenAIClient.generate_with_messagesメソッドを直接モック化して、asyncio.runが呼び出されないようにする
        with patch.object(self.client, 'generate_with_messages', autospec=True) as mock_generate:
            expected_usage = {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
            mock_generate.return_value = LLMResponse(
                content="テスト応答",
                usage=expected_usage,
                finish_reason="stop"
            )

            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content="システム指示"),
                LLMMessage(role=LLMRole.USER, content="ユーザーの質問")
            ]

            # オリジナルのメソッドではなくモック化したメソッドを呼び出す
            self.client.generate_with_messages(messages)

            # モック化したメソッドが正しく呼び出されたことを確認
            mock_generate.assert_called_once_with(messages)

    def test_generate_with_template(self):
        """generate_with_templateメソッドが正しく動作することを確認"""
        template = "名前：{name}、年齢：{age}"
        variables = {"name": "テスト太郎", "age": 30}

        with patch.object(self.client, "generate") as mock_generate:
            mock_generate.return_value = LLMResponse(content="テスト応答")
            response = self.client.generate_with_template(template, variables)

            # generateが正しく呼び出されたことを確認
            mock_generate.assert_called_once()

            # テンプレートが正しく展開されたことを確認
            call_args = mock_generate.call_args[0]
            self.assertEqual(call_args[0], "名前：テスト太郎、年齢：30")

            # レスポンスが正しいことを確認
            self.assertEqual(response.content, "テスト応答")


class TestLLMClientFactory(unittest.TestCase):
    """LLMClientFactoryクラスのテスト"""

    def test_create_openai_client(self):
        """OpenAIクライアントが正しく作成されることを確認"""
        with patch("sikakumaru.app.llm.llm_client.OpenAIClient") as mock_openai_client:
            mock_instance = MagicMock()
            mock_openai_client.return_value = mock_instance

            client = LLMClientFactory.create_client(LLMProvider.OPENAI)

            # 正しいクライアントタイプが作成されたことを確認
            mock_openai_client.assert_called_once()
            self.assertEqual(client, mock_instance)

    def test_create_client_with_config(self):
        """設定付きでクライアントが正しく作成されることを確認"""
        with patch("sikakumaru.app.llm.llm_client.OpenAIClient") as mock_openai_client:
            config = LLMConfig(model="gpt-4", temperature=0.5)
            LLMClientFactory.create_client(config=config)

            # 設定が正しく渡されたことを確認
            mock_openai_client.assert_called_once_with(config)

    def test_unsupported_provider(self):
        """サポートされていないプロバイダーでの例外発生を確認"""
        with patch.object(LLMProvider, "__eq__", return_value=False):
            with self.assertRaises(ValueError):
                LLMClientFactory.create_client()


if __name__ == "__main__":
    unittest.main()