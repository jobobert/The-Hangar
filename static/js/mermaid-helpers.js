(function (global) {
    let _initialized = false;
    let _renderCounter = 0;

    function ensureInit() {
        if (_initialized) return;
        // suppressErrorRendering: without it, mermaid.render() injects its
        // own "bomb" error graphic directly into the document (not into
        // our target container) on any parse failure — including the
        // routine case of an empty/still-being-typed diagram — leaving a
        // stray error box on the page that our try/catch below can't
        // clean up because it isn't ours to clean up. With it, a failed
        // render only rejects the promise, matching the old Viz.js call
        // sites' "leave the last good render in place" behavior.
        mermaid.initialize({ startOnLoad: false, securityLevel: 'loose', suppressErrorRendering: true });
        _initialized = true;
    }

    // kind: 'none'|'arrow'|'circle'|'cross' -> the marker character Mermaid
    // expects adjacent to the dashes at that end (arrow is directional —
    // '<' pointing in at the start, '>' pointing out at the end; circle/
    // cross use the same character at either end).
    function markerChar(kind, position) {
        if (kind === 'arrow') return position === 'start' ? '<' : '>';
        if (kind === 'circle') return 'o';
        if (kind === 'cross') return 'x';
        return '';
    }

    // Matches one of our generated/hand-written labeled edge lines, with
    // or without arrowhead markers on either side: "A -- \"text\" --- B"
    // (the base, no-marker form every generator emits — note the
    // asymmetric 2/3 dash split, which is what Mermaid actually parses as
    // a plain no-arrow link with text), "A <-- \"text\" --x B" (both
    // marked), or a mix like "A o-- \"text\" -- B" (only the start
    // marked — note the END correctly drops to a bare 2 dashes here, not
    // 3, once the split is no longer the plain-link base form). Allowing
    // 2-3 dashes on both sides (rather than a fixed alternation) covers
    // every combination without the two sides needing to agree on count.
    // Capture groups: indent, from, label, to.
    const LABELED_EDGE_RE = /^(\s*)(\S+)\s*[<ox]?-{2,3}\s*"([^"]*)"\s*-{2,3}[>ox]?\s*(\S+)\s*$/;

    // Recomputes linkStyle lines AND rewrites each labeled edge's
    // arrowhead markers to match its wire-type name label (in document
    // order, matching Mermaid's own internal edge indexing — legend
    // edges, then a receiver's internal port-wiring, then body
    // connections, however they appear). Never mutates the caller's
    // stored text: this is a render-time-only augmentation, so a wire
    // type's color/width/dash/arrowheads always reflect its current
    // admin-configured value without every diagram needing to be
    // re-saved, and it isn't fragile to edges being added/removed/
    // reordered live in the Connections table the way baked-in
    // positional linkStyle lines (or baked-in arrowhead characters)
    // would be. Arrowhead choice can't be a pure linkStyle CSS overlay
    // like color/width/dash — Mermaid has no CSS-time control over
    // marker shape — so it's the one property here that requires
    // rewriting the edge's own dash/marker characters, not just
    // appending a style line.
    function injectLinkStyles(text, edgeStyles) {
        if (!edgeStyles) return text;
        let base = text.replace(/^[ \t]*linkStyle\s+\d+.*$/gm, '').replace(/\n{3,}/g, '\n\n');

        base = base.replace(new RegExp(LABELED_EDGE_RE, 'gm'), (m, indent, from, label, to) => {
            const style = edgeStyles[label] || edgeStyles['default'];
            const sKind = style ? style.arrowStart : 'none';
            const eKind = style ? style.arrowEnd : 'none';
            if ((!sKind || sKind === 'none') && (!eKind || eKind === 'none')) {
                return m; // no arrowheads configured — leave the base "-- ... ---" form untouched
            }
            const sMark = markerChar(sKind, 'start');
            const eMark = markerChar(eKind, 'end');
            return `${indent}${from} ${sMark}-- "${label}" --${eMark} ${to}`;
        });

        const plain = /^\s*\S+\s*---\s*\S+\s*$/;
        const styleLines = [];
        let edgeIndex = 0;
        base.split('\n').forEach(line => {
            const m = line.match(LABELED_EDGE_RE);
            if (m) {
                const style = edgeStyles[m[3]] || edgeStyles['default'];
                if (style) {
                    const dash = style.style === 'dashed' ? ',stroke-dasharray:5 5'
                        : (style.style === 'dotted' ? ',stroke-dasharray:1 3' : '');
                    styleLines.push(`linkStyle ${edgeIndex} stroke:${style.color},stroke-width:${style.width}px${dash}`);
                }
                edgeIndex++;
            } else if (plain.test(line)) {
                edgeIndex++;
            }
        });
        return base + (styleLines.length ? '\n\n' + styleLines.join('\n') : '');
    }

    // Renders mermaidText into container; on invalid input, leaves the last
    // good render in place (mirrors the old Viz.js call sites' behavior).
    // Pass opts.edgeStyles (a name -> {color,width,style} map) to have
    // wire-type styling computed live via injectLinkStyles() above.
    async function renderMermaidInto(container, mermaidText, opts) {
        opts = opts || {};
        if (!mermaidText || !mermaidText.trim()) {
            container.innerHTML = '';
            return false;
        }
        ensureInit();
        const text = injectLinkStyles(mermaidText, opts.edgeStyles);
        const id = 'mmd-' + (++_renderCounter) + '-' + Date.now();
        try {
            const { svg } = await mermaid.render(id, text);
            container.innerHTML = svg;
            if (opts.maxWidth !== false) {
                const svgEl = container.querySelector('svg');
                if (svgEl) svgEl.style.maxWidth = opts.maxWidth || '100%';
            }
            return true;
        } catch (e) {
            if (opts.onError) opts.onError(e);
            return false;
        }
    }

    // Graphviz shape name -> Mermaid classic flowchart bracket tokens,
    // mirroring controllers/diagram.py's GRAPHVIZ_SHAPE_TO_MERMAID (kept in
    // sync manually — both are small, stable lookup tables).
    const MERMAID_SHAPE_TOKENS = {
        box: ['[', ']'], rect: ['[', ']'], square: ['[', ']'],
        circle: ['((', '))'], doublecircle: ['((', '))'],
        ellipse: ['(', ')'], oval: ['(', ')'], egg: ['(', ')'],
        diamond: ['{', '}'], Mdiamond: ['{', '}'],
        triangle: ['[/', '\\]'], invtriangle: ['[\\', '/]'],
        trapezium: ['[\\', '/]'], invtrapezium: ['[/', '\\]'],
        parallelogram: ['[/', '/]'],
        house: ['[/', '\\]'], invhouse: ['[/', '\\]'],
        pentagon: ['{{', '}}'], hexagon: ['{{', '}}'], septagon: ['{{', '}}'],
        octagon: ['{{', '}}'], doubleoctagon: ['{{', '}}'], tripleoctagon: ['{{', '}}'],
        star: ['{{', '}}'], polygon: ['{{', '}}'],
        box3d: ['[(', ')]'], component: ['[(', ')]'], cylinder: ['[(', ')]'],
        Msquare: ['[', ']'], Mcircle: ['((', '))'],
        plaintext: ['[', ']'], none: ['[', ']'], note: ['[', ']'],
        tab: ['[', ']'], folder: ['[', ']'],
        cds: ['[', ']'], promoter: ['[', ']'], rpromoter: ['[', ']'],
        terminator: ['[', ']'], utr: ['[', ']'],
        larrow: ['[', ']'], rarrow: ['[', ']'],
        point: ['((', '))'],
    };

    function mermaidShapeTokens(shape) {
        return MERMAID_SHAPE_TOKENS[shape] || ['[', ']'];
    }

    global.renderMermaidInto = renderMermaidInto;
    global.injectMermaidLinkStyles = injectLinkStyles;
    global.mermaidMarkerChar = markerChar;
    global.MERMAID_SHAPE_TOKENS = MERMAID_SHAPE_TOKENS;
    global.mermaidShapeTokens = mermaidShapeTokens;
})(window);
