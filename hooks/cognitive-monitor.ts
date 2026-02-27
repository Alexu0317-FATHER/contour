#!/usr/bin/env bun

/**
 * Contour Cognitive Monitor — Stop Hook
 *
 * Fires after every assistant response.
 * Classifies the user's message for cognitive signals via Haiku,
 * then updates Domain State when a signal is detected.
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { execSync } from "child_process";

// --- Anti-recursion: exit if triggered by our own inference call ---
if (process.env.CONTOUR_MONITOR_ACTIVE === "1") {
  process.exit(0);
}

// --- Config ---
const DOMAIN_STATE_PATH = process.argv[2];
if (!DOMAIN_STATE_PATH || !existsSync(DOMAIN_STATE_PATH)) {
  process.exit(0);
}

// Git Bash path for Windows (passed as argv[3], optional)
const GIT_BASH_PATH = process.argv[3] || "";

// --- Read Stop hook payload from stdin ---
let payload: any;
try {
  const input = await Bun.stdin.text();
  payload = JSON.parse(input);
} catch {
  process.exit(0);
}

const assistantResponse: string = payload.last_assistant_message || "";
const transcriptPath: string = payload.transcript_path || "";

if (!assistantResponse || !transcriptPath) {
  process.exit(0);
}

// --- Extract last user message from transcript ---
let userMessage = "";
try {
  const lines = readFileSync(transcriptPath, "utf-8")
    .split("\n")
    .filter(Boolean);

  for (let i = lines.length - 1; i >= 0; i--) {
    try {
      const entry = JSON.parse(lines[i]);
      const role = entry.role || entry.type;
      if (role === "human" || role === "user") {
        const content = entry.message?.content || entry.content || "";
        if (typeof content === "string") {
          userMessage = content;
        } else if (Array.isArray(content)) {
          userMessage = content
            .filter((b: any) => b.type === "text")
            .map((b: any) => b.text)
            .join("\n");
        } else {
          userMessage = JSON.stringify(content);
        }
        break;
      }
    } catch {
      continue;
    }
  }
} catch {
  process.exit(0);
}

if (!userMessage) {
  process.exit(0);
}

// --- Read current Domain State ---
let domainState: string;
try {
  domainState = readFileSync(DOMAIN_STATE_PATH, "utf-8");
} catch {
  process.exit(0);
}

// Parse table: extract header and data rows
const allLines = domainState.split("\n");
const tableLines = allLines.filter(
  (line) => line.startsWith("|") && !line.includes("---")
);
const dataLines = tableLines.slice(1); // skip header

interface TrackedConcept {
  concept: string;
  partial: boolean;
  mastered: boolean;
  raw: string;
}

const existingConcepts: TrackedConcept[] = dataLines
  .map((line) => {
    const cells = line
      .split("|")
      .map((c) => c.trim())
      .filter(Boolean);
    return {
      concept: cells[0] || "",
      partial: cells[1]?.includes("✓") || false,
      mastered: cells[2]?.includes("✓") || false,
      raw: line,
    };
  })
  .filter((c) => c.concept);

// --- Build classification prompt ---
const classificationPrompt = `You are a cognitive signal classifier. Analyze this conversation turn.

<user_message>
${userMessage.substring(0, 1000)}
</user_message>

<assistant_response>
${assistantResponse.substring(0, 500)}
</assistant_response>

<tracked_concepts>
${existingConcepts.map((c) => `- ${c.concept}: ${c.mastered ? "mastered" : "partial"}`).join("\n") || "(none)"}
</tracked_concepts>

Classify whether the USER's message contains a cognitive signal:

1. "inquiry" — User asks a conceptual question: "What is X?", "How does X work?", "Explain X", "I don't understand X", "Introduce X"
2. "mastery" — User demonstrates competence with a concept previously marked partial (applies it correctly, asks nuanced follow-ups)
3. "regression" — User asks a basic question about something marked mastered
4. "clarity" — User confirms understanding: "I see", "got it", "makes sense now"

NOT a signal:
- Operational questions (syntax, flags, "how do I run X?")
- Task instructions ("fix this", "write code for", "go ahead")
- AI explaining things user didn't ask about
- Concept already at correct status in tracked list
- Meta-discussion about tools or processes

Respond with ONLY valid JSON, nothing else:
If no signal: {"signal":false}
If signal: {"signal":true,"type":"inquiry","concept":"short concept name","status":"partial"}

Rules for status field:
- inquiry or clarity → "partial"
- mastery → "mastered"
- regression → "partial"`;

// --- Call Haiku for classification ---
interface Classification {
  signal: boolean;
  type?: "inquiry" | "mastery" | "regression" | "clarity";
  concept?: string;
  status?: "partial" | "mastered";
}

let classification: Classification | null = null;
try {
  const envVars: Record<string, string> = {
    ...process.env as Record<string, string>,
    CONTOUR_MONITOR_ACTIVE: "1",
  };
  // Remove CLAUDECODE to allow nested invocation
  delete envVars.CLAUDECODE;

  // Set Git Bash path if provided (Windows)
  if (GIT_BASH_PATH) {
    envVars.CLAUDE_CODE_GIT_BASH_PATH = GIT_BASH_PATH;
  }

  const result = execSync(
    `claude -p --model haiku --no-session-persistence`,
    {
      input: classificationPrompt,
      encoding: "utf-8",
      timeout: 30000,
      env: envVars,
    }
  );

  // Extract JSON from response
  const jsonMatch = result.match(/\{[\s\S]*?\}/);
  if (jsonMatch) {
    classification = JSON.parse(jsonMatch[0]);
  }
} catch {
  process.exit(0);
}

if (
  !classification?.signal ||
  !classification?.concept ||
  !classification?.status
) {
  process.exit(0);
}

const { type, concept, status } = classification;

// --- Validate against existing state ---
const existing = existingConcepts.find(
  (c) =>
    c.concept.toLowerCase().includes(concept!.toLowerCase()) ||
    concept!.toLowerCase().includes(c.concept.toLowerCase())
);

// Skip if already at correct status
if (existing) {
  if (type === "inquiry" && existing.partial && !existing.mastered)
    process.exit(0);
  if (type === "clarity" && existing.partial && !existing.mastered)
    process.exit(0);
  if (type === "mastery" && existing.mastered) process.exit(0);
}
// Can't regress something not tracked
if (!existing && type === "regression") process.exit(0);

// --- Update Domain State ---
const now = new Date();
const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
const partialMark = status === "partial" ? "✓" : "";
const masteredMark = status === "mastered" ? "✓" : "";
const newRow = `| ${concept} | ${partialMark} | ${masteredMark} | ${dateStr} |`;

let updatedState: string;

if (existing) {
  // Replace existing row
  updatedState = domainState.replace(existing.raw, newRow);
} else {
  // Insert new row at end of table
  const lines = domainState.split("\n");
  let lastTableIdx = -1;
  for (let i = lines.length - 1; i >= 0; i--) {
    if (
      lines[i].startsWith("|") &&
      !lines[i].includes("---") &&
      !lines[i].includes("知识点") &&
      !lines[i].includes("Knowledge")
    ) {
      lastTableIdx = i;
      break;
    }
  }
  if (lastTableIdx >= 0) {
    lines.splice(lastTableIdx + 1, 0, newRow);
  }
  updatedState = lines.join("\n");
}

writeFileSync(DOMAIN_STATE_PATH, updatedState, "utf-8");
process.exit(0);
