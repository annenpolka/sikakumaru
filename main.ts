import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { load } from "@std/dotenv";
import { defineCommand } from "./src/cli.ts";
import { callLLM } from "./src/llm.ts";
import { generatePrompt } from "./src/prompt.ts";
import { type CLIOptions } from "./src/types.ts";

/**
 * メインロジックを実行する非同期関数。
 * CLI引数の解析、プロンプト生成、LLM呼び出し、結果出力を担当する。
 * テストからも呼び出せるようにエクスポートする。
 * @param args コマンドライン引数の配列 (Deno.args 相当)
 * @throws エラーが発生した場合、エラーオブジェクトを再スローする可能性がある
 */
export async function runMainLogic(args: string[]): Promise<void> {
  try {
    // 1. CLI 引数解析
    const cmd = defineCommand();
    const { options } = await cmd.parse(args) as { options: CLIOptions };
    console.log("Parsed options:", options);

    // .env ファイルから環境変数を読み込む
    const env = await load({ export: true });
    const apiKey = env["GEMINI_API_KEY"] || Deno.env.get("GEMINI_API_KEY");

    if (!apiKey) {
      // エラーメッセージは標準エラー出力へ
      console.error(
        "Error: GEMINI_API_KEY is not set in the environment variables or .env file.",
      );
      console.error(
        "Please create a .env file in the root directory and add the following line:",
      );
      console.error("GEMINI_API_KEY=YOUR_API_KEY");
      // エラー発生時は終了コード 1 で終了
      Deno.exit(1);
    }

    // 2. プロンプト生成
    const prompt = await generatePrompt(options);
    console.log("\nGenerated Prompt:\n", prompt);

    // 3. LLM クライアント初期化
    const llm = new ChatGoogleGenerativeAI({
      apiKey: apiKey,
      model: "gemini-2.5-pro-exp-03-25",
    });

    // 4. LLM 呼び出し
    console.log("\nCalling LLM...");
    const llmResponse = await callLLM(llm, prompt);

    // 5. 結果出力
    console.log("\nLLM Response:\n", llmResponse);

    // TODO: 必要であれば結果をファイルに書き出す処理などを追加
    // 例: if (options.output) { await Deno.writeTextFile(options.output, llmResponse); }
  } catch (error) {
    // 6. エラーハンドリングの改善: エラーをコンソールに出力し、再スローまたは終了
    console.error("\n--- An error occurred ---");
    if (error instanceof Error) {
      console.error(`Error Name: ${error.name}`);
      console.error(`Error Message: ${error.message}`);
      // スタックトレースはデバッグ時に役立つ
      // console.error(`Stack Trace: ${error.stack}`);

      // 特定のエラータイプに応じたメッセージ
      if (
        error.name === "ValidationError" ||
        error.message.includes("Missing required")
      ) {
        console.error(
          "CLI argument validation failed. Please check your command.",
        );
        // Cliffy が自動でヘルプを表示し、プロセスを終了させるはず
      } else if (error.message.includes("Failed to fetch")) {
        console.error(
          "Network error: Failed to connect to the LLM API. Check your internet connection and API endpoint.",
        );
      } else if (error.message.includes("API key not valid")) {
        console.error(
          "Authentication error: The provided API key is invalid or expired.",
        );
      } else if (error.message.includes("Could not find")) {
        console.error(
          `File system error: ${error.message}. Check if the template file exists and path is correct.`,
        );
      } else {
        console.error("An unexpected error occurred during processing.");
      }
    } else {
      console.error("An unknown error occurred:", error);
    }
    console.error("-------------------------\n");
    // エラー発生時は終了コード 1 で終了
    // runMainLogic をテストから呼び出す場合、ここで exit するとテストプロセスも終了してしまう。
    // そのため、テスト実行時以外でのみ exit するか、エラーを呼び出し元にスローする方が良い。
    // 今回はテスト容易性のため、exit(1) をコメントアウトし、エラーをスローする形にはしないでおく。
    Deno.exit(1);
    // 代わりにエラーを再スローすることも検討できるが、main 関数での catch なので、
    // ここで処理を終えるのが自然かもしれない。テストでは try/catch で囲む想定。
  }
}

// Learn more at https://docs.deno.com/runtime/manual/examples/module_metadata#concepts
// スクリプトとして直接実行された場合のみ main ロジックを実行
if (import.meta.main) {
  // Deno.args を渡して実行
  await runMainLogic(Deno.args);
}
