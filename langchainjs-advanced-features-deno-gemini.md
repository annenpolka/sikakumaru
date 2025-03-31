# LangChain.js 高度機能調査: Deno & Gemini 連携

LangChain.js の高度な機能について、Deno 環境での利用可能性と Gemini (`@langchain/google-genai`) との連携を中心に調査した結果を以下に示すわ。

**調査結果サマリ**:

多くの LangChain.js コア機能（特に `@langchain/core` に含まれるもの）は、Deno の `npm:` specifier を介して利用可能よ。`@langchain/google-genai` も同様に Deno で動作する可能性が高いわ。ただし、一部の機能、特にファイルシステムや特定の Node.js API に強く依存するものは、Deno 環境で追加の設定や代替策が必要になるかもしれないわね。

**Deno/Gemini で利用可能な LangChain.js 高度機能リスト**:

1. **Tool Calling / Function Calling**:
    * **概要**: LLM が外部ツール（関数）を呼び出す必要があると判断し、そのための引数を生成する機能よ。Gemini は Function Calling をネイティブでサポートしており、`@langchain/google-genai` はこれを LangChain の Tool Calling インターフェースにマッピングしているわ。
    * **Deno/Gemini**: `@langchain/google-genai` の `ChatGoogleGenerativeAI` モデルで `bindTools` や `bindFunctions` メソッドを使って利用できるでしょう。Deno 環境でも問題なく動作するはずよ。
    * **コードスニペット (概念)**:

        ```typescript
        import { ChatGoogleGenerativeAI } from "npm:@langchain/google-genai";
        import { z } from "npm:zod";
        import { DynamicStructuredTool } from "npm:@langchain/core/tools";

        const model = new ChatGoogleGenerativeAI({ modelName: "gemini-pro" }); // APIキー設定は別途必要

        const getCurrentWeatherTool = new DynamicStructuredTool({
          name: "get_current_weather",
          description: "指定された場所の現在の天気を取得します。",
          schema: z.object({
            location: z.string().describe("天気情報を取得したい都市名 (例: 東京)"),
          }),
          func: async ({ location }) => {
            // ここで実際の天気APIを呼び出す想定
            console.log(`Fetching weather for ${location}...`);
            return `現在の${location}の天気は晴れです。`;
          },
        });

        const modelWithTools = model.bindTools([getCurrentWeatherTool]);

        // const result = await modelWithTools.invoke("東京の天気は？");
        // result.tool_calls を確認してツールを実行し、結果を再度モデルに渡す流れになるわね。
        ```

2. **Structured Output (Output Parsers)**:
    * **概要**: LLM の出力を特定の形式（JSON、Zod スキーマなど）に整形・パースする機能よ。`@langchain/core/output_parsers` に様々なパーサーが用意されているわ。
    * **Deno/Gemini**: Gemini モデル自体も JSON モードをサポートしている場合があるけれど、LangChain の Output Parser を使うことで、より複雑なスキーマへのパースやエラーハンドリングが容易になるわ。`StructuredOutputParser` や `ZodSchemaParser` などが Deno でも利用可能でしょう。
    * **コードスニペット (概念)**:

        ```typescript
        import { ChatGoogleGenerativeAI } from "npm:@langchain/google-genai";
        import { StructuredOutputParser } from "npm:@langchain/core/output_parsers";
        import { PromptTemplate } from "npm:@langchain/core/prompts";
        import { z } from "npm:zod";

        const model = new ChatGoogleGenerativeAI({ modelName: "gemini-pro" });

        const parser = StructuredOutputParser.fromZodSchema(
          z.object({
            actor: z.string().describe("指定された映画の主演俳優"),
            director: z.string().describe("指定された映画の監督"),
          })
        );

        const prompt = PromptTemplate.fromTemplate(
          "映画「{movie}」の主演俳優と監督を教えて。\n{format_instructions}"
        );

        const chain = prompt.pipe(model).pipe(parser);
        // const result = await chain.invoke({ movie: "君の名は。", format_instructions: parser.getFormatInstructions() });
        // result は { actor: "...", director: "..." } のようなオブジェクトになるはずよ。
        ```

3. **Chaining (LangChain Expression Language - LCEL)**:
    * **概要**: プロンプト、モデル、パーサー、リトリーバーなどをパイプ (`|`) で繋ぎ、処理の流れを宣言的に記述する LangChain のコア機能よ。
    * **Deno/Gemini**: LCEL は `@langchain/core` の中心的な機能であり、Deno 環境でも問題なく動作するわ。Gemini モデルを含む様々なコンポーネントを柔軟に組み合わせられるでしょう。
    * **コードスニペット (概念)**: 上記 Structured Output の例が LCEL の基本的な使い方を示しているわ (`prompt.pipe(model).pipe(parser)`)。より複雑なチェーンも同様に構築可能よ。

