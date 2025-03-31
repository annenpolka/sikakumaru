import { dirname, fromFileUrl, join } from "@std/path"; // Import path functions
import { Eta } from "eta"; // Import Eta
import type { CLIOptions } from "./types.ts";

// Etaのインスタンスを作成
// Etaを選定した理由: 軽量、高速、構文がシンプルで学習コストが低い。Denoでの利用実績もある。
const eta = new Eta();

// Define the path relative to the current file
const templateFilePath = join(dirname(fromFileUrl(import.meta.url)), "../templates/exam-prompt.eta");

/**
 * Generates the final prompt string using an Eta template file and CLIOptions.
 * Reads the template file and renders it synchronously.
 *
 * @param options The command line options provided by the user.
 * @returns The prompt string with placeholders filled.
 * @throws {Error} If the template file cannot be read or if template rendering fails.
 */
export function generatePrompt(options: CLIOptions): string {
  try {
    // Read the template file synchronously
    // --allow-read パーミッションが必要になる点に注意
    const template = Deno.readTextFileSync(templateFilePath);

    // Prepare data for the template
    const templateData = {
      qualificationName: options.qualification || "[Not Specified]",
      fieldsString: options.field?.join(", ") || "[Not Specified]",
      numberOfQuestions: options.count?.toString() || "[Not Specified]",
      // Note: Other placeholders like domain distribution, difficulty, etc.,
      // are still hardcoded in the template for this step.
    };

    // Render the template synchronously
    const result = eta.renderString(template, templateData); // Use renderString instead of render

    // eta.render が string | undefined を返す可能性があるため型ガード (実際には同期版は string を返すはずだが念のため)
    if (typeof result !== "string") {
      throw new Error("Template rendering failed or did not return a string.");
    }

    return result;
  } catch (error) {
    // error が Error インスタンスか確認
    if (error instanceof Error) {
      console.error(`Error in generatePrompt: ${error.message}`);
      // エラーハンドリング: エラーを再スローして呼び出し元に処理を委ねる
      // より丁寧なエラー処理 (特定の型のエラーを返すなど) は今後の改善点
      throw new Error(`Failed to generate prompt: ${error.message}`, {
        cause: error,
      });
    } else {
      // Error インスタンスでない場合 (文字列など)
      console.error(`An unexpected error occurred in generatePrompt: ${error}`);
      throw new Error(`Failed to generate prompt due to an unexpected error.`);
    }
  }
}
