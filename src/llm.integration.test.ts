import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { assert } from "@std/assert";
import { loadSync } from "@std/dotenv";
// 修正: createExamQuestionSetParser は削除されたのでインポートしない
import { callLLM, callLLMForJson } from "./llm.ts";
// import { z } from "zod"; // .withStructuredOutput を使う場合、テスト側での直接利用は必須ではない

// 既存の callLLM のテスト (変更なし)
Deno.test({
  name: "[Integration] callLLM should return a response from actual Gemini API",
  fn: async () => {
    try {
      loadSync({ export: true, allowEmptyValues: true, examplePath: null });
    } catch (e) {
      if (e instanceof Deno.errors.NotFound) {
        console.warn(".env file not found, skipping actual API call test.");
        assert(false, ".env file not found. Cannot run actual API test.");
        return;
      }
      throw e;
    }

    const apiKey = Deno.env.get("GEMINI_API_KEY");
    if (!apiKey) {
      assert(
        false,
        "GEMINI_API_KEY is not set in .env file for the actual test.",
      );
      return;
    }
    const actualClient = new ChatGoogleGenerativeAI({
      apiKey: apiKey,
      // model: "gemini-2.5-pro-exp-03-25", // 古いモデル指定の可能性
      model: "gemini-1.5-flash-latest", // 新しいモデルを指定
    });

    const prompt = "Hello";
    try {
      const result = await callLLM(actualClient, prompt);

      assert(typeof result === "string", "Result should be a string.");
      assert(result.length > 0, "Result should not be empty.");
      console.log("\n--- Actual Gemini API Response (callLLM) ---");
      console.log(result);
      console.log("-------------------------------------------\n");
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : String(error);
      console.error(
        "Error during actual API call test (callLLM):",
        errorMessage,
      );
      assert(false, `API call failed (callLLM): ${errorMessage}`);
    }
  },
  sanitizeOps: false, // API呼び出しに必要
  sanitizeResources: false, // API呼び出しに必要
});

// --- callLLMForJson のテストケース (修正版) ---

Deno.test({
  name:
    "[Integration] callLLMForJson should return a parsed JSON object matching the schema",
  fn: async () => {
    try {
      loadSync({ export: true, allowEmptyValues: true, examplePath: null });
    } catch (e) {
      if (e instanceof Deno.errors.NotFound) {
        console.warn(
          ".env file not found, skipping actual API call test for JSON mode.",
        );
        assert(
          false,
          ".env file not found. Cannot run actual API test for JSON mode.",
        );
        return;
      }
      throw e;
    }

    const apiKey = Deno.env.get("GEMINI_API_KEY");
    if (!apiKey) {
      assert(
        false,
        "GEMINI_API_KEY is not set in .env file for the actual JSON test.",
      );
      return;
    }

    // 修正: 通常のクライアントを初期化
    const client = new ChatGoogleGenerativeAI({
      apiKey: apiKey,
      model: "gemini-1.5-flash-latest", // JSONモード対応のモデルが良いでしょう
    });

    // 修正: 簡単なJSON生成を指示するプロンプト (フォーマット指示は不要)
    const promptForJson = `簡単なIT関連の試験問題を1つだけ生成してください。`; // フォーマット指示は callLLMForJson 内部で処理される想定

    try {
      // 修正: 引数は client と prompt のみ
      const result = await callLLMForJson(client, promptForJson);

      // 結果が配列であることを確認
      assert(
        Array.isArray(result),
        "Result should be an array (ExamQuestionSet).",
      );
      // 結果が空でないことを確認 (1問生成を期待)
      assert(result.length > 0, "Result array should not be empty.");

      // 最初の問題オブジェクトの構造と型を検証 (より厳密に)
      const firstQuestion = result[0];
      assert(firstQuestion, "First question object should exist.");
      assert(
        typeof firstQuestion.questionNumber === "number" &&
          Number.isInteger(firstQuestion.questionNumber) &&
          firstQuestion.questionNumber > 0,
        `questionNumber should be a positive integer, got: ${firstQuestion.questionNumber}`,
      );
      assert(
        typeof firstQuestion.questionText === "string" &&
          firstQuestion.questionText.length > 0,
        "questionText should be a non-empty string.",
      );
      assert(
        Array.isArray(firstQuestion.options),
        "options should be an array.",
      );
      assert(
        firstQuestion.options.length > 1, // 通常、選択肢は複数あるはず
        `options array should have more than one item, got: ${firstQuestion.options.length}`,
      );
      // 最初の選択肢を検証
      const firstOption = firstQuestion.options[0];
      assert(firstOption, "First option object should exist.");
      assert(
        typeof firstOption.letter === "string" && firstOption.letter.length > 0,
        "option letter should be a non-empty string.",
      );
      assert(
        typeof firstOption.text === "string" && firstOption.text.length > 0,
        "option text should be a non-empty string.",
      );
      assert(
        typeof firstQuestion.correctAnswer === "string" &&
          firstQuestion.correctAnswer.length > 0,
        "correctAnswer should be a non-empty string.",
      );
      assert(
        typeof firstQuestion.explanation === "string" &&
          firstQuestion.explanation.length > 0,
        "explanation should be a non-empty string.",
      );
      // reference は optional なので存在チェックのみ
      if (firstQuestion.reference !== undefined) {
        assert(
          typeof firstQuestion.reference === "string",
          "reference should be a string if present.",
        );
      }

      console.log(
        "\n--- Actual Gemini API JSON Response (Parsed - callLLMForJson) ---",
      );
      console.log(JSON.stringify(result, null, 2));
      console.log(
        "-----------------------------------------------------------------\n",
      );
    } catch (error) {
      let errorMessage = "Unknown error during JSON API call test";
      if (error instanceof Error) {
        errorMessage = error.message +
          (error.stack ? `\nStack: ${error.stack}` : "");
      }
      console.error(
        "Error during actual JSON API call test (callLLMForJson):",
        errorMessage,
      );
      assert(false, `JSON API call failed (callLLMForJson): ${errorMessage}`);
    }
  },
  sanitizeOps: false, // API呼び出しに必要
  sanitizeResources: false, // API呼び出しに必要
});
