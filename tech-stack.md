# しかくまるプロジェクト：技術スタック情報

このドキュメントには、しかくまるプロジェクトの技術スタック情報がまとめられています。`.clinerules`および`.cursorrules`から参照されます。

## プロジェクト基本情報

```json
{
  "projectName": "しかくまる",
  "description": "資格試験対策のための自動問題生成システム"
}
```

## プロジェクト固有のルール

```json
{
  "projectSpecificRules": {
    "apis": {
      "llm": {
        "implementation": "必ず抽象化レイヤーを通して利用する",
        "preferredProviders": ["未定"],
        "defaultParameters": {
          "temperature": 0.7,
          "maxTokens": 2000
        }
      },
      "search": {
        "implementation": "検索結果はキャッシュ機構を実装する",
        "preferredProviders": ["未定"]
      }
    },
    "security": {
      "credentials": "常に暗号化して扱う",
      "userInput": "必ず検証を行う"
    },
    "outputFormat": {
      "anki": {
        "validation": "厳密な検証を行う",
        "structure": {
          "front": "問題文",
          "back": "解答",
          "tags": ["資格名", "トピック", "難易度"]
        }
      }
    },
    "errorHandling": "詳細に実装する"
  }
}
```

## 技術スタック

```json
{
  "techStack": {
    "backend": "Python 3.11+",
    "pythonLibraries": {
      "web": "FastAPI 0.100+",
      "async": "asyncio, httpx",
      "llm": "langchain, openai",
      "search": "googlesearch-python",
      "validation": "pydantic v2",
      "testing": "pytest, hypothesis",
      "typeChecking": "mypy, pyright",
      "caching": "redis, diskcache",
      "security": "cryptography, python-jose"
    },
    "database": "SQLite/JSON",
    "testing": "pytest, hypothesis",
    "cicd": "GitHub Actions"
  }
}
```

## Python型注釈のルール

```json
{
  "pythonTyping": {
    "description": "Pythonでの型注釈の徹底",
    "principles": [
      "すべての関数に対して引数と戻り値の型注釈を必ず記述する",
      "mypy, Pylance, Pyrightなどの型チェッカーを利用する",
      "from __future__ import annotationsを使用して型注釈の前方参照を可能にする",
      "Optionalやジェネリック型など高度な型注釈を適切に使用する",
      "stub (.pyi) ファイルを必要に応じて作成する",
      "TypedDictやProtocolなど厳密な型定義を活用する"
    ]
  }
}
```

## コードパターン

```json
{
  "codePatterns": {
    "llmApiCall": {
      "description": "LLM APIを呼び出すパターン",
      "example": "async def call_llm(prompt: str, params: Optional[Dict[str, Any]] = None) -> str:\n    client = get_llm_client()\n    try:\n        return await client.complete(prompt, params or {})\n    except Exception as e:\n        logger.error(f\"LLM API error: {e}\")\n        raise LLMException(f\"API呼び出しエラー: {e}\")"
    },
    "ankiCardGeneration": {
      "description": "Ankiカード生成パターン",
      "example": "def generate_anki_card(question: str, answer: str, tags: List[str]) -> Dict[str, Any]:\n    card: Dict[str, Any] = {\n        \"front\": question,\n        \"back\": answer,\n        \"tags\": tags\n    }\n    validate_anki_card(card)\n    return card"
    },
    "errorHandling": {
      "description": "エラーハンドリングパターン",
      "example": "try:\n    result = process_data(input_data)\nexcept ValidationError as e:\n    logger.warning(f\"入力検証エラー: {e}\")\n    return {\"status\": \"error\", \"message\": str(e)}\nexcept Exception as e:\n    logger.error(f\"予期せぬエラー: {e}\", exc_info=True)\n    return {\"status\": \"error\", \"message\": \"システムエラーが発生しました\"}"
    },
    "typedFunction": {
      "description": "型注釈を徹底した関数定義パターン",
      "example": "from typing import Dict, List, Optional, TypedDict, Union, Any\nfrom dataclasses import dataclass\n\nclass QuestionMetadata(TypedDict):\n    difficulty: str\n    topics: List[str]\n    source: Optional[str]\n\n@dataclass\nclass Question:\n    text: str\n    answer: str\n    metadata: QuestionMetadata\n\ndef analyze_question(question: Question) -> Dict[str, Any]:\n    \"\"\"質問を分析し、関連情報を返す\n\n    Args:\n        question: 分析する質問オブジェクト\n\n    Returns:\n        分析結果を含む辞書\n    \"\"\"\n    result: Dict[str, Any] = {}\n    # 実装\n    return result"
    }
  }
}
```

## プロジェクト構造

```json
{
  "projectStructure": {
    "app": {
      "description": "メインアプリケーション",
      "modules": {
        "core": ["input_processor.py", "scope_extractor.py", "topic_analyzer.py", "question_generator.py", "quality_checker.py"],
        "llm": ["api_client.py", "analysis.py"],
        "search": ["api_client.py"],
        "output": ["anki_converter.py"]
      }
    },
    "tests": {
      "description": "テスト",
      "modules": ["test_core.py", "test_llm.py", "test_output.py"]
    }
  }
}