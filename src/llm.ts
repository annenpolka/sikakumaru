import { HumanMessage } from "@langchain/core/messages";
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { loadSync } from "@std/dotenv"; // dotenv の loadSync をインポート

// .env ファイルから環境変数をロード (存在すれば)
// export: true を指定すると Deno.env に自動で設定される
// allowEmptyValues: true は空の値も許可する場合 (今回は不要そうだけど念のため)
// examplePath: null で .env.example のチェックを無効化
loadSync({ export: true, allowEmptyValues: true, examplePath: null });

/**
 * Gemini API に接続し、指定されたプロンプトに対する応答を取得します。
 * @param prompt LLM に送信するプロンプト文字列。
 * @returns LLM からの応答文字列。
 * @throws Error GEMINI_API_KEY 環境変数が設定されていない場合、または API 呼び出しに失敗した場合。
 */
export async function callLLM(prompt: string): Promise<string> {
  // loadSync({ export: true }) によって Deno.env に設定されているはず
  const apiKey = Deno.env.get("GEMINI_API_KEY");
  if (!apiKey) {
    // APIキーがない場合は明確なエラーを投げる
    // .env ファイルがない、またはキーが設定されていない可能性を示すメッセージに変更
    throw new Error(
      "Environment variable GEMINI_API_KEY is not set. Please ensure it's defined in your .env file or environment.",
    );
  }

  // Gemini モデルを初期化
  // model プロパティが正しいはず
  const model = new ChatGoogleGenerativeAI({
    apiKey: apiKey,
    model: "gemini-1.5-pro", // ドキュメントにあったモデル名に変更
    // temperature: 0.7, // 例: 応答の多様性を調整
    // maxOutputTokens: 1024, // 例: 最大出力トークン数を設定
  });

  try {
    // プロンプトを HumanMessage として送信し、応答 (BaseMessage) を取得
    const response = await model.invoke([
      new HumanMessage(prompt),
    ]);

    // 応答からテキストコンテンツを抽出
    // response.content は string または (string | object)[] の可能性がある
    if (typeof response.content === "string") {
      return response.content;
    } else if (Array.isArray(response.content)) {
      // マルチモーダル応答の場合、テキスト部分を探す
      const textPart = response.content.find((part) =>
        typeof part === "object" && part !== null && "type" in part &&
        part.type === "text"
      );
      // textPart が MessageContentText 型であることを確認してから text プロパティにアクセス
      if (
        textPart && typeof textPart === "object" && "text" in textPart &&
        typeof textPart.text === "string"
      ) {
        return textPart.text;
      }
      // 単純な文字列配列の場合 (あまりないはずだが念のため)
      const firstString = response.content.find((part) =>
        typeof part === "string"
      );
      if (typeof firstString === "string") {
        return firstString;
      }
    }

    // 予期しない応答形式の場合
    console.error("Unexpected LLM response format:", response);
    throw new Error(
      "Failed to extract text content from the LLM response. Unexpected format.",
    );
  } catch (error) {
    // API呼び出し中のエラーを捕捉し、より詳細な情報と共に再スロー
    console.error("Error calling LLM API:", error);
    const errorMessage = error instanceof Error ? error.message : String(error);
    // スタックトレースも含めるとデバッグに役立つかもしれないわね
    const stack = error instanceof Error ? `\nStack: ${error.stack}` : "";
    throw new Error(`LLM API call failed: ${errorMessage}${stack}`);
  }
}
