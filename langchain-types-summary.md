# LangChain 型定義調査サマリー (`@langchain/core@0.3.43`, `@langchain/openai@0.5.2`)

Deno キャッシュディレクトリ (`/Users/annenpolka/Library/Caches/deno/npm/registry.npmjs.org/`) 内のファイルを調査し、`@langchain/core@0.3.43` および `@langchain/openai@0.5.2` の主要な型定義を確認しました。

両パッケージともに、トップレベルの `.d.ts` ファイルは `dist` ディレクトリ内の実体ファイルを再エクスポートするエントリーポイントとして機能している構造が多く見られました。

以下に、確認できた主要な型定義とその概要をまとめます。

## @langchain/core@0.3.43

### Runnables (LCEL: LangChain Expression Language) (`dist/runnables/base.d.ts` など)

* **`Runnable`**: すべての実行可能コンポーネントの基底クラス。`invoke`, `stream`, `batch` などのメソッドを持つ。
* **`RunnableSequence`**: Runnable を直列に接続するクラス。
* **`RunnableMap` / `RunnableParallel`**: Runnable を並列に実行するクラス。
* **`RunnablePassthrough`**: 入力をそのまま、あるいは加工して後続に渡すクラス。
* **`RunnableConfig`**: Runnable の実行時設定（コールバック、タグなど）を管理する型。

### Language Models (`dist/language_models/base.d.ts`, `dist/language_models/chat_models.d.ts` など)

* **`BaseLanguageModel`**: LLM と Chat Model の共通基底クラス。
* **`BaseChatModel`**: Chat Model の基底クラス。`invoke`, `generate`, `bindTools`, `withStructuredOutput` などのメソッドを持つ。
* **`BaseLLM`**: テキスト補完型 LLM の基底クラス。
* **`BaseChatModelParams`, `BaseLLMParams`**: 各モデルの基本的なパラメータ。
* **`BaseChatModelCallOptions`, `BaseLLMCallOptions`**: モデル呼び出し時のオプション。

### Prompts (`dist/prompts/base.d.ts`, `dist/prompts/chat.d.ts` など)

* **`BasePromptTemplate`**: プロンプトテンプレートの基底クラス。`format`, `formatPromptValue` メソッドを持つ。
* **`ChatPromptTemplate`**: Chat Model 用のプロンプトテンプレート。`formatMessages` メソッドを持つ。
* **`PromptTemplate`**: 文字列ベースのプロンプトテンプレート。
* **`MessagesPlaceholder`**: チャット履歴などを挿入するためのプレースホルダー。

### Messages (`dist/messages/base.d.ts`, `dist/messages/ai.d.ts`, `dist/messages/human.d.ts` など)

* **`BaseMessage`**: すべてのメッセージタイプの基底クラス (`content`, `name`, `additional_kwargs` など)。
* **`AIMessage`, `HumanMessage`, `SystemMessage`, `ToolMessage`, `FunctionMessage`**: 各役割に応じたメッセージクラス。
* **`BaseMessageChunk`**: ストリーミング時のメッセージ断片を表す基底クラス。
* **`MessageContent`**: メッセージの内容を表す型 (文字列またはテキスト/画像URLオブジェクトの配列)。

### Outputs (`dist/outputs.d.ts` など)

* **`ChatResult`, `LLMResult`**: モデルからの生成結果全体を表す型。
* **`ChatGeneration`, `Generation`**: 個々の生成結果。
* **`ChatGenerationChunk`, `GenerationChunk`**: ストリーミング時の生成結果の断片。

### Tools (`dist/tools.d.ts` など)

* **`Tool`**: 関数の実行を抽象化するクラス。`name`, `description`, `schema` (zod スキーマ) を持つ。
* **`StructuredTool`**: より複雑な入出力スキーマを持つツールの基底クラス。

## @langchain/openai@0.5.2

### Chat Models (`dist/chat_models.d.ts`)

* **`ChatOpenAI`**: OpenAI の Chat Completion API (gpt-4, gpt-3.5-turbo など) を利用するためのクラス。`@langchain/core` の `BaseChatModel` を継承。
* **`ChatOpenAIFields`**: `ChatOpenAI` のコンストラクタ引数。`model`, `temperature`, `apiKey` など。
* **`ChatOpenAICallOptions`**: `ChatOpenAI` の呼び出し時オプション。`tools`, `tool_choice`, `response_format` など、OpenAI 固有のオプションを含む。

### LLMs (`dist/llms.d.ts`)

* **`OpenAI`**: OpenAI の Completion API (旧モデル) を利用するためのクラス。`@langchain/core` の `BaseLLM` を継承。
* **`OpenAIInput`**: `OpenAI` のコンストラクタ引数。

### Embeddings (`dist/embeddings.d.ts`)

* **`OpenAIEmbeddings`**: OpenAI の Embedding API を利用するためのクラス。`@langchain/core` の `Embeddings` を継承。
* **`OpenAIEmbeddingsParams`**: `OpenAIEmbeddings` のコンストラクタ引数。`model`, `dimensions`, `batchSize` など。

### Tools (`dist/tools/index.d.ts`, `dist/tools/dalle.js`)

* **`OpenAITool`**: OpenAI の Function Calling / Tool Calling に対応する Tool の型定義 (内部利用が主)。
* **`DallETool`**: DALL-E を利用するためのツールクラス (具体的な定義は `dalle.js` 内)。

### Utilities (`dist/utils/openai.js`, `dist/utils/prompts.js` など)

* OpenAI API との連携に必要な変換関数やヘルパー関数 (例: `messageToOpenAIRole`, `_convertMessagesToOpenAIParams`, `convertToolToOpenAIFunction`)。

これで、LangChain の Core と OpenAI パッケージの主要な型定義の概要は把握できたでしょう。
