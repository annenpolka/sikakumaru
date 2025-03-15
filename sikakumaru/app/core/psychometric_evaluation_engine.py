"""
心理測定学評価エンジン

このモジュールは、問題の心理測定学的品質（妥当性、信頼性、識別力など）を
評価するための機能を提供します。項目応答理論（IRT）のモデルも適用します。
"""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    Difficulty,
    Question,
    QuestionFormat,
)


@dataclass
class ItemAnalysisResult:
    """問題項目分析の結果"""
    difficulty_index: float  # P-値（正答率）：0.0〜1.0
    discrimination_index: float  # 識別力指数：-1.0〜1.0
    distractor_efficiency: Dict[str, float]  # 各ディストラクターの効率性
    bloom_level_match: float  # 意図した認知レベルとの一致度：0.0〜1.0
    reliability_contribution: float  # 信頼性係数への貢献度

    def get_difficulty_category(self) -> Difficulty:
        """難易度カテゴリを取得する"""
        if self.difficulty_index > 0.7:
            return Difficulty.EASY
        elif self.difficulty_index >= 0.4:
            return Difficulty.MEDIUM
        else:
            return Difficulty.HARD

    def is_good_discriminator(self) -> bool:
        """識別力が良好かどうかを判定する"""
        return self.discrimination_index >= 0.3

    def get_quality_score(self) -> float:
        """問題の総合品質スコアを計算する（0.0〜1.0）"""
        # 理想的な難易度は0.5付近（極端に簡単/難しい問題は避ける）
        difficulty_quality = 1.0 - abs(self.difficulty_index - 0.5) * 2.0

        # 識別力は高いほど良い（0.3以上が望ましい）
        discrimination_quality = min(self.discrimination_index / 0.3, 1.0) if self.discrimination_index > 0 else 0.0

        # ディストラクター効率性の平均
        distractor_quality = sum(self.distractor_efficiency.values()) / len(self.distractor_efficiency) if self.distractor_efficiency else 0.0

        # 認知レベル一致度
        bloom_quality = self.bloom_level_match

        # 重み付け平均
        return (
            difficulty_quality * 0.25 +
            discrimination_quality * 0.35 +
            distractor_quality * 0.25 +
            bloom_quality * 0.15
        )

    def get_improvement_suggestions(self) -> List[str]:
        """問題改善のための提案を生成する"""
        suggestions = []

        # 難易度に関する提案
        if self.difficulty_index > 0.9:
            suggestions.append("問題が非常に簡単すぎます。もう少し複雑な概念や応用が必要です。")
        elif self.difficulty_index < 0.2:
            suggestions.append("問題が非常に難しすぎます。もう少し基本的な内容にするか、ヒントを追加することを検討してください。")

        # 識別力に関する提案
        if self.discrimination_index < 0.2:
            suggestions.append("問題の識別力が低いです。高知識群と低知識群を区別できていません。より明確な選択肢を設計してください。")
        elif self.discrimination_index < 0:
            suggestions.append("問題の識別力が負の値です。これは低知識群の方が正答率が高いことを示しており、問題設計に問題があります。")

        # ディストラクターに関する提案
        low_efficiency_distractors = [k for k, v in self.distractor_efficiency.items() if v < 0.1]
        if low_efficiency_distractors:
            distractor_ids = ", ".join(low_efficiency_distractors)
            suggestions.append(f"選択肢 {distractor_ids} の効率が低いです。より魅力的なディストラクターに改善してください。")

        # 認知レベルに関する提案
        if self.bloom_level_match < 0.6:
            suggestions.append("意図した認知レベルと実際の問題の難易度が一致していません。問題をより適切な認知プロセスに合わせて調整してください。")

        return suggestions


