# AI Interaction Log & Prompt Decisions

## Top 5 Prompts Used
1. **Task 1 Hybrid Search & Citation Prompt**: Directing Claude to strictly cite only retrieved Brilliant Directories articles and reject unsupported statements.
2. **Task 1 Multimodal Screenshot Extraction Prompt**: Instructing vision models to extract UI labels, action buttons, and configuration toggles from admin screenshots.
3. **Task 2 Email Classification Schema**: Directing Claude to classify customer emails into 7 strict categories with associated risk and urgency ratings.
4. **Task 3 Transcript Extraction Prompt**: Directing the analyst agent to extract concrete deliverables, exclusions, and quote verbatim sentences from messy client dialogue.
5. **Task 3 Scope Diffing Agent**: Directing the agent to compute additions, removals, and cost impacts against the approved baseline rather than previous draft iterations.

## Example AI Suggestion Rejected & Rationale
**Rejection**: The AI initially suggested automatically retraining or fine-tuning the model weights after every 10 customer emails sent.
**Why Rejected**: Incremental online weight training causes catastrophic forgetting, high cost, and unversioned behavior drift. Instead, we implemented prompt-level few-shot adaptation paired with the deterministic 20-consecutive-approval streak manager and instant rollback on human edits.