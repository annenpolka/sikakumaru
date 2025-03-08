"""
しかくまるドメインモデル

このモジュールには、問題生成システムの中心となるドメインモデルが含まれています。
DDDの原則に従い、エンティティと値オブジェクトを適切に分離しています。
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum, auto
from typing import Dict, List, Any, Optional


class Difficulty(Enum):
    """
    問題の難易度を表す列挙型

    DDDの原則に従い、ドメイン固有の値オブジェクトとして実装
    """
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

    @classmethod
    def from_str(cls, difficulty_str: str) -> Difficulty:
        """
        文字列から難易度を生成する

        Args:
            difficulty_str: 難易度を表す文字列

        Returns:
            対応するDifficultyオブジェクト

        Raises:
            ValueError: 不明な難易度文字列の場合
        """
        try:
            return cls(difficulty_str)
        except ValueError:
            valid_values = [d.value for d in cls]
            raise ValueError(f"不明な難易度: {difficulty_str}。有効な値: {', '.join(valid_values)}")


@dataclass(frozen=True)
class QuestionMetadata:
    """
    問題のメタデータを表す値オブジェクト

    関数型プログラミングの原則に従い不変（イミュータブル）として実装
    """
    difficulty: Difficulty
    topics: List[str]
    certification: str
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        メタデータを辞書形式に変換する

        Returns:
            メタデータの辞書表現
        """
        result = asdict(self)
        result["difficulty"] = self.difficulty.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> QuestionMetadata:
        """
        辞書からメタデータを生成する

        Args:
            data: メタデータの辞書表現

        Returns:
            QuestionMetadataオブジェクト
        """
        if "difficulty" in data and isinstance(data["difficulty"], str):
            data = data.copy()  # 入力データを変更しないようにコピー
            data["difficulty"] = Difficulty.from_str(data["difficulty"])
        return cls(**data)


@dataclass(frozen=True)
class Question:
    """
    問題エンティティ

    DDDの原則に従い、システムの中心となるエンティティとして実装
    """
    text: str
    answer: str
    metadata: QuestionMetadata

    def to_dict(self) -> Dict[str, Any]:
        """
        問題を辞書形式に変換する

        Returns:
            問題の辞書表現
        """
        return {
            "text": self.text,
            "answer": self.answer,
            "metadata": self.metadata.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Question:
        """
        辞書から問題を生成する

        Args:
            data: 問題の辞書表現

        Returns:
            Questionオブジェクト
        """
        metadata = QuestionMetadata.from_dict(data.get("metadata", {}))
        return cls(
            text=data.get("text", ""),
            answer=data.get("answer", ""),
            metadata=metadata
        )