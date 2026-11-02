/**
 * Tryll Engine — contact form alerts in Slack (Cloudflare Worker).
 *
 * After HubSpot has accepted a message, the site's contact form (assets/js/forms.js)
 * sends a copy here, and this posts it to the team's Slack channel through an incoming
 * webhook. The webhook stays a secret of this Worker: in the site's code anyone could
 * use it to post to the channel.
 *
 * Settings (Cloudflare > this Worker > Settings > Variables and Secrets):
 *   SLACK_WEBHOOK_URL  secret: a Slack Workflow Builder webhook (https://hooks.slack.com/triggers/...,
 *                      variables name, company, email, message, page) or an app's incoming
 *                      webhook (https://hooks.slack.com/services/...)
 *   ALLOWED_ORIGINS    optional, comma-separated; default: tryllengine.com and the team preview
 *
 * Setup and deploy: README.md next to this file. Self-check: node scripts/lead-alerts/test.mjs
 */
const ORIGINS = ['https://tryllengine.com', 'https://www.tryllengine.com', 'https://tryllengine.github.io'];
const LIMITS = { name: 120, company: 160, email: 200, message: 3000, page: 300 };
const recent = new Map();   // IP -> times of its recent alerts (per Worker instance: a brake on floods)

// Slack reads <...> as links and mentions (<!channel>, <@U123>): escape so a visitor can't ping anyone.
function slack(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Workflow Builder shows variables as they are, so break up <...> without changing how it reads.
function plain(s) {
    return s.replace(/</g, '<​');
}

export default {
    async fetch(request, env) {
        const allowed = env.ALLOWED_ORIGINS ? env.ALLOWED_ORIGINS.split(',').map(s => s.trim()) : ORIGINS;
        const origin = request.headers.get('Origin') || '';
        if (!allowed.includes(origin)) return new Response('Forbidden', { status: 403 });
        const cors = { 'Access-Control-Allow-Origin': origin, Vary: 'Origin' };
        if (request.method === 'OPTIONS') {
            return new Response(null, { status: 204, headers: { ...cors, 'Access-Control-Allow-Methods': 'POST',
                                                                'Access-Control-Allow-Headers': 'Content-Type' } });
        }
        if (request.method !== 'POST') return new Response('Method not allowed', { status: 405, headers: cors });
        if (!env.SLACK_WEBHOOK_URL) return new Response('Not configured', { status: 500, headers: cors });

        let lead;
        try {
            lead = JSON.parse(await request.text());
        } catch (e) {
            return new Response('Bad request', { status: 400, headers: cors });
        }
        if (!lead || typeof lead !== 'object') return new Response('Bad request', { status: 400, headers: cors });
        if (lead.website) return new Response(null, { status: 204, headers: cors });   // honeypot: say OK, post nothing
        const f = {};
        for (const k in LIMITS) f[k] = String(lead[k] || '').trim().slice(0, LIMITS[k]);
        if (!/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(f.email)) return new Response('Bad request', { status: 400, headers: cors });

        const ip = request.headers.get('CF-Connecting-IP') || '';
        const now = Date.now();
        const times = (recent.get(ip) || []).filter(t => now - t < 10 * 60 * 1000);
        if (times.length >= 5) return new Response('Too many requests', { status: 429, headers: cors });
        if (recent.size > 1000) recent.clear();
        recent.set(ip, times.concat(now));

        const text = [
            '*New message from the website contact form*',
            `*Name:* ${slack(f.name || '-')}`,
            f.company && `*Studio:* ${slack(f.company)}`,
            `*Email:* ${slack(f.email)}`,
            f.message && `*Message:*\n>${slack(f.message).replace(/\n/g, '\n>')}`,
            f.page && `_Sent from ${slack(f.page)}_`,
        ].filter(Boolean).join('\n');
        // A Workflow Builder webhook takes the fields as its variables and lays out the message
        // in Slack; an app's incoming webhook takes the finished text.
        const workflow = /\/(triggers|workflows)\//.test(env.SLACK_WEBHOOK_URL);
        const body = workflow
            ? Object.fromEntries(Object.keys(LIMITS).map(k => [k, plain(f[k]) || '-']))
            : { text, unfurl_links: false, unfurl_media: false };
        const r = await fetch(env.SLACK_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return new Response(null, { status: r.ok ? 204 : 502, headers: cors });
    },
};
