"""
LLMを使用した問題生成エンジン

このモジュールは、LLMを活用して高品質な問題生成を行うためのエンジンを提供します。
問題生成エンジンをLLM機能で拡張し、より高度な問題生成を可能にします。
"""

import json
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from sikakumaru.app.core.question_generation_engine import (
    DistractorGenerator,
    ExplanationGenerator,
    QuestionDifficultyLevel,
    QuestionGenerationEngine,
    QuestionGenerator,
)
from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    Certification,
    Choice,
    Difficulty,
    DistractorType,
    Domain,
    Explanation,
    Question,
    QuestionFormat,
    Topic,
)
from sikakumaru.app.llm.llm_client import (
    LLMClient,
    LLMClientFactory,
    LLMConfig,
    LLMMessage,
    LLMRole,
)


class LLMDrivenDistractorGenerator(DistractorGenerator):
    """LLMを使用した誤答選択肢生成クラス"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Args:
            llm_client: 使用するLLMクライアント。指定しない場合はデフォルトクライアントを使用。
        """
        super().__init__()
        self.llm_client = llm_client or LLMClientFactory.create_client()

    def generate_distractors(
        self,
        correct_answer: str,
        distractor_type: DistractorType,
        count: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """LLMを使用して指定された種類の誤答選択肢を生成する"""
        context = context or {}
        topic = context.get("topic", "一般的な知識")
        bloom_level = context.get("bloom_level", BloomsTaxonomyLevel.UNDERSTAND)

        # 誤答選択肢生成プロンプトの作成
        prompt = self._create_distractor_prompt(
            correct_answer=correct_answer,
            distractor_type=distractor_type,
            count=count,
            topic=topic,
            bloom_level=bloom_level,
            context=context
        )

        # LLMを使用して誤答選択肢を生成
        try:
            response = self.llm_client.generate(prompt)
            return self._parse_distractor_response(response.content, count)
        except Exception as e:
            # エラー時はフォールバックとしてデフォルトジェネレータを使用
            print(f"LLMによる誤答選択肢生成中にエラーが発生しました: {str(e)}")
            return super().generate_distractors(correct_answer, distractor_type, count, context)

    def _create_distractor_prompt(
        self,
        correct_answer: str,
        distractor_type: DistractorType,
        count: int,
        topic: Any,
        bloom_level: BloomsTaxonomyLevel,
        context: Dict[str, Any]
    ) -> str:
        """誤答選択肢生成用のプロンプトを作成"""
        topic_name = topic.name if hasattr(topic, "name") else str(topic)

        distractor_type_descriptions = {
            DistractorType.COMMON_MISCONCEPTION: "よくある誤解や混同しやすい概念に基づく誤答",
            DistractorType.SIMILAR_CONCEPT: "正解と似ているが異なる概念に基づく誤答",
            DistractorType.PARTIAL_TRUTH: "部分的に正しいが、全体として不正確な誤答",
            DistractorType.RELATED_BUT_IRRELEVANT: "トピックに関連はするが、質問に対しては無関係な誤答",
            DistractorType.EXTREME_STATEMENT: "極端な表現を含む誤答"
        }

        distractor_desc = distractor_type_descriptions.get(
            distractor_type,
            "紛らわしく、もっともらしいが不正確な選択肢"
        )

        # コンテキストから追加情報を取得
        question_text = context.get("question_text", "")

        prompt = f"""
# 誤答選択肢生成

## 正解
{correct_answer}

## 質問内容
{question_text}

## トピック
{topic_name}

## 認知レベル
{bloom_level.name}

## 誤答タイプ
{distractor_type.name}: {distractor_desc}

## 指示
上記の正解に対して、{count}個の誤答選択肢を生成してください。
生成する誤答選択肢は、指定された誤答タイプの特性を持ち、学習者が間違えやすいものにしてください。
正解とは明確に区別できるが、単純すぎず、十分に紛らわしい選択肢を生成してください。

回答形式:
1. [誤答選択肢1]
2. [誤答選択肢2]
3. [誤答選択肢3]
...

回答は上記の形式のみで、説明や余計なテキストは含めないでください。
"""
        return prompt

    def _parse_distractor_response(self, response_text: str, expected_count: int) -> List[str]:
        """LLMからのレスポンスを解析して誤答選択肢のリストを抽出"""
        lines = response_text.strip().split("\n")
        distractors = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 数字で始まる行を選択肢として抽出
            if line[0].isdigit() and ". " in line:
                distractor = line.split(". ", 1)[1].strip()
                if distractor and len(distractor) > 0:
                    distractors.append(distractor)

        # 十分な数の選択肢が得られなかった場合の処理
        if not distractors or len(distractors) < expected_count:
            # 行ごとに処理し直し、できるだけ多くの選択肢を抽出
            for line in lines:
                line = line.strip()
                if line and line not in distractors and not line[0].isdigit():
                    distractors.append(line)
                    if len(distractors) >= expected_count:
                        break

        # それでも足りない場合はダミー選択肢で補完
        while len(distractors) < expected_count:
            distractors.append(f"誤答選択肢 {len(distractors) + 1}")

        return distractors[:expected_count]


class LLMDrivenExplanationGenerator(ExplanationGenerator):
    """LLMを使用した解説生成クラス"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Args:
            llm_client: 使用するLLMクライアント。指定しない場合はデフォルトクライアントを使用。
        """
        super().__init__()
        self.llm_client = llm_client or LLMClientFactory.create_client()

    def generate_explanation(
        self,
        question_text: str,
        correct_answer: str,
        distractors: List[str],
        bloom_level: BloomsTaxonomyLevel,
        topic: Topic,
        context: Optional[Dict[str, Any]] = None
    ) -> Explanation:
        """LLMを使用して問題の解説を生成する"""
        context = context or {}

        # 解説生成プロンプトの作成
        prompt = self._create_explanation_prompt(
            question_text=question_text,
            correct_answer=correct_answer,
            distractors=distractors,
            bloom_level=bloom_level,
            topic=topic,
            context=context
        )

        try:
            # LLMを使用して解説を生成
            response = self.llm_client.generate(prompt)

            # レスポンスから解説を解析・構造化
            return self._parse_explanation_response(
                response.content,
                correct_answer,
                distractors,
                topic
            )
        except Exception as e:
            # エラー時はフォールバックとしてデフォルトジェネレータを使用
            print(f"LLMによる解説生成中にエラーが発生しました: {str(e)}")
            return super().generate_explanation(
                question_text,
                correct_answer,
                distractors,
                bloom_level,
                topic,
                context
            )

    def _create_explanation_prompt(
        self,
        question_text: str,
        correct_answer: str,
        distractors: List[str],
        bloom_level: BloomsTaxonomyLevel,
        topic: Topic,
        context: Dict[str, Any]
    ) -> str:
        """解説生成用のプロンプトを作成"""
        topic_name = topic.name if hasattr(topic, "name") else str(topic)

        # 選択肢を整形
        choices_text = f"A. {correct_answer}\n"
        for i, distractor in enumerate(distractors):
            choices_text += f"{chr(66 + i)}. {distractor}\n"

        prompt = f"""
# 問題解説生成

## 問題
{question_text}

## 選択肢
{choices_text}

## 正解
A. {correct_answer}

## トピック
{topic_name}

## 認知レベル
{bloom_level.name}

## 指示
以下の構造で詳細な解説を生成してください。
1. 正解の説明: なぜこの選択肢が正解なのか、概念的背景や理由を詳しく説明
2. 各誤答選択肢の分析: 各誤答選択肢がなぜ不正解なのか、どのような誤解や問題があるのかを説明
3. 重要な概念: この問題に関連する重要な概念や原則を説明
4. 学習リソース: この問題の理解を深めるための参考資料や学習リソースを3つ程度提案

回答は以下のJSON形式で提供してください:
```json
{{
  "main_explanation": "正解の詳細な説明",
  "distractor_analysis": {{
    "選択肢B": "選択肢Bが不正解である理由",
    "選択肢C": "選択肢Cが不正解である理由",
    ...
  }},
  "key_concepts": ["重要な概念1", "重要な概念2", ...],
  "learning_resources": ["リソース1", "リソース2", "リソース3"],
  "common_mistakes": ["よくある間違い1", "よくある間違い2"]
}}
```

JSONフォーマットのみで回答し、余計なテキストは含めないでください。
"""
        return prompt

    def _parse_explanation_response(
        self,
        response_text: str,
        correct_answer: str,
        distractors: List[str],
        topic: Topic
    ) -> Explanation:
        """LLMからのレスポンスを解析して解説オブジェクトを作成"""
        explanation_id = str(uuid.uuid4())

        # JSONの抽出（```json と ``` で囲まれている場合の対応）
        json_text = response_text
        if "```json" in response_text and "```" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_text = response_text[start:end].strip()

        try:
            # JSONとしてパース
            explanation_data = json.loads(json_text)

            # 必須フィールドのチェックと補完
            main_explanation = explanation_data.get("main_explanation", f"この問題の正解は「{correct_answer}」です。")

            # 誤答選択肢の分析
            distractor_analysis = explanation_data.get("distractor_analysis", {})

            # キーが文字列でない場合の対応
            formatted_distractor_analysis = {}
            for i, distractor in enumerate(distractors):
                key = f"選択肢{chr(66 + i)}"
                if key in distractor_analysis:
                    formatted_distractor_analysis[f"distractor_{i+1}"] = distractor_analysis[key]
                elif distractor in distractor_analysis:
                    formatted_distractor_analysis[f"distractor_{i+1}"] = distractor_analysis[distractor]
                else:
                    formatted_distractor_analysis[f"distractor_{i+1}"] = f"選択肢「{distractor}」は不正確です。"

            # その他のフィールドを取得
            related_concepts = explanation_data.get("key_concepts", [topic.name])
            learning_resources = explanation_data.get("learning_resources", [
                "参考書X の第Y章",
                "オンライン講座Z",
                "公式ドキュメントのセクションA"
            ])

            return Explanation(
                id=explanation_id,
                text=main_explanation,
                correct_answer_justification=main_explanation,
                distractor_analysis=formatted_distractor_analysis,
                related_concepts=related_concepts,
                learning_resources=learning_resources
            )

        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # JSON解析エラー時のフォールバック処理
            print(f"解説JSONのパース中にエラーが発生しました: {str(e)}")

            # シンプルな解説オブジェクトを作成
            return Explanation(
                id=explanation_id,
                text=f"この問題は{topic.name}に関する理解を問うものです。正解は「{correct_answer}」です。",
                correct_answer_justification=f"正解は「{correct_answer}」です。",
                distractor_analysis={
                    f"distractor_{i+1}": f"選択肢「{d}」は誤りです。" for i, d in enumerate(distractors)
                },
                related_concepts=[topic.name],
                learning_resources=["参考書X", "オンラインリソースY", "学習ガイドZ"]
            )


class LLMDrivenQuestionGenerator(QuestionGenerator):
    """LLMを使用した問題生成クラス"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Args:
            llm_client: 使用するLLMクライアント。指定しない場合はデフォルトクライアントを使用。
        """
        super().__init__()
        self.llm_client = llm_client or LLMClientFactory.create_client()

        # LLM駆動のコンポーネントに置き換え
        self.distractor_generator = LLMDrivenDistractorGenerator(self.llm_client)
        self.explanation_generator = LLMDrivenExplanationGenerator(self.llm_client)

    def generate_question(
        self,
        topic: Topic,
        bloom_level: BloomsTaxonomyLevel,
        format_type: QuestionFormat,
        difficulty: QuestionDifficultyLevel,
        distractor_type: DistractorType,
        context: Optional[Dict[str, Any]] = None
    ) -> Question:
        """LLMを使用して問題を生成"""
        context = context or {}

        # 問題生成プロンプトの作成
        prompt = self._create_question_prompt(
            topic=topic,
            bloom_level=bloom_level,
            format_type=format_type,
            difficulty=difficulty,
            context=context
        )

        try:
            # LLMを使用して問題を生成
            response = self.llm_client.generate(prompt)

            # レスポンスから問題と正解を抽出
            question_text, correct_answer = self._parse_question_response(response.content)

            # コンテキストに問題文を追加（誤答選択肢生成で使用）
            generation_context = context.copy()
            generation_context["question_text"] = question_text
            generation_context["topic"] = topic
            generation_context["bloom_level"] = bloom_level

            # 誤答選択肢を生成
            distractors = self.distractor_generator.generate_distractors(
                correct_answer,
                distractor_type,
                count=3,
                context=generation_context
            )

            # 選択肢をシャッフル
            all_choices = [correct_answer] + distractors
            choice_indices = list(range(len(all_choices)))
            import random
            random.shuffle(choice_indices)

            # Choice オブジェクトのリストを作成
            choices = []
            for i, idx in enumerate(choice_indices):
                choice_text = all_choices[idx]
                is_correct = (choice_text == correct_answer)
                choice_id = f"choice_{i+1}"

                # 不正解選択肢の場合はディストラクタータイプを設定
                choice_distractor_type = distractor_type if not is_correct else None

                choices.append(Choice(
                    id=choice_id,
                    text=choice_text,
                    is_correct=is_correct,
                    distractor_type=choice_distractor_type
                ))

            # 解説を生成
            explanation = self.explanation_generator.generate_explanation(
                question_text,
                correct_answer,
                distractors,
                bloom_level,
                topic,
                generation_context
            )

            # ドメインモデルのDifficultyに変換
            domain_difficulty = Difficulty.EASY
            if difficulty == QuestionDifficultyLevel.MEDIUM:
                domain_difficulty = Difficulty.MEDIUM
            elif difficulty in [QuestionDifficultyLevel.HARD, QuestionDifficultyLevel.VERY_HARD]:
                domain_difficulty = Difficulty.HARD

            # メタデータを作成
            metadata = {
                "difficulty": domain_difficulty,
                "cognitive_level": bloom_level,
                "topics": [topic.id],
                "certification": "dummy_certification_id",  # 実際の実装では適切な値を設定
                "domains": []  # 実際の実装では適切な値を設定
            }

            # Question オブジェクトを作成して返す
            from sikakumaru.app.domain.models import QuestionMetadata

            return Question(
                id=str(uuid.uuid4()),
                text=question_text,
                question_format=format_type,
                choices=choices,
                explanation=explanation,
                metadata=QuestionMetadata(**metadata),
                tags=[topic.name, bloom_level.name, difficulty.value]
            )

        except Exception as e:
            # エラー時はフォールバックとしてデフォルトジェネレータを使用
            print(f"LLMによる問題生成中にエラーが発生しました: {str(e)}")
            return super().generate_question(
                topic,
                bloom_level,
                format_type,
                difficulty,
                distractor_type,
                context
            )

    def _create_question_prompt(
        self,
        topic: Topic,
        bloom_level: BloomsTaxonomyLevel,
        format_type: QuestionFormat,
        difficulty: QuestionDifficultyLevel,
        context: Dict[str, Any]
    ) -> str:
        """問題生成用のプロンプトを作成"""
        topic_name = topic.name if hasattr(topic, "name") else str(topic)

        # 認知レベルの説明
        bloom_descriptions = {
            BloomsTaxonomyLevel.REMEMBER: "知識の想起と再生を問う",
            BloomsTaxonomyLevel.UNDERSTAND: "概念の説明と関連付けを問う",
            BloomsTaxonomyLevel.APPLY: "知識の新状況への適用を問う",
            BloomsTaxonomyLevel.ANALYZE: "要素間の関係と構造の検証を問う",
            BloomsTaxonomyLevel.EVALUATE: "基準に基づく判断形成を問う",
            BloomsTaxonomyLevel.CREATE: "新しい解決策や構造の構築を問う"
        }

        bloom_desc = bloom_descriptions.get(
            bloom_level,
            "理解度を評価する"
        )

        # 難易度の説明
        difficulty_descriptions = {
            QuestionDifficultyLevel.EASY: "基本的な概念の理解を問う簡単な難易度",
            QuestionDifficultyLevel.MEDIUM: "概念の応用や関連付けを問う中程度の難易度",
            QuestionDifficultyLevel.HARD: "複雑な概念や高度な応用を問う難しい難易度",
            QuestionDifficultyLevel.VERY_HARD: "専門的な知識と高度な分析を要求する非常に難しい難易度"
        }

        difficulty_desc = difficulty_descriptions.get(
            difficulty,
            "標準的な難易度"
        )

        # 問題形式の説明と例
        format_descriptions = {
            QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER: "単一の正解を選ぶ多肢選択式問題",
            QuestionFormat.MULTIPLE_CHOICE_MULTIPLE_ANSWER: "複数の正解を選ぶ多肢選択式問題",
            QuestionFormat.SCENARIO_BASED: "シナリオを読んで質問に答える問題",
            QuestionFormat.ORDERING: "項目を正しい順序に並べ替える問題",
            QuestionFormat.MATCHING: "項目同士を正しく対応付ける問題",
            QuestionFormat.HOTSPOT: "図や画像の特定の位置を選択する問題",
            QuestionFormat.CASE_STUDY: "ケーススタディに基づく一連の問題"
        }

        format_desc = format_descriptions.get(
            format_type,
            "標準的な問題形式"
        )

        # サブトピックがあれば取得
        subtopics = context.get("subtopics", [])
        subtopics_text = ""
        if subtopics:
            subtopics_text = "サブトピック:\n" + "\n".join([f"- {st}" for st in subtopics])

        prompt = f"""
# 問題生成

## トピック
{topic_name}
{subtopics_text}

## 認知レベル
{bloom_level.name}: {bloom_desc}

## 難易度
{difficulty.name}: {difficulty_desc}

## 問題形式
{format_type.name}: {format_desc}

## 指示
上記の条件に基づいて、質の高い問題と正解を生成してください。
問題は明確かつ簡潔で、指定された認知レベルと難易度を満たす必要があります。

回答は以下のJSON形式で提供してください:
```json
{{
  "question": "生成された問題文",
  "correct_answer": "正解"
}}
```

JSONフォーマットのみで回答し、余計なテキストは含めないでください。
"""
        return prompt

    def _parse_question_response(self, response_text: str) -> Tuple[str, str]:
        """LLMからのレスポンスを解析して問題文と正解を抽出"""
        # JSONの抽出（```json と ``` で囲まれている場合の対応）
        json_text = response_text
        if "```json" in response_text and "```" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_text = response_text[start:end].strip()

        try:
            # JSONとしてパース
            question_data = json.loads(json_text)

            # 必須フィールドのチェック
            question_text = question_data.get("question", "")
            correct_answer = question_data.get("correct_answer", "")

            if not question_text or not correct_answer:
                raise ValueError("問題文または正解が空です")

            return question_text, correct_answer

        except (json.JSONDecodeError, ValueError) as e:
            # JSON解析エラー時のフォールバック処理
            print(f"問題生成JSONのパース中にエラーが発生しました: {str(e)}")

            # テキストから問題文と正解を抽出する試み
            lines = response_text.strip().split("\n")
            question_text = "生成された問題に解析エラーが発生しました。"
            correct_answer = "正解情報が取得できませんでした。"

            for line in lines:
                line = line.strip()
                if line.startswith("問題:") or line.startswith("質問:"):
                    question_text = line.split(":", 1)[1].strip()
                elif line.startswith("正解:") or line.startswith("答え:"):
                    correct_answer = line.split(":", 1)[1].strip()

            return question_text, correct_answer


class LLMQuestionGenerationEngine(QuestionGenerationEngine):
    """LLMを活用した問題生成エンジン"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Args:
            llm_client: 使用するLLMクライアント。指定しない場合はデフォルトクライアントを使用。
        """
        super().__init__()
        self.llm_client = llm_client or LLMClientFactory.create_client()
        self.question_generator = LLMDrivenQuestionGenerator(self.llm_client)
        self.loaded_templates = True  # LLM版ではテンプレート読み込みは不要

    def set_llm_config(self, config: LLMConfig) -> None:
        """LLMの設定を変更する"""
        self.llm_client = LLMClientFactory.create_client(config=config)
        self.question_generator = LLMDrivenQuestionGenerator(self.llm_client)


# 便利なシングルトンインスタンス
default_llm_question_engine = LLMQuestionGenerationEngine()