import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { assert } from "@std/assert";
import { loadSync } from "@std/dotenv";
import { callLLM } from "./llm.ts"; // テスト対象の関数をインポート

// モック用のインターフェース定義は不要

// --- 実通信テスト (インテグレーションテスト) ---
Deno.test({
  name: "[Integration] callLLM should return a response from actual Gemini API",
  fn: async () => {
    // .env ファイルから環境変数をロード (テスト実行時のみ)
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

    // 実際の ChatGoogleGenerativeAI インスタンスを作成
    const actualClient = new ChatGoogleGenerativeAI({
      apiKey: apiKey,
      model: "gemini-1.5-pro",
    });

    const prompt = "Hello";
    try {
      const result = await callLLM(actualClient, prompt);

      assert(typeof result === "string", "Result should be a string.");
      assert(result.length > 0, "Result should not be empty.");
      console.log("\n--- Actual Gemini API Response ---");
      console.log(result);
      console.log("--------------------------------\n");
    } catch (error) {
      const errorMessage = error instanceof Error
        ? error.message
        : String(error);
      console.error("Error during actual API call test:", errorMessage);
      assert(false, `API call failed: ${errorMessage}`);
    }
  },
  // API通信は時間がかかる可能性があるので、サニタイザーを無効化
  sanitizeOps: false,
  sanitizeResources: false,
});
