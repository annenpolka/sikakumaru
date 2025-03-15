"""
LLMクライアント

このモジュールは、様々なLLMサービスとの通信を抽象化し、
問題生成システムでLLMを活用するための統一インターフェースを提供します。
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import openai
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI as LangchainOpenAI
from openai import AsyncOpenAI, OpenAI

from sikakumaru.app.infrastructure.env_manager import LLMEnvVars


class LLMProvider(Enum):
    """サポートされているLLMプロバイダの列挙型"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    # 将来的に他のプロバイダを追加可能


class LLMRole(Enum):
    """LLMの役割を表す列挙型"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class LLMMessage:
    """LLMとのメッセージ交換を表すクラス"""

    def __init__(self, role: Union[LLMRole, str], content: str):
        """
        Args:
            role: メッセージの役割（SYSTEM, USER, ASSISTANT）
            content: メッセージの内容
        """
        self.role = role if isinstance(role, LLMRole) else LLMRole(role)
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """OpenAI APIの形式に変換"""
        return {
            "role": self.role.value,
            "content": self.content
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "LLMMessage":
        """辞書からLLMMessageを作成"""
        return cls(role=data["role"], content=data["content"])


class LLMConfig:
    """LLMの設定を保持するクラス"""

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        timeout: int = 60,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ):
        self.provider = provider
        self.model = model or LLMEnvVars.get_default_model()
        self.temperature = temperature if temperature is not None else LLMEnvVars.get_temperature()
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.timeout = timeout
        self.api_key = api_key or LLMEnvVars.get_api_key()
        self.api_base = api_base or LLMEnvVars.get_api_base()
        self.additional_params = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """設定を辞書に変換"""
        result = {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }

        if self.max_tokens:
            result["max_tokens"] = self.max_tokens

        result.update(self.additional_params)
        return result


class LLMResponse:
    """LLMからのレスポンスを表すクラス"""

    def __init__(
        self,
        content: str,
        raw_response: Any = None,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None
    ):
        self.content = content
        self.raw_response = raw_response
        self.usage = usage or {}
        self.finish_reason = finish_reason

    def __str__(self) -> str:
        return self.content


class LLMClient(ABC):
    """LLMクライアントの抽象基底クラス"""

    @abstractmethod
    def generate(self, prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        """単一のプロンプトからテキストを生成"""
        pass

    @abstractmethod
    async def generate_async(self, prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        """単一のプロンプトからテキストを非同期生成"""
        pass

    @abstractmethod
    def generate_with_messages(self, messages: List[LLMMessage], config: Optional[LLMConfig] = None) -> LLMResponse:
        """メッセージリストからテキストを生成"""
        pass

    @abstractmethod
    async def generate_with_messages_async(self, messages: List[LLMMessage], config: Optional[LLMConfig] = None) -> LLMResponse:
        """メッセージリストからテキストを非同期生成"""
        pass

    @abstractmethod
    def generate_with_template(
        self,
        template: str,
        variables: Dict[str, Any],
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """テンプレートと変数からテキストを生成"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI APIを使用するLLMクライアント"""

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Args:
            config: OpenAI APIの設定。指定しない場合はデフォルト設定が使用されます。
        """
        self.config = config or LLMConfig()
        self.client = OpenAI(api_key=self.config.api_key)
        self.async_client = AsyncOpenAI(api_key=self.config.api_key)

        if self.config.api_base:
            self.client.base_url = self.config.api_base
            self.async_client.base_url = self.config.api_base

    def generate(self, prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        """
        単一のプロンプトからテキストを生成

        Args:
            prompt: 生成のためのプロンプトテキスト
            config: 生成設定。指定しない場合はクライアントのデフォルト設定が使用されます。

        Returns:
            LLMResponse: 生成されたテキストを含むレスポンス
        """
        messages = [LLMMessage(LLMRole.USER, prompt)]
        return self.generate_with_messages(messages, config)

    async def generate_async(self, prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        """
        単一のプロンプトからテキストを非同期生成

        Args:
            prompt: 生成のためのプロンプトテキスト
            config: 生成設定。指定しない場合はクライアントのデフォルト設定が使用されます。

        Returns:
            LLMResponse: 生成されたテキストを含むレスポンス
        """
        messages = [LLMMessage(LLMRole.USER, prompt)]
        return await self.generate_with_messages_async(messages, config)

    def generate_with_messages(self, messages: List[LLMMessage], config: Optional[LLMConfig] = None) -> LLMResponse:
        """
        メッセージリストからテキストを生成

        Args:
            messages: LLMMessageのリスト
            config: 生成設定。指定しない場合はクライアントのデフォルト設定が使用されます。

        Returns:
            LLMResponse: 生成されたテキストを含むレスポンス
        """
        cfg = config or self.config
        params = cfg.to_dict()

        try:
            messages_dict = []
            for message in messages:
                msg_dict = {"role": message.role.value, "content": message.content}
                messages_dict.append(msg_dict)

            response = self.client.chat.completions.create(
                messages=messages_dict,
                **params
            )

            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            return LLMResponse(
                content=content,
                raw_response=response,
                usage=usage,
                finish_reason=finish_reason
            )
        except Exception as e:
            # 本番環境では適切なエラーハンドリングを実装すべき
            raise Exception(f"OpenAI API呼び出し中にエラーが発生しました: {str(e)}")

    async def generate_with_messages_async(self, messages: List[LLMMessage], config: Optional[LLMConfig] = None) -> LLMResponse:
        """
        メッセージリストからテキストを非同期生成

        Args:
            messages: LLMMessageのリスト
            config: 生成設定。指定しない場合はクライアントのデフォルト設定が使用されます。

        Returns:
            LLMResponse: 生成されたテキストを含むレスポンス
        """
        cfg = config or self.config
        params = cfg.to_dict()

        try:
            messages_dict = []
            for message in messages:
                msg_dict = {"role": message.role.value, "content": message.content}
                messages_dict.append(msg_dict)

            response = await self.async_client.chat.completions.create(
                messages=messages_dict,
                **params
            )

            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            return LLMResponse(
                content=content,
                raw_response=response,
                usage=usage,
                finish_reason=finish_reason
            )
        except Exception as e:
            # 本番環境では適切なエラーハンドリングを実装すべき
            raise Exception(f"OpenAI API非同期呼び出し中にエラーが発生しました: {str(e)}")

    def generate_with_template(
        self,
        template: str,
        variables: Dict[str, Any],
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """
        テンプレートと変数からテキストを生成

        Args:
            template: プロンプトテンプレート文字列 (例: "こんにちは、{name}さん")
            variables: テンプレート変数の辞書 (例: {"name": "太郎"})
            config: 生成設定。指定しない場合はクライアントのデフォルト設定が使用されます。

        Returns:
            LLMResponse: 生成されたテキストを含むレスポンス
        """
        prompt_template = PromptTemplate.from_template(template)
        prompt = prompt_template.format(**variables)
        return self.generate(prompt, config)


class LLMClientFactory:
    """LLMクライアントを作成するファクトリークラス"""

    @staticmethod
    def create_client(provider: LLMProvider = LLMProvider.OPENAI, config: Optional[LLMConfig] = None) -> LLMClient:
        """
        指定されたプロバイダのLLMクライアントを作成

        Args:
            provider: LLMプロバイダ
            config: LLM設定

        Returns:
            LLMClient: 作成されたLLMクライアント

        Raises:
            ValueError: サポートされていないプロバイダが指定された場合
        """
        if provider == LLMProvider.OPENAI:
            return OpenAIClient(config)
        elif provider == LLMProvider.AZURE_OPENAI:
            # 将来的に実装
            raise NotImplementedError("Azure OpenAIクライアントはまだ実装されていません")
        else:
            raise ValueError(f"サポートされていないLLMプロバイダです: {provider}")


# 便利なシングルトンインスタンス
default_llm_client = LLMClientFactory.create_client()
