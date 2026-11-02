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
    // Small and out of the way: one sentence with the links, then "Reject all" and
    // "Accept all" as identical buttons, so saying no is as easy as saying yes. On phones
    // it is a slim sheet at the bottom: the sentence, then both buttons in one row.
    // Its own CSS, because the old-design pages load this script without site.css.
    var BANNER_ID = 'tryll-cookie-banner';
    var B = '#' + BANNER_ID;
    var FONT = '"Space Grotesk",Inter,system-ui,sans-serif';
    var CSS =
        B + '{position:fixed;left:16px;right:16px;bottom:16px;z-index:2147483000;margin:0 auto;max-width:1352px;' +
            'padding:14px 14px 14px 24px;box-sizing:border-box;background:#161D29;border:1px solid rgba(255,255,255,.1);' +
            'border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.35);font:15px/1.5 ' + FONT + ';color:rgba(255,255,255,.72)}' +
        B + ' p{margin:0}' +
        B + ' b{color:#fff;font-weight:500}' +
        B + ' .tcc{display:flex;align-items:center;gap:24px}' +
        B + ' .tcc>p{flex:1}' +
        B + ' a,' + B + ' .tcc-link{color:#fff;text-decoration:underline;text-underline-offset:2px}' +
        B + ' .tcc-link{padding:0;border:0;background:none;font:inherit;cursor:pointer}' +
        B + ' .tcc-act{display:flex;align-items:center;gap:8px;flex-shrink:0}' +
        B + ' .tcc-btn{height:44px;padding:0 20px;border:0;border-radius:8px;background:#fff;color:#181716;' +
            'font:500 15px/1 ' + FONT + ';cursor:pointer;white-space:nowrap}' +
        B + ' .tcc-btn:hover{background:#F7F2EC}' +
        B + ' button:focus-visible,' + B + ' a:focus-visible,' + B + ' input:focus-visible{outline:2px solid #fff;outline-offset:2px}' +
        B + ' .tcc-row{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 0;' +
            'border-top:1px solid rgba(255,255,255,.08)}' +
        B + ' .tcc-row small{display:block;font-size:13px;line-height:1.4;color:rgba(255,255,255,.5)}' +
        B + ' .tcc-on{font-size:13px;color:rgba(255,255,255,.5);white-space:nowrap}' +
        B + ' input{width:18px;height:18px;flex-shrink:0;accent-color:#fff;cursor:pointer}' +
        B + ' .tcc-end{justify-content:flex-end;gap:16px;margin-top:6px}' +
        '@media (max-width:640px){' +
            B + '{left:8px;right:8px;bottom:calc(8px + env(safe-area-inset-bottom,0px));padding:12px;border-radius:14px;' +
                'font-size:14px;line-height:1.4}' +
            B + ' .tcc{flex-direction:column;align-items:stretch;gap:10px}' +
            B + ' .tcc-act{display:grid;grid-template-columns:1fr 1fr}' +
            B + ' .tcc-btn{height:42px;padding:0 12px}' +
        '}';

    function closeBanner() {
        var el = document.getElementById(BANNER_ID);
        if (el) el.remove();
    }

    function decide(analytics) {
        saveChoice(analytics);
        applyChoice(analytics);
        closeBanner();
    }

    function renderMain(wrap) {
        wrap.innerHTML =
            '<div class="tcc">' +
                '<p><b>Cookies.</b> We use analytics cookies to see how the site is used. No ads, no cross-site ' +
                'tracking. <a href="/privacy-policy">Privacy Policy</a> · ' +
                '<button type="button" class="tcc-link" id="tryll-cookie-customize">Customize</button></p>' +
                '<div class="tcc-act">' +
                    '<button type="button" class="tcc-btn" id="tryll-cookie-reject">Reject all</button>' +
                    '<button type="button" class="tcc-btn" id="tryll-cookie-accept">Accept all</button>' +
                '</div>' +
            '</div>';

        document.getElementById('tryll-cookie-accept').addEventListener('click', function () { decide(true); });
        document.getElementById('tryll-cookie-reject').addEventListener('click', function () { decide(false); });
        document.getElementById('tryll-cookie-customize').addEventListener('click', function () { renderSettings(wrap); });
    }

    function renderSettings(wrap) {
        var saved = readChoice();
        var analyticsOn = saved ? !!saved.analytics : false;

        wrap.innerHTML =
            '<p style="margin-bottom:6px"><b>Cookie settings</b></p>' +
            '<div class="tcc-row">' +
                '<div><b>Strictly necessary</b><small>Required for the site to work.</small></div>' +
                '<span class="tcc-on">Always on</span>' +
            '</div>' +
            '<label class="tcc-row" for="tryll-cookie-analytics-toggle">' +
                '<div><b>Analytics</b><small>Google Analytics: usage statistics, never used for ads.</small></div>' +
                '<input type="checkbox" id="tryll-cookie-analytics-toggle"' + (analyticsOn ? ' checked' : '') + '>' +
            '</label>' +
            '<div class="tcc-act tcc-end">' +
                '<button type="button" class="tcc-link" id="tryll-cookie-back">Back</button>' +
                '<button type="button" class="tcc-btn" id="tryll-cookie-save">Save preferences</button>' +
            '</div>';

        document.getElementById('tryll-cookie-back').addEventListener('click', function () { renderMain(wrap); });
        document.getElementById('tryll-cookie-save').addEventListener('click', function () {
            decide(document.getElementById('tryll-cookie-analytics-toggle').checked);
        });
    }

    function showBanner() {
        if (document.getElementById(BANNER_ID)) return;
        if (!document.getElementById('tryll-cookie-css')) {
            var style = document.createElement('style');
            style.id = 'tryll-cookie-css';
            style.textContent = CSS;
            document.head.appendChild(style);
        }

        var wrap = document.createElement('div');
        wrap.id = BANNER_ID;
        wrap.setAttribute('role', 'dialog');
        wrap.setAttribute('aria-label', 'Cookie consent');
        document.body.appendChild(wrap);
        renderMain(wrap);
    }

    // Public hook: reopen the banner (used by the footer "Cookie Settings" link).
    window.tryllCookieSettings = showBanner;

    // --- Footer "Cookie Settings" link -----------------------------------
    function injectFooterLink() {
        if (document.getElementById('tryll-cookie-settings-link')) return;
        // The last one: some footers hold a newsletter form whose fine print links the policy too.
        var links = document.querySelectorAll('footer a[href*="privacy-policy"]');
        var privacyLink = links[links.length - 1];
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
