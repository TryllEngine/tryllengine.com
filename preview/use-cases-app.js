// use-cases-app.js
// Logic for the 3 modes: Atlas, Console, Playground.

(function () {
    const USE_CASES = window.USE_CASES || [];
    const CATEGORIES = window.CATEGORIES || [];
    const GENRES = window.GENRES || [];

    // --- Status bucketing -------------------------------------------------
    // Buckets: now (SLM + embeddings + memory)
    //          soon (TTS, STT, RAG)
    //          later (Vision, image, music)
    //          far (experimental / speculative feasibility)
    // Rules:
    //   - If feasibility is 'speculative' -> far
    //   - Else if available_now=true -> now
    //   - Else inspect models string for coming-soon vs later tech
    function classify(uc) {
        if (uc.feasibility === 'speculative') return 'far';
        if (uc.available_now) return 'now';
        const m = (uc.models || '').toLowerCase();
        if (m.includes('tts') || m.includes('stt') || m.includes('rag') || m.includes('knowledge base') || m.includes('xtts') || m.includes('kokoro') || m.includes('piper')) return 'soon';
        if (m.includes('vlm') || m.includes('vision') || m.includes('mediapipe') || m.includes('sdxl') || m.includes('lcm') || m.includes('image') || m.includes('musicgen') || m.includes('music') || m.includes('audio') || m.includes('sfx') || m.includes('cnn') || m.includes('rl') || m.includes('policy') || m.includes('lora') || m.includes('florence')) return 'later';
        return 'later';
    }

    // VRAM estimate by model signature
    function vramFor(uc) {
        const m = (uc.models || '').toLowerCase();
        let v = 0;
        if (m.includes('slm')) v += 6;
        if (m.includes('embedding')) v += 1;
        if (m.includes('tts') || m.includes('kokoro') || m.includes('piper') || m.includes('xtts')) v += 2;
        if (m.includes('stt')) v += 1;
        if (m.includes('lora')) v += 1;
        if (m.includes('rl') || m.includes('policy')) v += 1;
        if (m.includes('vlm') || m.includes('vision') || m.includes('florence')) v += 4;
        if (m.includes('sdxl') || m.includes('lcm')) v += 6;
        if (m.includes('musicgen') || m.includes('music')) v += 4;
        if (m.includes('mediapipe') || m.includes('cnn') || m.includes('classifier')) v += 1;
        if (v === 0) v = 4;
        return Math.min(v, 24);
    }

    // Pre-process
    USE_CASES.forEach(uc => {
        uc._status = classify(uc);
        uc._vram = vramFor(uc);
    });

    const STATUS_META = {
        now:   { label: 'Available now', cls: 'status-now' },
        soon:  { label: 'Coming soon',    cls: 'status-soon' },
        later: { label: 'Later',          cls: 'status-later' },
        far:   { label: 'Experimental',   cls: 'status-far' }
    };

    const FEAS_META = {
        proven:       { label: 'Proven',       cls: 'feas-proven' },
        likely:       { label: 'Likely',       cls: 'feas-likely' },
        experimental: { label: 'Experimental', cls: 'feas-experimental' },
        speculative:  { label: 'Speculative',  cls: 'feas-speculative' }
    };

    const CAT_MAP = Object.fromEntries(CATEGORIES.map(c => [c.id, c]));
    const GENRE_MAP = Object.fromEntries(GENRES.map(g => [g.id, g]));

    // --- Hero stats --------------------------------------------------------
    (function heroStats() {
        const now = USE_CASES.filter(u => u._status === 'now').length;
        const soon = USE_CASES.filter(u => u._status === 'soon').length;
        const exp = USE_CASES.filter(u => u._status === 'later' || u._status === 'far').length;
        document.getElementById('stat-now').textContent = now;
        document.getElementById('stat-soon').textContent = soon;
        document.getElementById('stat-exp').textContent = exp;
        document.getElementById('stat-genres').textContent = GENRES.length;
    })();

    // --- Mode switch -------------------------------------------------------
    const modeButtons = document.querySelectorAll('.mode-btn');
    const panels = { atlas: document.getElementById('mode-atlas'), console: document.getElementById('mode-console'), playground: document.getElementById('mode-playground') };
    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;
            modeButtons.forEach(b => b.classList.toggle('active', b === btn));
            Object.keys(panels).forEach(k => panels[k].classList.toggle('hidden', k !== mode));
            try { localStorage.setItem('tryll_uc_mode', mode); } catch (e) {}
        });
    });
    // Restore mode
    try {
        const saved = localStorage.getItem('tryll_uc_mode');
        if (saved && panels[saved]) {
            modeButtons.forEach(b => b.classList.toggle('active', b.dataset.mode === saved));
            Object.keys(panels).forEach(k => panels[k].classList.toggle('hidden', k !== saved));
        }
    } catch (e) {}

    // ===================== VARIATION A — ATLAS =============================
    const genreList = document.getElementById('genre-list');
    const atlasGrid = document.getElementById('atlas-grid');
    const atlasGenreName = document.getElementById('atlas-genre-name');
    const atlasGenreBlurb = document.getElementById('atlas-genre-blurb');
    const atlasCount = document.getElementById('atlas-count');
    const atlasTotal = document.getElementById('atlas-total');
    let currentGenre = 'rpg';

    function countForGenre(gid) {
        return USE_CASES.filter(u => u.genres.includes(gid)).length;
    }

    function renderGenreList() {
        genreList.innerHTML = '';
        GENRES.forEach(g => {
            const btn = document.createElement('button');
            btn.className = 'genre-tab' + (g.id === currentGenre ? ' active' : '');
            btn.innerHTML = `
                <span>${g.name}</span>
                <span class="count">${countForGenre(g.id)}</span>
            `;
            btn.addEventListener('click', () => {
                currentGenre = g.id;
                renderGenreList();
                renderAtlasCards();
            });
            genreList.appendChild(btn);
        });
    }

    function activeStatusFilters() {
        return Array.from(document.querySelectorAll('.atlas-status:checked')).map(c => c.value);
    }

    function renderAtlasCards() {
        const g = GENRE_MAP[currentGenre];
        atlasGenreName.textContent = g.name;
        atlasGenreBlurb.textContent = g.blurb;

        const allForGenre = USE_CASES.filter(u => u.genres.includes(currentGenre));
        const statuses = activeStatusFilters();
        const visible = allForGenre.filter(u => statuses.includes(u._status));

        atlasTotal.textContent = allForGenre.length;
        atlasCount.textContent = visible.length;

        atlasGrid.innerHTML = '';
        if (!visible.length) {
            atlasGrid.innerHTML = `<div class="col-span-full text-center py-12" style="color: rgba(255,255,255,0.5);">
                <div class="mono text-sm">No mechanics match. Try enabling more statuses.</div>
            </div>`;
            return;
        }
        visible.forEach(u => {
            const cat = CAT_MAP[u.cat];
            const st = STATUS_META[u._status];
            const feas = FEAS_META[u.feasibility];
            const card = document.createElement('article');
            card.className = 'card-base atlas-card';
            card.innerHTML = `
                <div class="flex items-start justify-between gap-3">
                    <div>
                        <span class="id">${u.id.padStart(4, '0')} · ${cat ? cat.short : u.cat}</span>
                        <h3 class="mt-1">${u.title}</h3>
                    </div>
                    <span class="badge ${st.cls}" style="flex-shrink:0;"><span class="badge-dot"></span>${st.label}</span>
                </div>
                <p>${u.blurb}</p>
                <div class="atlas-meta">
                    <span class="atlas-model">${u.models}</span>
                    <span class="atlas-model">~${u._vram}GB</span>
                    <span class="mono text-[10.5px] ${feas.cls}" style="margin-left:auto; letter-spacing:0.06em; text-transform:uppercase;">${feas.label}</span>
                </div>
            `;
            atlasGrid.appendChild(card);
        });
    }

    document.querySelectorAll('.atlas-status').forEach(cb => cb.addEventListener('change', renderAtlasCards));

    renderGenreList();
    renderAtlasCards();

    // ===================== VARIATION B — CONSOLE ===========================
    const cGenre = document.getElementById('c-genre');
    const cStatus = document.getElementById('c-status');
    const cVram = document.getElementById('c-vram');
    const cVramLabel = document.getElementById('c-vram-label');
    const cRows = document.getElementById('console-rows');
    const cCount = document.getElementById('console-count');
    const cFit = document.getElementById('console-fitable');
    const cExec = document.getElementById('console-exec');
    const cQuery = document.getElementById('console-query');

    // populate genre dropdown
    GENRES.forEach(g => {
        const o = document.createElement('option');
        o.value = g.id; o.textContent = g.name.toLowerCase();
        cGenre.appendChild(o);
    });

    function renderConsole() {
        const genre = cGenre.value;
        const status = cStatus.value;
        const budget = parseInt(cVram.value, 10);
        cVramLabel.textContent = budget + 'GB';

        let filtered = USE_CASES.slice();
        if (genre !== 'all') filtered = filtered.filter(u => u.genres.includes(genre));
        if (status !== 'all') filtered = filtered.filter(u => u._status === status);

        // query string
        cQuery.textContent = `--genre=${genre} --status=${status} --vram=${budget}`;

        cRows.innerHTML = '';
        const fitCount = filtered.filter(u => u._vram <= budget).length;
        cCount.textContent = filtered.length;
        cFit.textContent = fitCount;
        cExec.textContent = (0.04 + Math.random() * 0.09).toFixed(2);

        if (!filtered.length) {
            cRows.innerHTML = `<div class="p-8 text-center mono text-sm" style="color: rgba(255,255,255,0.5);">no results. adjust filters.</div>`;
            return;
        }

        filtered.forEach(u => {
            const st = STATUS_META[u._status];
            const fits = u._vram <= budget;
            const row = document.createElement('div');
            row.className = 'console-row';
            if (!fits) row.style.opacity = '0.42';
            row.innerHTML = `
                <div class="cid">${u.id.padStart(4, '0')}</div>
                <div>
                    <div class="ctitle">${u.title}</div>
                    <div class="cblurb">${u.blurb}</div>
                </div>
                <div class="cmodel">${u.models}</div>
                <div><span class="badge ${st.cls}"><span class="badge-dot"></span>${st.label}</span></div>
                <div class="cvram">${fits ? '' : '<span style="color:#fcd34d;">over · </span>'}~${u._vram}GB</div>
            `;
            cRows.appendChild(row);
        });
    }

    [cGenre, cStatus, cVram].forEach(el => el.addEventListener('input', renderConsole));
    cGenre.value = 'rpg';
    renderConsole();

    // ===================== VARIATION C — PLAYGROUND ========================
    const pgGenreChips = document.getElementById('pg-genre-chips');
    const pgCatChips = document.getElementById('pg-cat-chips');
    const pgVram = document.getElementById('pg-vram');
    const pgVramLabel = document.getElementById('pg-vram-label');
    const pgSpec = document.getElementById('pg-spec-container');
    const pgTotal = document.getElementById('pg-total');
    const pgNow = document.getElementById('pg-now');
    const pgBar = document.getElementById('pg-bar');
    const pgPct = document.getElementById('pg-pct');
    const pgGenreName = document.getElementById('pg-genre-name');

    let pgGenre = 'rpg';
    const pgCatsOn = new Set(CATEGORIES.map(c => c.id));

    function renderGenreChips() {
        pgGenreChips.innerHTML = '';
        GENRES.forEach(g => {
            const b = document.createElement('button');
            b.className = 'pg-chip' + (g.id === pgGenre ? ' on' : '');
            b.textContent = g.name;
            b.addEventListener('click', () => { pgGenre = g.id; renderGenreChips(); renderPlayground(); });
            pgGenreChips.appendChild(b);
        });
    }

    function renderCatChips() {
        pgCatChips.innerHTML = '';
        CATEGORIES.forEach(c => {
            const b = document.createElement('button');
            b.className = 'pg-chip' + (pgCatsOn.has(c.id) ? ' on' : '');
            b.textContent = c.short;
            b.addEventListener('click', () => {
                if (pgCatsOn.has(c.id)) pgCatsOn.delete(c.id); else pgCatsOn.add(c.id);
                renderCatChips();
                renderPlayground();
            });
            pgCatChips.appendChild(b);
        });
    }

    function renderPlayground() {
        const budget = parseInt(pgVram.value, 10);
        pgVramLabel.textContent = budget;

        const g = GENRE_MAP[pgGenre];
        pgGenreName.textContent = g.name;

        const selected = USE_CASES.filter(u =>
            u.genres.includes(pgGenre) &&
            pgCatsOn.has(u.cat) &&
            u._vram <= budget
        );

        const total = selected.length;
        const nowCount = selected.filter(u => u._status === 'now').length;
        const pct = total ? Math.round((nowCount / total) * 100) : 0;

        // Animate
        [pgTotal, pgNow, pgPct].forEach(el => { el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); });
        pgTotal.textContent = total;
        pgNow.textContent = nowCount;
        pgPct.textContent = pct;
        pgBar.style.width = pct + '%';

        // Group by category
        pgSpec.innerHTML = '';
        if (!selected.length) {
            pgSpec.innerHTML = `<div class="p-10 text-center mono text-sm" style="color: rgba(255,255,255,0.5);">
                No mechanics fit this configuration. Try a bigger VRAM budget or more categories.
            </div>`;
            return;
        }

        const byCat = {};
        selected.forEach(u => { (byCat[u.cat] = byCat[u.cat] || []).push(u); });

        CATEGORIES.forEach(c => {
            const items = byCat[c.id];
            if (!items) return;
            items.forEach(u => {
                const st = STATUS_META[u._status];
                const row = document.createElement('div');
                row.className = 'pg-cap-row';
                row.innerHTML = `
                    <span class="cat-tag">${c.short}</span>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-baseline gap-3 flex-wrap">
                            <span class="heading-tertiary text-base" style="font-size: 15px;">${u.title}</span>
                            <span class="badge ${st.cls}"><span class="badge-dot"></span>${st.label}</span>
                        </div>
                        <p class="mt-1 text-sm" style="color: rgba(255,255,255,0.62); line-height: 1.5;">${u.blurb}</p>
                        <div class="mt-1.5 mono text-[10.5px]" style="color: rgba(255,255,255,0.45); letter-spacing: 0.04em;">
                            ${u.models} · ~${u._vram}GB
                        </div>
                    </div>
                `;
                pgSpec.appendChild(row);
            });
        });
    }

    pgVram.addEventListener('input', renderPlayground);
    renderGenreChips();
    renderCatChips();
    renderPlayground();

    // --- Mobile menu -------------------------------------------------------
    const mmBtn = document.getElementById('mobile-menu-btn');
    const mmClose = document.getElementById('mobile-menu-close');
    const mm = document.getElementById('mobile-menu');
    function openMm() { mm.classList.remove('opacity-0', 'invisible'); }
    function closeMm() { mm.classList.add('opacity-0', 'invisible'); }
    mmBtn && mmBtn.addEventListener('click', openMm);
    mmClose && mmClose.addEventListener('click', closeMm);
    mm && mm.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMm));
})();
