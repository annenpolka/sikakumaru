import { assertSnapshot } from "jsr:@std/testing/snapshot";
import { generatePrompt } from "./prompt.ts"; // 実装ファイル
import type { CLIOptions } from "./types.ts";
Deno.test("generatePrompt snapshot test - Basic", async (t) => {
  const cliOptions: CLIOptions = {
    qualification: "応用情報技術者試験",
    field: ["テクノロジ", "マネジメント"],
    count: 10,
    output: "dummy_output.json",
    configPath: "dummy_config.yaml",
    templatePath: "",
  };
  const result = generatePrompt(cliOptions);
  await assertSnapshot(t, result);
});

Deno.test("generatePrompt snapshot test - Defaults", async (t) => {
  const cliOptions: CLIOptions = {
    qualification: undefined, // Test default
    field: undefined, // Test default
    count: undefined, // Test default
    output: "dummy_output.json",
    configPath: "dummy_config.yaml",
    templatePath: "",
  };
  const result = generatePrompt(cliOptions);
  await assertSnapshot(t, result);
});

Deno.test("generatePrompt snapshot test - Empty Fields", async (t) => {
  const cliOptions: CLIOptions = {
    qualification: "基本情報技術者試験",
    field: [], // Test empty array
    count: 5,
    output: "dummy_output.json",
    configPath: "dummy_config.yaml",
    templatePath: "",
  };
  const result = generatePrompt(cliOptions);
  await assertSnapshot(t, result);
});
