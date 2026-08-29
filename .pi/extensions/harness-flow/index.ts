import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { StringEnum } from "@earendil-works/pi-ai";

function textResult(text: string, details: unknown = {}) {
  return { content: [{ type: "text" as const, text }], details };
}

function formalActive(): boolean {
  return process.env.HARNESS_FORMAL_MODE === "1" || process.env.HARNESS_FORMAL_MODE === "true";
}

function notApplicable(tool: string) {
  return textResult(`${tool}: not_applicable\nReason: Harness is in simple/passive mode. Formal Round, handoff, review, and widget capabilities require explicit Owner-approved formal activation.`, {
    status: "not_applicable",
    formalMode: false,
    projectWrites: false,
  });
}

export default function harnessFlow(pi: ExtensionAPI): void {
  // Passive by default: no session_start/session_tree widget restoration and no automatic gates.
  pi.registerTool({
    name: "harness_request_plan_approval",
    label: "Harness Plan Approval",
    description: "Optional structured Owner approval for a complete Plan Preview. Does not write project files and does not activate fixed-Round/formal mode by itself.",
    promptSnippet: "Request explicit Owner approval for a complete Plan Preview without writing project files",
    promptGuidelines: [
      "Use only after the complete Plan Preview is visible in chat.",
      "Accepting discovery defaults is not Plan approval.",
      "Approval authorizes only the described Plan persistence; formal Round/review/handoff requires separate explicit activation if requested.",
    ],
    parameters: Type.Object({
      previewTitle: Type.String({ maxLength: 160 }),
      previewSummary: Type.String({ maxLength: 4000 }),
      previewComplete: Type.Boolean(),
      discoveryDefaultsAccepted: Type.Boolean(),
    }),
    executionMode: "sequential",
    async execute(_id, params, _signal, _update, ctx) {
      if (!params.previewComplete) return textResult("Plan approval result: changes_requested\nReason: Plan Preview is not complete.", { status: "changes_requested", projectWritesAuthorized: false });
      if (!ctx.hasUI) return textResult("Plan approval result: cancelled\nReason: Owner UI is unavailable; use manual confirmation fallback.", { status: "cancelled", projectWritesAuthorized: false });
      const choice = await ctx.ui.select(`Plan approval — ${params.previewTitle}\n\n${params.previewSummary}\n\nThis approves durable Plan persistence only; it does not enable formal mode unless the Preview explicitly asks for it.`, [
        "Approve durable Plan persistence",
        "Request changes",
        "Cancel",
      ]);
      if (choice === "Approve durable Plan persistence") return textResult("Plan approval result: approved", { status: "approved", projectWritesAuthorized: true, discoveryDefaultsAccepted: params.discoveryDefaultsAccepted });
      if (choice === "Request changes") {
        const requested = await ctx.ui.input("Requested Plan changes", "Describe the changes needed");
        return textResult(`Plan approval result: changes_requested${requested ? `\nRequested changes: ${requested}` : ""}`, { status: "changes_requested", projectWritesAuthorized: false, requestedChanges: requested });
      }
      return textResult("Plan approval result: cancelled", { status: "cancelled", projectWritesAuthorized: false });
    },
  });

  pi.registerTool({
    name: "harness_offer_session_handoff",
    label: "Harness Session Handoff",
    description: "Formal-mode helper for approved fixed-Round handoff. Returns not_applicable in default simple/passive mode.",
    parameters: Type.Object({ planPath: Type.String({ maxLength: 500 }), roundId: Type.String({ maxLength: 20 }), sessionName: Type.String({ maxLength: 80 }) }),
    executionMode: "sequential",
    async execute() { return formalActive() ? textResult("Formal handoff capability is intentionally disabled in this lightweight starter build; use explicit manual instructions from the approved formal Plan.", { status: "blocked", formalMode: true }) : notApplicable("harness_offer_session_handoff"); },
  });

  pi.registerTool({
    name: "harness_update_round_progress",
    label: "Harness Round Progress",
    description: "Formal-mode fixed-Round widget helper. Returns not_applicable in default simple/passive mode.",
    parameters: Type.Object({
      roundId: Type.String({ maxLength: 20 }),
      stage: StringEnum(["scope_dor", "implementation", "verification", "review", "fix_verify_rereview", "owner_commit_gate", "blocked"] as const),
      status: StringEnum(["active", "done", "blocked"] as const),
      message: Type.Optional(Type.String({ maxLength: 500 })),
    }),
    executionMode: "sequential",
    async execute() { return formalActive() ? textResult("Round progress widget requires the heavier formal extension build; no widget was changed.", { status: "blocked", formalMode: true, projectWrites: false }) : notApplicable("harness_update_round_progress"); },
  });

  pi.registerTool({
    name: "harness_run_independent_review",
    label: "Harness Independent Review",
    description: "Formal-mode Independent Review helper. Returns not_applicable in default simple/passive mode.",
    parameters: Type.Object({
      reviewRole: StringEnum(["per_round", "final_integrated"] as const),
      roundId: Type.String({ maxLength: 20 }),
      planPath: Type.String({ maxLength: 500 }),
      deliveryClass: StringEnum(["product", "governance_maintenance"] as const),
      candidateSummary: Type.String({ maxLength: 20000 }),
      validationSummary: Type.String({ maxLength: 30000 }),
      candidatePaths: Type.Array(Type.String({ maxLength: 500 }), { maxItems: 100 }),
      contextPaths: Type.Optional(Type.Array(Type.String({ maxLength: 500 }), { maxItems: 100 })),
      environmentPaths: Type.Optional(Type.Array(Type.String({ maxLength: 500 }), { maxItems: 100 })),
      fixEvidence: Type.Optional(Type.String({ maxLength: 4000 })),
      timeoutSeconds: Type.Optional(Type.Integer({ minimum: 30, maximum: 1800, default: 600 })),
    }),
    executionMode: "sequential",
    async execute() { return formalActive() ? textResult("Independent Review requires the heavier formal extension build or an Owner-approved distinct human fallback; no review was run.", { decision: "blocked", formalMode: true }) : notApplicable("harness_run_independent_review"); },
  });
}
