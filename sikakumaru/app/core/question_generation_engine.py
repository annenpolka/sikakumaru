import random
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

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
    QuestionMetadata,
    Topic,
)


class QuestionDifficultyLevel(Enum):
    """問題の難易度レベルを表す列挙型"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class QuestionTemplate:
    """問題テンプレートを表すクラス"""

    def __init__(
        self,
        template_id: str,
        template_text: str,
        bloom_level: BloomsTaxonomyLevel,
        format_type: QuestionFormat,
        difficulty: QuestionDifficultyLevel,
        domain: Optional[Domain] = None,
        certification: Optional[Certification] = None,
        variables: Optional[Dict[str, Any]] = None
    ):
        self.template_id = template_id
        self.template_text = template_text
        self.bloom_level = bloom_level
        self.format_type = format_type
        self.difficulty = difficulty
        self.domain = domain
        self.certification = certification
        self.variables = variables or {}

    def fill_template(self, variable_values: Dict[str, Any]) -> str:
        """テンプレートに変数値を埋め込む"""
        result = self.template_text
        for var_name, var_value in variable_values.items():
            placeholder = f"{{{var_name}}}"
            result = result.replace(placeholder, str(var_value))
        return result


class DistractorGenerator:
    """誤答選択肢生成クラス"""

    def __init__(self):
        self.strategies = {
            DistractorType.COMMON_MISCONCEPTION: self._generate_misconception_distractors,
            DistractorType.SIMILAR_CONCEPT: self._generate_similar_concept_distractors,
            DistractorType.PARTIAL_TRUTH: self._generate_partial_truth_distractors,
            DistractorType.RELATED_BUT_IRRELEVANT: self._generate_related_but_irrelevant_distractors
        }

    def generate_distractors(
        self,
        correct_answer: str,
        distractor_type: DistractorType,
        count: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """指定された種類の誤答選択肢を生成する"""
        context = context or {}
        if distractor_type in self.strategies:
            return self.strategies[distractor_type](correct_answer, count, context)
        return self._generate_default_distractors(correct_answer, count, context)

    def _generate_misconception_distractors(
        self,
        correct_answer: str,
        count: int,
        context: Dict[str, Any]
    ) -> List[str]:
        """一般的な誤解に基づく誤答選択肢を生成"""
        # 実際の実装では、LLMを使用して誤解に基づく選択肢を生成
        # ここではダミー実装
        misconceptions = context.get("common_misconceptions", [])
        if len(misconceptions) >= count:
            return random.sample(misconceptions, count)

        # 不足分はデフォルト生成で補完
        return misconceptions + self._generate_default_distractors(
            correct_answer,
            count - len(misconceptions),
            context
        )

    def _generate_similar_concept_distractors(
        self,
        correct_answer: str,
        count: int,
        context: Dict[str, Any]
    ) -> List[str]:
        """類似概念に基づく誤答選択肢を生成"""
        similar_concepts = context.get("similar_concepts", [])
        if len(similar_concepts) >= count:
            return random.sample(similar_concepts, count)

        return similar_concepts + self._generate_default_distractors(
            correct_answer,
            count - len(similar_concepts),
            context
        )

    def _generate_partial_truth_distractors(
        self,
        correct_answer: str,
        count: int,
        context: Dict[str, Any]
    ) -> List[str]:
        """部分的に正しい要素を含む誤答選択肢を生成"""
        partial_truths = context.get("partial_truths", [])
        if len(partial_truths) >= count:
            return random.sample(partial_truths, count)

        return partial_truths + self._generate_default_distractors(
            correct_answer,
            count - len(partial_truths),
            context
        )

    def _generate_related_but_irrelevant_distractors(
        self,
        correct_answer: str,
        count: int,
        context: Dict[str, Any]
    ) -> List[str]:
        """関連はあるが無関係な誤答選択肢を生成"""
        related_concepts = context.get("related_concepts", [])
        if len(related_concepts) >= count:
            return random.sample(related_concepts, count)

        return related_concepts + self._generate_default_distractors(
            correct_answer,
            count - len(related_concepts),
            context
        )

    def _generate_default_distractors(
        self,
        correct_answer: str,
        count: int,
        context: Dict[str, Any]
    ) -> List[str]:
        """デフォルトの誤答選択肢生成（実際の実装ではLLMを使用）"""
        # ダミー実装
        return [f"誤答選択肢 {i+1}" for i in range(count)]


class ExplanationGenerator:
    """解説生成クラス"""

    def generate_explanation(
        self,
        question_text: str,
        correct_answer: str,
        distractors: List[str],
        bloom_level: BloomsTaxonomyLevel,
        topic: Topic,
        context: Optional[Dict[str, Any]] = None
    ) -> Explanation:
        """問題の解説を生成する"""
        # 実際の実装ではLLMを使用して解説を生成
        # ここではダミー実装

        explanation_id = str(uuid.uuid4())
        explanation_text = f"この問題は{topic.name}に関する{bloom_level.name}レベルの理解を問うものです。"
        justification = f"正解は「{correct_answer}」です。その理由は..."

        # 各誤答選択肢の解説
        distractor_analysis = {}
        for i, distractor in enumerate(distractors):
            distractor_analysis[f"distractor_{i+1}"] = f"選択肢「{distractor}」が不正解である理由: ダミー解説 {i+1}"

        # 学習リソース（実際の実装ではコンテキストから取得）
        learning_resources = [
            "参考書X の第Y章",
            "オンライン講座Z",
            "公式ドキュメントのセクションA"
        ]

        # 関連概念
        related_concepts = [topic.name, f"{topic.name}の基礎", f"{topic.name}の応用"]

        return Explanation(
            id=explanation_id,
            text=explanation_text,
            correct_answer_justification=justification,
            distractor_analysis=distractor_analysis,
            related_concepts=related_concepts,
            learning_resources=learning_resources
        )


class QuestionGenerator:
    """問題生成クラス"""

    def __init__(self):
        self.distractor_generator = DistractorGenerator()
        self.explanation_generator = ExplanationGenerator()
        self.templates = {}  # テンプレート辞書（実際の実装では外部から読み込む）

    def add_template(self, template: QuestionTemplate):
        """テンプレートを追加"""
        self.templates[template.template_id] = template

    def generate_question(
        self,
        topic: Topic,
        bloom_level: BloomsTaxonomyLevel,
        format_type: QuestionFormat,
        difficulty: QuestionDifficultyLevel,
        distractor_type: DistractorType,
        context: Optional[Dict[str, Any]] = None
    ) -> Question:
        """指定された条件に基づいて問題を生成"""
        context = context or {}

        # 適切なテンプレートを選択（実際の実装ではより洗練された選択ロジック）
        template = self._select_template(bloom_level, format_type, difficulty, topic.domain.id if topic.domain else None)

        # テンプレート変数の値を設定（実際の実装ではLLMを使用）
        variable_values = self._generate_variable_values(template, topic, context)

        # 問題文を生成
        question_text = template.fill_template(variable_values)

        # 正解を生成（実際の実装ではLLMを使用）
        correct_answer = self._generate_correct_answer(question_text, topic, context)

        # 誤答選択肢を生成
        distractors = self.distractor_generator.generate_distractors(
            correct_answer,
            distractor_type,
            count=3,  # 選択肢の数は調整可能
            context=context
        )

        # 選択肢をシャッフル
        all_choices = [correct_answer] + distractors
        random.shuffle(all_choices)

        # Choice オブジェクトのリストを作成
        choices = []
        for i, choice_text in enumerate(all_choices):
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
            context
        )

        # メタデータを作成
        # ドメインモデルのDifficultyに変換
        domain_difficulty = Difficulty.EASY
        if difficulty == QuestionDifficultyLevel.MEDIUM:
            domain_difficulty = Difficulty.MEDIUM
        elif difficulty in [QuestionDifficultyLevel.HARD, QuestionDifficultyLevel.VERY_HARD]:
            domain_difficulty = Difficulty.HARD

        metadata = QuestionMetadata(
            difficulty=domain_difficulty,
            cognitive_level=bloom_level,
            topics=[topic.id],
            certification="dummy_certification_id",  # 実際の実装では適切な値を設定
            domains=[]  # 実際の実装では適切な値を設定
        )

        # Question オブジェクトを作成して返す
        return Question(
            id=str(uuid.uuid4()),
            text=question_text,
            question_format=format_type,
            choices=choices,
            explanation=explanation,
            metadata=metadata,
            tags=[topic.name, bloom_level.name, difficulty.value]
        )

    def _select_template(
        self,
        bloom_level: BloomsTaxonomyLevel,
        format_type: QuestionFormat,
        difficulty: QuestionDifficultyLevel,
        domain: Optional[str] = None
    ) -> QuestionTemplate:
        """条件に合うテンプレートを選択"""
        # 実際の実装ではより洗練された選択ロジック
        matching_templates = []

        for template in self.templates.values():
            if (template.bloom_level == bloom_level and
                template.format_type == format_type and
                template.difficulty == difficulty):

                # ドメイン一致の優先度を高く
                if domain and template.domain and template.domain.id == domain:
                    matching_templates.insert(0, template)
                else:
                    matching_templates.append(template)

        if matching_templates:
            return matching_templates[0]

        # 適切なテンプレートがない場合はデフォルトテンプレート
        return self._create_default_template(bloom_level, format_type, difficulty)

    def _create_default_template(
        self,
        bloom_level: BloomsTaxonomyLevel,
        format_type: QuestionFormat,
        difficulty: QuestionDifficultyLevel
    ) -> QuestionTemplate:
        """デフォルトテンプレートを作成"""
        template_id = f"default_{bloom_level.name.lower()}_{format_type.name.lower()}_{difficulty.value}"

        if format_type == QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER:
            template_text = "次の{topic}に関する問題について、最も適切な選択肢を選びなさい。\n\n{question_context}"
        elif format_type == QuestionFormat.SCENARIO_BASED:
            template_text = "次のシナリオを読んで質問に答えなさい。\n\n{scenario}\n\n質問: {question}"
        else:
            template_text = "{topic}に関する次の問題に答えなさい。\n\n{question}"

        return QuestionTemplate(
            template_id=template_id,
            template_text=template_text,
            bloom_level=bloom_level,
            format_type=format_type,
            difficulty=difficulty
        )

    def _generate_variable_values(
        self,
        template: QuestionTemplate,
        topic: Topic,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """テンプレート変数の値を生成"""
        # 実際の実装ではLLMを使用
        # ここではダミー実装
        values = {
            "topic": topic.name,
            "question_context": f"{topic.name}に関するコンテキスト（ダミー）",
            "statement": f"{topic.name}に関する記述（ダミー）",
            "scenario": f"{topic.name}に関するシナリオ（ダミー）",
            "question": f"{topic.name}に関する質問（ダミー）"
        }

        # コンテキストから追加の変数値を取得
        if context:
            for var_name in template.variables:
                if var_name in context:
                    values[var_name] = context[var_name]

        return values

    def _generate_correct_answer(
        self,
        question_text: str,
        topic: Topic,
        context: Dict[str, Any]
    ) -> str:
        """正解を生成"""
        # 実際の実装ではLLMを使用
        # ここではダミー実装
        return f"{topic.name}に関する正解（ダミー）"


class QuestionGenerationEngine:
    """問題生成エンジン"""

    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.loaded_templates = False

    def load_templates(self, templates_source: Any):
        """テンプレートを読み込む"""
        # 実際の実装ではファイルやデータベースからテンプレートを読み込む
        # ここではダミー実装
        self.loaded_templates = True

    def generate_question(
        self,
        topic: Topic,
        bloom_level: BloomsTaxonomyLevel,
        format_type: QuestionFormat = QuestionFormat.MULTIPLE_CHOICE_SINGLE_ANSWER,
        difficulty: QuestionDifficultyLevel = QuestionDifficultyLevel.MEDIUM,
        distractor_type: DistractorType = DistractorType.COMMON_MISCONCEPTION,
        context: Optional[Dict[str, Any]] = None
    ) -> Question:
        """単一の問題を生成"""
        if not self.loaded_templates:
            self.load_templates(None)

        return self.question_generator.generate_question(
            topic=topic,
            bloom_level=bloom_level,
            format_type=format_type,
            difficulty=difficulty,
            distractor_type=distractor_type,
            context=context
        )

    def generate_question_set(
        self,
        topics: List[Topic],
        bloom_distribution: Dict[BloomsTaxonomyLevel, float],
        format_distribution: Dict[QuestionFormat, float],
        difficulty_distribution: Dict[QuestionDifficultyLevel, float],
        count: int,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Question]:
        """指定された分布に基づいて問題セットを生成"""
        if not self.loaded_templates:
            self.load_templates(None)

        questions = []

        # 各分布に基づいて問題パラメータを決定
        for _ in range(count):
            # トピックをランダム選択
            topic = random.choice(topics)

            # Bloom's Taxonomy レベルを分布に基づいて選択
            bloom_level = self._weighted_choice(bloom_distribution)

            # 問題形式を分布に基づいて選択
            format_type = self._weighted_choice(format_distribution)

            # 難易度を分布に基づいて選択
            difficulty = self._weighted_choice(difficulty_distribution)

            # 誤答選択肢タイプをランダム選択（実際の実装ではより洗練された選択ロジック）
            distractor_type = random.choice(list(DistractorType))

            # 問題を生成
            question = self.question_generator.generate_question(
                topic=topic,
                bloom_level=bloom_level,
                format_type=format_type,
                difficulty=difficulty,
                distractor_type=distractor_type,
                context=context
            )

            questions.append(question)

        return questions

    def _weighted_choice(self, distribution: Dict[Any, float]) -> Any:
        """重み付き確率分布に基づいて選択"""
        items = list(distribution.keys())
        weights = list(distribution.values())

        # 重みの合計が1になるように正規化
        total = sum(weights)
        normalized_weights = [w / total for w in weights]

        return random.choices(items, weights=normalized_weights, k=1)[0]

    def generate_adaptive_question(
        self,
        previous_questions: List[Question],
        previous_results: List[bool],
        topics: List[Topic],
        context: Optional[Dict[str, Any]] = None
    ) -> Question:
        """適応型問題生成 - 前の問題の結果に基づいて次の問題を生成"""
        if not previous_questions:
            # 初回の問題はデフォルト設定で生成
            return self.generate_question(
                topic=random.choice(topics),
                bloom_level=BloomsTaxonomyLevel.UNDERSTAND,
                difficulty=QuestionDifficultyLevel.MEDIUM,
                context=context
            )

        # 前回の結果に基づいて難易度を調整
        last_question = previous_questions[-1]
        last_result = previous_results[-1]

        current_bloom_level = last_question.metadata.cognitive_level

        # ドメインモデルのDifficultyからQuestionDifficultyLevelに変換
        current_difficulty = QuestionDifficultyLevel.MEDIUM
        if last_question.metadata.difficulty == Difficulty.EASY:
            current_difficulty = QuestionDifficultyLevel.EASY
        elif last_question.metadata.difficulty == Difficulty.HARD:
            current_difficulty = QuestionDifficultyLevel.HARD

        if last_result:  # 前回正解した場合
            # 難易度を上げる
            next_difficulty = self._increase_difficulty(current_difficulty)
            # 一定確率でBloom's Taxonomyレベルも上げる
            next_bloom_level = self._increase_bloom_level(current_bloom_level) if random.random() > 0.7 else current_bloom_level
        else:  # 前回不正解だった場合
            # 難易度を下げるか同じにする
            next_difficulty = current_difficulty if random.random() > 0.5 else self._decrease_difficulty(current_difficulty)
            # Bloom's Taxonomyレベルは同じか下げる
            next_bloom_level = current_bloom_level if random.random() > 0.3 else self._decrease_bloom_level(current_bloom_level)

        # トピックは前回と同じか関連トピックを選択
        # トピックIDからトピックオブジェクトを取得する必要がある（実際の実装ではリポジトリから取得）
        # ここではダミー実装として最初のトピックを使用
        next_topic = topics[0]

        # 問題形式はランダムに変える（実際の実装ではより洗練された選択ロジック）
        next_format = random.choice(list(QuestionFormat))

        return self.generate_question(
            topic=next_topic,
            bloom_level=next_bloom_level,
            format_type=next_format,
            difficulty=next_difficulty,
            context=context
        )

    def _increase_difficulty(self, current_difficulty: QuestionDifficultyLevel) -> QuestionDifficultyLevel:
        """難易度を上げる"""
        difficulty_levels = list(QuestionDifficultyLevel)
        current_index = difficulty_levels.index(current_difficulty)

        if current_index < len(difficulty_levels) - 1:
            return difficulty_levels[current_index + 1]
        return current_difficulty

    def _decrease_difficulty(self, current_difficulty: QuestionDifficultyLevel) -> QuestionDifficultyLevel:
        """難易度を下げる"""
        difficulty_levels = list(QuestionDifficultyLevel)
        current_index = difficulty_levels.index(current_difficulty)

        if current_index > 0:
            return difficulty_levels[current_index - 1]
        return current_difficulty

    def _increase_bloom_level(self, current_level: BloomsTaxonomyLevel) -> BloomsTaxonomyLevel:
        """Bloom's Taxonomyレベルを上げる"""
        bloom_levels = list(BloomsTaxonomyLevel)
        current_index = bloom_levels.index(current_level)

        if current_index < len(bloom_levels) - 1:
            return bloom_levels[current_index + 1]
        return current_level

    def _decrease_bloom_level(self, current_level: BloomsTaxonomyLevel) -> BloomsTaxonomyLevel:
        """Bloom's Taxonomyレベルを下げる"""
        bloom_levels = list(BloomsTaxonomyLevel)
        current_index = bloom_levels.index(current_level)

        if current_index > 0:
            return bloom_levels[current_index - 1]
        return current_level