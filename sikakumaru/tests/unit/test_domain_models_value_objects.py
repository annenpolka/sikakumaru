import unittest
import uuid
from datetime import datetime

from sikakumaru.app.domain.models import (
    BloomsTaxonomyLevel,
    Choice,
    Difficulty,
    DistractorType,
    Domain,
    Explanation,
    QuestionMetadata,
    Topic,
)


class TestTopic(unittest.TestCase):
    """Topicクラスのテスト"""

    def test_create_topic(self):
        """トピックが正しく作成されることを確認"""
        topic = Topic(
            id="topic-123",
            name="Pythonプログラミング",
            parent_id="parent-123"
        )

        self.assertEqual(topic.id, "topic-123")
        self.assertEqual(topic.name, "Pythonプログラミング")
        self.assertEqual(topic.parent_id, "parent-123")

    def test_create_topic_without_parent(self):
        """親を持たないトピックが正しく作成されることを確認"""
        topic = Topic(
            id="topic-123",
            name="プログラミング基礎"
        )

        self.assertEqual(topic.id, "topic-123")
        self.assertEqual(topic.name, "プログラミング基礎")
        self.assertIsNone(topic.parent_id)

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        topic = Topic(
            id="topic-123",
            name="データベース",
            parent_id="parent-123"
        )

        topic_dict = topic.to_dict()

        self.assertEqual(topic_dict["id"], "topic-123")
        self.assertEqual(topic_dict["name"], "データベース")
        self.assertEqual(topic_dict["parent_id"], "parent-123")

    def test_from_dict(self):
        """from_dictメソッドが正しく動作することを確認"""
        topic_dict = {
            "id": "topic-123",
            "name": "ネットワーク",
            "parent_id": None
        }

        topic = Topic.from_dict(topic_dict)

        self.assertEqual(topic.id, "topic-123")
        self.assertEqual(topic.name, "ネットワーク")
        self.assertIsNone(topic.parent_id)

    def test_to_from_dict_consistency(self):
        """to_dictとfrom_dictの相互変換が一貫していることを確認"""
        original_topic = Topic(
            id="topic-123",
            name="セキュリティ",
            parent_id="parent-123"
        )

        topic_dict = original_topic.to_dict()
        reconstructed_topic = Topic.from_dict(topic_dict)

        self.assertEqual(reconstructed_topic.id, original_topic.id)
        self.assertEqual(reconstructed_topic.name, original_topic.name)
        self.assertEqual(reconstructed_topic.parent_id, original_topic.parent_id)


class TestDomain(unittest.TestCase):
    """Domainクラスのテスト"""

    def test_create_domain(self):
        """ドメインが正しく作成されることを確認"""
        domain = Domain(
            id="domain-123",
            name="Web開発",
            weight=0.7,
            certification_id="cert-123"
        )

        self.assertEqual(domain.id, "domain-123")
        self.assertEqual(domain.name, "Web開発")
        self.assertEqual(domain.weight, 0.7)
        self.assertEqual(domain.certification_id, "cert-123")

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        domain = Domain(
            id="domain-123",
            name="アプリケーション設計",
            weight=0.5,
            certification_id="cert-123"
        )

        domain_dict = domain.to_dict()

        self.assertEqual(domain_dict["id"], "domain-123")
        self.assertEqual(domain_dict["name"], "アプリケーション設計")
        self.assertEqual(domain_dict["weight"], 0.5)
        self.assertEqual(domain_dict["certification_id"], "cert-123")

    def test_from_dict(self):
        """from_dictメソッドが正しく動作することを確認"""
        domain_dict = {
            "id": "domain-123",
            "name": "データベース設計",
            "weight": 0.3,
            "certification_id": "cert-123"
        }

        domain = Domain.from_dict(domain_dict)

        self.assertEqual(domain.id, "domain-123")
        self.assertEqual(domain.name, "データベース設計")
        self.assertEqual(domain.weight, 0.3)
        self.assertEqual(domain.certification_id, "cert-123")


