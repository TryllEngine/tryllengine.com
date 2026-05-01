/**
 * Tryll Plugin Alpha — ELA Acceptance backend.
 *
 * Apps Script bound to the "ELA Acceptances" Google Sheet.
 * Receives POST requests from /tryll-plugin-alpha.html when an evaluator
 * accepts the agreement. Validates the token, stamps the acceptance row,
 * notifies the admin, sends a receipt to the evaluator, and returns the
 * Drive URL the page should reveal.
 *
 * Setup: see scripts/SETUP.md
 */

// ====== CONFIG ======
const ADMIN_EMAIL = 'sasha.glotov@tryllengine.com';
const FROM_NAME = 'Tryll Engine';
const SHEET_NAME = 'Acceptances';
// ====================

const COL = {
  CLIENT_NAME: 1,   // A
  EMAIL:       2,   // B
  TOKEN:       3,   // C
  INVITED_AT:  4,   // D
  ACCEPTED_AT: 5,   // E
  ELA_VERSION: 6,   // F
  USER_AGENT:  7,   // G
  PAGE_URL:    8,   // H
  DRIVE_URL:   9,   // I
  STATUS:     10,   // J
  NOTES:      11    // K
};

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents || '{}');
    const token = (payload.token || '').toString().trim();

    if (!token) {
      return jsonResponse({ status: 'error', message: 'Missing access token.' });
    }

    const sheet = SpreadsheetApp.getActive().getSheetByName(SHEET_NAME);
    if (!sheet) {
      return jsonResponse({ status: 'error', message: 'Server misconfigured (sheet not found).' });
    }

    const rowIndex = findRowByToken(sheet, token);
    if (rowIndex === -1) {
      return jsonResponse({ status: 'error', message: 'Invalid or unrecognized access token. Please contact ' + ADMIN_EMAIL + '.' });
    }

    const row = sheet.getRange(rowIndex, 1, 1, 11).getValues()[0];
    const driveUrl = (row[COL.DRIVE_URL - 1] || '').toString().trim();
    const status = (row[COL.STATUS - 1] || '').toString().trim().toLowerCase();
    const existingAcceptedAt = row[COL.ACCEPTED_AT - 1];

    if (status === 'revoked') {
      return jsonResponse({ status: 'error', message: 'This access link has been revoked. Please contact ' + ADMIN_EMAIL + '.' });
    }

    if (!driveUrl) {
      return jsonResponse({ status: 'error', message: 'Download is not yet ready for your account. Please contact ' + ADMIN_EMAIL + '.' });
    }

    // Idempotent: if already accepted, return the original timestamp + drive URL.
    if (existingAcceptedAt) {
      return jsonResponse({
        status: 'ok',
        acceptedAt: toIso(existingAcceptedAt),
        driveUrl: driveUrl,
        message: 'Already accepted.'
      });
    }

    // First-time acceptance — stamp the row.
    const acceptedAtIso = (payload.acceptedAt || new Date().toISOString()).toString();
    const elaVersion = (payload.elaVersion || '').toString();
    const userAgent = (payload.userAgent || '').toString();
    const pageUrl = (payload.pageUrl || '').toString();

    sheet.getRange(rowIndex, COL.ACCEPTED_AT).setValue(new Date(acceptedAtIso));
    if (elaVersion) sheet.getRange(rowIndex, COL.ELA_VERSION).setValue(elaVersion);
    if (userAgent)  sheet.getRange(rowIndex, COL.USER_AGENT).setValue(userAgent);
    if (pageUrl)    sheet.getRange(rowIndex, COL.PAGE_URL).setValue(pageUrl);
    sheet.getRange(rowIndex, COL.STATUS).setValue('accepted');

    const clientName = (row[COL.CLIENT_NAME - 1] || '').toString();
    const evaluatorEmail = (row[COL.EMAIL - 1] || '').toString().trim();

    // Fire-and-forget notifications (errors logged but don't fail the request).
    try { notifyAdmin(clientName, evaluatorEmail, token, acceptedAtIso, elaVersion, userAgent); }
    catch (err) { Logger.log('notifyAdmin failed: ' + err); }

    if (evaluatorEmail) {
      try { sendReceipt(evaluatorEmail, clientName, acceptedAtIso, elaVersion); }
      catch (err) { Logger.log('sendReceipt failed: ' + err); }
    }

    return jsonResponse({
      status: 'ok',
      acceptedAt: acceptedAtIso,
      driveUrl: driveUrl
    });
  } catch (err) {
    Logger.log('doPost error: ' + err);
    return jsonResponse({ status: 'error', message: 'Server error: ' + err.message });
  }
}

