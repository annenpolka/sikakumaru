"""
資格特化型プロンプト管理エンジン

このモジュールは、資格特有の要件に基づくプロンプトテンプレートの管理機能を提供します。
様々な資格試験に適したプロンプトをカスタマイズし、問題生成の品質を向上させます。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from langchain.prompts import PromptTemplate

from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    Certification,
    Difficulty,
    QuestionFormat,
)


class PromptTemplateManager:
    """資格試験プロンプトテンプレート管理クラス"""

    _instance = None
    _base_template_path = Path(__file__).parent.parent.parent.parent / "comprehensive-exam-generator-prompt.md"
    _template_cache: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(PromptTemplateManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """初期化処理"""
        self._load_base_template()
        self._custom_templates_dir = Path(__file__).parent / "templates"
        self._custom_templates_dir.mkdir(exist_ok=True)
        self._load_custom_templates()

    def _load_base_template(self) -> None:
        """基本プロンプトテンプレートを読み込む"""
        try:
            with open(self._base_template_path, "r", encoding="utf-8") as f:
                self._base_template = f.read()
        except FileNotFoundError:
            # デフォルトのプロンプト内容（短縮版）
            self._base_template = """
# 資格試験問題生成プロンプト

あなたは資格試験の問題作成専門家です。教育心理学、認知科学、心理測定学の原則に基づいて高品質な問題を生成してください。

## 基本原則
- 明確で曖昧さのない問題文
- 実務に即した応用力を試す問題設計
- 適切な難易度と識別力
- 効果的な選択肢と妥当なディストラクター

