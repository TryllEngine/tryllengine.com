# Tryll Plugin Alpha — Team Guide

Short reference for the Tryll team: what the alpha access system is, and how to invite a new evaluator.

## What this is

We give invited partners temporary alpha access to the Tryll Plugin (Unreal & Unity). Each evaluator gets a **personal access link** (a unique token in the URL). Clicking it opens the Evaluation User Agreement (ELA). When they tick "I agree" and submit:

- The acceptance is logged in the [ELA Acceptances Sheet](https://docs.google.com/spreadsheets/d/1t9rMx_6xJQIIJvmZ56ut7_05WHbgoj1XugCEP2VgPAc/edit?gid=0#gid=0) with timestamp, browser info, and ELA version.
- An admin notification is sent to `evaluations@tryllengine.com` so the whole team is in the loop.
- An automated receipt is sent to the evaluator (BCC'd to `evaluations@`).
- The page reveals the evaluator's Google Drive folder where they download the build.

The build archive is **password-protected**. The password is sent by us in a separate email — never shown on the page.

## The flow at a glance

1. **You invite** — add a row in the sheet with the evaluator's name, email, and Drive folder URL. Generate a token via the menu. Copy the personal link from the `page_url` cell.
2. **You email the evaluator** — send them the personal link + the archive password.
3. **They open the link, read the ELA, click Accept** — the team gets a notification, the evaluator gets a receipt, and they see the Drive folder to download from.

## How to invite a new evaluator

You'll need:

- The evaluator's name and work email
- A Google Drive folder URL with the build prepared for them (or a shared folder used for everyone)

### Steps

1. Open the [ELA Acceptances Sheet](https://docs.google.com/spreadsheets/d/1t9rMx_6xJQIIJvmZ56ut7_05WHbgoj1XugCEP2VgPAc/edit?gid=0#gid=0).

2. Go to a new row and fill in:
   - **Column A — `client_name`**: e.g. "Acme Studios — Alex Kim"
   - **Column B — `email`**: their work email (this is where the receipt goes)
   - **Column I — `drive_url`**: the Google Drive folder URL with the build for this evaluator

3. Click on the **`token`** cell of that row (column C) — just one click, to select it.

4. In the **top menu bar of Google Sheets** (the row where **File**, **Edit**, **View**, **Insert**, ..., **Help** live), find the custom **Tryll ELA** menu — it's the rightmost menu item, appearing after Help. Click **Tryll ELA → Generate token for selected row**.

   The script auto-fills, on that same row:
   - `token` (column C) — 16-character random string
   - `page_url` (column H) — the personal access link, ready to send
   - `invited_at` (column D) — today's date
   - `status` (column J) — `invited`

5. Copy the URL from the **`page_url`** cell (column H) of that row.

6. Compose your invitation email to the evaluator. Include:
   - The personal access link (from `page_url`)
   - The archive password
   - Short instructions, e.g.:
     > Open the link, read and accept our Evaluation User Agreement, then download the build from the Google Drive folder shown on the page. The archive uses the password above. The plugin is licensed for a 90-day evaluation period.

7. Send. When the evaluator accepts, the `evaluations@` group receives a notification, and `accepted_at` (column E) is filled in for that row.

## Operations / FAQ

**Can multiple evaluators share the same Drive folder?**
Yes — paste the same Drive URL into `drive_url` on every row.

**An evaluator forwarded their link / I want to disable a token.**
Set `status` (column J) to `revoked` in that row. Future fetches with that token will return an error. If the legitimate evaluator still needs access, generate a new token for them (via the same menu — it'll prompt to replace the old one).

**I need to change the Drive folder for an evaluator after they've already accepted.**
Edit `drive_url` in their row. To get the new link, the evaluator needs to click "Re-read agreement" on the page (or you can just send them the new Drive URL directly via email).

**Where do I see who has accepted?**
Column E (`accepted_at`) is filled in for every accepted evaluator. The `evaluations@` group inbox also has the notifications.

**The evaluator says they get an error when accepting.**
Common causes:

- Token in their URL doesn't match column C — check they're using the link from `page_url`.
- `drive_url` (column I) is empty for that row — fill it in.
- `status` is `revoked` — change to `invited` (or generate a new token if it was revoked for cause).

**What ELA version are evaluators currently accepting?**
Currently `0.1-draft`. The final version replaces the page text when ready — until then, evaluators see the placeholder text marked "Version 0.1 — Draft".