class TestQuestionMetadata(unittest.TestCase):
    """QuestionMetadataクラスのテスト"""

    def test_create_metadata(self):
        """問題メタデータが正しく作成されることを確認"""
        metadata = QuestionMetadata(
            difficulty=Difficulty.MEDIUM,
            topics=["Python", "データ構造"],
            certification="プログラミング検定",
            cognitive_level=BloomsTaxonomyLevel.UNDERSTAND,
            domains=["プログラミング", "アルゴリズム"],
            source="公式問題集",
            version="1.0"
        )

        self.assertEqual(metadata.difficulty, Difficulty.MEDIUM)
        self.assertEqual(metadata.topics, ["Python", "データ構造"])
        self.assertEqual(metadata.certification, "プログラミング検定")
        self.assertEqual(metadata.cognitive_level, BloomsTaxonomyLevel.UNDERSTAND)
        self.assertEqual(metadata.domains, ["プログラミング", "アルゴリズム"])
        self.assertEqual(metadata.source, "公式問題集")
        self.assertEqual(metadata.version, "1.0")

    def test_create_metadata_minimal(self):
        """最小限の情報で問題メタデータが正しく作成されることを確認"""
        metadata = QuestionMetadata(
            difficulty=Difficulty.EASY,
            topics=["データベース"],
            certification="DB検定",
            cognitive_level=BloomsTaxonomyLevel.REMEMBER
        )

        self.assertEqual(metadata.difficulty, Difficulty.EASY)
        self.assertEqual(metadata.topics, ["データベース"])
        self.assertEqual(metadata.certification, "DB検定")
        self.assertEqual(metadata.cognitive_level, BloomsTaxonomyLevel.REMEMBER)
        self.assertEqual(metadata.domains, [])
        self.assertIsNone(metadata.source)
        self.assertIsNone(metadata.version)

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        metadata = QuestionMetadata(
            difficulty=Difficulty.HARD,
            topics=["ネットワーク", "セキュリティ"],
            certification="ネットワークスペシャリスト",
            cognitive_level=BloomsTaxonomyLevel.APPLY,
            domains=["LAN", "WAN"],
            source="模擬試験",
            version="2023"
        )

        metadata_dict = metadata.to_dict()

        self.assertEqual(metadata_dict["difficulty"], "HARD")
        self.assertEqual(metadata_dict["topics"], ["ネットワーク", "セキュリティ"])
        self.assertEqual(metadata_dict["certification"], "ネットワークスペシャリスト")
        self.assertEqual(metadata_dict["cognitive_level"], "APPLY")
        self.assertEqual(metadata_dict["domains"], ["LAN", "WAN"])
        self.assertEqual(metadata_dict["source"], "模擬試験")
        self.assertEqual(metadata_dict["version"], "2023")

    def test_from_dict(self):
        """from_dictメソッドが正しく動作することを確認"""
        metadata_dict = {
            "difficulty": "MEDIUM",
            "topics": ["Java", "オブジェクト指向"],
            "certification": "Javaプログラマ",
            "cognitive_level": "EVALUATE",
            "domains": ["言語仕様", "設計"],
            "source": "過去問",
            "version": "SE11"
        }

        metadata = QuestionMetadata.from_dict(metadata_dict)

        self.assertEqual(metadata.difficulty, Difficulty.MEDIUM)
        self.assertEqual(metadata.topics, ["Java", "オブジェクト指向"])
        self.assertEqual(metadata.certification, "Javaプログラマ")
        self.assertEqual(metadata.cognitive_level, BloomsTaxonomyLevel.EVALUATE)
        self.assertEqual(metadata.domains, ["言語仕様", "設計"])
        self.assertEqual(metadata.source, "過去問")
        self.assertEqual(metadata.version, "SE11")


class TestChoice(unittest.TestCase):
    """Choiceクラスのテスト"""

    def test_create_correct_choice(self):
        """正解の選択肢が正しく作成されることを確認"""
        choice = Choice(
            id="choice-123",
            text="Pythonはインタープリタであるとともにコンパイラでもある",
            is_correct=True,
            explanation="Pythonはソースコードを中間コードにコンパイルし、それを実行するため"
        )

        self.assertEqual(choice.id, "choice-123")
        self.assertEqual(choice.text, "Pythonはインタープリタであるとともにコンパイラでもある")
        self.assertTrue(choice.is_correct)
        self.assertEqual(choice.explanation, "Pythonはソースコードを中間コードにコンパイルし、それを実行するため")
        self.assertIsNone(choice.distractor_type)

    def test_create_distractor_choice(self):
        """誤答選択肢が正しく作成されることを確認"""
        choice = Choice(
            id="choice-456",
            text="Pythonは純粋なインタープリタ言語である",
            is_correct=False,
            distractor_type=DistractorType.COMMON_MISCONCEPTION,
            explanation="これは一般的な誤解です"
        )

        self.assertEqual(choice.id, "choice-456")
        self.assertEqual(choice.text, "Pythonは純粋なインタープリタ言語である")
        self.assertFalse(choice.is_correct)
        self.assertEqual(choice.distractor_type, DistractorType.COMMON_MISCONCEPTION)
        self.assertEqual(choice.explanation, "これは一般的な誤解です")

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        choice = Choice(
            id="choice-123",
            text="SQLはチューリング完全である",
            is_correct=False,
            distractor_type=DistractorType.PARTIAL_TRUTH,
            explanation="標準SQLはチューリング完全ではないが、拡張によってループや条件分岐が可能"
        )

        choice_dict = choice.to_dict()

        self.assertEqual(choice_dict["id"], "choice-123")
        self.assertEqual(choice_dict["text"], "SQLはチューリング完全である")
        self.assertEqual(choice_dict["is_correct"], False)
        self.assertEqual(choice_dict["distractor_type"], "PARTIAL_TRUTH")
        self.assertEqual(choice_dict["explanation"], "標準SQLはチューリング完全ではないが、拡張によってループや条件分岐が可能")

    def test_from_dict(self):
        """from_dictメソッドが正しく動作することを確認"""
        choice_dict = {
            "id": "choice-123",
            "text": "TCPはコネクションレス型プロトコルである",
            "is_correct": False,
            "distractor_type": "COMMON_MISCONCEPTION",
            "explanation": "TCPはコネクション型プロトコルです"
        }

        choice = Choice.from_dict(choice_dict)

        self.assertEqual(choice.id, "choice-123")
        self.assertEqual(choice.text, "TCPはコネクションレス型プロトコルである")
        self.assertFalse(choice.is_correct)
        self.assertEqual(choice.distractor_type, DistractorType.COMMON_MISCONCEPTION)
        self.assertEqual(choice.explanation, "TCPはコネクション型プロトコルです")


