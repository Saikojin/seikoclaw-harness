# Comprehension Standard

This standard defines the quality bar for clarity, self-containment, and comprehensibility of technical specifications and designs.

## Core Principle

A specification passes if a competent engineer (or fresh AI session) who is unfamiliar with the project or team history can read the document from top to bottom and fully understand the proposal without guessing, asking clarifying questions, or encountering unstated tribal knowledge.

## 1. Paraphrase Requirement

* **Independent Reconstruction**: An isolated reader must be able to summarize:
  1. *What the document proposes* in 2–4 sentences.
  2. *How the existing system works* (as described in the document) in 2–4 sentences.
* If a reader cannot paraphrase the design or the paraphrase diverges from the author's intent, the document fails this standard with a blocking finding.

## 2. Self-Containment & Zero Tribal Knowledge

* **Unambiguous Terminology**: Any internal acronym, service name, subsystem, or custom concept must be defined inline or linked to authoritative documentation.
* **No Unstated Prerequisites**: Do not assume the reader knows implicit team conventions, private setup steps, or unmentioned environment configurations.
* **No Vague Hand-Waving**: Prohibit hand-waving phrases like "the system handles this automatically" or "standard authentication is applied" without specifying *how* or linking to the authoritative component.

## 3. Clear Boundaries & User Journeys

* **Explicit Actors**: The document must clearly identify which actor, component, or client triggers each action.
* **Concrete Flows**: Critical User Journeys (CUJs) and system interaction flows must be step-by-step and reproducible.
