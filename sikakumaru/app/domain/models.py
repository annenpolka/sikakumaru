"""
しかくまるドメインモデル

このモジュールには、問題生成システムの中心となるドメインモデルが含まれています。
DDDの原則に従い、エンティティと値オブジェクトを適切に分離しています。
認知科学と心理測定学の原則に基づいた問題生成のためのモデルを提供します。
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Union


class BloomsTaxonomyLevel(Enum):
    """
    Bloom's Taxonomyの認知レベル階層を表す列挙型

    問題が評価する認知プロセスの複雑さレベルを表します。
    """
    REMEMBER = "REMEMBER"  # 記憶：知識の想起と再生
    UNDERSTAND = "UNDERSTAND"  # 理解：概念の説明と関連付け
    APPLY = "APPLY"  # 応用：知識の新状況への適用
    ANALYZE = "ANALYZE"  # 分析：要素間の関係と構造の検証
    EVALUATE = "EVALUATE"  # 評価：基準に基づく判断形成
    CREATE = "CREATE"  # 創造：新しい解決策や構造の構築

    @classmethod
    def from_str(cls, level_str: str) -> BloomsTaxonomyLevel:
        """
        文字列から認知レベルを生成する

        Args:
            level_str: 認知レベルを表す文字列

        Returns:
            対応するBloomsTaxonomyLevelオブジェクト

        Raises:
            ValueError: 不明な認知レベル文字列の場合
        """
        try:
            return cls(level_str)
        except ValueError:
            valid_values = [level.value for level in cls]
            raise ValueError(f"不明な認知レベル: {level_str}。有効な値: {', '.join(valid_values)}")


class Difficulty(Enum):
    """
    問題の難易度を表す列挙型

    DDDの原則に従い、ドメイン固有の値オブジェクトとして実装。
    心理測定学的分類に基づきます。
    """
    EASY = "EASY"     # P-値 > 0.7：基礎レベル
    MEDIUM = "MEDIUM"  # P-値 0.4〜0.7：中級レベル
    HARD = "HARD"     # P-値 < 0.4：上級レベル

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


class QuestionFormat(Enum):
    """
    問題形式を表す列挙型

    様々な問題形式を表現します。
    """
    MULTIPLE_CHOICE_SINGLE_ANSWER = "MULTIPLE_CHOICE_SINGLE_ANSWER"  # 単一回答の選択式問題
    MULTIPLE_CHOICE_MULTIPLE_ANSWER = "MULTIPLE_CHOICE_MULTIPLE_ANSWER"  # 複数回答の選択式問題
    SCENARIO_BASED = "SCENARIO_BASED"  # シナリオベースの問題
    ORDERING = "ORDERING"  # 順序付け問題
    MATCHING = "MATCHING"  # マッチング問題
    HOTSPOT = "HOTSPOT"  # ホットスポット/グラフィック選択問題
    CASE_STUDY = "CASE_STUDY"  # ケーススタディ連続問題

    @classmethod
    def from_str(cls, format_str: str) -> QuestionFormat:
        """
        文字列から問題形式を生成する

        Args:
            format_str: 問題形式を表す文字列

        Returns:
            対応するQuestionFormatオブジェクト

        Raises:
            ValueError: 不明な問題形式文字列の場合
        """
        try:
            return cls(format_str)
        except ValueError:
            valid_values = [f.value for f in cls]
            raise ValueError(f"不明な問題形式: {format_str}。有効な値: {', '.join(valid_values)}")


class DistractorType(Enum):
    """
    不正解選択肢（ディストラクター）のタイプを表す列挙型

    効果的な不正解選択肢の設計のための分類です。
    """
    COMMON_MISCONCEPTION = "COMMON_MISCONCEPTION"  # 一般的な誤解に基づくもの
    PARTIAL_TRUTH = "PARTIAL_TRUTH"  # 部分的に正しい要素を含むもの
    SIMILAR_CONCEPT = "SIMILAR_CONCEPT"  # 類似した概念だが不正確なもの
    RELATED_BUT_IRRELEVANT = "RELATED_BUT_IRRELEVANT"  # 関連はあるが無関係なもの
    EXTREME_STATEMENT = "EXTREME_STATEMENT"  # 極端な表現を含むもの

    @classmethod
    def from_str(cls, type_str: str) -> DistractorType:
        """
        文字列からディストラクタータイプを生成する

        Args:
            type_str: ディストラクタータイプを表す文字列

        Returns:
            対応するDistractionTypeオブジェクト

        Raises:
            ValueError: 不明なディストラクタータイプ文字列の場合
        """
        try:
            return cls(type_str)
        except ValueError:
            valid_values = [t.value for t in cls]
            raise ValueError(f"不明なディストラクタータイプ: {type_str}。有効な値: {', '.join(valid_values)}")


@dataclass(frozen=True)
class Topic:
    """
    問題のトピックを表す値オブジェクト

    資格試験の特定の出題領域を表します。
    """
    id: str
    name: str
    parent_id: Optional[str] = None  # 親トピックID（サブトピックの場合）

    def to_dict(self) -> Dict[str, Any]:
        """トピックを辞書形式に変換する"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Topic:
        """辞書からトピックを生成する"""
        return cls(**data)


