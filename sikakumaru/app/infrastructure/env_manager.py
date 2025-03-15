"""
環境変数管理モジュール

このモジュールは、アプリケーション全体で使用される環境変数の管理を提供します。
.envファイルのロード、環境変数の検証、タイプ変換、デフォルト値の提供などの機能をサポートします。
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast

# python-dotenvをインポートしますが、インストールされていない場合も動作するようにします
try:
    from dotenv import load_dotenv
    dotenv_available = True
except ImportError:
    dotenv_available = False


# ロガーの設定
logger = logging.getLogger(__name__)


class EnvVarNotFoundError(Exception):
    """環境変数が見つからない場合に発生する例外"""
    pass


class EnvVarValidationError(Exception):
    """環境変数の検証に失敗した場合に発生する例外"""
    pass


# 環境変数のカテゴリを表す列挙型
class EnvCategory(Enum):
    """環境変数のカテゴリ"""
    GENERAL = "一般設定"
    API = "API設定"
    DATABASE = "データベース設定"
    SECURITY = "セキュリティ設定"
    LOGGING = "ログ設定"
    FEATURE_FLAGS = "機能フラグ"
    SERVICE = "サービス設定"


@dataclass
class EnvVarDefinition:
    """環境変数の定義を表すデータクラス"""
    key: str
    description: str
    category: EnvCategory
    required: bool = False
    default: Optional[Any] = None
    validator: Optional[Callable[[str], bool]] = None
    converter: Optional[Callable[[str], Any]] = None
    sensitive: bool = False  # パスワードやAPIキーなど機密性の高い情報を示すフラグ


class EnvManager:
    """環境変数を管理するクラス"""

    _instance = None
    _initialized = False
    _env_vars: Dict[str, Any] = {}
    _definitions: Dict[str, EnvVarDefinition] = {}

    def __new__(cls):
        """シングルトンパターンを実装"""
        if cls._instance is None:
            cls._instance = super(EnvManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初期化（一度だけ実行）"""
        if not self._initialized:
            self._initialized = True
            self._load_env_definitions()

    def _load_env_definitions(self) -> None:
        """
        環境変数の定義をロード
        新しい環境変数を追加する場合はここに定義を追加します
        """
        # LLM設定関連
        self._add_definition(
            EnvVarDefinition(
                key="OPENAI_API_KEY",
                description="OpenAI APIキー",
                category=EnvCategory.API,
                required=True,
                sensitive=True
            )
        )

        self._add_definition(
            EnvVarDefinition(
                key="OPENAI_API_BASE",
                description="OpenAI APIのベースURL（カスタムエンドポイントを使用する場合）",
                category=EnvCategory.API,
                required=False
            )
        )

        self._add_definition(
            EnvVarDefinition(
                key="DEFAULT_LLM_MODEL",
                description="デフォルトで使用するLLMモデル",
                category=EnvCategory.API,
                required=False,
                default="gpt-4"
            )
        )

        self._add_definition(
            EnvVarDefinition(
                key="LLM_TEMPERATURE",
                description="LLMの温度パラメータ（0.0-1.0）",
                category=EnvCategory.API,
                required=False,
                default="0.7",
                validator=lambda v: 0.0 <= float(v) <= 1.0,
                converter=float
            )
        )

        # アプリケーション設定
        self._add_definition(
            EnvVarDefinition(
                key="APP_ENV",
                description="アプリケーション環境（development, production, testing）",
                category=EnvCategory.GENERAL,
                required=False,
                default="development",
                validator=lambda v: v in ["development", "production", "testing"]
            )
        )

        self._add_definition(
            EnvVarDefinition(
                key="LOG_LEVEL",
                description="ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）",
                category=EnvCategory.LOGGING,
                required=False,
                default="INFO",
                validator=lambda v: v in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            )
        )

        self._add_definition(
            EnvVarDefinition(
                key="MAX_QUESTIONS_PER_REQUEST",
                description="一度のリクエストで生成できる最大問題数",
                category=EnvCategory.FEATURE_FLAGS,
                required=False,
                default="10",
                converter=int,
                validator=lambda v: int(v) > 0
            )
        )

        # データベース設定
        self._add_definition(
            EnvVarDefinition(
                key="DATABASE_URL",
                description="データベース接続URL",
                category=EnvCategory.DATABASE,
                required=False,
                sensitive=True
            )
        )

    def _add_definition(self, definition: EnvVarDefinition) -> None:
        """環境変数の定義を追加"""
        self._definitions[definition.key] = definition

    def load_env_file(self, env_file_path: Optional[str] = None) -> bool:
        """
        .envファイルから環境変数をロード

        Args:
            env_file_path: .envファイルのパス。Noneの場合はプロジェクトルートの.envを探します。

        Returns:
            bool: ロードに成功した場合はTrue、失敗した場合はFalse
        """
        if not dotenv_available:
            logger.warning("python-dotenvがインストールされていないため、.envファイルを読み込めません。")
            return False

        # パスが指定されていない場合、デフォルトのパスを使用
        if env_file_path is None:
            # プロジェクトルートを探して.envを参照
            current_dir = Path.cwd()
            # もしカレントディレクトリに.envがある場合はそれを使用
            if (current_dir / ".env").exists():
                env_file_path = str(current_dir / ".env")
                logger.info(f"カレントディレクトリで.envファイルを見つけました: {env_file_path}")
            else:
                # なければ上位ディレクトリを探索
                while current_dir.name and not (current_dir / ".env").exists():
                    if current_dir.parent == current_dir:  # ルートディレクトリに達した
                        break
                    current_dir = current_dir.parent

                env_file_path = str(current_dir / ".env")
                logger.info(f"探索した.envファイルのパス: {env_file_path}")

        # .envファイルが存在する場合のみロード
        env_file = Path(env_file_path)
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            logger.info(f".envファイルをロードしました: {env_file}")
            return True
        else:
            logger.warning(f".envファイルが見つかりません: {env_file}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        環境変数の値を取得

        Args:
            key: 環境変数の名前
            default: 環境変数が定義されていない場合のデフォルト値

        Returns:
            環境変数の値（変換されている場合は変換後の値）

        Raises:
            EnvVarNotFoundError: 必須環境変数が見つからない場合
            EnvVarValidationError: 環境変数の検証に失敗した場合
        """
        # キャッシュされた値があればそれを返す
        if key in self._env_vars:
            return self._env_vars[key]

        # 環境変数の定義を取得
        definition = self._definitions.get(key)

        # 定義があれば、それに基づいて環境変数を処理
        if definition:
            # 環境変数の値を取得
            value = os.environ.get(key)

            # 値が見つからない場合
            if value is None:
                # デフォルト値がある場合はそれを使用
                if definition.default is not None:
                    value = definition.default
                # 必須で値がない場合はエラー
                elif definition.required:
                    raise EnvVarNotFoundError(f"必須環境変数 {key} が設定されていません")
                # それ以外は引数で指定されたデフォルト値を使用
                else:
                    return default

            # バリデータがある場合は検証
            if definition.validator and not definition.validator(value):
                raise EnvVarValidationError(f"環境変数 {key} の値 '{value}' が無効です")

            # コンバータがある場合は変換
            if definition.converter:
                try:
                    value = definition.converter(value)
                except Exception as e:
                    raise EnvVarValidationError(f"環境変数 {key} の値 '{value}' を変換できません: {str(e)}")

            # キャッシュに保存
            self._env_vars[key] = value
            return value

        # 定義がない場合は直接環境変数から取得
        return os.environ.get(key, default)

    def get_int(self, key: str, default: Optional[int] = None) -> Optional[int]:
        """整数値として環境変数を取得"""
        value = self.get(key, default)
        if value is None:
            return None

        if isinstance(value, int):
            return value

        try:
            return int(value)
        except (ValueError, TypeError):
            raise EnvVarValidationError(f"環境変数 {key} の値 '{value}' を整数に変換できません")

    def get_float(self, key: str, default: Optional[float] = None) -> Optional[float]:
        """浮動小数点数値として環境変数を取得"""
        value = self.get(key, default)
        if value is None:
            return None

        if isinstance(value, float):
            return value

        try:
            return float(value)
        except (ValueError, TypeError):
            raise EnvVarValidationError(f"環境変数 {key} の値 '{value}' を浮動小数点数に変換できません")

    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        """ブール値として環境変数を取得"""
        value = self.get(key, default)
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            true_values = ["true", "yes", "1", "on", "t", "y"]
            false_values = ["false", "no", "0", "off", "f", "n"]

            if value.lower() in true_values:
                return True
            elif value.lower() in false_values:
                return False

        raise EnvVarValidationError(f"環境変数 {key} の値 '{value}' をブール値に変換できません")

    def get_list(self, key: str, separator: str = ",", default: Optional[List[str]] = None) -> Optional[List[str]]:
        """カンマ区切りの文字列をリストとして環境変数を取得"""
        value = self.get(key)
        if value is None:
            return default

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            return [item.strip() for item in value.split(separator)]

        raise EnvVarValidationError(f"環境変数 {key} の値 '{value}' をリストに変換できません")

    def validate_all_required(self) -> List[str]:
        """
        すべての必須環境変数が設定されているか検証

        Returns:
            List[str]: 見つからなかった必須環境変数のリスト
        """
        missing = []

        for key, definition in self._definitions.items():
            if definition.required:
                try:
                    self.get(key)
                except EnvVarNotFoundError:
                    missing.append(key)

        return missing

    def get_all_as_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        すべての環境変数を辞書として取得

        Args:
            include_sensitive: 機密情報を含めるかどうか

        Returns:
            Dict[str, Any]: 環境変数の辞書
        """
        result = {}

        for key, definition in self._definitions.items():
            if definition.sensitive and not include_sensitive:
                continue

            try:
                value = self.get(key)
                if value is not None:  # Noneの場合は含めない
                    result[key] = value
            except (EnvVarNotFoundError, EnvVarValidationError):
                pass

        return result

    def describe_env_vars(self) -> Dict[EnvCategory, List[Dict[str, Any]]]:
        """
        環境変数の説明情報をカテゴリごとにグループ化して取得

        Returns:
            Dict[EnvCategory, List[Dict[str, Any]]]: カテゴリごとの環境変数情報
        """
        result = {category: [] for category in EnvCategory}

        for key, definition in self._definitions.items():
            # 現在の値を取得（エラーの場合はNone）
            try:
                value = self.get(key)
                # 機密情報はマスク
                if definition.sensitive and value is not None:
                    value = "********"
            except (EnvVarNotFoundError, EnvVarValidationError):
                value = None

            # カテゴリに情報を追加
            result[definition.category].append({
                "key": key,
                "description": definition.description,
                "required": definition.required,
                "has_default": definition.default is not None,
                "current_value": value,
                "sensitive": definition.sensitive
            })

        return result

    def reset_cache(self) -> None:
        """環境変数のキャッシュをリセット"""
        self._env_vars.clear()


# シングルトンインスタンス
env_manager = EnvManager()


# 便利なヘルパー関数
def get_env(key: str, default: Any = None) -> Any:
    """環境変数の値を取得するヘルパー関数"""
    return env_manager.get(key, default)


def load_env_file(path: Optional[str] = None) -> bool:
    """環境変数ファイルをロードするヘルパー関数"""
    return env_manager.load_env_file(path)


def validate_env() -> List[str]:
    """必須環境変数を検証するヘルパー関数"""
    return env_manager.validate_all_required()


# LLM関連の環境変数にアクセスするための特化したクラス
class LLMEnvVars:
    """LLM関連の環境変数にアクセスするための便利なメソッドを提供"""

    @staticmethod
    def get_api_key() -> str:
        """OpenAI APIキーを取得"""
        return cast(str, env_manager.get("OPENAI_API_KEY"))

    @staticmethod
    def get_api_base() -> Optional[str]:
        """OpenAI APIのベースURLを取得"""
        return cast(Optional[str], env_manager.get("OPENAI_API_BASE"))

    @staticmethod
    def get_default_model() -> str:
        """デフォルトで使用するLLMモデルを取得"""
        return cast(str, env_manager.get("DEFAULT_LLM_MODEL"))

    @staticmethod
    def get_temperature() -> float:
        """LLMの温度パラメータを取得"""
        return cast(float, env_manager.get_float("LLM_TEMPERATURE"))

    @staticmethod
    def is_production() -> bool:
        """本番環境かどうかを判定"""
        return env_manager.get("APP_ENV") == "production"


# アプリケーション関連の環境変数にアクセスするための特化したクラス
class AppEnvVars:
    """アプリケーション関連の環境変数にアクセスするための便利なメソッドを提供"""

    @staticmethod
    def get_log_level() -> str:
        """ログレベルを取得"""
        return cast(str, env_manager.get("LOG_LEVEL"))

    @staticmethod
    def get_max_questions_per_request() -> int:
        """一度のリクエストで生成できる最大問題数を取得"""
        return cast(int, env_manager.get_int("MAX_QUESTIONS_PER_REQUEST"))

    @staticmethod
    def get_database_url() -> Optional[str]:
        """データベース接続URLを取得"""
        return cast(Optional[str], env_manager.get("DATABASE_URL"))

    @staticmethod
    def is_development() -> bool:
        """開発環境かどうかを判定"""
        return env_manager.get("APP_ENV") == "development"

    @staticmethod
    def is_testing() -> bool:
        """テスト環境かどうかを判定"""
        return env_manager.get("APP_ENV") == "testing"