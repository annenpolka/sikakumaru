// src/types.ts

// design-plan.md とテストコードで定義したオプションに対応する型
export interface CLIOptions {
  qualification?: string; // Optional
  field?: string[]; // Optional
  count?: number; // Optional
  output: string;
  configPath: string;
  templatePath: string;
}

// 今後、他の型定義 (AppConfig, ExamResultSet など) もここに追加していくことになるでしょうね。