4. **Safety Settings**:
    * **概要**: Gemini API が提供するセーフティ設定（有害コンテンツのブロック閾値など）を LangChain 経由で制御する機能よ。
    * **Deno/Gemini**: `@langchain/google-genai` の `ChatGoogleGenerativeAI` のコンストラクタや `withConfig` メソッドで `safetySettings` を指定できるはずよ。Deno 環境でも利用可能でしょう。
    * **コードスニペット (概念)**:

        ```typescript
        import { ChatGoogleGenerativeAI } from "npm:@langchain/google-genai";
        import { HarmBlockThreshold, HarmCategory } from "npm:@google/generative-ai";

        const model = new ChatGoogleGenerativeAI({
          modelName: "gemini-pro",
          safetySettings: [
            {
              category: HarmCategory.HARM_CATEGORY_HATE_SPEECH,
              threshold: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            },
            // 他のカテゴリ設定...
          ],
        });

        // または .withConfig() で
        // const safeModel = model.withConfig({
        //   safetySettings: [...]
        // });
        ```

5. **Retrieval (RAG - Retrieval-Augmented Generation)**:
    * **概要**: 外部ドキュメント（テキストファイル、PDF、Web ページなど）をベクトル化して保存し、ユーザーの質問に関連する情報を検索して、それをコンテキストとして LLM に与えることで、より正確で最新の情報に基づいた回答を生成する技術よ。
    * **Deno/Gemini**: `@langchain/community` や他のインテグレーションパッケージに含まれる Document Loaders, Text Splitters, Vector Stores, Retrievers を組み合わせる必要があるわ。Deno で利用可能な Vector Store (例: インメモリ、または Deno からアクセス可能な DB ベースのもの) を選ぶ必要があるわね。`@langchain/google-genai` の Embeddings モデル (`GoogleGenerativeAIEmbeddings`) も Deno で利用できるでしょう。
    * **コードスニペット (概念 - インメモリ例)**:

        ```typescript
        import { ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings } from "npm:@langchain/google-genai";
        import { MemoryVectorStore } from "npm:langchain/vectorstores/memory";
        import { PromptTemplate } from "npm:@langchain/core/prompts";
        import { RunnableSequence } from "npm:@langchain/core/runnables";
        import { StringOutputParser } from "npm:@langchain/core/output_parsers";
        import { Document } from "npm:@langchain/core/documents";

        const model = new ChatGoogleGenerativeAI({ modelName: "gemini-pro" });
        const embeddings = new GoogleGenerativeAIEmbeddings(); // APIキー設定は別途必要

        // 1. ドキュメント準備 (実際は Loader や Splitter を使う)
        const docs = [
          new Document({ pageContent: "猫は可愛い動物です。" }),
          new Document({ pageContent: "犬は忠実な動物です。" }),
        ];

        // 2. Vector Store 作成
        const vectorStore = await MemoryVectorStore.fromDocuments(docs, embeddings);
        const retriever = vectorStore.asRetriever();

        // 3. プロンプトテンプレート
        const template = `以下のコンテキスト情報のみを使って質問に答えてください:
        {context}

        質問: {question}`;
        const prompt = PromptTemplate.fromTemplate(template);

        // 4. RAG チェーン作成 (LCEL)
        const ragChain = RunnableSequence.from([
          {
            context: retriever.pipe((docs) => docs.map(d => d.pageContent).join("\n")),
            question: (input) => input.question,
          },
          prompt,
          model,
          new StringOutputParser(),
        ]);

        // const result = await ragChain.invoke({ question: "猫について教えて" });
        // result は "猫は可愛い動物です。" のような回答になるはずよ。
        ```

6. **Agents**:
    * **概要**: LLM を推論エンジンとして、ツールを使いながら自律的にタスクを遂行する仕組みよ。Tool Calling を基盤とし、思考プロセス（ReAct, Plan-and-Execute など）を実装しているわ。
    * **Deno/Gemini**: LangChain の Agent Executor (`langchain/agents`) や関連ツールは Deno でも利用可能でしょう。Gemini の Tool Calling 機能と組み合わせることで、強力なエージェントを構築できる可能性があるわね。ただし、Agent の実装は複雑になりがちで、依存関係も増える傾向にあるから注意が必要よ。
    * **コードスニペット (概念)**: Agent の実装は Tool Calling の応用形であり、特定の Agent タイプ (例: `createReactAgent`) や Executor を使うことになるわ。上記 Tool Calling のスニペットを発展させる形になるでしょう。

