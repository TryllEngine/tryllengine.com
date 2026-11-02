# Contact form → Slack

The contact form posts to HubSpot. Once HubSpot has accepted a message, the page sends a copy to this Cloudflare Worker (`worker.js`), which posts it to the team's Slack channel through an incoming webhook. The webhook address lives only in the Worker's secrets: anyone who has it can post to the channel, so it must never go into the site's code.

## Set up (once)

1. **Slack**: create the channel (for example `#leads`), then make a webhook for it, either way:
   - *Workflow Builder* (no app needed): new workflow → *From a webhook* → add the variables `name`, `company`, `email`, `message`, `page` (all *Text*) → *Continue* → add the step *Send a message to a channel*, pick the channel and write the message with those variables → *Publish* → copy the webhook URL (`https://hooks.slack.com/triggers/...`).
   - *A Slack app*: at https://api.slack.com/apps: *Create New App* → *From scratch* → *Incoming Webhooks* → turn on → *Add New Webhook to Workspace* → choose the channel → copy the URL (`https://hooks.slack.com/services/...`). The Worker writes the message itself.
2. **Cloudflare** (a free account is enough): *Workers & Pages* → *Create* → *Create Worker* → name it `tryll-lead-alerts` → *Deploy* → *Edit code* → replace everything with `worker.js` from this folder → *Deploy*.
3. In the Worker: *Settings* → *Variables and Secrets* → *Add* → type *Secret*, name `SLACK_WEBHOOK_URL`, value: the webhook URL → *Deploy*.
4. Put the Worker's address (`https://tryll-lead-alerts.<your-account>.workers.dev`) in `LEAD_ALERTS` in `scripts/site-build/config.py` and run `py -3 scripts/site-build/build.py`. That switches the form on and adds Slack and Cloudflare to the Privacy Policy.

Or with the CLI, from this folder: `npx wrangler login`, `npx wrangler deploy`, `npx wrangler secret put SLACK_WEBHOOK_URL`.

## How it guards the channel

- Only requests from tryllengine.com and the team preview are accepted (set `ALLOWED_ORIGINS` to change that).
- A honeypot field, an email check and length limits; at most 5 alerts per address per 10 minutes.
- Slack link and mention syntax in the message is escaped, so a visitor can't `@channel` the team.

If spam ever gets through anyway, the next step is Cloudflare Turnstile on the form, checked by the Worker.

## Check

`node scripts/lead-alerts/test.mjs` runs the Worker against every case above with Slack stubbed out.