class ValidityEvaluator:
    """問題の妥当性評価クラス"""

    def evaluate_content_validity(
        self,
        question: Question,
        syllabus_topics: List[str],
        expert_ratings: Optional[Dict[str, float]] = None
    ) -> float:
        """
        内容的妥当性を評価する

        Args:
            question: 評価対象の問題
            syllabus_topics: シラバスのトピックリスト
            expert_ratings: 専門家による評価（オプション）

        Returns:
            内容的妥当性スコア（0.0〜1.0）
        """
        # 問題のトピックがシラバスに含まれているか確認
        topic_coverage = sum(1 for topic in question.metadata.topics if topic in syllabus_topics)
        topic_coverage_ratio = topic_coverage / len(question.metadata.topics) if question.metadata.topics else 0.0

        # 専門家による評価がある場合は考慮
        if expert_ratings and question.id in expert_ratings:
            expert_score = expert_ratings[question.id]
            # 専門家評価と範囲カバレッジを組み合わせる
            return (topic_coverage_ratio * 0.6) + (expert_score * 0.4)

        return topic_coverage_ratio

    def evaluate_construct_validity(
        self,
        question: Question,
        intended_bloom_level: BloomsTaxonomyLevel
    ) -> float:
        """
        構成概念妥当性を評価する（意図した認知プロセスを測定しているか）

        Args:
            question: 評価対象の問題
            intended_bloom_level: 意図した認知レベル

        Returns:
            構成概念妥当性スコア（0.0〜1.0）
        """
        # 実装例：問題の認知レベルと意図したレベルの一致度
        question_bloom_level = question.metadata.cognitive_level

        # 完全一致
        if question_bloom_level == intended_bloom_level:
            return 1.0

        # 認知レベルの階層関係に基づく評価
        bloom_hierarchy = {
            BloomsTaxonomyLevel.REMEMBER: 1,
            BloomsTaxonomyLevel.UNDERSTAND: 2,
            BloomsTaxonomyLevel.APPLY: 3,
            BloomsTaxonomyLevel.ANALYZE: 4,
            BloomsTaxonomyLevel.EVALUATE: 5,
            BloomsTaxonomyLevel.CREATE: 6
        }

        # 階層差に基づくスコア計算
        level_diff = abs(bloom_hierarchy[question_bloom_level] - bloom_hierarchy[intended_bloom_level])
        max_diff = 5  # 最大階層差

        return max(0.0, 1.0 - (level_diff / max_diff))


class ReliabilityAnalyzer:
    """問題の信頼性分析クラス"""

    def calculate_internal_consistency(
        self,
        questions: List[Question],
        responses: List[Dict[str, bool]]  # 問題IDと正誤のマッピング
    ) -> Tuple[float, Dict[str, float]]:
        """
        内的一貫性（クロンバックのα）を計算する

        Args:
            questions: 評価対象の問題リスト
            responses: 回答データ（各受験者の各問題に対する正誤）

        Returns:
            クロンバックのα係数と各問題の貢献度
        """
        n_items = len(questions)
        if n_items <= 1:
            return 0.0, {}

        # 問題IDのリスト
        question_ids = [q.id for q in questions]

        # 応答データを行列に変換
        response_matrix = []
        for response in responses:
            row = [1 if response.get(q_id, False) else 0 for q_id in question_ids]
            response_matrix.append(row)

        response_array = np.array(response_matrix)

        # 各項目の分散
        item_variances = np.var(response_array, axis=0, ddof=1)

        # 総合スコアの分散
        total_scores = np.sum(response_array, axis=1)
        total_variance = np.var(total_scores, ddof=1)

        # クロンバックのα係数
        if total_variance == 0:
            alpha = 0.0
        else:
            alpha = (n_items / (n_items - 1)) * (1 - np.sum(item_variances) / total_variance)

        # 各問題の貢献度計算
        item_contributions = {}
        for i, q_id in enumerate(question_ids):
            # i番目の項目を除外した場合のα係数
            if n_items > 2:
                remaining_items = np.delete(response_array, i, axis=1)
                remaining_total = np.sum(remaining_items, axis=1)
                remaining_variance = np.var(remaining_total, ddof=1)
                remaining_item_variances = np.var(remaining_items, axis=0, ddof=1)

                alpha_if_deleted = ((n_items - 1) / (n_items - 2)) * (1 - np.sum(remaining_item_variances) / remaining_variance)
                contribution = alpha - alpha_if_deleted
            else:
                # 項目が2つしかない場合
                correlation = np.corrcoef(response_array[:, 0], response_array[:, 1])[0, 1]
                contribution = correlation / 2

            item_contributions[q_id] = contribution

        return alpha, item_contributions


