import { AIMessageChunk } from "@langchain/core/messages"; // HumanMessage も必要ならインポート
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { assert, assertEquals } from "@std/assert";
import { resolvesNext, stub } from "@std/testing/mock"; // resolvesNext をインポート
import { callLLM } from "./llm.ts";

// --- モックテスト ---
Deno.test("callLLM should return mocked response for a simple prompt", async () => {
  const mockResponse = "Mocked response from Gemini!";
  // callLLM が内部で ChatGoogleGenerativeAI を使うと仮定し、invoke をスタブ化
  const modelStub = stub(
    ChatGoogleGenerativeAI.prototype,
    "invoke",
    resolvesNext([new AIMessageChunk({ content: mockResponse })]), // resolvesNext を使用
  );
  // Deno.env.get もスタブ化してダミーの API キーを返す
  const envStub = stub(Deno.env, "get", (key: string) => {
    if (key === "GEMINI_API_KEY") {
      return "DUMMY_API_KEY_FOR_TESTING";
    }
    // 元の Deno.env.get の挙動を模倣（他の環境変数を壊さないため）
    // ただし、テスト環境で他の環境変数に依存するのは避けるべき
    // ここではシンプルに undefined を返すか、必要なら元の関数を呼ぶ
    // return Deno.env.get(key); // 元の関数を呼ぶ場合 (非推奨)
    return undefined; // 他のキーは undefined を返す
  });

  try {
    const prompt = "Test prompt";
    const result = await callLLM(prompt);
    assertEquals(result, mockResponse);
  } finally {
    modelStub.restore(); // スタブを元に戻す
    envStub.restore(); // 環境変数のスタブも元に戻す
  }
});

// --- 実通信テスト ---
Deno.test({
  name: "callLLM should return a response from actual Gemini API",
  // 環境変数 GEMINI_API_KEY がなければテストを無視
  // ここでの Deno.env.get はスタブ化されていない元の関数が使われる
  ignore: !Deno.env.get("GEMINI_API_KEY"),
  fn: async () => {
    const prompt = "Hello"; // 簡単なテストプロンプト
    try {
      const result = await callLLM(prompt);

      // 具体的な応答内容は問わず、文字列であり空でないことだけを確認
      assert(typeof result === "string", "Result should be a string.");
      assert(result.length > 0, "Result should not be empty.");
      console.log("\n--- Actual Gemini API Response ---");
      console.log(result);
      console.log("--------------------------------\n");
    } catch (error) {
      // error が Error インスタンスか確認してから message を使う
      const errorMessage = error instanceof Error
        ? error.message
        : String(error);
      // APIキーが不正などの理由で失敗する可能性もあるため、エラーを出力
      console.error("Error during actual API call test:", errorMessage);
      assert(false, `API call failed: ${errorMessage}`);
    }
  },
  // API通信は時間がかかる可能性があるので、サニタイザーを無効化
  sanitizeOps: false,
  sanitizeResources: false,
});