## 認知レベル
- 記憶（Remember）: 知識の想起と再生
- 理解（Understand）: 概念の説明と関連付け
- 応用（Apply）: 知識の新状況への適用
- 分析（Analyze）: 要素間の関係と構造の検証
- 評価（Evaluate）: 基準に基づく判断形成
- 創造（Create）: 新しい解決策や構造の構築
"""

    def _load_custom_templates(self) -> None:
        """カスタムテンプレートを読み込む"""
        if not self._custom_templates_dir.exists():
            return

        for template_file in self._custom_templates_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    certification_id = template_data.get("certification_id")
                    if certification_id:
                        self._template_cache[certification_id] = template_data
            except (json.JSONDecodeError, KeyError) as e:
                print(f"テンプレートの読み込みエラー: {template_file.name} - {str(e)}")

    def get_base_template(self) -> str:
        """基本的なシステムプロンプトの内容を取得する"""
        return self._base_template

    def get_certification_template(self, certification_id: str) -> Optional[Dict[str, Any]]:
        """特定の資格用カスタムテンプレートを取得する"""
        return self._template_cache.get(certification_id)

    def save_certification_template(self, certification_id: str, template_data: Dict[str, Any]) -> bool:
        """資格特化型テンプレートを保存する"""
        if not certification_id:
            return False

        template_data["last_updated"] = datetime.now().isoformat()
        template_data["certification_id"] = certification_id

        try:
            template_path = self._custom_templates_dir / f"{certification_id}.json"
            with open(template_path, "w", encoding="utf-8") as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            # キャッシュを更新
            self._template_cache[certification_id] = template_data
            return True
        except Exception as e:
            print(f"テンプレート保存エラー: {certification_id} - {str(e)}")
            return False

    def delete_certification_template(self, certification_id: str) -> bool:
        """資格特化型テンプレートを削除する"""
        if not certification_id or certification_id not in self._template_cache:
            return False

        try:
            template_path = self._custom_templates_dir / f"{certification_id}.json"
            if template_path.exists():
                os.remove(template_path)

            # キャッシュから削除
            if certification_id in self._template_cache:
                del self._template_cache[certification_id]

            return True
        except Exception as e:
            print(f"テンプレート削除エラー: {certification_id} - {str(e)}")
            return False


class CertificationPromptEngine:
    """資格特化型プロンプト管理エンジン"""

    def __init__(self):
        """初期化"""
        self.template_manager = PromptTemplateManager()

    def generate_question_prompt(
        self,
        certification: Union[Certification, str],
        domains: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        cognitive_levels: Optional[List[Union[BloomsTaxonomyLevel, str]]] = None,
        difficulty: Optional[Union[Difficulty, str]] = None,
        question_formats: Optional[List[Union[QuestionFormat, str]]] = None,
        count: int = 1
    ) -> str:
        """問題生成用のプロンプトを生成する

        Args:
            certification: 対象資格（オブジェクトまたはID）
            domains: 出題ドメイン
            topics: 出題トピック
            cognitive_levels: 認知レベル
            difficulty: 難易度
            question_formats: 問題形式
            count: 生成する問題数

        Returns:
            問題生成プロンプト
        """
        # 認証情報の処理
        certification_id = certification.id if isinstance(certification, Certification) else certification

        # 資格特化型テンプレートの取得
        certification_template = self.template_manager.get_certification_template(certification_id)

        # システムプロンプト
        system_prompt = self.template_manager.get_base_template()

        # 認知レベルの文字列変換
        if cognitive_levels:
            cognitive_levels_str = [
                level.value if isinstance(level, BloomsTaxonomyLevel) else level
                for level in cognitive_levels
            ]
        else:
            cognitive_levels_str = ["REMEMBER", "UNDERSTAND", "APPLY"]

        # 難易度の文字列変換
        if difficulty:
            difficulty_str = difficulty.value if isinstance(difficulty, Difficulty) else difficulty
        else:
            difficulty_str = "MEDIUM"

        # 問題形式の文字列変換
        if question_formats:
            formats_str = [
                format.value if isinstance(format, QuestionFormat) else format
                for format in question_formats
            ]
        else:
            formats_str = ["MULTIPLE_CHOICE_SINGLE_ANSWER"]

        # 資格特化型指示の構築
        if certification_template:
            certification_name = certification_template.get("name", "指定された資格")
            domains_info = certification_template.get("domains", [])
            specific_instructions = certification_template.get("specific_instructions", "")
        else:
            certification_name = "指定された資格"
            domains_info = []
            specific_instructions = ""

        # ドメイン情報の文字列化
        domains_str = ""
        if domains_info and domains:
            for domain_info in domains_info:
                if domain_info.get("id") in domains:
                    domains_str += f"- {domain_info.get('name')}: {domain_info.get('description', '')}\n"

                    # サブトピックの追加
                    domain_topics = domain_info.get("topics", [])
                    if domain_topics and topics:
                        domains_str += "  サブトピック:\n"
                        for topic in domain_topics:
                            if topic.get("id") in topics:
                                domains_str += f"  - {topic.get('name')}: {topic.get('description', '')}\n"

        # トピックのフォールバック
        topics_str = ""
        if topics and not domains_str:
            topics_str = "出題トピック:\n" + "\n".join([f"- {topic}" for topic in topics])

        # 生成指示の構築
        generation_instruction = f"""
# {certification_name}試験のための問題生成

## 出題要件
- 資格: {certification_name}
- 難易度: {difficulty_str}
- 認知レベル: {', '.join(cognitive_levels_str)}
- 問題形式: {', '.join(formats_str)}
- 生成数: {count}問

## 出題範囲
{domains_str or topics_str or "指定された範囲から出題してください。"}

## 資格特有の指示
{specific_instructions}

## 出力形式
以下の形式で出力してください：

