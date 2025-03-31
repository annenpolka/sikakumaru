import { BaseMessage, HumanMessage } from "@langchain/core/messages";
// ChatGoogleGenerativeAI は型情報としてのみ必要になる可能性がある
// import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
// dotenv のインポートは削除
// import { loadSync } from "@std/dotenv";

// dotenv のロード処理は削除
// loadSync({ export: true, allowEmptyValues: true, examplePath: null });

// テストコードで定義したインターフェースと合わせる
// もしくは ChatGoogleGenerativeAI の公開インターフェースに合わせる
// ここでは、テストで使った MockLLMClient と同様の構造を持つインターフェースを定義する
// より汎用的にするなら BaseChatModel を継承した型にするのが良いかもしれない
interface LLMClient {
  invoke(messages: BaseMessage[]): Promise<BaseMessage>;
}

/**
 * 指定された LLM クライアントを使用して、プロンプトに対する応答を取得します。
 * @param client LLM クライアントのインスタンス (invoke メソッドを持つオブジェクト)。
 * @param prompt LLM に送信するプロンプト文字列。
 * @returns LLM からの応答文字列。
 * @throws Error API 呼び出しに失敗した場合、または応答からテキストを抽出できなかった場合。
 */
export async function callLLM(
  client: LLMClient, // 依存性を注入
  prompt: string,
): Promise<string> {
  // APIキーのチェックは呼び出し元の責務になるため削除
  // const apiKey = Deno.env.get("GEMINI_API_KEY");
  // if (!apiKey) {
  //   throw new Error(
  //     "Environment variable GEMINI_API_KEY is not set. Please ensure it's defined in your .env file or environment.",
  //   );
  // }

  // モデルの初期化も呼び出し元で行うため削除
  // const model = new ChatGoogleGenerativeAI({
  //   apiKey: apiKey,
  //   model: "gemini-1.5-pro",
  //   // temperature: 0.7,
  //   // maxOutputTokens: 1024,
  // });

  try {
    // 注入されたクライアントの invoke メソッドを使用
    const response = await client.invoke([
      new HumanMessage(prompt),
    ]);

    // 応答からテキストコンテンツを抽出 (このロジックは変更なし)
    if (typeof response.content === "string") {
      return response.content;
    } else if (Array.isArray(response.content)) {
      const textPart = response.content.find((part) =>
        typeof part === "object" && part !== null && "type" in part &&
        part.type === "text"
      );
      if (
        textPart && typeof textPart === "object" && "text" in textPart &&
        typeof textPart.text === "string"
      ) {
        return textPart.text;
      }
      const firstString = response.content.find((part) =>
        typeof part === "string"
      );
      if (typeof firstString === "string") {
        return firstString;
      }
    }

    console.error("Unexpected LLM response format:", response);
    throw new Error(
      "Failed to extract text content from the LLM response. Unexpected format.",
    );
  } catch (error) {
    console.error("Error calling LLM API:", error);
    const errorMessage = error instanceof Error ? error.message : String(error);
    const stack = error instanceof Error ? `\nStack: ${error.stack}` : "";
    throw new Error(`LLM API call failed: ${errorMessage}${stack}`);
  }
}
