import { assertEquals, assertStringIncludes, fail } from "jsr:@std/assert";
import { describe, it } from "jsr:@std/testing/bdd";
import { defineCommand } from "./cli.ts";
async function parseHelper(
  cmd: ReturnType<typeof defineCommand>,
  args: string[],
) {
  return await cmd.noExit().parse(args);
}

describe("defineCommand", () => {
  describe("正常系テスト", () => {
    it("必須引数がすべて指定された場合、正しく解析される", async () => {
      const cmd = defineCommand();
      const args = [
        "--qualification",
        "基本情報技術者試験",
        "--field",
        "テクノロジ系",
        "--field",
        "マネジメント系",
        "--count",
        "10",
        "--output",
        "output.json",
      ];
      const { options } = await parseHelper(cmd, args);
      const expectedOptions = {
        qualification: "基本情報技術者試験",
        field: ["テクノロジ系", "マネジメント系"],
        count: 10,
        output: "output.json",
        configPath: "./config.yaml", // デフォルト値
        templatePath: "./prompt.md", // デフォルト値
      };
      assertEquals(options, expectedOptions);
    });

    it("オプション引数が指定された場合、それらが反映される", async () => {
      const cmd = defineCommand();
      const args = [
        "--qualification",
        "応用情報技術者試験",
        "--field",
        "ストラテジ系",
        "--count",
        "5",
        "--output",
        "exam.json",
        "--configPath",
        "custom_config.json",
        "--templatePath",
        "custom_template.md",
      ];
      const { options } = await parseHelper(cmd, args);
      const expectedOptions = {
        qualification: "応用情報技術者試験",
        field: ["ストラテジ系"],
        count: 5,
        output: "exam.json",
        configPath: "custom_config.json",
        templatePath: "custom_template.md",
      };
      assertEquals(options, expectedOptions);
    });
  });

  describe("必須オプション欠落テスト", () => {
    const baseArgs = (missing: string) => {
      const allArgs = {
        "--qualification": "基本情報技術者試験",
        "--field": "テクノロジ系",
        "--count": "10",
        "--output": "output.json",
      };
      // deno-lint-ignore no-dynamic-delete
      delete allArgs[missing as keyof typeof allArgs];
      return Object.entries(allArgs).flat();
    };

    const testMissingOption = async (optionName: string) => {
      const cmd = defineCommand();
      const args = baseArgs(optionName);
      try {
        await parseHelper(cmd, args);
        fail(`エラーがスローされませんでした (${optionName} 欠落)`);
      } catch (error) {
        if (error instanceof Error) {
          assertStringIncludes(
            error.message,
            `Missing required option "${optionName}"`,
          );
        } else {
          fail("予期しないエラータイプです");
        }
      }
    };

    it("--qualification が欠けている場合、エラーをスローする", async () => {
      await testMissingOption("--qualification");
    });

    it("--field が欠けている場合、エラーをスローする", async () => {
      await testMissingOption("--field");
    });

    it("--count が欠けている場合、エラーをスローする", async () => {
      await testMissingOption("--count");
    });

    it("--output が欠けている場合、エラーをスローする", async () => {
      await testMissingOption("--output");
    });
  });

  describe("型エラーテスト", () => {
    it("--count に数値以外が指定された場合、エラーをスローする", async () => {
      const cmd = defineCommand();
      const args = [
        "--qualification",
        "基本情報技術者試験",
        "--field",
        "テクノロジ系",
        "--count",
        "abc", // 不正な値
        "--output",
        "output.json",
      ];
      try {
        await parseHelper(cmd, args);
        fail("エラーがスローされませんでした (--count 型エラー)");
      } catch (error) {
        if (error instanceof Error) {
          assertStringIncludes(
            error.message,
            'Option "--count" must be of type "number"',
          );
        } else {
          fail("予期しないエラータイプです");
        }
      }
    });
  });

  describe("境界値テスト", () => {
    it("--count に 0 が指定された場合、エラーをスローしない (仕様確認)", async () => {
      const cmd = defineCommand();
      const args = [
        "--qualification",
        "基本情報技術者試験",
        "--field",
        "テクノロジ系",
        "--count",
        "0",
        "--output",
        "output.json",
      ];
      const { options } = await parseHelper(cmd, args);
      assertEquals(options.count, 0);
    });

    it("--count に負数が指定された場合、エラーをスローしない (仕様確認)", async () => {
      const cmd = defineCommand();
      const args = [
        "--qualification",
        "基本情報技術者試験",
        "--field",
        "テクノロジ系",
        "--count",
        "-1",
        "--output",
        "output.json",
      ];
      const { options } = await parseHelper(cmd, args);
      assertEquals(options.count, -1);
    });
  });

  describe("ヘルプ/バージョン表示テスト", () => {
    const runCli = async (args: string[]) => {
      const command = new Deno.Command(Deno.execPath(), {
        args: [
          "run",
          "main.ts", // CLIのエントリポイント
          ...args,
        ],
        stdout: "piped",
        stderr: "piped",
      });
      const output = await command.output();
      const stdout = new TextDecoder().decode(output.stdout);
      const stderr = new TextDecoder().decode(output.stderr);
      return { stdout, stderr, code: output.code };
    };

    it("-h が指定された場合、ヘルプメッセージが stdout に表示され、正常終了する", async () => {
      const { stdout, stderr, code } = await runCli(["-h"]);
      assertEquals(code, 0, `stderr: ${stderr}`); // 正常終了を確認
      assertStringIncludes(
        stdout,
        "Usage:",
        "ヘルプメッセージに 'Usage:' が含まれていません",
      );
      assertStringIncludes(
        stdout,
        "--qualification",
        "ヘルプメッセージに '--qualification' が含まれていません",
      );
    });

    it("--help が指定された場合、ヘルプメッセージが stdout に表示され、正常終了する", async () => {
      const { stdout, stderr, code } = await runCli(["--help"]);
      assertEquals(code, 0, `stderr: ${stderr}`);
      assertStringIncludes(stdout, "Usage:");
      assertStringIncludes(stdout, "--qualification");
    });
    it.ignore("-V が指定された場合、バージョン情報が表示される", async () => {
    });

    it.ignore("--version が指定された場合、バージョン情報が表示される", async () => {
    });
  });

  describe("不正オプションテスト", () => {
    it("定義されていないオプションが指定された場合、エラーをスローする", async () => {
      const cmd = defineCommand();
      const args = ["--unknown-option", "value"];
      try {
        await parseHelper(cmd, args);
        fail("エラーがスローされませんでした (不正なオプション)");
      } catch (error) {
        if (error instanceof Error) {
          assertStringIncludes(
            error.message,
            'Unknown option "--unknown-option"',
          );
        } else {
          fail("予期しないエラータイプです");
        }
      }
    });
  });
});
