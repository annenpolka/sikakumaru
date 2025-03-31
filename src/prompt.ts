import { dirname, fromFileUrl, join } from "@std/path"; // Import path functions
import { Eta } from "eta"; // Import Eta
import type { CLIOptions } from "./types.ts";

// Etaのインスタンスを作成
const eta = new Eta();
const templateFilePath = join(
  dirname(fromFileUrl(import.meta.url)),
  "../templates/exam-prompt.eta",
);

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
    const template = Deno.readTextFileSync(templateFilePath);
    const templateData = {
      qualificationName: options.qualification || "[Not Specified]",
      fieldsString: options.field?.join(", ") || "[Not Specified]",
      numberOfQuestions: options.count?.toString() || "[Not Specified]",
    };
    const result = eta.renderString(template, templateData); // Use renderString instead of render
    if (typeof result !== "string") {
      throw new Error("Template rendering failed or did not return a string.");
    }

    return result;
  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error in generatePrompt: ${error.message}`);
      throw new Error(`Failed to generate prompt: ${error.message}`, {
        cause: error,
      });
    } else {
      console.error(`An unexpected error occurred in generatePrompt: ${error}`);
      throw new Error(`Failed to generate prompt due to an unexpected error.`);
    }
  }
}
