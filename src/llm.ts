import { BaseMessage, HumanMessage } from "@langchain/core/messages";
// StructuredOutputParser は .withStructuredOutput() で内部的に使われるため、直接のインポートは不要になる場合がある
// import { StructuredOutputParser } from "@langchain/core/output_parsers";
import type { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { z } from "zod";
import type { ExamQuestionSet } from "./types.ts";

// 既存の LLMClient インターフェース (変更なし)
interface LLMClient {
  invoke(messages: BaseMessage[]): Promise<BaseMessage>;
}

/**
 * 指定された LLM クライアントを使用して、プロンプトに対する応答を **文字列** として取得します。
 * (既存の callLLM 関数 - 変更なし)
 */
export async function callLLM(
  client: LLMClient,
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
    console.error("Unexpected LLM response format in callLLM:", response);
    throw new Error(
      "Failed to extract text content from the LLM response in callLLM. Unexpected format.",
    );
  } catch (error) {
    console.error("Error calling LLM API in callLLM:", error);
    let errorMessage = "An unknown error occurred in callLLM";
    let stack = "";
    if (error instanceof Error) {
      errorMessage = error.message;
      stack = error.stack ? `\nStack: ${error.stack}` : "";
    }
    throw new Error(`LLM API call failed in callLLM: ${errorMessage}${stack}`);
  }
}

// --- JSON 処理関連の定義 ---

/**
 * 試験問題の選択肢に対応する Zod スキーマ
 */
const examOptionSchema = z.object({
  letter: z.string().describe("選択肢の記号 (例: A, B, C)"),
  text: z.string().describe("選択肢のテキスト"),
});

/**
 * 一つの試験問題に対応する Zod スキーマ
 */
const examQuestionSchema = z.object({
  // 修正: .positive() を削除
  questionNumber: z.number().int().describe("問題番号"),
  questionText: z.string().describe("問題文またはシナリオ"),
  options: z.array(examOptionSchema).describe("選択肢のリスト"),
  correctAnswer: z.string().describe("正解の選択肢記号 (例: 'A', 'B,C')"),
  explanation: z.string().describe("詳細な解説"),
  reference: z.string().optional().describe("参考文献 (任意)"),
});

/**
 * 試験問題セット全体に対応する Zod スキーマ (ルート)
 */
const examQuestionSetSchema = z.array(examQuestionSchema);

/**
 * 指定された Gemini クライアントを使用して、プロンプトに対する応答を
 * **JSON (ExamQuestionSet)** として取得し、パースします。
 * LangChain の `.withStructuredOutput()` メソッドを利用します。
 *
 * @param client ChatGoogleGenerativeAI のインスタンス。JSONモード設定は不要。
 * @param prompt LLM に送信するプロンプト文字列。フォーマット指示は不要 (内部で処理される)。
 * @returns パースされた試験問題セット (ExamQuestionSet)。
 * @throws Error API 呼び出し、JSON パース、またはスキーマ検証に失敗した場合。
 */
export async function callLLMForJson(
  client: ChatGoogleGenerativeAI, // 具体的な型を指定
  prompt: string,
): Promise<ExamQuestionSet> {
  try {
    // .withStructuredOutput() を使用して JSON モードとスキーマを指定
    const modelWithStructuredOutput = client.withStructuredOutput(
      examQuestionSetSchema,
      {
        name: "exam_question_set_formatter", // ツール名を指定 (必須)
        // description: "Formats the output as a set of exam questions." // 必要に応じて説明を追加
      },
    );

    // 構造化出力モデルを呼び出し
    const response = await modelWithStructuredOutput.invoke([
      new HumanMessage(prompt),
    ]);

    // response は直接パース済みの ExamQuestionSet 型になるはず
    // Zod スキーマでの検証は .withStructuredOutput() 内で行われる
    // 必要であれば、ここで追加の検証を行うことも可能
    if (!Array.isArray(response)) {
      console.error(
        "Unexpected response type from withStructuredOutput:",
        response,
      );
      throw new Error(
        "Expected an array (ExamQuestionSet) but received a different type.",
      );
    }

    // 型が ExamQuestionSet であることを確認 (念のため)
    // zod.safeParse は不要 (既に内部で検証されているため)
    return response as ExamQuestionSet;
  } catch (error) {
    console.error("Error in callLLMForJson:", error);
    // 型ガードを追加して修正
    let errorMessage = "An unknown error occurred in callLLMForJson";
    let stack = "";
    let errorType = "Unknown Error";

    if (error instanceof Error) {
      errorMessage = error.message;
      stack = error.stack ? `\nStack: ${error.stack}` : "";
      // エラーメッセージの内容に基づいてエラータイプを分類 (より詳細に)
      if (errorMessage.includes("Zod")) { // Zod関連のエラー
        errorType = "Schema Validation/Parsing Failed";
      } else if (
        errorMessage.includes("API key") ||
        errorMessage.includes("permission denied")
      ) {
        errorType = "API Authentication/Permission Error";
      } else if (
        errorMessage.includes("timed out") || errorMessage.includes("fetch") ||
        errorMessage.includes("Bad Request")
      ) { // 400 Bad Request も含める
        errorType = "Network/API Call Error";
      } else {
        errorType = "LLM Processing/Other Error";
      }
    }
    // より詳細なエラーメッセージを投げる
    throw new Error(`[${errorType}] ${errorMessage}${stack}`);
  }
}
