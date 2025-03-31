import { AIMessage, BaseMessage, HumanMessage } from "@langchain/core/messages";
import { assert, assertEquals } from "@std/assert";
import { spy } from "@std/testing/mock"; // spy のみをインポート
import { callLLM } from "./llm.ts"; // テスト対象の関数をインポート
interface LLMClient {
  invoke(messages: BaseMessage[]): Promise<BaseMessage>;
}
class MockLLMClient implements LLMClient {
  mockResponse: string;

  constructor(mockResponse: string) {
    this.mockResponse = mockResponse;
  }
  invoke(_messages: BaseMessage[]): Promise<BaseMessage> {
    return Promise.resolve(new AIMessage({ content: this.mockResponse }));
  }
}
Deno.test("callLLM should return mocked response for a simple prompt", async () => {
  const mockResponse = "Mocked response from Gemini!";
  const mockClient = new MockLLMClient(mockResponse);
  const invokeSpy = spy(mockClient, "invoke");

  try {
    const prompt = "Test prompt";
    const result = await callLLM(mockClient, prompt); // クラスインスタンスを注入
    assertEquals(result, mockResponse);
    assertEquals(invokeSpy.calls.length, 1);
    const firstCallArgs = invokeSpy.calls[0].args[0];
    assert(
      Array.isArray(firstCallArgs) && firstCallArgs[0] instanceof HumanMessage,
    );
    assertEquals((firstCallArgs[0] as HumanMessage).content, prompt);
  } finally {
    invokeSpy.restore();
  }
});