@dataclass(frozen=True)
class Domain:
    """
    問題のドメイン（大分類）を表す値オブジェクト

    資格試験の主要な出題分野を表します。
    """
    id: str
    name: str
    weight: float  # 試験内での比重（0.0〜1.0）
    certification_id: str

    def to_dict(self) -> Dict[str, Any]:
        """ドメインを辞書形式に変換する"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Domain:
        """辞書からドメインを生成する"""
        return cls(**data)


@dataclass(frozen=True)
class Certification:
    """
    資格を表す値オブジェクト

    特定の資格試験の情報を表します。
    """
    id: str
    name: str
    provider: str
    version: str
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """資格を辞書形式に変換する"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Certification:
        """辞書から資格を生成する"""
        return cls(**data)


@dataclass(frozen=True)
class QuestionMetadata:
    """
    問題のメタデータを表す値オブジェクト

    関数型プログラミングの原則に従い不変（イミュータブル）として実装
    """
    difficulty: Difficulty
    topics: List[str]
    certification: str
    cognitive_level: BloomsTaxonomyLevel
    domains: List[str] = field(default_factory=list)
    source: Optional[str] = None
    version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        メタデータを辞書形式に変換する

        Returns:
            メタデータの辞書表現
        """
        result = asdict(self)
        result["difficulty"] = self.difficulty.value
        result["cognitive_level"] = self.cognitive_level.value
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
        new_data = data.copy()  # 入力データを変更しないようにコピー

        if "difficulty" in new_data and isinstance(new_data["difficulty"], str):
            new_data["difficulty"] = Difficulty.from_str(new_data["difficulty"])

        if "cognitive_level" in new_data and isinstance(new_data["cognitive_level"], str):
            new_data["cognitive_level"] = BloomsTaxonomyLevel.from_str(new_data["cognitive_level"])

        return cls(**new_data)


@dataclass(frozen=True)
class Choice:
    """
    選択肢を表す値オブジェクト

    問題の選択肢情報を表します。
    """
    id: str
    text: str
    is_correct: bool
    distractor_type: Optional[DistractorType] = None  # 不正解選択肢の場合のみ設定
    explanation: Optional[str] = None  # 選択肢に対する個別の説明

    def to_dict(self) -> Dict[str, Any]:
        """選択肢を辞書形式に変換する"""
        result = asdict(self)
        if self.distractor_type:
            result["distractor_type"] = self.distractor_type.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Choice:
        """辞書から選択肢を生成する"""
        new_data = data.copy()

        if "distractor_type" in new_data and new_data["distractor_type"] and isinstance(new_data["distractor_type"], str):
            new_data["distractor_type"] = DistractorType.from_str(new_data["distractor_type"])

        return cls(**new_data)


@dataclass(frozen=True)
class Explanation:
    """
    問題の解説を表す値オブジェクト

    詳細な解説情報を提供します。
    """
    id: str
    text: str
    correct_answer_justification: str
    distractor_analysis: Dict[str, str] = field(default_factory=dict)  # 選択肢IDと分析のマッピング
    related_concepts: List[str] = field(default_factory=list)
    learning_resources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """解説を辞書形式に変換する"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Explanation:
        """辞書から解説を生成する"""
        return cls(**data)


@dataclass(frozen=True)
class Question:
    """
    問題エンティティ

    DDDの原則に従い、システムの中心となるエンティティとして実装
    """
    id: str
    text: str
    question_format: QuestionFormat
    choices: List[Choice]
    metadata: QuestionMetadata
    explanation: Optional[Explanation] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        問題を辞書形式に変換する

        Returns:
            問題の辞書表現
        """
        result = {
            "id": self.id,
            "text": self.text,
            "question_format": self.question_format.value,
            "choices": [choice.to_dict() for choice in self.choices],
            "metadata": self.metadata.to_dict(),
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        if self.explanation:
            result["explanation"] = self.explanation.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Question:
        """
        辞書から問題を生成する

        Args:
            data: 問題の辞書表現

        Returns:
            Questionオブジェクト
        """
        new_data = data.copy()

        if "metadata" in new_data:
            new_data["metadata"] = QuestionMetadata.from_dict(new_data["metadata"])

        if "question_format" in new_data and isinstance(new_data["question_format"], str):
            new_data["question_format"] = QuestionFormat.from_str(new_data["question_format"])

        if "choices" in new_data:
            new_data["choices"] = [Choice.from_dict(choice) for choice in new_data["choices"]]

        if "explanation" in new_data and new_data["explanation"]:
            new_data["explanation"] = Explanation.from_dict(new_data["explanation"])

        if "created_at" in new_data and isinstance(new_data["created_at"], str):
            new_data["created_at"] = datetime.fromisoformat(new_data["created_at"])

        if "updated_at" in new_data and isinstance(new_data["updated_at"], str):
            new_data["updated_at"] = datetime.fromisoformat(new_data["updated_at"])

        return cls(**new_data)

    @property
    def correct_answers(self) -> List[Choice]:
        """正解の選択肢のリストを取得する"""
        return [choice for choice in self.choices if choice.is_correct]

    @property
    def distractors(self) -> List[Choice]:
        """不正解の選択肢（ディストラクター）のリストを取得する"""
        return [choice for choice in self.choices if not choice.is_correct]

    def is_valid(self) -> bool:
        """問題が有効かどうかを検証する"""
        # 選択肢が存在するか
        if not self.choices:
            return False

        # 正解が少なくとも1つ存在するか
        if not any(choice.is_correct for choice in self.choices):
            return False

        # 問題形式に応じた検証
        if self.question_format == QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER:
            # 正解がちょうど1つであることを確認
            return sum(1 for choice in self.choices if choice.is_correct) == 1

        # その他の検証ロジックを問題形式に応じて追加可能

        return True