class ItemDiscriminationCalculator:
    """問題の識別力計算クラス"""

    def calculate_discrimination_index(
        self,
        question: Question,
        responses: List[Tuple[str, bool]],  # (user_id, is_correct)のリスト
        overall_scores: Dict[str, float]  # user_idと総合スコアのマッピング
    ) -> float:
        """
        問題の識別力指数を計算する

        Args:
            question: 評価対象の問題
            responses: この問題に対する回答データ
            overall_scores: 各ユーザーの全体的な成績

        Returns:
            識別力指数（-1.0〜1.0）
        """
        if not responses or len(responses) < 10:  # 最低サンプル数
            return 0.0

        # ユーザーを総合スコアで上位27%と下位27%に分ける
        user_scores = [(user_id, overall_scores.get(user_id, 0.0)) for user_id, _ in responses]
        user_scores.sort(key=lambda x: x[1], reverse=True)

        group_size = max(1, int(len(user_scores) * 0.27))
        upper_group = set(user_id for user_id, _ in user_scores[:group_size])
        lower_group = set(user_id for user_id, _ in user_scores[-group_size:])

        # 各グループの正答率を計算
        upper_correct = sum(1 for user_id, is_correct in responses if user_id in upper_group and is_correct)
        upper_total = sum(1 for user_id, _ in responses if user_id in upper_group)

        lower_correct = sum(1 for user_id, is_correct in responses if user_id in lower_group and is_correct)
        lower_total = sum(1 for user_id, _ in responses if user_id in lower_group)

        if upper_total == 0 or lower_total == 0:
            return 0.0

        upper_p = upper_correct / upper_total
        lower_p = lower_correct / lower_total

        # 識別力指数 = 上位グループ正答率 - 下位グループ正答率
        return upper_p - lower_p

    def calculate_distractor_efficiency(
        self,
        question: Question,
        choice_selections: Dict[str, int]  # 選択肢IDと選択回数のマッピング
    ) -> Dict[str, float]:
        """
        ディストラクター（不正解選択肢）の効率性を計算する

        Args:
            question: 評価対象の問題
            choice_selections: 各選択肢の選択回数

        Returns:
            選択肢IDと効率性スコア（0.0〜1.0）のマッピング
        """
        total_selections = sum(choice_selections.values())
        if total_selections == 0:
            return {choice.id: 0.0 for choice in question.choices}

        # 正解の選択肢を特定
        correct_choices = [choice.id for choice in question.choices if choice.is_correct]

        # 各選択肢の効率性計算
        efficiency = {}
        for choice in question.choices:
            if choice.id in correct_choices:
                # 正解の場合、選択率が高いほど良い
                efficiency[choice.id] = choice_selections.get(choice.id, 0) / total_selections
            else:
                # 不正解の場合、誘引率が均等に分散していることが理想
                ideal_distractor_rate = (1.0 - sum(efficiency.get(c, 0.0) for c in correct_choices)) / (len(question.choices) - len(correct_choices))
                actual_rate = choice_selections.get(choice.id, 0) / total_selections

                # 理想的な率に近いほど効率的（逆U字カーブ）
                if actual_rate <= ideal_distractor_rate:
                    efficiency[choice.id] = actual_rate / ideal_distractor_rate
                else:
                    # 過剰に選ばれている場合、効率が下がる
                    efficiency[choice.id] = 1.0 - min(1.0, (actual_rate - ideal_distractor_rate) / ideal_distractor_rate)

        return efficiency


