// ax_gemini_deno_example.ts

// Deno標準の dotenv モジュールを JSR specifier でインポートするわ
import { load } from "jsr:@std/dotenv@^0.224.0";
// @ax-llm/ax ライブラリを npm specifier でインポートするわ
// AxGen と AxAIGoogleGeminiModel もインポート (Enum は比較のため残しておくわ)
import { AxAI, AxGen } from "npm:@ax-llm/ax";

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

// AxAI インスタンスを初期化し、GeminiモデルとAPIキーを設定するの
// config は削除し、シンプルな初期化にするわ
const ai = new AxAI({
  name: "google-gemini", // プロバイダー名を指定
  apiKey: googleApiKey,
  // モデル指定は削除。デフォルト (gemini-pro) が使われるわ
});

// AxGen を使ってプログラムを作成するわ
const signature = "question: string -> answer: string"; // 簡単な質問応答シグネチャ
const gen = new AxGen(signature); // AxGen を使用

// 簡単な質問
const question = "日本の首都は？";

// プログラムを実行して結果を取得するのよ
try {
  console.log(`質問: "${question}"`);
  // forward メソッドの第三引数を削除し、モデル指定を行わない
  const result = await gen.forward(
    ai,
    { question } as any, // 第二引数の型エラーは any で回避
    // 第三引数のモデル指定は削除
  );
  console.log("Geminiからの応答:");
  // 結果オブジェクトから answer プロパティを取得
  console.log(result.answer);
} catch (error) {
  console.error("エラーが発生しましたわ:", error);
  Deno.exit(1);
}
