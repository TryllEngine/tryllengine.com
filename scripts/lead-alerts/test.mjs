// Self-check for worker.js with Node (no packages):  node scripts/lead-alerts/test.mjs
// Slack is never called: fetch is replaced by a stub that records what would be posted.
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const src = readFileSync(new URL('./worker.js', import.meta.url), 'utf8');
const worker = (await import('data:text/javascript;base64,' + Buffer.from(src).toString('base64'))).default;

const posted = [];
globalThis.fetch = async (url, init) => { posted.push({ url, body: JSON.parse(init.body) }); return new Response(null, { status: 200 }); };
const env = { SLACK_WEBHOOK_URL: 'https://hooks.slack.com/services/T000/B000/TEST' };
const lead = { name: 'Ada Lovelace', company: 'Analytical Games', email: 'ada@example.com',
               message: 'Hi <!channel>\nWe make a colony sim.', page: 'https://tryllengine.com/' };

function req(body, { origin = 'https://tryllengine.com', method = 'POST', ip = '203.0.113.7' } = {}) {
    return new Request('https://alerts.example.workers.dev/', {
        method, body: method === 'POST' ? JSON.stringify(body) : undefined,
        headers: { Origin: origin, 'Content-Type': 'text/plain', 'CF-Connecting-IP': ip },
    });
}

let r = await worker.fetch(req(null, { method: 'OPTIONS' }), env);
assert.equal(r.status, 204);
assert.equal(r.headers.get('Access-Control-Allow-Origin'), 'https://tryllengine.com');

r = await worker.fetch(req(lead, { origin: 'https://evil.example' }), env);
assert.equal(r.status, 403);

r = await worker.fetch(req(lead), env);
assert.equal(r.status, 204);
assert.equal(posted.length, 1);
assert.equal(posted[0].url, env.SLACK_WEBHOOK_URL);
assert.match(posted[0].body.text, /\*Name:\* Ada Lovelace/);
assert.match(posted[0].body.text, /\*Studio:\* Analytical Games/);
assert.match(posted[0].body.text, /&lt;!channel&gt;/, 'mentions must be escaped');
assert.ok(!posted[0].body.text.includes('<!channel>'));
assert.match(posted[0].body.text, /\n>We make a colony sim\./, 'each message line is quoted');

r = await worker.fetch(req({ ...lead, website: 'bot' }), env);
assert.equal(r.status, 204);
assert.equal(posted.length, 1, 'honeypot posts nothing');

r = await worker.fetch(req({ ...lead, email: 'not-an-email' }), env);
assert.equal(r.status, 400);

for (let i = 0; i < 4; i++) await worker.fetch(req(lead, { ip: '198.51.100.9' }), env);
r = await worker.fetch(req(lead, { ip: '198.51.100.9' }), env);
assert.equal(r.status, 204, 'fifth alert from one address still goes');
r = await worker.fetch(req(lead, { ip: '198.51.100.9' }), env);
assert.equal(r.status, 429, 'sixth within 10 minutes is refused');

r = await worker.fetch(req(lead, { ip: '192.0.2.1' }), {});
assert.equal(r.status, 500, 'no webhook configured');

// Workflow Builder webhook: the fields go as its variables, mentions broken up.
const wf = { SLACK_WEBHOOK_URL: 'https://hooks.slack.com/triggers/T000/123/abc' };
r = await worker.fetch(req({ ...lead, company: '' }, { ip: '192.0.2.2' }), wf);
assert.equal(r.status, 204);
const body = posted.at(-1).body;
assert.deepEqual(Object.keys(body).sort(), ['company', 'email', 'message', 'name', 'page']);
assert.equal(body.name, 'Ada Lovelace');
assert.equal(body.company, '-', 'empty field shows a dash');
assert.ok(body.message.includes('<​!channel>') && !body.message.includes('<!channel>'));

console.log(`lead-alerts worker: all checks passed (${posted.length} Slack posts stubbed)`);
