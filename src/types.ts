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
