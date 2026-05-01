# ELA Acceptance Backend — Setup Guide

This sets up the Google Sheet + Apps Script backend that records each evaluator's acceptance of the Tryll Plugin Alpha ELA, sends notifications, and returns the per-client Drive URL to `tryll-plugin-alpha.html`.

One-time setup, ~10 minutes. After that, inviting a new client = adding a row to the sheet and copying their personal link.

## 1. Create the Google Sheet

1. Go to https://sheets.google.com and create a new spreadsheet. Name it **"Tryll ELA Acceptances"** (or anything you like).
2. Rename the first tab to **`Acceptances`** (must match — the script looks for this name).
3. Set up the header row exactly as below (row 1):

| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| client_name | email | token | invited_at | accepted_at | ela_version | user_agent | page_url | drive_url | status | notes |

4. Optional but recommended — freeze the header row: **View → Freeze → 1 row**.

## 2. Add the Apps Script

1. In the sheet: **Extensions → Apps Script**.
2. Delete the default `Code.gs` content and paste the entire contents of [`ela-acceptance.gs`](./ela-acceptance.gs).
3. At the top of the file, confirm the config:
   - `ADMIN_EMAIL` — where acceptance notifications are sent. Defaults to `evaluations@tryllengine.com`.
   - `FROM_NAME` — sender name on outgoing emails (admin notification + receipt to evaluator).
   - `SHEET_NAME` — must match your tab name (`Acceptances`).
4. Click the **Save** icon (or Ctrl/Cmd-S).

## 3. Authorize the script

The script needs permissions to read/write the sheet and send emails on your behalf.

1. In the Apps Script editor, select the function `doGet` from the dropdown next to the Run button.
2. Click **Run**. Google will pop up a permissions dialog.
3. Click **Review permissions** → choose your Google account → click **Advanced** → **Go to (unsafe)** (this warning appears for any unverified personal Apps Script — it's expected).
4. Approve access to Google Sheets and Gmail/MailApp.

## 4. Deploy as a Web App

1. In the Apps Script editor: **Deploy → New deployment**.
2. Click the gear icon next to "Select type" → choose **Web app**.
3. Configure:
   - **Description**: `Tryll ELA acceptance v1`
   - **Execute as**: **Me** (your account)
   - **Who has access**: **Anyone** (this is required so the public page can call the endpoint; the token is what gates access, not the URL)
4. Click **Deploy**.
5. Copy the **Web app URL** — looks like `https://script.google.com/macros/s/AKfy.../exec`.

## 5. Wire the URL into the page

1. Open [`tryll-plugin-alpha.html`](../tryll-plugin-alpha.html).
2. Find the line near the bottom of the `<script>`:
   ```js
   const ENDPOINT_URL = 'https://script.google.com/macros/s/REPLACE_WITH_DEPLOYMENT_ID/exec';
   ```
3. Replace the URL with your deployed Web app URL from step 4.
4. Commit and push.

## 6. Reload the sheet to see the custom menu

Refresh the spreadsheet tab. After ~5 seconds a new menu **"Tryll ELA"** appears next to *Help*. (If it doesn't, refresh once more — Apps Script triggers can lag on first load.)

## How to invite a new client

1. Open the sheet, go to a new row.
2. Fill in:
   - **client_name** — e.g. "Acme Studios — Alex Kim"
   - **email** — the evaluator's work email
   - **drive_url** — the Google Drive folder URL with the build for this client
3. Select that row's `token` cell (column C), then **Tryll ELA → Generate token for selected row**. A 16-char token is generated; `page_url` (the personal access link), `invited_at`, and `status=invited` are auto-filled in the same row.
4. Compose the invitation email to the client. Include:
   - Personal access link: copy the URL from the `page_url` cell (column H) of that row — it already has the token baked in
   - The archive password
   - Brief instructions ("read the ELA on that page, accept, then download from the Drive link that appears")

When the client accepts:

- The sheet row gets `accepted_at`, `user_agent`, `status=accepted` filled in (`page_url` was already set at token generation and is left untouched)
- You receive an admin email notification
- The evaluator receives an automated receipt

## Operations

- **Revoke access**: change the row's `status` to `revoked`. Future fetches with that token will be denied (an existing accepted client who already loaded the page on their browser will see the cached Drive link in localStorage until they clear it; the page does not re-validate on subsequent visits).
- **Replace Drive folder for a client**: edit `drive_url` in the sheet. The new URL will be served on the next acceptance fetch. (For already-accepted clients, ask them to click "Re-read agreement" on the page to refresh.)
- **Update the script later**: edit `ela-acceptance.gs` in Apps Script, then **Deploy → Manage deployments → edit (pencil) → New version → Deploy**. The endpoint URL stays the same.

## Security notes

- The token is a 96-bit random string in the URL. Treat it like a password — don't post screenshots of the URL bar.
- If a client forwards their link, a third party could accept on their behalf. The ELA itself prohibits redistribution; in practice, the audit trail in the sheet (with the original `client_name` you set) ties the acceptance to the invited party regardless of who clicked.
- If you suspect a token leaked, set its row's `status` to `revoked` and issue a new token for the legitimate client.

## Troubleshooting

- **"Access link missing or invalid" on the page**: token query param `?c=` is missing or empty. Double-check the URL you sent.
- **"Invalid or unrecognized access token"**: the token doesn't exist in the sheet, or has trailing whitespace. Verify column C of the matching row.
- **CORS error in browser console**: The page sends `Content-Type: text/plain;charset=utf-8` deliberately to skip CORS preflight (Apps Script Web Apps don't support custom CORS preflight). If you see preflight errors, confirm the page hasn't been changed to send `application/json`.
- **No email notifications arriving**: re-run the authorization (step 3) and confirm Gmail/MailApp scope is granted. MailApp has a daily quota (~100 emails/day for personal accounts) — fine for an alpha.