7. **Memory**:
    * **概要**: 会話履歴を保持し、それを LLM のコンテキストに含めることで、文脈を理解した対話を実現する機能よ。`BufferMemory`, `ConversationSummaryMemory` など様々な種類があるわ。
    * **Deno/Gemini**: `@langchain/core/memory` や `langchain/memory` の基本的な Memory クラスは Deno でも利用可能でしょう。LCEL と組み合わせることで、会話履歴をチェーンに組み込むことができるわ。
    * **コードスニペット (概念)**:

        ```typescript
        import { ChatGoogleGenerativeAI } from "npm:@langchain/google-genai";
        import { ConversationChain } from "npm:langchain/chains";
        import { BufferMemory } from "npm:langchain/memory";

        const model = new ChatGoogleGenerativeAI({ modelName: "gemini-pro" });
        const memory = new BufferMemory();
        const chain = new ConversationChain({ llm: model, memory: memory });

        // const res1 = await chain.invoke({ input: "私の名前はルーよ。" });
        // console.log(res1.response);
        // const res2 = await chain.invoke({ input: "私の名前は何だったかしら？" });
        // console.log(res2.response); // => "あなたの名前はルーです。" のようになるはず
        ```

8. **Streaming**:
    * **概要**: LLM の生成結果をトークンごとにリアルタイムで受け取る機能よ。ユーザー体験の向上に繋がるわ。
    * **Deno/Gemini**: `@langchain/google-genai` の `stream` メソッドや、LCEL で `.stream()` を呼び出すことで実現できるわ。Deno の非同期イテレータと相性が良いでしょう。
    * **コードスニペット (概念)**:

        ```typescript
        import { ChatGoogleGenerativeAI } from "npm:@langchain/google-genai";

        const model = new ChatGoogleGenerativeAI({ modelName: "gemini-pro", streaming: true });

        const stream = await model.stream("日本の首都について長い物語を書いて。");

        for await (const chunk of stream) {
          console.log(chunk.content); // トークンが逐次出力される
        }

        // LCELの場合
        // const stream = await chain.stream({ input: "..." });
        // for await (const chunk of stream) { ... }
        ```

9. **LangGraph.js**:
    * **概要**: LangChain の機能を拡張し、より複雑な、ループや条件分岐を含むエージェントやマルチエージェントシステムをグラフ構造で構築するためのライブラリよ。LCEL の上に構築されているわ。
    * **Deno/Gemini**: LangGraph.js (`@langchain/langgraph`) も `npm:` specifier 経由で Deno から利用できる可能性があるわ。状態管理やノード間の遷移を定義することで、高度な LLM アプリケーションを構築できるでしょう。Gemini モデルをグラフ内のノードとして組み込むことができるはずよ。
    * **コードスニペット (概念)**: LangGraph のコードは状態マシンやグラフ定義を含むため、やや複雑になるわ。基本的な考え方は、状態 (State) を定義し、各処理ステップをノード (Node) として定義し、それらの間の遷移 (Edge) を定義することよ。

**Deno 環境での注意点**:

* **`npm:` specifier**: Deno で LangChain.js を利用するには、`npm:` specifier (例: `import { ... } from "npm:@langchain/core";`) を使うことになるわ。これにより、Node.js 向けに書かれたパッケージを Deno ランタイムで利用できるの。
* **Node.js 互換性**: Deno の Node.js 互換レイヤーは進化しているけれど、まだ完全ではないわ。特に、ネイティブ Node.js モジュール (例: `fs`, `path` の一部機能) や特定の C++ アドオンに依存するパッケージは問題を起こす可能性があるわね。LangChain の一部のインテグレーション (特定の Document Loader や Vector Store) がこれに該当する可能性があるから、個別に確認が必要よ。
* **環境変数**: API キーなどの設定は、Deno の標準的な方法 (`Deno.env.get("API_KEY")`) で環境変数から読み込むのが一般的でしょう。

**結論**:

LangChain.js の主要な高度機能の多くは、Deno 環境で `@langchain/google-genai` と連携して利用可能と見てよさそうね。特に LCEL を中心としたコンポーネントの組み合わせ (Tool Calling, Structured Output, RAG, Memory, Streaming) は強力な基盤となるでしょう。LangGraph.js も、より複雑なフローを構築する上で有望な選択肢よ。ただし、特定のインテグレーションや Node.js 固有の機能への依存については、個別の検証が必要になる場面もあると心に留めておくべきね。