class TestExplanation(unittest.TestCase):
    """Explanationクラスのテスト"""

    def test_create_explanation(self):
        """解説が正しく作成されることを確認"""
        explanation = Explanation(
            id="explanation-123",
            text="TLS（Transport Layer Security）は、インターネット上の通信を暗号化するプロトコルです。",
            correct_answer_justification="TLSはSSLの後継であり、現在のWebセキュリティの中核をなしています。",
            distractor_analysis={
                "choice-1": "SSLはTLSの後継ではなく、前身です。",
                "choice-2": "TLSはトランスポート層ではなくアプリケーション層で動作します。"
            },
            related_concepts=["SSL", "HTTPS", "証明書"],
            learning_resources=["RFC 8446", "https://example.com/tls-guide"]
        )

        self.assertEqual(explanation.id, "explanation-123")
        self.assertEqual(explanation.text, "TLS（Transport Layer Security）は、インターネット上の通信を暗号化するプロトコルです。")
        self.assertEqual(explanation.correct_answer_justification, "TLSはSSLの後継であり、現在のWebセキュリティの中核をなしています。")
        self.assertEqual(explanation.distractor_analysis["choice-1"], "SSLはTLSの後継ではなく、前身です。")
        self.assertEqual(explanation.related_concepts, ["SSL", "HTTPS", "証明書"])
        self.assertEqual(explanation.learning_resources, ["RFC 8446", "https://example.com/tls-guide"])

    def test_to_dict(self):
        """to_dictメソッドが正しく動作することを確認"""
        explanation = Explanation(
            id="explanation-123",
            text="データベースのインデックスは検索を高速化するための技術です。",
            correct_answer_justification="B-treeなどの構造を使って効率的なデータアクセスを実現します。",
            distractor_analysis={
                "choice-1": "インデックスはデータ整合性のためではなく、検索速度のための機能です。",
                "choice-2": "インデックスは検索速度を遅くするのではなく、向上させます。"
            },
            related_concepts=["B-tree", "ハッシュインデックス", "クラスタードインデックス"],
            learning_resources=["データベース設計の基礎", "https://example.com/db-index-guide"]
        )

        explanation_dict = explanation.to_dict()

        self.assertEqual(explanation_dict["id"], "explanation-123")
        self.assertEqual(explanation_dict["text"], "データベースのインデックスは検索を高速化するための技術です。")
        self.assertEqual(explanation_dict["correct_answer_justification"], "B-treeなどの構造を使って効率的なデータアクセスを実現します。")
        self.assertEqual(explanation_dict["distractor_analysis"]["choice-1"], "インデックスはデータ整合性のためではなく、検索速度のための機能です。")
        self.assertEqual(explanation_dict["related_concepts"], ["B-tree", "ハッシュインデックス", "クラスタードインデックス"])
        self.assertEqual(explanation_dict["learning_resources"], ["データベース設計の基礎", "https://example.com/db-index-guide"])

    def test_from_dict(self):
        """from_dictメソッドが正しく動作することを確認"""
        explanation_dict = {
            "id": "explanation-123",
            "text": "ハッシュ関数は一方向性の関数で、元の値を復元するのが困難です。",
            "correct_answer_justification": "これは暗号学的安全性の重要な特性です。",
            "distractor_analysis": {
                "choice-1": "ハッシュ関数には衝突可能性があり、完全に一意ではありません。",
                "choice-2": "全てのハッシュ関数が暗号学的に安全なわけではありません。"
            },
            "related_concepts": ["MD5", "SHA-256", "衝突耐性"],
            "learning_resources": ["暗号技術入門", "https://example.com/hash-functions"]
        }

        explanation = Explanation.from_dict(explanation_dict)

        self.assertEqual(explanation.id, "explanation-123")
        self.assertEqual(explanation.text, "ハッシュ関数は一方向性の関数で、元の値を復元するのが困難です。")
        self.assertEqual(explanation.correct_answer_justification, "これは暗号学的安全性の重要な特性です。")
        self.assertEqual(explanation.distractor_analysis["choice-1"], "ハッシュ関数には衝突可能性があり、完全に一意ではありません。")
        self.assertEqual(explanation.related_concepts, ["MD5", "SHA-256", "衝突耐性"])
        self.assertEqual(explanation.learning_resources, ["暗号技術入門", "https://example.com/hash-functions"])


if __name__ == "__main__":
    unittest.main()