function doGet(e) {
  // Health check / diagnostic only.
  return jsonResponse({ status: 'ok', service: 'tryll-ela-acceptance', time: new Date().toISOString() });
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function findRowByToken(sheet, token) {
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return -1;
  const tokens = sheet.getRange(2, COL.TOKEN, lastRow - 1, 1).getValues();
  for (let i = 0; i < tokens.length; i++) {
    if ((tokens[i][0] || '').toString().trim() === token) {
      return i + 2; // +2 because range starts at row 2 and array is 0-indexed
    }
  }
  return -1;
}

function toIso(value) {
  if (value instanceof Date) return value.toISOString();
  try { return new Date(value).toISOString(); } catch (e) { return value.toString(); }
}

function notifyAdmin(clientName, evaluatorEmail, token, acceptedAtIso, elaVersion, userAgent) {
  const subject = '[Tryll ELA] ' + (clientName || evaluatorEmail || token) + ' accepted ELA ' + elaVersion;
  const body =
    'A new evaluator has accepted the Tryll Plugin Alpha ELA.\n\n' +
    'Client:        ' + (clientName || '(not set)') + '\n' +
    'Email:         ' + (evaluatorEmail || '(not set)') + '\n' +
    'Token:         ' + token + '\n' +
    'Accepted at:   ' + acceptedAtIso + '\n' +
    'ELA version:   ' + elaVersion + '\n' +
    'User agent:    ' + userAgent + '\n\n' +
    'Reminder: send the archive password to the evaluator (and attach a PDF copy of the ELA they accepted).';
  MailApp.sendEmail({
    to: ADMIN_EMAIL,
    subject: subject,
    body: body,
    name: FROM_NAME
  });
}

function sendReceipt(evaluatorEmail, clientName, acceptedAtIso, elaVersion) {
  const greeting = clientName ? ('Hi ' + clientName.split(' ')[0] + ',') : 'Hi,';
  const subject = 'Your Tryll Plugin Alpha — ELA acceptance receipt';
  const body =
    greeting + '\n\n' +
    'This message confirms that you accepted the Tryll Engine Plugin Alpha\n' +
    'Evaluation User Agreement (version ' + elaVersion + ') on ' + acceptedAtIso + '.\n\n' +
    'The archive password will follow in a separate email from us. The evaluation\n' +
    'period is 90 days from first installation.\n\n' +
    'Keep this email for your records.\n\n' +
    'Tryll Engine, Inc.\n' +
    ADMIN_EMAIL;
  MailApp.sendEmail({
    to: evaluatorEmail,
    subject: subject,
    body: body,
    name: FROM_NAME
  });
}

// ====== Custom menu: helper to generate a token for the active row ======
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Tryll ELA')
    .addItem('Generate token for selected row', 'generateTokenForActiveRow')
    .addItem('Generate tokens for empty cells', 'generateTokensForEmptyCells')
    .addToUi();
}

function generateTokenForActiveRow() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const row = sheet.getActiveCell().getRow();
  if (row < 2) {
    SpreadsheetApp.getUi().alert('Select a data row (row 2 or later).');
    return;
  }
  const cell = sheet.getRange(row, COL.TOKEN);
  if ((cell.getValue() || '').toString().trim()) {
    const ui = SpreadsheetApp.getUi();
    const resp = ui.alert('Token already set', 'Replace the existing token?', ui.ButtonSet.YES_NO);
    if (resp !== ui.Button.YES) return;
  }
  cell.setValue(makeToken());
  if (!sheet.getRange(row, COL.INVITED_AT).getValue()) {
    sheet.getRange(row, COL.INVITED_AT).setValue(new Date());
  }
  if (!sheet.getRange(row, COL.STATUS).getValue()) {
    sheet.getRange(row, COL.STATUS).setValue('invited');
  }
}

function generateTokensForEmptyCells() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  const range = sheet.getRange(2, COL.TOKEN, lastRow - 1, 1);
  const values = range.getValues();
  let updated = 0;
  for (let i = 0; i < values.length; i++) {
    if (!(values[i][0] || '').toString().trim()) {
      // Only fill if there is some client info in that row.
      const rowNum = i + 2;
      const name = sheet.getRange(rowNum, COL.CLIENT_NAME).getValue();
      const email = sheet.getRange(rowNum, COL.EMAIL).getValue();
      if (name || email) {
        sheet.getRange(rowNum, COL.TOKEN).setValue(makeToken());
        if (!sheet.getRange(rowNum, COL.INVITED_AT).getValue()) {
          sheet.getRange(rowNum, COL.INVITED_AT).setValue(new Date());
        }
        if (!sheet.getRange(rowNum, COL.STATUS).getValue()) {
          sheet.getRange(rowNum, COL.STATUS).setValue('invited');
        }
        updated++;
      }
    }
  }
  SpreadsheetApp.getUi().alert('Generated ' + updated + ' token(s).');
}

function makeToken() {
  // 16 url-safe chars, ~96 bits of entropy. Plenty for a private alpha.
  const alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let out = '';
  for (let i = 0; i < 16; i++) {
    out += alphabet.charAt(Math.floor(Math.random() * alphabet.length));
  }
  return out;
}
