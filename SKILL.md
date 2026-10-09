---
name: "volumarc-pipeline"
description: "Set up or run the daily AI reels pipeline: generate video, watermark, host on Google Drive, schedule to Facebook/Instagram/TikTok via Buffer."
---

# Volumarc Pipeline

## Purpose

Replicable workflow for daily AI-generated reels posting through Buffer.
Use this skill when the user wants to set up this pipeline on a new
instance, or to run/maintain it.

## Setup

Follow `SETUP-CHECKLIST.md` in order: secure credential dialog (Buffer),
Google Drive connection, then verification, then intake questions, then
config, then schedule. Do not skip verification.

## Daily run

Follow `WORKFLOW.md` exactly.

## Tooling

- `bin/buffer.py` — Buffer GraphQL API: `account`, `channels --org <id>`,
  `create-post --service <facebook|instagram|tiktok> --channel <id> --text <caption> --video-url <url> --due-at <ISO-8601 UTC>`.
  Auth via the stored `custom.buffer` credential through the authd surrogate helper
  (`/opt/hatch/skills/skill-creator/bin/dynamic_credentials.py`).
- Google Drive — media hosting, via `hatch_gws_cli drive ...` (see the
  google-drive skill): `drive status` (connect), `drive +upload` into the
  media folder, `drive permissions create` with `{"type":"anyone","role":"reader"}`
  for the public link, direct URL `https://drive.google.com/uc?export=download&id=<fileId>`.
- Never handle raw API keys; Buffer's key goes through the secure entry dialog,
  Drive through its connector OAuth flow.

## Rules

1. Never ask for API keys or tokens in chat; always use the secure entry dialog.
2. Never invent Drive file/folder ids; use only ids returned by earlier commands.
3. Verify every credential/connection with a real call before proceeding.
4. Never schedule a post in the past; if a slot already passed, move it to the next day.
5. One video asset per post; video must be reachable via public URL (verify HTTP 200).
6. Report every run; never silently skip a failure.
