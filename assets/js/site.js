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
 * attributes whose value actually changed. Each element's bindings are read
 * from its data-* attributes once, so a frame costs little more than the
 * design logic itself; the animation clock (tryllClock) also rests while
 * nothing it moves is near the screen.
 */
(function () {
    'use strict';

    var UNITLESS = /^(opacity|zIndex|flex|flexGrow|flexShrink|fontWeight|lineHeight|order|zoom|orphans|widows|scale)$/;
    var inst = null;
    var queued = false;
    var loops = {};
    var bound = [];       // bound elements outside loops
    var loopEls = {};     // loop id -> [[el per child key], ...] per item

    function get(scope, parts) {
        var v = scope;
        for (var i = 0; i < parts.length && v != null; i++) v = v[parts[i]];
        return v;
    }

    // An element's bindings, read once: [kind, name, path], kind 0 = attribute,
    // 1 = event handler, 2 = text. The markup's bindings never change after baking.
    function ops(el) {
        if (el.__ops) return el.__ops;
        var out = [], attrs = el.attributes;
        for (var i = 0; i < attrs.length; i++) {
            var a = attrs[i].name;
            if (a.indexOf('data-b-') === 0) out.push([0, a.slice(7), attrs[i].value.split('.')]);
            else if (a.indexOf('data-on-') === 0) out.push([1, a.slice(8), attrs[i].value.split('.')]);
            else if (a === 'data-t') out.push([2, null, attrs[i].value.split('.')]);
        }
        el.__ops = out;
        return out;
    }

    function setStyle(el, v) {
        if (typeof v === 'string') {
            if (el.__css === v) return;
            el.style.cssText = v; el.__css = v; el.__st = {};
            changed(el);
            return;
        }
        el.__css = null;
        var prev = el.__st || {};
        var next = {};
        var diff = false;
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
            diff = true;
        }
        for (var n in next) if (prev[n] !== next[n]) {
            if (n.indexOf('--') === 0) el.style.setProperty(n, next[n]); else el.style[n] = next[n];
            diff = true;
        }
        el.__st = next;
        if (diff) changed(el);
    }

    function setAttr(el, name, v) {
        if (name === 'style') { setStyle(el, v); return; }
        var cache = el.__v || (el.__v = {});
        if (cache[name] === v) return;
        cache[name] = v;
        changed(el);
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
        var o = ops(el);
        for (var i = 0; i < o.length; i++) {
            var op = o[i], v = get(scope, op[2]);
            if (op[0] === 0) setAttr(el, op[1], v);
            else if (op[0] === 1) { listen(el, op[1]); el.__h[op[1]] = v; }
            else {
                v = v == null ? '' : String(v);
                if (el.__t !== v) { el.textContent = v; el.__t = v; changed(el); }
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

    // The bound elements of one loop item (its elements and everything inside them), found once.
    function itemBound(item) {
        if (!item.bound) {
            item.bound = [];
            item.forEach(function (el) { item.bound.push.apply(item.bound, boundWithin(el)); });
        }
        return item.bound;
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
        var list = get(scope, meta.path || (meta.path = meta.list.split('.'))) || [];
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
            var b = itemBound(items[i]);
            for (var j = 0; j < b.length; j++) if (!resting(b[j])) bindEl(b[j], s);
        }
    }

    // --- What the clock animates ------------------------------------------
    // A render caused only by the clock notes every element it changes (a die's lines,
    // say); each one's box is watched, and the clock keeps running while one is near the
    // screen. Such a render also leaves alone what it moves away from the screen: a die
    // further down catches up once it comes near. Renders after anything else (a click,
    // a timer or observer in the design logic, a resize) update everything and note
    // nothing, so a menu that was opened doesn't keep the clock awake.
    var byClock = false;    // since the last render, state changed from the clock...
    var byOther = false;    // ...or from anything else
    var tracking = false;   // this render is the clock's alone
    var near = 0;           // watched boxes near the screen
    var watcher = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
            var was = !!e.target.__near;
            e.target.__near = e.isIntersecting;
            if (was !== e.isIntersecting) near += e.isIntersecting ? 1 : -1;
        });
        if (near > 0) wakeClocks();
    }, { rootMargin: '200px 0px' }) : null;

    function changed(el) {
        if (!tracking || el.__box) return;
        var box = el;
        while (box.ownerSVGElement) box = box.ownerSVGElement;   // a die's line: watch its whole drawing
        el.__box = box;
        if (box.__watch) return;
        box.__watch = true;
        watcher.observe(box);
    }

    // Moved by the clock and away from the screen, in a render that is the clock's alone
    // (a box counts as near until the observer first reports on it).
    function resting(el) {
        return tracking && el.__box !== undefined && el.__box.__near === false;
    }

    function render() {
        queued = false;
        tracking = !!watcher && byClock && !byOther;
        byClock = byOther = false;
        var vals = (inst.renderVals ? inst.renderVals() : {}) || {};
        var scope = Object.assign({}, inst.props, vals);
        for (var i = 0; i < bound.length; i++) if (!resting(bound[i])) bindEl(bound[i], scope);
        for (var id in loops) applyLoop(id, scope);
        tracking = false;
    }

    function schedule() {
        if (queued) return;
        queued = true;
        requestAnimationFrame(function () { if (queued) render(); });
    }

    // --- Animation clock ---------------------------------------------------
    var clocks = [];
    var ticking = false;    // inside a clock tick: the setState it makes is the clock's
    var busyUntil = 0;      // after loading or any other change the clock runs at least this long

    function activity() {
        byOther = true;
        busyUntil = performance.now() + 2000;
        wakeClocks();
    }

    function awake(now) {
        return !watcher || near > 0 || now < busyUntil;
    }

    function wakeClocks() {
        for (var i = 0; i < clocks.length; i++) run(clocks[i]);
    }

    function step(c, now) {
        if (c.last === null) c.last = now;
        if (now - c.last < 10) return;
        var dt = Math.min((now - c.last) / 1000, 0.1);
        c.last = now;
        ticking = true;
        try { c.tick(dt); } finally { ticking = false; }
    }

    function run(c) {
        if (c.on) return;
        c.on = true;
        c.last = null;
        clearTimeout(c.probe);
        requestAnimationFrame(function frame(now) {
            if (awake(now)) {
                step(c, now);
                requestAnimationFrame(frame);
            } else {
                c.on = false;
                rest(c);
            }
        });
    }

    // Nothing the clock moves is near the screen: one step a second instead of every frame,
    // so an animation that starts later, or one not seen yet, still gets noticed.
    function rest(c) {
        c.probe = setTimeout(function () {
            if (c.on) return;
            var now = performance.now();
            c.last = now - 100;
            step(c, now);
            if (awake(now)) run(c); else rest(c);
        }, 1000);
    }

    function DCLogic(props) {
        this.props = props || {};
        if (this.state === undefined) this.state = null;
    }
    DCLogic.prototype.setState = function (patch) {
        if (typeof patch === 'function') patch = patch(this.state || {}, this.props);
        this.state = Object.assign({}, this.state, patch);
        if (ticking) byClock = true; else activity();
        schedule();
    };
    DCLogic.prototype.forceUpdate = function () { activity(); schedule(); };

    window.DCLogic = DCLogic;

    /**
     * Animation clock for the design logic. build.py swaps it in for the design's
     * setInterval of 40 ms, whose 25 steps a second showed on the dice. Calls
     * tick(seconds since the last call) on animation frames, at most every 10 ms;
     * like any animation frame, it pauses while the tab is hidden. While nothing it
     * moves is near the screen it steps once a second instead (at most 0.1 s a step,
     * as after a hidden tab), until something it moves comes near or anything else
     * changes the page.
     */
    window.tryllClock = function (tick) {
        var c = { tick: tick, last: null, on: false, probe: 0 };
        clocks.push(c);
        run(c);
    };

    /** Called by /assets/js/pages/<page>.js with the page's Component class. */
    window.tryllBoot = function (Component, propsMeta) {
        var props = {};
        for (var k in propsMeta || {}) {
            if (propsMeta[k] && propsMeta[k].default !== undefined) props[k] = propsMeta[k].default;
        }
        var lj = document.getElementById('dc-loops');
        loops = lj ? JSON.parse(lj.textContent) : {};
        index();
        busyUntil = performance.now() + 2000;
        inst = new Component(props);
        inst.props = props;
        render();
        if (inst.componentDidMount) inst.componentDidMount();
        // Layout-dependent values (carousel sizes, mobile art) follow the viewport. What a
        // resize changes isn't the clock's, even when a clock frame renders it first.
        var rt;
        window.addEventListener('resize', function () {
            byOther = true;
            clearTimeout(rt);
            rt = setTimeout(function () { activity(); schedule(); }, 100);
        });
    };
})();
