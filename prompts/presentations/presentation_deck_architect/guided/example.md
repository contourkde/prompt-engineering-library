# Example: SRE Automation and Configuration Drift

This example shows all 14 variable inputs and handoffs for a manual run. The selections below are illustrative editorial choices, not recorded model output or verified infrastructure findings. No external sources have been checked for this example.

## Stage 1: Shared Brief

**persona**

```text
Developer Advocate with an SRE-focused perspective. Explain infrastructure automation through practical workflows without claiming personal production incidents or unprovided credentials.
```

**topic**

```text
Designing infrastructure automation to detect, explain, and reconcile configuration drift. Use an illustrative Broadcom/VMware migration planning scenario, not claims about actual vendor policies or observed migration results.
```

**objective**

```text
Help SREs design a reviewable automation workflow that compares desired and observed state, identifies ownership, and proposes safe reconciliation. Connect domain-driven design (DDD), bounded contexts, and explicit ownership to the example's design choices.
```

**audience**

```text
SREs and platform engineers familiar with infrastructure as code. They want actionable guidance on drift, change review, rollback planning, and ownership boundaries. Do not assume prior DDD expertise.
```

For every multiline question, finish with a separate line containing only `.`. Run the rendered structure prompt in an AI chat, review its three alternatives, and press Enter in the terminal to continue.

## Stage 2: Structure and Hook Context

**chosen_structure**

```text
Name: From unexpected drift to a reviewable change.
Beginning: Introduce a hypothetical routine change that reveals a difference between desired and observed infrastructure state. Ask who owns the decision to reconcile it.
Middle: Walk through a proposed compare, classify, review, and reconcile workflow. Introduce DDD bounded contexts as a design lens for separating ownership in this illustrative system. Show a synthetic change review, not measured production results.
End: Invite the audience to map one drift scenario to an owner, a review gate, and a rollback plan.
Rationale: A single scenario ties automation mechanics to explicit ownership and gives the audience a concrete design exercise.
```

**hook_context**

```text
Use a hypothetical infrastructure change during migration planning. No checked sources or measured downtime data are available. Do not use the unsupported 95% downtime statistic. Broadcom/VMware details are illustrative; actual licensing, migration behavior, and API rate limits are unknown here. Prefer a nonnumeric question about drift and ownership.
```

Run the hook prompt in your AI chat. Retain the chosen hook and its evidence notes, then press Enter in the terminal.

## Stage 3: Hook and Tone

**selected_hook**

```text
What would you check first if a routine change exposed unexpected configuration drift: the configuration, the automation, or who owns the decision?
Bridge: Let's use a hypothetical migration planning exercise to design a reviewable path from that question to a safe proposed change.
Evidence note: This is a hypothetical question, not a reported incident or statistical claim. Vendor-specific migration behavior and API limits remain UNVERIFIED and are not asserted by the hook.
```

**tone_start**: `Curious and empathetic`

**tone_end**: `Practical and confident without overpromising`

You can accept the tone defaults with empty input. Run the opening prompt in your AI chat, choose one of its three approximately 60-second options, edit it as needed, and press Enter in the terminal.

## Stage 4: Opening, Relevance, Duration, and Evidence

**selected_opening**

```text
What would you check first if a routine change exposed unexpected configuration drift: the configuration, the automation, or who owns the decision?

Imagine that question arriving during a migration planning exercise. This is a hypothetical scenario, not a report of a customer incident. You have a desired configuration, an observed configuration, and a proposed change. Before deciding what to automate, where would you place the review gate, and whose approval would you need?

Today we will design one possible answer. We will compare desired and observed state, classify the difference, identify an owner, and prepare a proposed reconciliation with a rollback plan. We will also use domain-driven design as a lens for discussing ownership boundaries in this example.

The goal is not to promise a migration outcome or an improvement percentage. It is to leave with a workflow you can examine and adapt. Let's start with the two configurations and the decision between them.

Evidence note: The scenario and proposed workflow are illustrative. No vendor-specific capabilities, API limits, or measured outcomes are asserted. Any factual explanation added about DDD or automation needs a checked source and date before delivery.
```

**timeframe**: `Q3 2026 (July through September 2026)`

This is the period that factual claims must describe, not the talk duration.

**presentation_duration**: `20 minutes total, including 5 minutes for Q&A`

**fast_changing_subtopic**

```text
Broadcom/VMware migration-related product behavior, licensing documentation, and any applicable automation API constraints. Exact products, versions, endpoints, and limits have not been established.
```

**current_context**

```text
Illustrative intended delivery date: 2026-10-15.
Factual scope: Q3 2026. The later delivery date does not extend this period. Any later-published evidence must explicitly support conditions during Q3 2026.
No current external sources have been supplied or checked. Product versions and API endpoints are unspecified. Treat vendor-specific claims as UNVERIFIED; do not imply known rate limits or migration outcomes.
Any configuration records, migration diagrams, or demo outputs must be labeled synthetic or illustrative. They are not observed production data.
Before delivery, obtain the applicable official product and API documentation with publication/update dates and version scope. Obtain dated supporting sources for factual DDD and automation explanations as well. Until then, use the nonnumeric hypothetical scenario and proposed design rather than unsupported factual claims.
```

The renderer exits after printing the final prompt, without another Enter pause. Run that prompt in your AI chat. Confirm each slide has a title, 3-4 supporting bullets, and speaker notes. Check the timing total, confirm the opening is counted, and inspect every claim-ledger entry for relevance to Q3 2026. Keep unresolved evidence gaps marked `UNVERIFIED` and use safe fallback wording in audience-facing content.

## Expected Artifacts

The run prints four prompts. If `--output-dir generated/my-deck` is supplied, it also writes:

- `generated/my-deck/01_structure.md`
- `generated/my-deck/02_hook.md`
- `generated/my-deck/03_opening.md`
- `generated/my-deck/04_slides.md`

These files contain rendered prompts, not model responses or finished slides. Existing files are not overwritten. Selected AI responses must be carried forward manually during the same run; there is no saved session to resume.

Return to the [guided workflow](README.md).
