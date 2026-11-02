/**
 * Tryll Engine — forms on the redesign pages.
 *
 * Contact (#contact-form)  -> HubSpot (data-provider="hubspot"), else Formspree.
 * Newsletter ([data-ml-form]) -> MailerLite, same group as the old blog form.
 *
 * Both are real <form> submits, so GTM's "Form submission" trigger keeps
 * firing on every attempt. Only once the service has accepted the form does
 * GA4 get generate_lead (contact) or sign_up (newsletter).
 */
(function () {
    'use strict';

    var ML_ACCOUNT = '2274886';
    var GA4 = 'G-V0BH3P7R63';   // the GA4 property GTM loads

    // GTM's Google tag only takes events from the page when they name its property (send_to).
    function ga4(name, params) {
        params.send_to = GA4;
        window.dataLayer = window.dataLayer || [];
        (function () { window.dataLayer.push(arguments); })('event', name, params);
    }

    function status(el, text, ok) {
        if (!el) return;
        el.textContent = text;
        el.className = 'fmsg ' + (ok ? 'ok' : 'err');
    }

    // HubSpot Forms API: fields are contact properties, and the one Name field
    // becomes first + last name. The consent text is stored with the contact.
    function hubspotRequest(form) {
        var f = form.elements;
        var name = f['name'].value.trim().split(/\s+/);
        var fields = [
            ['email', f['email'].value.trim()],
            ['firstname', name.shift()],
            ['lastname', name.join(' ')],
            ['company', f['company'].value.trim()],
            ['message', f['message'].value.trim()]
        ].filter(function (x) { return x[1]; }).map(function (x) {
            return { objectTypeId: '0-1', name: x[0], value: x[1] };
        });
        return {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
            body: JSON.stringify({
                fields: fields,
                context: { pageUri: location.href, pageName: document.title },
                legalConsentOptions: { consent: {
                    consentToProcess: true,
                    text: 'I accept the privacy policy: https://tryllengine.com/privacy-policy'
                } }
            })
        };
    }

    // A copy of an accepted message for the team's Slack channel, through the Worker in
    // data-alerts (scripts/lead-alerts). Best effort: the visitor never waits for it.
    function alertTeam(form) {
        var url = form.getAttribute('data-alerts');
        if (!url) return;
        var f = form.elements;
        fetch(url, {
            method: 'POST',
            keepalive: true,
            headers: { 'Content-Type': 'text/plain' },   // a simple request: no CORS preflight
            body: JSON.stringify({
                name: f['name'].value.trim(), company: f['company'].value.trim(),
                email: f['email'].value.trim(), message: f['message'].value.trim(), page: location.href
            })
        }).catch(function () {});
    }

    function errorText(j) {
        var e = j.errors && j.errors[0] || {};
        if (e.errorType === 'INVALID_EMAIL') return 'Please check your email address.';
        return e.message && !e.errorType ? e.message : 'Something went wrong.';   // Formspree's are readable
    }

    // --- Contact ---------------------------------------------------------
    var cf = document.getElementById('contact-form');
    if (cf) {
        var consent = cf.querySelector('[data-consent]');
        var msg = cf.querySelector('.fmsg');
        var btn = cf.querySelector('button[type="submit"]');

        // The checkbox look is driven by the page logic (class "on"); keep ARIA in sync.
        new MutationObserver(function () {
            consent.setAttribute('aria-checked', consent.classList.contains('on') ? 'true' : 'false');
        }).observe(consent, { attributes: true, attributeFilter: ['class'] });

        cf.addEventListener('submit', function (e) {
            e.preventDefault();
            if (cf.querySelector('[name="_gotcha"]').value) return;
            if (!cf.reportValidity()) return;
            if (!consent.classList.contains('on')) {
                status(msg, 'Please accept the privacy policy so we can reply to you.', false);
                consent.focus();
                return;
            }
            var req;
            if (cf.getAttribute('data-provider') === 'hubspot') {
                req = hubspotRequest(cf);
            } else {
                var data = new FormData(cf);
                data.append('privacy_policy_consent', 'accepted');
                req = { method: 'POST', body: data, headers: { Accept: 'application/json' } };
            }
            btn.disabled = true;
            status(msg, 'Sending…', true);
            fetch(cf.action, req)
                .then(function (r) {
                    if (!r.ok) return r.json().catch(function () { return {}; }).then(function (j) {
                        throw new Error(errorText(j));
                    });
                    alertTeam(cf);   // before reset: it reads the fields
                    cf.reset();
                    if (consent.classList.contains('on')) consent.click();
                    status(msg, 'Thanks! We got your message and will get back to you soon.', true);
                    ga4('generate_lead', { form_name: 'contact' });
                })
                .catch(function (err) {
                    status(msg, err.message + ' You can also email us at support@tryllengine.com.', false);
                })
                .then(function () { btn.disabled = false; });
        });
    }

    // --- Newsletter (MailerLite) ----------------------------------------
    Array.prototype.forEach.call(document.querySelectorAll('form[data-ml-form]'), function (form) {
        var msg = form.parentNode.querySelector('.fmsg');
        var btn = form.querySelector('button[type="submit"]');
        var url = 'https://assets.mailerlite.com/jsonp/' + ML_ACCOUNT + '/forms/' + form.getAttribute('data-ml-form') + '/subscribe';

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (form.querySelector('[name="website"]').value) return;
            if (!form.reportValidity()) return;
            var body = new URLSearchParams();
            body.append('fields[email]', form.email.value.trim());
            body.append('fields[signup_source]', form.getAttribute('data-source') || 'website');
            body.append('ml-submit', '1');
            body.append('anticsrf', 'true');
            var opts = { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body.toString() };
            btn.disabled = true;

            function done() {
                form.reset();
                status(msg, 'You’re subscribed. Check your inbox to confirm.', true);
                ga4('sign_up', { method: 'newsletter', form_name: form.getAttribute('data-source') || 'newsletter' });
            }

            fetch(url, opts)
                .then(function (r) {
                    return r.json().catch(function () { return {}; }).then(function (j) {
                        if (r.ok && j.success !== false) return done();
                        var err = j.errors && j.errors.fields && j.errors.fields.email;
                        status(msg, (err && err[0]) || 'Subscription failed. Please try again.', false);
                    });
                })
                .catch(function () {
                    // CORS refusal still delivers the request; fall back to fire-and-forget.
                    opts.mode = 'no-cors';
                    return fetch(url, opts).then(done, function () {
                        status(msg, 'Network error. Please try again.', false);
                    });
                })
                .then(function () { btn.disabled = false; });
        });
    });
})();
