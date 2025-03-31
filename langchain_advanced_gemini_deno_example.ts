// langchain_advanced_gemini_deno_example.ts

// Deno標準ライブラリからdotenvをインポートして環境変数を読み込む
import "jsr:@std/dotenv/load";
// LangChainのコアモジュールとGoogle GenAIモジュールをnpm経由でインポート
import { HumanMessage, ToolMessage } from "npm:@langchain/core/messages";
import { DynamicStructuredTool } from "npm:@langchain/core/tools";
import { ChatGoogleGenerativeAI } from "npm:@langchain/google-genai";
import { z } from "npm:zod"; // zodをインポートしてスキーマ定義
// ToolMessage の content 型定義のためにインポート (必要に応じて)
// CallbackManagerForToolRun と RunnableConfig の型をインポート (func の型定義のため)
import type { CallbackManagerForToolRun } from "npm:@langchain/core/callbacks/manager";
import type { RunnableConfig } from "npm:@langchain/core/runnables";

// 環境変数からAPIキーを取得
const apiKey = Deno.env.get("GOOGLE_API_KEY");

if (!apiKey) {
  console.error(
    "エラー: GOOGLE_API_KEY が .env ファイルに設定されていません。",
  );
  Deno.exit(1);
}

// --- ツールのスキーマ定義 ---
// 循環参照を避けるためにスキーマを先に定義するわ
const addToolSchema = z.object({
  a: z.number().describe("最初の数値"),
  b: z.number().describe("二番目の数値"),
});

// --- ツールの定義 ---
// 簡単な足し算を行うツールを定義するわ
const addTool = new DynamicStructuredTool({
  name: "add",
  description: "二つの数値を加算します。",
  // 先に定義したスキーマを参照
  schema: addToolSchema,
  // ツールの実処理
  // async を削除し、戻り値を Promise.resolve でラップする
  func: (
    args: z.infer<typeof addToolSchema>,
    _runManager?: CallbackManagerForToolRun, // 未使用でも型定義に合わせる
    _config?: RunnableConfig, // 未使用でも型定義に合わせる
  ): Promise<string> => { // 戻り値の型を明示的に Promise<string> に
    console.log(`ツール実行: add(${args.a}, ${args.b})`);
    const result = args.a + args.b;
    // ツール実行の結果を文字列で返し、Promise.resolveでラップ
    return Promise.resolve(`計算結果: ${result}`);
  },
});

// --- モデルの初期化 ---
// Geminiモデルを初期化
const model = new ChatGoogleGenerativeAI({
  apiKey: apiKey,
  model: "gemini-1.5-flash", // または "gemini-pro" など、利用可能なモデルを指定
  temperature: 0.7,
});

// --- モデルとツールのバインド ---
// 作成したツールをモデルにバインドするわ
const modelWithTools = model.bindTools([addTool]);

// --- メイン処理 ---
async function main() {
  console.log("Geminiモデル (Tool Calling) のサンプルを開始します...");

  try {
    // ユーザーからのメッセージ (ツール利用を促す内容)
    const userMessage = new HumanMessage("5 と 8 を足すといくつになりますか？");
    console.log(`\nユーザー: ${userMessage.content}`);

    // 1回目のモデル呼び出し (ツール呼び出しを期待)
    const initialResponse = await modelWithTools.invoke([userMessage]);
    console.log("\nモデル (1回目):", initialResponse);

    // 応答にツール呼び出しが含まれているか確認
    if (
      initialResponse.tool_calls && initialResponse.tool_calls.length > 0
    ) {
      console.log("\nツール呼び出しを検出しました。");
      const toolMessages: ToolMessage[] = [];

      // 複数のツール呼び出しに対応 (await を使用)
      for (const toolCall of initialResponse.tool_calls) {
        const toolName = toolCall.name;
        const toolArgs = toolCall.args;

        console.log(`  ツール名: ${toolName}`);
        console.log(`  引数: ${JSON.stringify(toolArgs)}`);

        // 対応するツールを探して実行
        if (toolName === addTool.name) {
          try {
            // zod スキーマで引数を安全にパース・検証する
            const parsedArgs = addToolSchema.safeParse(toolArgs);
            if (!parsedArgs.success) {
              throw new Error(
                `ツール '${toolName}' の引数が不正です: ${parsedArgs.error.message}`,
              );
            }
            // 検証済みの引数でツール関数を呼び出す (await を使用)
            // func は Promise<string> を返すので await する
            const toolResult: string = await addTool.func(parsedArgs.data);
            console.log(`  ツール実行結果: ${toolResult}`);
            // ツール実行結果をToolMessageとして保存
            toolMessages.push(
              new ToolMessage({
                content: toolResult, // toolResult は string
                tool_call_id: toolCall.id ?? crypto.randomUUID(),
              }),
            );
          } catch (toolError) {
            // エラーが Error インスタンスか確認する型ガード
            const errorMessage = toolError instanceof Error
              ? toolError.message
              : String(toolError);
            console.error(
              `  ツール '${toolName}' の実行中にエラーが発生しました:`,
              errorMessage,
            );
            // エラーが発生した場合も、その情報をToolMessageとして記録できる
            toolMessages.push(
              new ToolMessage({
                content:
                  `ツール '${toolName}' の実行中にエラー: ${errorMessage}`, // ここも string
                tool_call_id: toolCall.id ?? crypto.randomUUID(),
              }),
            );
          }
        } else {
          console.warn(`  未定義のツール '${toolName}' が呼び出されました。`);
          // 未知のツール呼び出しに対するメッセージ
          toolMessages.push(
            new ToolMessage({
              content: `ツール '${toolName}' は定義されていません。`,
              tool_call_id: toolCall.id ?? crypto.randomUUID(),
            }),
          );
        }
      }

      // ツール実行結果を含めて再度モデルを呼び出す
      console.log("\nツール実行結果をモデルに渡して再度呼び出します...");
      const finalResponse = await modelWithTools.invoke([
        userMessage, // 元のユーザーメッセージ
        initialResponse, // 最初のモデル応答 (ツール呼び出し指示を含むAIMessage)
        ...toolMessages, // ツール実行結果のToolMessage群
      ]);

      console.log("\nモデル (最終応答):", finalResponse);
      console.log(`\n最終的な回答: ${finalResponse.content}`);
    } else {
      // ツール呼び出しがなかった場合
      console.log("\nツール呼び出しは行われませんでした。");
      console.log(`\nモデルの回答: ${initialResponse.content}`);
    }
  } catch (error) {
    // メイン処理全体のエラーハンドリング
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error("\n処理中に予期せぬエラーが発生しました:", errorMessage);
    if (error instanceof Error && error.stack) {
      console.error("スタックトレース:", error.stack);
    }
  } finally {
    console.log("\nサンプルを終了します。");
  }
}

// メイン処理を実行
main();