class IRTModelApplicator:
    """項目応答理論モデル適用クラス"""

    def apply_1pl_model(
        self,
        question: Question,
        responses: List[Tuple[str, bool]],  # (user_id, is_correct)のリスト
        ability_estimates: Dict[str, float]  # user_idと能力推定値のマッピング
    ) -> float:
        """
        1パラメータモデル（ラッシュモデル）を適用し、問題の難易度パラメータを推定する

        Args:
            question: 評価対象の問題
            responses: この問題に対する回答データ
            ability_estimates: 各ユーザーの能力推定値

        Returns:
            問題の難易度パラメータ
        """
        if not responses:
            return 0.0

        # 繰り返し推定のためのパラメータ
        max_iterations = 20
        convergence_criterion = 0.001
        current_difficulty = 0.0  # 初期値

        for _ in range(max_iterations):
            expected_probabilities = {}
            for user_id, _ in responses:
                ability = ability_estimates.get(user_id, 0.0)
                expected_probabilities[user_id] = self._logistic_function(ability - current_difficulty)

            # 期待正答数
            expected_correct = sum(expected_probabilities.values())

            # 実際の正答数
            actual_correct = sum(1 for _, is_correct in responses if is_correct)

            # 勾配（実際の正答数 - 期待正答数）
            gradient = actual_correct - expected_correct

            # 更新量
            step_size = gradient / len(responses)

            # 難易度パラメータの更新
            new_difficulty = current_difficulty - step_size

            # 収束判定
            if abs(new_difficulty - current_difficulty) < convergence_criterion:
                return new_difficulty

            current_difficulty = new_difficulty

        return current_difficulty

    def _logistic_function(self, x: float) -> float:
        """ロジスティック関数"""
        try:
            return 1.0 / (1.0 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0


class PsychometricEvaluationEngine:
    """心理測定学評価エンジン"""

    def __init__(self):
        """初期化"""
        self.validity_evaluator = ValidityEvaluator()
        self.reliability_analyzer = ReliabilityAnalyzer()
        self.discrimination_calculator = ItemDiscriminationCalculator()
        self.irt_model_applicator = IRTModelApplicator()

    def analyze_item(
        self,
        question: Question,
        responses: List[Tuple[str, bool]],
        overall_scores: Dict[str, float],
        choice_selections: Dict[str, int],
        intended_bloom_level: Optional[BloomsTaxonomyLevel] = None
    ) -> ItemAnalysisResult:
        """
        問題項目を総合的に分析する

        Args:
            question: 評価対象の問題
            responses: この問題に対する回答データ
            overall_scores: 各ユーザーの全体的な成績
            choice_selections: 各選択肢の選択回数
            intended_bloom_level: 意図した認知レベル

        Returns:
            問題項目分析の結果
        """
        # 難易度指数（P-値）計算
        total_responses = len(responses)
        correct_responses = sum(1 for _, is_correct in responses if is_correct)
        difficulty_index = correct_responses / total_responses if total_responses > 0 else 0.5

        # 識別力指数計算
        discrimination_index = self.discrimination_calculator.calculate_discrimination_index(
            question, responses, overall_scores
        )

        # ディストラクター効率性計算
        distractor_efficiency = self.discrimination_calculator.calculate_distractor_efficiency(
            question, choice_selections
        )

        # 認知レベル一致度計算
        bloom_level_match = 1.0
        if intended_bloom_level:
            bloom_level_match = self.validity_evaluator.evaluate_construct_validity(
                question, intended_bloom_level
            )

        # 信頼性への貢献度計算
        # 疑似相関係数として、識別力と難易度の適切さから計算
        optimal_difficulty = 0.5  # 最適難易度
        difficulty_quality = 1.0 - 2.0 * abs(difficulty_index - optimal_difficulty)
        reliability_contribution = (discrimination_index + 1.0) / 2.0 * difficulty_quality

        return ItemAnalysisResult(
            difficulty_index=difficulty_index,
            discrimination_index=discrimination_index,
            distractor_efficiency=distractor_efficiency,
            bloom_level_match=bloom_level_match,
            reliability_contribution=reliability_contribution
        )

    def evaluate_test_reliability(
        self,
        questions: List[Question],
        responses: List[Dict[str, bool]]
    ) -> Tuple[float, Dict[str, float]]:
        """
        テスト全体の信頼性を評価する

        Args:
            questions: 評価対象の問題リスト
            responses: 回答データ

        Returns:
            信頼性係数と各問題の貢献度
        """
        return self.reliability_analyzer.calculate_internal_consistency(questions, responses)

    def calibrate_difficulty_levels(
        self,
        questions: List[Question],
        item_analysis_results: Dict[str, ItemAnalysisResult]
    ) -> Dict[str, Difficulty]:
        """
        問題の難易度レベルを調整する

        Args:
            questions: 評価対象の問題リスト
            item_analysis_results: 各問題の分析結果

        Returns:
            問題IDと調整後の難易度のマッピング
        """
        calibrated_levels = {}

        for question in questions:
            if question.id in item_analysis_results:
                result = item_analysis_results[question.id]
                calibrated_levels[question.id] = result.get_difficulty_category()

        return calibrated_levels

    def get_improvement_recommendations(
        self,
        questions: List[Question],
        item_analysis_results: Dict[str, ItemAnalysisResult]
    ) -> Dict[str, List[str]]:
        """
        問題改善のための推奨事項を提供する

        Args:
            questions: 評価対象の問題リスト
            item_analysis_results: 各問題の分析結果

        Returns:
            問題IDと改善提案のリストのマッピング
        """
        recommendations = {}

        for question in questions:
            if question.id in item_analysis_results:
                result = item_analysis_results[question.id]
                recommendations[question.id] = result.get_improvement_suggestions()

        return recommendations