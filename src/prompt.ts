import type { CLIOptions } from "./types.ts";

/**
 * Generates the final prompt string using template literals and CLIOptions.
 *
 * @param options The command line options provided by the user.
 * @returns The prompt string with placeholders filled.
 */
export function generatePrompt(options: CLIOptions): string {
  // Destructure options for easier use in the template literal
  const { qualification, field, count } = options;

  // Join the fields array into a comma-separated string
  const fieldsString = field?.join(", ") || "[Not Specified]";
  const qualificationName = qualification || "[Not Specified]";
  const numberOfQuestions = count?.toString() || "[Not Specified]";

  // English prompt template using template literals
  const prompt = `
# Role
You are an expert exam question creation assistant specializing in the specified qualification field. Generate clear, high-quality exam questions based on educational principles.

# Basic Instructions
Create a question set for the ${qualificationName} exam according to the following requirements.

## 1. Scope and Focus Areas
*   **Qualification Name:** ${qualificationName}
*   **Fields:** ${fieldsString}
*   **Scope:** Based on the following domains and ratios:
    *   [Domain 1 Name] ([XX]%)
    *   [Domain 2 Name] ([XX]%)
    *   *(Add domains as needed)*
*   **Reference Materials:** If possible, refer to [Specify official guidelines, documents, standards, etc.].

## 2. Question Structure
*   **Total Questions:** ${numberOfQuestions}
*   **Difficulty Distribution (Approx.):**
    *   Basic: [XX]% (Recall/Understanding of basic knowledge, definitions, concepts)
    *   Intermediate: [XX]% (Application of knowledge, simple analysis, execution of standard procedures)
    *   Advanced: [XX]% (Complex situation analysis, integration of multiple concepts, evaluation, judgment)
*   **Cognitive Level (Approx.):** Based on Bloom's Taxonomy:
    *   Remember: [XX]% - Recall facts, terms, basic concepts (e.g., define, list)
    *   Understand: [XX]% - Explain concepts, summarize, interpret (e.g., explain, classify)
    *   Apply: [XX]% - Use learned knowledge in new situations (e.g., execute, apply)
    *   Analyze: [XX]% - Break down information, identify structures or relationships (e.g., compare, distinguish)
    *   Evaluate: [XX]% - Make judgments based on criteria, determine value (e.g., evaluate, justify)
    *   Create: [XX]% - Generate something new (plan, product, perspective) (Measured in MCQs mainly through evaluating design approaches)
*   **Question Formats:** Combine the following formats appropriately:
    *   Standard Multiple Choice (MCQ): [XX]%
    *   Scenario-based: [XX]%
    *   Multiple Select (if applicable): [XX]%
    *   **Other formats (include as needed):**
        *   **Ordering/Sequencing:** Ask for the correct order of processes or steps.
        *   **Matching:** Connect related items (e.g., terms and definitions).
        *   **Hotspot/Graphic Selection:** Have the user select specific areas on a diagram.
    *   *(Adjust format ratios to total 100%)*

## 3. Question Design Principles
*   **Theoretical Background:** Based on **Psychometrics** (for validity/reliability) and **Cognitive Science** (for reducing cognitive load and promoting understanding).
*   **Clarity:** Question stems should be specific, unambiguous, and interpretable in only one way. Avoid double negatives. (Reduces unnecessary cognitive load)
*   **Validity:**
    *   **Content Validity:** Accurately reflect the knowledge/skills required in the scope and practice.
    *   Be mindful of measuring the intended cognitive level (e.g., application, not just recall).
*   **Reliability:** Design questions with clear correct answers to ensure consistent measurement and reduce guessing.
*   **Item Discrimination:** Design questions, especially distractors, to differentiate between high and low knowledge levels.
*   **Relevance:** Focus on the essential question, excluding irrelevant information. (Reduces extraneous cognitive load)
*   **Fairness:** Avoid cultural biases that might advantage or disadvantage specific groups.

## 4. Multiple Choice Question (MCQ) Requirements
*   **Stem:** Should be a complete question or provide clear context.
*   **Options:**
    *   Only one clearly correct answer.
    *   All options should be grammatically and contextually homogeneous (similar topic, structure, length).
    *   Options should be mutually exclusive.
    *   Avoid "all of the above" / "none of the above".
    *   Use absolute terms ("always", "never") cautiously.
*   **Distractor Creation Strategies:** (Effective distractors improve **item discrimination** and reduce correct answers by **guessing**)
    *   **Common Misconceptions:** Reflect typical errors or misunderstandings.
    *   **Partial Correctness:** Include options that seem plausible but are incorrect in a key aspect or only correct in a different context.
    *   **Related Errors:** Create options conceptually close to the correct answer but clearly wrong.
    *   **Term Confusion:** Use similar but distinct terms or concepts.
    *   **Avoid Obviously Incorrect Options:** All options should appear plausible.

## 5. Scenario-Based Question Requirements
*   **Realism:** Set specific, realistic situations likely encountered in practice.
*   **Context:** Clearly describe necessary background, roles, constraints, and goals.
*   **Judgment:** Design to assess analysis, judgment, and problem-solving skills in context, not just simple knowledge recall.
*   **Complexity:** Adjust the number of elements, amount of information, and level of judgment required based on difficulty. Consider case study formats with multiple related questions.

## 6. Explanation Requirements
*   **Learning Effect:** (Based on **Cognitive Science** principles) Effective explanations go beyond simple correctness checks to promote deeper understanding and knowledge retention (transfer to long-term memory).
*   **Correct Answer Indication:** Clearly state the correct option.
*   **Rationale for Correct Answer:** Explain specifically why the option is correct based on relevant principles, theories, or facts.
*   **Analysis of Incorrect Answers:** Explain specifically why each other option is incorrect. Clarify the error points, especially for plausible distractors.
*   **Supplementary Information:** Briefly add relevant key concepts, practical considerations, or best practices. A metacognitive perspective (why one might have chosen incorrectly, how to think differently) is also useful.
*   **Reference:** If possible, cite the source material (document section, standard number, etc.).

## 7. Field-Specific Considerations (Customization Guide)
*   **Cloud Certifications (AWS/Azure/GCP, etc.):**
    *   Service selection trade-offs (cost, performance, security, operational load)
    *   Application of Well-Architected Framework / design principles
    *   Pricing models and cost optimization strategies
    *   Architecture design/evaluation in scenarios
    *   Security and compliance (shared responsibility model, etc.)
*   **Cybersecurity Certifications (CISSP/Security+, etc.):**
    *   Risk management and assessment (threats, vulnerabilities, impact)
    *   Security architecture and design principles (zero trust, defense-in-depth, etc.)
    *   Security operations (incident response, monitoring, log analysis)
    *   Compliance and regulations (GDPR, PCI DSS, etc.)
    *   Administrator vs. Technician perspective differences (depending on the cert)
*   **Project Management Certifications (PMP/Agile, etc.):**
    *   Appropriate application of methodologies (predictive, agile, hybrid)
    *   Situational judgment (stakeholders, risks, change management)
    *   Team management and leadership
    *   Alignment with business value and organizational strategy
    *   Ethical considerations and professional responsibility

*(Examples above. Add/modify specific considerations for the target qualification)*

## 8. Output Format
Provide questions and explanations in the following format:
\`\`\`
Question [Number]:
[Question stem or scenario]

A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
(Add/remove options as needed)

**Correct Answer:** [Correct option letter(s)]

**Explanation:**
[Detailed explanation based on the requirements above]

**Reference:** [Reference info, if applicable]

---
\`\`\`

## Final Checkpoints
*   Generated questions and explanations do not guarantee final quality.
*   **Always perform review and validation by Subject Matter Experts (SMEs)**, especially for highly specialized content or actual exam use.
*   Accuracy and currency require constant attention as technology and standards evolve.
*   If possible, collect trial data (pass rates, item discrimination) and learner feedback to continuously improve the question set.

Proceed with generating the question set according to these instructions.
`;

  // Note: Other placeholders like domain distribution, difficulty, etc.,
  // are not yet handled in this PoC step (2b). They will be addressed later.

  return prompt;
}