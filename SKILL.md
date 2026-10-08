---
name: "volumarc-pipeline"
description: "Set up or run the daily AI reels pipeline: generate video, watermark, host on GitHub, schedule to Facebook/Instagram/TikTok via Buffer."
---

# Volumarc Pipeline

## Purpose

Replicable workflow for daily AI-generated reels posting through Buffer.
Use this skill when the user wants to set up this pipeline on a new
instance, or to run/maintain it.

## Setup

Follow `SETUP-CHECKLIST.md` in order: secure credential dialogs, then
verification, then intake questions, then config, then schedule.
Do not skip verification.

## Daily run

Follow `WORKFLOW.md` exactly.

## Tooling

- `bin/buffer.py` — Buffer GraphQL API: `account`, `channels --org <id>`,
  `create-post --service <facebook|instagram|tiktok> --channel <id> --text <caption> --video-url <url> --due-at <ISO-8601 UTC>`.
  Auth via the stored `custom.buffer` credential through the authd surrogate helper.
- `bin/gh.py` — GitHub REST API: `user`, `create-repo --name <n>`, `upload --repo <owner/repo> --path <p> --file <f>`.
  Auth via the stored `custom.github` credential.
- Both CLIs import the dynamic credential helper from the skill-creator
  scaffold (`/opt/hatch/skills/skill-creator/bin/dynamic_credentials.py`).
  If that path is missing on this instance, scaffold the connector skill
  first, then keep the CLI logic.

## Rules

1. Never ask for API keys or tokens in chat; always use the secure entry dialog.
2. Verify every credential with a real API call before proceeding.
3. Never schedule a post in the past; if a slot already passed, move it to the next day.
4. One video asset per post; video must be reachable via public URL.
5. Report every run; never silently skip a failure.
