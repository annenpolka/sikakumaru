import { AIMessage, BaseMessage, HumanMessage } from "@langchain/core/messages";
// ChatGoogleGenerativeAI はユニットテストには不要
import { assert, assertEquals } from "@std/assert";
import { spy } from "@std/testing/mock"; // spy のみをインポート
import { callLLM } from "./llm.ts"; // テスト対象の関数をインポート

// モック用のインターフェース (src/llm.ts の LLMClient と合わせる)
interface LLMClient {
  invoke(messages: BaseMessage[]): Promise<BaseMessage>;
}

// モッククライアントをクラスとして定義
class MockLLMClient implements LLMClient {
  mockResponse: string;

  constructor(mockResponse: string) {
    this.mockResponse = mockResponse;
  }

  // invoke メソッドの実装 (async は不要)
  invoke(_messages: BaseMessage[]): Promise<BaseMessage> {
    // Promise.resolve でラップして返す
    return Promise.resolve(new AIMessage({ content: this.mockResponse }));
  }
}

// --- モックテスト (ユニットテスト) ---
Deno.test("callLLM should return mocked response for a simple prompt", async () => {
  const mockResponse = "Mocked response from Gemini!";
  const mockClient = new MockLLMClient(mockResponse);
  // インスタンス化後に spy を適用
  const invokeSpy = spy(mockClient, "invoke");

  try {
    const prompt = "Test prompt";
    const result = await callLLM(mockClient, prompt); // クラスインスタンスを注入
    assertEquals(result, mockResponse);

    // spy を使って呼び出しを確認
    assertEquals(invokeSpy.calls.length, 1);
    const firstCallArgs = invokeSpy.calls[0].args[0];
    assert(
      Array.isArray(firstCallArgs) && firstCallArgs[0] instanceof HumanMessage,
    );
    assertEquals((firstCallArgs[0] as HumanMessage).content, prompt);
  } finally {
    // spy をリストア
    invokeSpy.restore();
  }
});
