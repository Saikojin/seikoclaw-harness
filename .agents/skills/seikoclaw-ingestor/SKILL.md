---
name: seikoclaw-ingestor
description: Processes unstructured files (PDFs, transcripts, CSVs) to ground the Master Vision Plan in external reality.
---

# Seikoclaw Ingestor (Heavy File Ingestion)

## Goal
To convert dense, heavy files into lean Markdown or CSV artifacts so the Architect and Interviewer can reason over clean data instead of struggling with raw binaries or massive documents.

## Workflow
1. **File Identification**: Target the provided heavy files.
2. **Data Extraction**: Extract the raw text, tables, or structural data.
3. **Cleanup**: Convert the extracted data into a lean Markdown representation or structured CSV.
4. **Indexing**: Create an index artifact pointing to the cleaned resources.

## Required Inputs
- Paths to the heavy files to be ingested.

## Output Format
- Cleaned markdown artifacts (`<filename>_clean.md`).
- A `source_index.md` mapping original files to their cleaned counterparts.

## Boundaries
- Do not attempt to analyze the meaning of the files here. Only convert and structure them. Analysis is the job of the Architect.
