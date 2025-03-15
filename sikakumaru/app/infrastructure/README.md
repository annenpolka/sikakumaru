# インフラストラクチャモジュール

このパッケージには、アプリケーションのインフラストラクチャ層のコンポーネントが含まれています。

## 環境変数管理 (env_manager.py)

環境変数管理モジュールは、アプリケーション全体で使用される環境変数の一元管理を提供します。

### 主な機能

- **.env ファイルのロード**: プロジェクトルートの.env ファイルを自動検出してロード
- **環境変数の検証**: 必須環境変数のチェックと値の検証
- **タイプ変換**: 文字列から整数、浮動小数点数、ブール値などへの自動変換
- **デフォルト値**: 定義されていない環境変数に対するデフォルト値の提供
- **値のキャッシュ**: パフォーマンス向上のためのメモリキャッシュ
- **カテゴリ分類**: 環境変数のカテゴリによる分類と管理
- **機密情報の保護**: パスワードや API キーなどの機密情報の適切な取り扱い

### 基本的な使用方法

```python
# 1. ヘルパー関数による利用
from sikakumaru.app.infrastructure import get_env, validate_env

# 環境変数の取得（定義されていない場合はデフォルト値を返す）
api_key = get_env("OPENAI_API_KEY")
debug_mode = get_env("DEBUG_MODE", False)

# 必須環境変数の検証
missing_vars = validate_env()
if missing_vars:
    print(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")
```

### 専用クラスによる利用

特定カテゴリの環境変数に特化したクラスも用意されています：

```python
# LLM関連の環境変数
from sikakumaru.app.infrastructure import LLMEnvVars

api_key = LLMEnvVars.get_api_key()
model = LLMEnvVars.get_default_model()
temperature = LLMEnvVars.get_temperature()

# アプリケーション関連の環境変数
from sikakumaru.app.infrastructure import AppEnvVars

log_level = AppEnvVars.get_log_level()
is_dev = AppEnvVars.is_development()
```

### 直接利用

より詳細な制御が必要な場合、`env_manager`インスタンスを直接使用できます：

```python
from sikakumaru.app.infrastructure import env_manager

# 異なる型での環境変数取得
max_tokens = env_manager.get_int("MAX_TOKENS", 2000)
temperature = env_manager.get_float("TEMPERATURE", 0.7)
debug_mode = env_manager.get_bool("DEBUG_MODE", False)
allowed_ips = env_manager.get_list("ALLOWED_IPS", default=["127.0.0.1"])

# すべての環境変数を辞書として取得（機密情報は除く）
all_vars = env_manager.get_all_as_dict()
print(all_vars)

# 環境変数情報の詳細表示（デバッグ用）
env_info = env_manager.describe_env_vars()
for category, vars in env_info.items():
    print(f"== {category.value} ==")
    for var in vars:
        print(f"  {var['key']}: {var['current_value']}")
```

### 環境変数の定義追加

新しい環境変数を追加するには、`env_manager.py`の`_load_env_definitions`メソッドに定義を追加します：

```python
self._add_definition(
    EnvVarDefinition(
        key="NEW_VAR_NAME",
        description="新しい環境変数の説明",
        category=EnvCategory.API,
        required=False,
        default="デフォルト値",
        validator=lambda v: v in ["値1", "値2", "値3"],  # オプション
        converter=int,  # オプション（文字列から他の型に変換）
        sensitive=False  # 機密情報かどうか
    )
)
```

### 例外処理

環境変数の取得時に発生する可能性のある例外を適切に処理することをお勧めします：

```python
from sikakumaru.app.infrastructure import get_env, EnvVarNotFoundError, EnvVarValidationError

try:
    api_key = get_env("API_KEY")
except EnvVarNotFoundError:
    print("必須環境変数APIキーが設定されていません")
    exit(1)
except EnvVarValidationError as e:
    print(f"環境変数の検証エラー: {e}")
    exit(1)
```

## 環境変数ファイル

`.env.example`ファイルには、設定可能なすべての環境変数のサンプルが含まれています。このファイルを`.env`としてコピーし、実際の値で更新して使用してください。

```bash
cp sikakumaru/.env.example sikakumaru/.env
# 環境変数の値を編集
```
