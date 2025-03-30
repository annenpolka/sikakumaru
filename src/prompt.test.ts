import { assertEquals } from "jsr:@std/assert";
import { generatePrompt } from "./prompt.ts"; // 実装ファイル
import type { CLIOptions } from "./types.ts";

// --- テストケース ---

Deno.test("generatePrompt は qualification プレースホルダーを置換するべき", () => {
  // Arrange
  const cliOptions: CLIOptions = { // 完全な CLIOptions 型を使用
    qualification: "応用情報技術者試験",
    field: [], // デフォルトの空配列を提供
    count: 0, // デフォルトの 0 を提供
    output: "dummy_output.json", // 型の完全性のためのダミー値
    configPath: "dummy_config.yaml", // ダミー値
    templatePath: "", // ダミー値 (generatePrompt では未使用)
  };
  // prompt.ts 内のテンプレートリテラルの正確な行と一致させる
  const expectedPromptPart = "*   **Qualification Name:** 応用情報技術者試験";
  const unexpectedDefaultPart = "*   **Qualification Name:** [Not Specified]";

  // Act
  const result = generatePrompt(cliOptions);

  // Assert
  assertEquals(result.includes(expectedPromptPart), true, `期待値 "${expectedPromptPart}" が含まれていません。`);
  assertEquals(result.includes(unexpectedDefaultPart), false, `デフォルト値 "${unexpectedDefaultPart}" が含まれていてはいけません。`);
});

Deno.test("generatePrompt は related fields プレースホルダーを置換するべき (配列を結合)", () => {
  // Arrange
  const cliOptions: CLIOptions = { // 完全な CLIOptions 型を使用
    qualification: "ダミー資格", // ダミー値を提供
    field: ["ストラテジ", "マネジメント"], // 配列入力
    count: 0, // デフォルトの 0 を提供
    output: "dummy_output.json",
    configPath: "dummy_config.yaml",
    templatePath: "",
  };
  // prompt.ts 内のテンプレートリテラルの正確な行と一致させる
  const expectedPromptPart = "*   **Fields:** ストラテジ, マネジメント"; // カンマ区切りを期待
  const unexpectedDefaultPart = "*   **Fields:** [Not Specified]";

  // Act
  const result = generatePrompt(cliOptions);

  // Assert
  assertEquals(result.includes(expectedPromptPart), true, `期待値 "${expectedPromptPart}" が含まれていません。`);
  assertEquals(result.includes(unexpectedDefaultPart), false, `デフォルト値 "${unexpectedDefaultPart}" が含まれていてはいけません。`);
});

Deno.test("generatePrompt は number of questions プレースホルダーを置換するべき", () => {
  // Arrange
  const cliOptions: CLIOptions = { // 完全な CLIOptions 型を使用
    qualification: "ダミー資格",
    field: [],
    count: 50,
    output: "dummy_output.json",
    configPath: "dummy_config.yaml",
    templatePath: "",
  };
  // prompt.ts 内のテンプレートリテラルの正確な行と一致させる
  const expectedPromptPart = "*   **Total Questions:** 50";
  const unexpectedDefaultPart = "*   **Total Questions:** [Not Specified]";

  // Act
  const result = generatePrompt(cliOptions);

  // Assert
  assertEquals(result.includes(expectedPromptPart), true, `期待値 "${expectedPromptPart}" が含まれていません。`);
  assertEquals(result.includes(unexpectedDefaultPart), false, `デフォルト値 "${unexpectedDefaultPart}" が含まれていてはいけません。`);
});

Deno.test("generatePrompt は複数のプレースホルダーを正しく置換するべき", () => {
  // Arrange
  const cliOptions: CLIOptions = {
    qualification: "ITパスポート",
    field: ["テクノロジ", "マネジメント"],
    count: 30,
    output: "output.json", // 完全な CLIOptions 型に必要
    configPath: "config.yaml", // 完全な CLIOptions 型に必要
    templatePath: "", // generatePrompt では未使用だが型の一部
  };
  // prompt.ts 内のテンプレートリテラルの正確な行と一致させる
  const expectedQualification = "*   **Qualification Name:** ITパスポート";
  const expectedFields = "*   **Fields:** テクノロジ, マネジメント";
  const expectedCount = "*   **Total Questions:** 30";
  const unexpectedDefaultQualification = "*   **Qualification Name:** [Not Specified]";
  const unexpectedDefaultFields = "*   **Fields:** [Not Specified]";
  const unexpectedDefaultCount = "*   **Total Questions:** [Not Specified]";


  // Act
  const result = generatePrompt(cliOptions);

  // Assert
  assertEquals(result.includes(expectedQualification), true, `期待値 "${expectedQualification}" が含まれていません。`);
  assertEquals(result.includes(expectedFields), true, `期待値 "${expectedFields}" が含まれていません。`);
  assertEquals(result.includes(expectedCount), true, `期待値 "${expectedCount}" が含まれていません。`);
  // オプションが欠落していた場合のデフォルト値を確認
  assertEquals(result.includes(unexpectedDefaultQualification), false, `デフォルト値 "${unexpectedDefaultQualification}" が含まれていてはいけません。`);
  assertEquals(result.includes(unexpectedDefaultFields), false, `デフォルト値 "${unexpectedDefaultFields}" が含まれていてはいけません。`);
  assertEquals(result.includes(unexpectedDefaultCount), false, `デフォルト値 "${unexpectedDefaultCount}" が含まれていてはいけません。`);
});