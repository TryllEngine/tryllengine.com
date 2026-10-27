/**
 * Tryll Engine — forms on the redesign pages.
 *
 * Contact (#contact-form)  -> Formspree, same inbox as the old site.
 * Newsletter ([data-ml-form]) -> MailerLite, same group as the old blog form.
 *
 * Both are real <form> submits, so GTM's "Form submission" trigger keeps
 * firing. A dataLayer custom_event is pushed on success, in the same shape
 * the old site used.
 */
(function () {
    'use strict';

    var ML_ACCOUNT = '2274886';

    function track(action, label) {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
            event: 'custom_event',
            event_category: 'form',
            event_action: action,
            event_label: label
        });
    }

    function status(el, text, ok) {
        if (!el) return;
        el.textContent = text;
        el.className = 'fmsg ' + (ok ? 'ok' : 'err');
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
            var data = new FormData(cf);
            data.append('privacy_policy_consent', 'accepted');
            btn.disabled = true;
            status(msg, 'Sending…', true);
            fetch(cf.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
                .then(function (r) {
                    if (!r.ok) return r.json().catch(function () { return {}; }).then(function (j) {
                        throw new Error(j.errors && j.errors[0] && j.errors[0].message || 'Something went wrong.');
                    });
                    cf.reset();
                    if (consent.classList.contains('on')) consent.click();
                    status(msg, 'Thanks! We got your message and will get back to you soon.', true);
                    track('submit', 'contact');
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
                track('subscribe', form.getAttribute('data-source') || 'newsletter');
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
