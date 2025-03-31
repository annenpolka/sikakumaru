// src/cli.test.ts (エラーメッセージ修正)
import { assertEquals, assertRejects } from "jsr:@std/assert";
import { Command } from "jsr:@cliffy/command@1.0.0-rc.7"; // バージョンも更新済み
import { defineCommand } from "./cli.ts";

async function parseHelper(cmd: ReturnType<typeof defineCommand>, args: string[]) {
    try {
        // parse の戻り値も推論に任せる
        // テスト実行時にプロセスが終了しないように noExit() を呼ぶ
        return await cmd.noExit().parse(args);
    } catch (error) {
        // エラーを再スローして assertRejects で捕捉できるようにする
        throw error;
    }
}

Deno.test("defineCommand: 必須引数がすべて指定された場合、正しく解析される", async () => {
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
        configPath: "./config.yaml",
        templatePath: "./prompt.md",
    };
    assertEquals(options, expectedOptions);
});

Deno.test("defineCommand: --qualification が欠けている場合、エラーをスローする", async () => {
    const cmd = defineCommand();
    const args = [
        "--field",
        "テクノロジ系",
        "--count",
        "10",
        "--output",
        "output.json",
    ];
    await assertRejects(
        () => parseHelper(cmd, args),
        Error,
        // 実際のメッセージに合わせて修正 (引用符とピリオド)
        'Missing required option "--qualification".',
    );
});

Deno.test("defineCommand: --output が欠けている場合、エラーをスローする", async () => {
    const cmd = defineCommand();
    const args = [
        "--qualification",
        "基本情報技術者試験",
        "--field",
        "テクノロジ系",
        "--count",
        "10",
    ];
    await assertRejects(
        () => parseHelper(cmd, args),
        Error,
        // 実際のメッセージに合わせて修正
        'Missing required option "--output".',
    );
});

Deno.test("defineCommand: --count が欠けている場合、エラーをスローする", async () => {
    const cmd = defineCommand();
    const args = [
        "--qualification",
        "基本情報技術者試験",
        "--field",
        "テクノロジ系",
        "--output",
        "output.json",
    ];
    await assertRejects(
        () => parseHelper(cmd, args),
        Error,
        // 実際のメッセージに合わせて修正
        'Missing required option "--count".',
    );
});

Deno.test("defineCommand: --field が欠けている場合、エラーをスローする", async () => {
    const cmd = defineCommand();
    const args = [
        "--qualification",
        "基本情報技術者試験",
        "--count",
        "10",
        "--output",
        "output.json",
    ];
    await assertRejects(
        () => parseHelper(cmd, args),
        Error,
        // 実際のメッセージに合わせて修正
        'Missing required option "--field".',
    );
});

Deno.test("defineCommand: オプション引数が指定された場合、それらが反映される", async () => {
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

Deno.test("defineCommand: --count に数値以外が指定された場合、エラーをスローする", async () => {
    const cmd = defineCommand();
    const args = [
        "--qualification",
        "基本情報技術者試験",
        "--field",
        "テクノロジ系",
        "--count",
        "abc",
        "--output",
        "output.json",
    ];
    await assertRejects(
        () => parseHelper(cmd, args),
        Error,
        // 実際のメッセージに合わせて修正 (引用符とピリオド)
        'Option "--count" must be of type "number", but got "abc".',
    );
});
