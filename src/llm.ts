import { BaseMessage, HumanMessage } from "@langchain/core/messages";
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
  try {
    const response = await client.invoke([
      new HumanMessage(prompt),
    ]);
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
