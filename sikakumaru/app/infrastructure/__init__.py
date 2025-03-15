"""
インフラストラクチャパッケージ

このパッケージには、アプリケーションのインフラストラクチャ層のコンポーネントが含まれています。
- 環境変数管理
- データベース接続
- 外部APIクライアント
- ファイルシステム操作
- キャッシュ管理
など
"""

from sikakumaru.app.infrastructure.env_manager import (
    AppEnvVars,
    EnvVarNotFoundError,
    EnvVarValidationError,
    LLMEnvVars,
    env_manager,
    get_env,
    load_env_file,
    validate_env,
)

# 環境変数ファイルの自動ロード
load_env_file()
