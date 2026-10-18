# System Architecture & Technical Design Document

## 1. Problem Statement & Business Justification
Software delivery pricing has collapsed by ~90% due to LLM-assisted programming (Cursor, Claude). To sustain operational margins, agencies must handle 10x-20x client volume. The operational bottleneck is no longer coding, but the surrounding consultation lifecycle:
1. Knowing complex SaaS/product settings inside-out to prevent quoting costly custom engineering when native configuration exists.
2. Managing high-volume client inboxes rapidly without hallucinations, policy violations, or brand degradation.
3. Transforming messy, multi-hour client discovery conversations into structured Scopes of Work (SOWs), developer estimates, and proposals.

## 2. Global Architecture Diagram

``mermaid
flowchart TD
    Sitemap[Brilliant Directories Sitemap & Help Center] --> KB[Task 1: Knowledge Brain FastAPI]
    KB --> KBApi[REST API: /query, /escalations]
    Inbox[Task 2: Inbox Agent TypeScript] -->|Query| KBApi
    Meeting[Task 3: Meeting to Scope Python] -->|Query| KBApi
    Inbox --> AutoSend[Autonomous Sending Safeguard: 20-streak]
    Meeting --> DiffReport[Baseline vs Revision SOW Diff]
``

## 3. Task Breakdown
- Task 1: Knowledge Brain with polite sitemap crawler, SQLite FTS5, screenshot analyzer, and human escalation.
- Task 2: Inbox Agent with 50 synthetic emails, risk classification, and 20-consecutive unedited approval autonomy.
- Task 3: Meeting to Scope with multi-agent analyst, feasibility checker, estimator, and scope differ.

## 4. Model Justification
Claude 3.5 Sonnet is selected for long-context meeting reasoning and visual screenshot understanding; Claude 3.5 Haiku is selected for sub-second email triage.