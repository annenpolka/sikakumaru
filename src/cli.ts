// src/cli.ts (リファクタリング後)
import { Command } from "jsr:@cliffy/command@1.0.0-rc.7";
// CLIOptions を types.ts からインポート
import type { CLIOptions } from "./types.ts";

/**
 * CLI コマンドの定義を行う関数。
 * cliffy の Command インスタンスを生成し、オプションを設定して返す。
 * @returns Command インスタンス (型推論に任せる)
 */
export function defineCommand() {
    const cmd = new Command()
        // .name("exam-generator") // アプリケーション名 (必要に応じて設定)
        // .version("0.1.0")      // バージョン (必要に応じて設定)
        // .description("資格試験問題を生成する CLI ツール") // 説明 (必要に応じて設定)
        .option(
            "-q, --qualification <name:string>",
            "資格名 (必須)",
            { required: true },
        )
        .option(
            "-f, --field <name:string>",
            "分野 (必須, 複数指定可能)",
            { required: true, collect: true },
        )
        .option(
            "-c, --count <value:number>",
            "生成する問題数 (必須)",
            { required: true },
        )
        .option(
            "-o, --output <path:string>",
            "出力 JSON ファイルパス (必須)",
            { required: true },
        )
        .option(
            "--configPath <path:string>",
            "設定ファイルのパス",
            { default: "./config.yaml" },
        )
        .option(
            "--templatePath <path:string>",
            "プロンプトテンプレートファイルのパス",
            { default: "./prompt.md" },
        );
    return cmd;
}
