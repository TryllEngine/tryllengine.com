/**
 * Tryll Engine — Cookie consent + Google Consent Mode v2
 *
 * Must be loaded synchronously BEFORE the GTM snippet on every page.
 * Sets all consent signals to "denied" by default, so Google tags fire
 * no cookies until the visitor accepts. The choice is stored in
 * localStorage and re-applied on every page load.
 *
 * A "Cookie Settings" link is injected into the footer next to the
 * Privacy Policy link so consent can be changed at any time
 * (window.tryllCookieSettings() reopens the banner).
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'tryll_cookie_consent';

    // --- Consent Mode v2 defaults (before GTM loads) -------------------
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }

    gtag('consent', 'default', {
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied',
        analytics_storage: 'denied',
        wait_for_update: 500
    });

    function readChoice() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (e) { return null; }
    }

    function saveChoice(analytics) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                analytics: analytics,
                ts: new Date().toISOString()
            }));
        } catch (e) { /* private mode etc. */ }
    }

    function applyChoice(analytics) {
        gtag('consent', 'update', {
            analytics_storage: analytics ? 'granted' : 'denied',
            ad_storage: 'denied',
            ad_user_data: 'denied',
            ad_personalization: 'denied'
        });
    }

    // Re-apply a previously saved choice immediately.
    var saved = readChoice();
    if (saved) applyChoice(!!saved.analytics);

    // --- Banner UI ------------------------------------------------------
    var BANNER_ID = 'tryll-cookie-banner';

    function closeBanner() {
        var el = document.getElementById(BANNER_ID);
        if (el) el.remove();
    }

    var BTN_BASE =
        'padding:10px 24px;border-radius:4px;font-weight:500;font-size:13px;' +
        'letter-spacing:0.05em;text-transform:uppercase;cursor:pointer;' +
        'font-family:inherit;transition:background 0.2s;white-space:nowrap;';
    var BTN_PRIMARY = BTN_BASE + 'border:0;background:#3B82F6;color:#fff;';
    var BTN_SECONDARY = BTN_BASE +
        'border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.06);color:#fff;';
    var BTN_GHOST = BTN_BASE +
        'border:0;background:transparent;color:rgba(255,255,255,0.55);' +
        'text-decoration:underline;text-underline-offset:3px;padding:10px 8px;';
    var MONO_LABEL =
        'font-family:\'JetBrains Mono\',monospace;font-size:11px;' +
        'letter-spacing:0.1em;text-transform:uppercase;color:rgba(59,130,246,0.75);';

    function decide(analytics) {
        saveChoice(analytics);
        applyChoice(analytics);
        closeBanner();
    }

    function renderMain(wrap) {
        wrap.innerHTML =
            '<div style="display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap;min-height:48px;">' +
                '<div style="flex:1;min-width:240px;">' +
                    '<div style="' + MONO_LABEL + 'margin-bottom:3px;">// cookies</div>' +
                    '<div style="color:rgba(255,255,255,0.65);">We use analytics cookies to understand how the site is used. ' +
                    'No advertising, no cross-site tracking. ' +
                    '<a href="/privacy-policy" style="color:#60a5fa;text-decoration:underline;' +
                    'text-underline-offset:2px;">Privacy Policy</a>.</div>' +
                '</div>' +
                '<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;">' +
                    '<button id="tryll-cookie-customize" style="' + BTN_GHOST + '">Customize</button>' +
                    '<button id="tryll-cookie-reject" style="' + BTN_SECONDARY + '">Reject all</button>' +
                    '<button id="tryll-cookie-accept" style="' + BTN_PRIMARY + '">Accept all</button>' +
                '</div>' +
            '</div>';

        document.getElementById('tryll-cookie-accept').addEventListener('click', function () { decide(true); });
        document.getElementById('tryll-cookie-reject').addEventListener('click', function () { decide(false); });
        document.getElementById('tryll-cookie-customize').addEventListener('click', function () { renderSettings(wrap); });
    }

    function renderSettings(wrap) {
        var saved = readChoice();
        var analyticsOn = saved ? !!saved.analytics : false;

        var rowStyle =
            'display:flex;align-items:center;justify-content:space-between;gap:16px;' +
            'padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.06);';

        wrap.innerHTML =
            '<div style="' + MONO_LABEL + 'margin-bottom:10px;">// cookie_settings</div>' +

            '<div style="' + rowStyle + 'border-top:1px solid rgba(255,255,255,0.06);">' +
                '<div>' +
                    '<div style="color:#fff;font-weight:500;">Strictly necessary</div>' +
                    '<div style="color:rgba(255,255,255,0.45);font-size:13px;">Required for the site to function. Cannot be disabled.</div>' +
                '</div>' +
                '<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;letter-spacing:0.08em;' +
                    'text-transform:uppercase;color:rgba(255,255,255,0.45);white-space:nowrap;">Always on</span>' +
            '</div>' +

            '<div style="' + rowStyle + '">' +
                '<div>' +
                    '<div style="color:#fff;font-weight:500;">Analytics</div>' +
                    '<div style="color:rgba(255,255,255,0.45);font-size:13px;">Google Analytics — aggregated usage statistics. No advertising use.</div>' +
                '</div>' +
                '<label style="display:inline-flex;align-items:center;cursor:pointer;">' +
                    '<input type="checkbox" id="tryll-cookie-analytics-toggle"' + (analyticsOn ? ' checked' : '') +
                    ' style="width:18px;height:18px;accent-color:#3B82F6;cursor:pointer;">' +
                '</label>' +
            '</div>' +

            '<div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:flex-end;margin-top:16px;">' +
                '<button id="tryll-cookie-back" style="' + BTN_GHOST + '">Back</button>' +
                '<button id="tryll-cookie-save" style="' + BTN_PRIMARY + '">Save preferences</button>' +
            '</div>';

        document.getElementById('tryll-cookie-back').addEventListener('click', function () { renderMain(wrap); });
        document.getElementById('tryll-cookie-save').addEventListener('click', function () {
            decide(document.getElementById('tryll-cookie-analytics-toggle').checked);
        });
    }

    function showBanner() {
        if (document.getElementById(BANNER_ID)) return;

        var wrap = document.createElement('div');
        wrap.id = BANNER_ID;
        wrap.setAttribute('role', 'dialog');
        wrap.setAttribute('aria-label', 'Cookie consent');
        // Mirrors the fixed nav header exactly: same width, bg, border, radius, height.
        wrap.style.cssText =
            'position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;' +
            'margin:0 auto;max-width:80rem;padding:16px 32px;' +
            'background:rgba(0,0,0,0.88);border:1px solid rgba(255,255,255,0.08);' +
            'border-radius:4px;box-shadow:0 4px 16px rgba(0,0,0,0.4);' +
            'font-family:"DM Sans",Inter,-apple-system,BlinkMacSystemFont,sans-serif;' +
            'color:rgba(255,255,255,0.85);font-size:13px;line-height:1.5;';

        document.body.appendChild(wrap);
        renderMain(wrap);
    }

    // Public hook: reopen the banner (used by the footer "Cookie Settings" link).
    window.tryllCookieSettings = showBanner;

    // --- Footer "Cookie Settings" link -----------------------------------
    function injectFooterLink() {
        if (document.getElementById('tryll-cookie-settings-link')) return;
        var privacyLink = document.querySelector('footer a[href*="privacy-policy"]');
        if (!privacyLink) return;
        var link = document.createElement('a');
        link.id = 'tryll-cookie-settings-link';
        link.href = '#';
        link.textContent = 'Cookie Settings';
        link.className = privacyLink.className;
        link.addEventListener('click', function (e) {
            e.preventDefault();
            showBanner();
        });
        privacyLink.parentNode.insertBefore(link, privacyLink.nextSibling);
    }

    function onReady() {
        injectFooterLink();
        if (!readChoice()) showBanner();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', onReady);
    } else {
        onReady();
    }
})();
