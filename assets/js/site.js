/**
 * Tryll Engine — page runtime for the baked redesign pages.
 *
 * Pages are designed in Claude Design and baked to static HTML by
 * scripts/site-build (so crawlers and link previews see real content).
 * Each page keeps its original design logic (`class Component extends
 * DCLogic`, in /assets/js/pages/<page>.js); this file is the small
 * runtime that runs it against the static markup instead of React:
 *
 *   data-b-<attr>="expr"   attribute / class / style bound to renderVals()
 *   data-on-<event>="expr" event handler from renderVals()
 *   data-t="expr"          text content
 *   data-loop / data-lk    items of an <sc-for> loop (see #dc-loops JSON)
 *
 * setState() batches into one requestAnimationFrame and only touches
 * attributes whose value actually changed.
 */
(function () {
    'use strict';

    var UNITLESS = /^(opacity|zIndex|flex|flexGrow|flexShrink|fontWeight|lineHeight|order|zoom|orphans|widows|scale)$/;
    var inst = null;
    var queued = false;
    var loops = {};
    var bound = [];       // bound elements outside loops
    var loopEls = {};     // loop id -> [[el per child key], ...] per item

    function get(scope, path) {
        var parts = path.split('.');
        var v = scope;
        for (var i = 0; i < parts.length && v != null; i++) v = v[parts[i]];
        return v;
    }

    function setStyle(el, v) {
        var prev = el.__st || {};
        var next = {};
        if (typeof v === 'string') { el.style.cssText = v; el.__st = {}; return; }
        if (v && typeof v === 'object') {
            for (var k in v) {
                var val = v[k];
                if (val == null || val === false) continue;
                if (typeof val === 'number' && !UNITLESS.test(k) && k.indexOf('--') !== 0) val = val + 'px';
                next[k] = String(val);
            }
        }
        for (var p in prev) if (!(p in next)) {
            if (p.indexOf('--') === 0) el.style.removeProperty(p); else el.style[p] = '';
        }
        for (var n in next) if (prev[n] !== next[n]) {
            if (n.indexOf('--') === 0) el.style.setProperty(n, next[n]); else el.style[n] = next[n];
        }
        el.__st = next;
    }

    function setAttr(el, name, v) {
        var cache = el.__v || (el.__v = {});
        if (name === 'style') { setStyle(el, v); return; }
        if (cache[name] === v) return;
        cache[name] = v;
        if (name === 'class') { el.setAttribute('class', v == null ? '' : String(v)); return; }
        if (v == null || v === false) el.removeAttribute(name);
        else el.setAttribute(name, v === true ? '' : String(v));
    }

    function listen(el, evt) {
        var hs = el.__h || (el.__h = {});
        if (evt in hs) return;
        hs[evt] = null;
        // Like React, discrete events (clicks) re-render right away so the next
        // click sees fresh handlers; continuous ones wait for the frame.
        var continuous = evt === 'scroll' || evt === 'pointermove';
        el.addEventListener(evt, function (e) {
            var h = el.__h[evt];
            if (typeof h === 'function') h(e);
            if (queued && !continuous) render();
        }, evt === 'scroll' ? { passive: true } : false);
    }

    function bindEl(el, scope) {
        var attrs = el.attributes;
        for (var i = 0; i < attrs.length; i++) {
            var a = attrs[i].name;
            if (a.indexOf('data-b-') === 0) setAttr(el, a.slice(7), get(scope, attrs[i].value));
            else if (a.indexOf('data-on-') === 0) { listen(el, a.slice(8)); el.__h[a.slice(8)] = get(scope, attrs[i].value); }
            else if (a === 'data-t') {
                var t = get(scope, attrs[i].value);
                t = t == null ? '' : String(t);
                if (el.__t !== t) { el.textContent = t; el.__t = t; }
            }
        }
    }

    function isBound(el) {
        var attrs = el.attributes;
        for (var i = 0; i < attrs.length; i++) {
            var a = attrs[i].name;
            if (a.indexOf('data-b-') === 0 || a.indexOf('data-on-') === 0 || a === 'data-t') return true;
        }
        return false;
    }

    function boundWithin(el) {
        var out = isBound(el) ? [el] : [];
        var all = el.getElementsByTagName('*');
        for (var i = 0; i < all.length; i++) if (isBound(all[i])) out.push(all[i]);
        return out;
    }

    function index() {
        var all = document.body.getElementsByTagName('*');
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            var lid = el.getAttribute('data-loop');
            if (lid) {
                var items = loopEls[lid] || (loopEls[lid] = []);
                var k = +el.getAttribute('data-lk');
                if (k === 0) items.push([]);
                items[items.length - 1][k] = el;
                continue;
            }
            if (isBound(el) && !(el.parentElement && el.parentElement.closest('[data-loop]'))) bound.push(el);
        }
    }

    function newItem(meta) {
        var box = meta.svg ? document.createElementNS('http://www.w3.org/2000/svg', 'svg')
                           : document.createElement('template');
        box.innerHTML = meta.tpl;
        var root = meta.svg ? box : box.content;
        return Array.prototype.slice.call(root.children);
    }

    function applyLoop(id, scope) {
        var meta = loops[id];
        var list = get(scope, meta.list) || [];
        var items = loopEls[id] || (loopEls[id] = []);
        var end = meta.end || (meta.end = document.querySelector('[data-loop-end="' + id + '"]'));
        if (!end) return;
        // Grow or shrink the rendered items to match the list length.
        while (items.length < list.length) {
            var item = newItem(meta);
            item.forEach(function (el) { end.parentNode.insertBefore(el, end); });
            items.push(item);
        }
        while (items.length > list.length) {
            items.pop().forEach(function (el) { el.remove(); });
        }
        for (var i = 0; i < items.length; i++) {
            var s = Object.create(scope);
            s[meta.as] = list[i];
            items[i].forEach(function (el) { boundWithin(el).forEach(function (b) { bindEl(b, s); }); });
        }
    }

    function render() {
        queued = false;
        var vals = (inst.renderVals ? inst.renderVals() : {}) || {};
        var scope = Object.assign({}, inst.props, vals);
        for (var i = 0; i < bound.length; i++) bindEl(bound[i], scope);
        for (var id in loops) applyLoop(id, scope);
    }

    function schedule() {
        if (queued) return;
        queued = true;
        requestAnimationFrame(function () { if (queued) render(); });
    }

    function DCLogic(props) {
        this.props = props || {};
        if (this.state === undefined) this.state = null;
    }
    DCLogic.prototype.setState = function (patch) {
        if (typeof patch === 'function') patch = patch(this.state || {}, this.props);
        this.state = Object.assign({}, this.state, patch);
        schedule();
    };
    DCLogic.prototype.forceUpdate = function () { schedule(); };

    window.DCLogic = DCLogic;

    /** Called by /assets/js/pages/<page>.js with the page's Component class. */
    window.tryllBoot = function (Component, propsMeta) {
        var props = {};
        for (var k in propsMeta || {}) {
            if (propsMeta[k] && propsMeta[k].default !== undefined) props[k] = propsMeta[k].default;
        }
        var lj = document.getElementById('dc-loops');
        loops = lj ? JSON.parse(lj.textContent) : {};
        index();
        inst = new Component(props);
        inst.props = props;
        render();
        if (inst.componentDidMount) inst.componentDidMount();
        // Layout-dependent values (carousel sizes, mobile art) follow the viewport.
        var rt;
        window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(schedule, 100); });
    };
})();
