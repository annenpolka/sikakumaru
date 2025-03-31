// langchain_gemini_deno_example.ts

// Deno標準の dotenv モジュールを JSR specifier でインポートするわ
import { load } from "jsr:@std/dotenv@^0.224.0";
// LangChainのコアモジュールとGoogle GenAI連携モジュールを npm specifier でインポートするわ
import { HumanMessage } from "npm:@langchain/core/messages";
import { ChatGoogleGenerativeAI } from "npm:@langchain/google-genai";

// .env ファイルから環境変数を非同期で読み込むのよ
// スクリプトと同じディレクトリに .env ファイルが存在することを期待しているわ
const env = await load();
const googleApiKey = env["GOOGLE_API_KEY"];

// APIキーが設定されていない場合はエラーメッセージを表示して終了するのよ
if (!googleApiKey) {
  console.error(
    "エラー: .env ファイルに 'GOOGLE_API_KEY' が設定されていないか、.env ファイルが存在しませんわ。",
  );
  Deno.exit(1);
}

// ChatGoogleGenerativeAI インスタンスを初期化するの
// モデルは 'gemini-1.5-pro' を指定してみましょうか
const model = new ChatGoogleGenerativeAI({
  apiKey: googleApiKey,
  model: "gemini-2.5-pro-exp-03-25",
  temperature: 0.7, // 少し創造的な応答を期待してみるわ
  maxOutputTokens: 2048, // 必要に応じて調整してちょうだい
});

// 簡単な質問を HumanMessage として作成するわ
const question = new HumanMessage(
  "LangChain.jsについて日本語で簡単に教えてちょうだい。",
);

// モデルを呼び出して結果を取得・表示するのよ
try {
  console.log("Geminiに質問中...");
  const response = await model.invoke([question]);

  console.log("\n--- Geminiからの応答 ---");
  console.log(response.content);
  console.log("------------------------\n");

  // トークン使用量も表示してみましょうか
  if (response.usage_metadata) {
    console.log("トークン使用量:");
    console.log(`  入力トークン: ${response.usage_metadata.input_tokens}`);
    console.log(`  出力トークン: ${response.usage_metadata.output_tokens}`);
    console.log(`  合計トークン: ${response.usage_metadata.total_tokens}`);
  }
} catch (error) {
  console.error("\nエラーが発生しましたわ:", error);
  // エラーオブジェクトの詳細も表示してみるわ
  if (error instanceof Error && error.cause) {
    console.error("エラー原因:", error.cause);
  }
  Deno.exit(1);
}
