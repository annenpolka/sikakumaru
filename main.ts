import { defineCommand } from "./src/cli.ts";

// Learn more at https://docs.deno.com/runtime/manual/examples/module_metadata#concepts
if (import.meta.main) {
  try {
    const cmd = defineCommand();
    // .name("exam-generator") // 必要に応じて設定
    // .version("0.1.0")      // 必要に応じて設定
    // .description("資格試験問題を生成する CLI ツール") // 必要に応じて設定

    const { options, args } = await cmd.parse(Deno.args);

    // ここでパースされたオプション (options) を使って
    // アプリケーションの主処理を実装する
    // 例:
    console.log("Parsed options:", options);
    console.log("Remaining args:", args);

    // TODO: Implement main application logic using parsed options
    // e.g., callLLM, generatePrompt, writeFile etc.
  } catch (error) {
    // cliffy がエラー処理 (ヘルプ表示など) を行うので、
    // ここで特別な処理は不要な場合が多い
    // 必要であればエラーログなどを出力
    if (error instanceof Error && error.message.includes("Missing required")) {
      // 必須オプション欠落時のエラーは cliffy がハンドルするはずなので、
      // ここで console.error する必要はないかもしれない
    } else if (error instanceof Error) {
      console.error("An unexpected error occurred:", error.message);
      // Deno.exit(1); // エラーコードで終了させる場合
    } else {
      console.error("An unknown error occurred:", error);
      // Deno.exit(1);
    }
    // cliffy が exit するので、テスト以外では Deno.exit は不要なことが多い
  }
}