```json
[
  {{
    "text": "問題文...",
    "question_format": "MULTIPLE_CHOICE_SINGLE_ANSWER",
    "cognitive_level": "UNDERSTAND",
    "difficulty": "MEDIUM",
    "choices": [
      {{
        "id": "a",
        "text": "選択肢A",
        "is_correct": false,
        "distractor_type": "PARTIAL_TRUTH",
        "explanation": "この選択肢が不正解である理由..."
      }},
      {{
        "id": "b",
        "text": "選択肢B",
        "is_correct": true,
        "explanation": "この選択肢が正解である理由..."
      }},
      // 他の選択肢...
    ],
    "explanation": {{
      "text": "問題全体の詳細な解説...",
      "correct_answer_justification": "正解の詳細な根拠...",
      "related_concepts": ["関連概念1", "関連概念2"]
    }},
    "tags": ["タグ1", "タグ2"]
  }},
  // 他の問題...
]
```
"""

        # システムプロンプトと生成指示を結合
        return system_prompt + "\n\n" + generation_instruction

    def generate_explanation_prompt(
        self,
        question_text: str,
        choices: List[Dict[str, Any]],
        correct_answer: Union[str, List[str]],
        certification: Union[Certification, str],
        cognitive_level: Union[BloomsTaxonomyLevel, str],
        detail_level: str = "COMPREHENSIVE"
    ) -> str:
        """解説生成用のプロンプトを生成する

        Args:
            question_text: 問題文
            choices: 選択肢リスト
            correct_answer: 正解の選択肢ID
            certification: 対象資格
            cognitive_level: 認知レベル
            detail_level: 解説の詳細レベル

        Returns:
            解説生成プロンプト
        """
        # システムプロンプト
        system_prompt = self.template_manager.get_base_template()

        # 認証情報の処理
        certification_id = certification.id if isinstance(certification, Certification) else certification

        # 資格特化型テンプレートの取得
        certification_template = self.template_manager.get_certification_template(certification_id)

        # 資格名の取得
        if certification_template:
            certification_name = certification_template.get("name", "指定された資格")
        else:
            certification_name = "指定された資格"

        # 認知レベルの文字列変換
        cognitive_level_str = cognitive_level.value if isinstance(cognitive_level, BloomsTaxonomyLevel) else cognitive_level

        # 選択肢の文字列化
        choices_str = ""
        for i, choice in enumerate(choices):
            choice_id = choice.get("id", chr(65 + i))  # A, B, C, ...
            choice_text = choice.get("text", "")
            choices_str += f"{choice_id}. {choice_text}\n"

        # 正解の文字列化
        if isinstance(correct_answer, list):
            correct_answer_str = ", ".join(correct_answer)
        else:
            correct_answer_str = correct_answer

        # 詳細レベルに応じた指示
        if detail_level == "BASIC":
            detail_instruction = "基本的な正解の説明と簡単な根拠を提供してください。"
        elif detail_level == "STANDARD":
            detail_instruction = "正解の説明と各選択肢の分析、関連する主要概念について説明してください。"
        else:  # COMPREHENSIVE
            detail_instruction = """
以下の要素を含む包括的な解説を提供してください：
1. 正解の詳細な根拠と説明
2. 各不正解選択肢が誤りである具体的理由
3. 問題に関連する概念の詳細な解説
4. 実務での応用例や注意点
5. 関連する追加知識や学習リソースの提案
6. メタ認知的アプローチ（この種の問題を解く際の思考プロセス）
"""

        # 生成指示の構築
        generation_instruction = f"""
# {certification_name}試験の問題解説生成

## 対象問題
{question_text}

## 選択肢
{choices_str}

## 正解
{correct_answer_str}

## 認知レベル
{cognitive_level_str}

## 解説要件
{detail_instruction}

## 出力形式
以下の形式で解説を出力してください：

```json
{{
  "text": "解説全文...",
  "correct_answer_justification": "正解の詳細な根拠...",
  "distractor_analysis": {{
    "A": "選択肢Aが不正解である理由...",
    "B": "選択肢Bが不正解である理由...",
    // 他の選択肢...
  }},
  "related_concepts": ["関連概念1", "関連概念2"],
  "learning_resources": ["学習リソース1", "学習リソース2"]
}}
```
"""

        # システムプロンプトと生成指示を結合
        return system_prompt + "\n\n" + generation_instruction