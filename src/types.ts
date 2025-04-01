/** 資格試験の名称 */
export type QualificationName = string;

/** 試験の分野・科目 */
export type SubjectArea = string;

/** 正の整数 (問題数など) */
export type PositiveInteger = number;

/** ファイルパス */
export type FilePath = string;
// design-plan.md とテストコードで定義したオプションに対応する型
export interface CLIOptions {
  qualification?: QualificationName; // Optional
  field?: SubjectArea[]; // Optional
  count?: PositiveInteger; // Optional
  output: FilePath;
  configPath: FilePath;
  templatePath: FilePath;
}

/**
 * 試験問題の選択肢を表す型
 */
export interface ExamOption {
  letter: string; // 例: "A", "B"
  text: string; // 選択肢の本文
}

/**
 * 一つの試験問題を表す型
 */
export interface ExamQuestion {
  questionNumber: number; // 問題番号
  questionText: string; // 問題文またはシナリオ
  options: ExamOption[]; // 選択肢のリスト
  correctAnswer: string; // 正解の選択肢記号 (例: "A", "B,C")
  explanation: string; // 解説
  reference?: string; // 参考文献 (任意)
}

/**
 * 試験問題セット全体を表す型 (LLMからのJSON出力のルート)
 */
export type ExamQuestionSet = ExamQuestion[];
