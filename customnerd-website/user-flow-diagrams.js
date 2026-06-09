/**
 * Inline SVG help diagrams for Configuration → User Flow sections.
 * Injected into elements with data-user-flow-diagram="<key>".
 */
(function () {
    'use strict';

    var DIAGRAMS = {
        'normal-search': {
            caption: 'Turn on to show a database search option on the question page. Users can search your article index alongside their question.',
            svg: '<svg class="flow-help-diagram" viewBox="0 0 640 196" width="100%" height="196" role="img" aria-labelledby="ufs-title ufs-desc">' +
                '<title id="ufs-title">Normal Search on the question page</title>' +
                '<desc id="ufs-desc">When off, users only ask a question. When on, a search-articles checkbox appears and queries your database.</desc>' +
                '<defs>' +
                '<linearGradient id="ufs-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="ufs-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#94A3B8"/></marker>' +
                '<marker id="ufs-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="8" y="8" width="296" height="172" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="156" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Hidden</text>' +
                '<text x="156" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="36" y="68" width="240" height="88" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="52" y="88" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Ask a question…</text>' +
                '<rect x="52" y="100" width="200" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="52" y="116" width="72" height="24" rx="6" fill="#E2E8F0"/>' +
                '<text x="88" y="132" text-anchor="middle" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Submit</text>' +
                '<rect x="108" y="8" width="72" height="20" rx="10" fill="#F1F5F9"/>' +
                '<text x="144" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">Question only</text>' +
                '<rect x="336" y="8" width="296" height="172" rx="12" fill="url(#ufs-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Search enabled</text>' +
                '<text x="484" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="364" y="58" width="240" height="108" rx="10" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="380" y="78" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Ask a question…</text>' +
                '<rect x="380" y="86" width="180" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="380" y="102" width="14" height="14" rx="3" fill="#007bff" stroke="#007bff" stroke-width="1.5"/>' +
                '<path d="M384 109 L387 112 L392 106" stroke="#FFFFFF" stroke-width="1.5" fill="none" stroke-linecap="round"/>' +
                '<text x="402" y="113" font-size="10" font-weight="600" fill="#334155" font-family="system-ui,sans-serif">Search articles</text>' +
                '<line x1="484" y1="124" x2="484" y2="136" stroke="#007bff" stroke-width="1.5" marker-end="url(#ufs-arrow-blue)"/>' +
                '<circle cx="484" cy="150" r="16" fill="#FFFFFF" stroke="#007bff" stroke-width="2"/>' +
                '<ellipse cx="484" cy="148" rx="8" ry="5" fill="none" stroke="#007bff" stroke-width="1.5"/>' +
                '<rect x="478" y="154" width="12" height="8" rx="1" fill="#007bff" opacity="0.3"/>' +
                '<rect x="452" y="168" width="20" height="14" rx="2" fill="#BFDBFE"/><rect x="476" y="168" width="20" height="14" rx="2" fill="#BFDBFE"/><rect x="500" y="168" width="20" height="14" rx="2" fill="#007bff" opacity="0.6"/>' +
                '<rect x="548" y="8" width="76" height="20" rx="10" fill="#DCFCE7"/>' +
                '<text x="586" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Database</text>' +
                '</svg>'
        },

        'id-specific-search': {
            caption: 'Turn on to let users paste article IDs and fetch those records directly instead of a keyword search.',
            svg: '<svg class="flow-help-diagram" viewBox="0 0 640 196" width="100%" height="196" role="img" aria-labelledby="uid-title uid-desc">' +
                '<title id="uid-title">ID Specific Search on the question page</title>' +
                '<desc id="uid-desc">When off, no ID field appears. When on, users enter IDs and the app fetches those articles.</desc>' +
                '<defs>' +
                '<linearGradient id="uid-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uid-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="8" y="8" width="296" height="172" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="156" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Hidden</text>' +
                '<text x="156" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="36" y="68" width="240" height="88" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="52" y="88" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Ask a question…</text>' +
                '<rect x="52" y="100" width="200" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="108" y="8" width="72" height="20" rx="10" fill="#F1F5F9"/>' +
                '<text x="144" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">No ID field</text>' +
                '<rect x="336" y="8" width="296" height="172" rx="12" fill="url(#uid-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">ID lookup</text>' +
                '<text x="484" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="364" y="58" width="240" height="36" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="380" y="80" font-size="10" font-weight="600" fill="#334155" font-family="system-ui,sans-serif">Article IDs</text>' +
                '<text x="380" y="86" font-size="9" fill="#64748B" font-family="monospace">1042, 8821, 330</text>' +
                '<line x1="484" y1="94" x2="484" y2="108" stroke="#007bff" stroke-width="1.5" marker-end="url(#uid-arrow-blue)"/>' +
                '<rect x="420" y="112" width="128" height="28" rx="6" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="130" text-anchor="middle" font-size="10" fill="#334155" font-family="system-ui,sans-serif">Fetch by ID</text>' +
                '<line x1="484" y1="140" x2="484" y2="152" stroke="#007bff" stroke-width="1.5" marker-end="url(#uid-arrow-blue)"/>' +
                '<rect x="438" y="156" width="36" height="20" rx="3" fill="#007bff" opacity="0.85"/><text x="456" y="170" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">1042</text>' +
                '<rect x="478" y="156" width="36" height="20" rx="3" fill="#007bff" opacity="0.55"/><text x="496" y="170" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">8821</text>' +
                '<rect x="518" y="156" width="36" height="20" rx="3" fill="#007bff" opacity="0.35"/><text x="536" y="170" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">330</text>' +
                '<rect x="548" y="8" width="76" height="20" rx="10" fill="#DCFCE7"/>' +
                '<text x="586" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Exact match</text>' +
                '</svg>'
        },

        'local-document-search': {
            caption: 'Turn on to let users upload PDFs on the question page. Uploaded text is included when the Nerd answers.',
            svg: '<svg class="flow-help-diagram" viewBox="0 0 640 196" width="100%" height="196" role="img" aria-labelledby="uloc-title uloc-desc">' +
                '<title id="uloc-title">Local Document Search on the question page</title>' +
                '<desc id="uloc-desc">When off, no upload option. When on, users attach PDFs that feed into the answer.</desc>' +
                '<defs>' +
                '<linearGradient id="uloc-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uloc-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="8" y="8" width="296" height="172" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="156" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Hidden</text>' +
                '<text x="156" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="36" y="68" width="240" height="88" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="52" y="92" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Question only — no uploads</text>' +
                '<rect x="52" y="104" width="200" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="108" y="8" width="72" height="20" rx="10" fill="#F1F5F9"/>' +
                '<text x="144" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">No PDFs</text>' +
                '<rect x="336" y="8" width="296" height="172" rx="12" fill="url(#uloc-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">PDF upload</text>' +
                '<text x="484" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="380" y="62" width="88" height="52" rx="6" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5" stroke-dasharray="4 3"/>' +
                '<path d="M424 74 L424 96 M414 84 L424 74 L434 84" stroke="#007bff" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
                '<text x="424" y="108" text-anchor="middle" font-size="9" fill="#64748B" font-family="system-ui,sans-serif">Upload PDF</text>' +
                '<rect x="476" y="68" width="108" height="44" rx="4" fill="#FFFFFF" stroke="#DC2626" stroke-width="1.5"/>' +
                '<text x="488" y="84" font-size="9" font-weight="700" fill="#DC2626" font-family="system-ui,sans-serif">PDF</text>' +
                '<rect x="488" y="90" width="80" height="4" rx="2" fill="#FECACA"/><rect x="488" y="98" width="60" height="4" rx="2" fill="#FECACA"/>' +
                '<line x1="484" y1="120" x2="484" y2="134" stroke="#007bff" stroke-width="1.5" marker-end="url(#uloc-arrow-blue)"/>' +
                '<rect x="364" y="138" width="240" height="36" rx="8" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="380" y="156" font-size="10" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Answer uses your document</text>' +
                '<rect x="380" y="162" width="160" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="548" y="8" width="76" height="20" rx="10" fill="#FEF3C7"/>' +
                '<text x="586" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#92400E" font-family="system-ui,sans-serif">Local files</text>' +
                '</svg>'
        },

        'query-cleaning': {
            caption: 'Turn on to run AI-generated queries through clean_query() before searching. Parses JSON into a flat, capped list of search strings.',
            svg: '<svg class="flow-help-diagram" viewBox="0 0 640 196" width="100%" height="196" role="img" aria-labelledby="uqc-title uqc-desc">' +
                '<title id="uqc-title">Query Cleaning in the search pipeline</title>' +
                '<desc id="uqc-desc">When off, raw LLM output may reach search. When on, clean_query normalizes expanded_queries into usable strings.</desc>' +
                '<defs>' +
                '<linearGradient id="uqc-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uqc-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#94A3B8"/></marker>' +
                '<marker id="uqc-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="8" y="8" width="296" height="172" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="156" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Cleaning off</text>' +
                '<text x="156" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="28" y="64" width="120" height="40" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="88" y="82" text-anchor="middle" font-size="10" fill="#334155" font-family="system-ui,sans-serif">LLM output</text>' +
                '<text x="88" y="96" text-anchor="middle" font-size="8" fill="#94A3B8" font-family="monospace">{ messy… }</text>' +
                '<line x1="148" y1="84" x2="168" y2="84" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uqc-arrow)"/>' +
                '<circle cx="200" cy="84" r="18" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>' +
                '<circle cx="196" cy="82" r="5" fill="none" stroke="#94A3B8" stroke-width="1.5"/>' +
                '<line x1="200" y1="86" x2="208" y2="92" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>' +
                '<line x1="218" y1="84" x2="268" y2="84" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uqc-arrow)"/>' +
                '<rect x="268" y="68" width="28" height="32" rx="3" fill="#FECACA" stroke="#F87171" stroke-width="1" opacity="0.7"/>' +
                '<text x="282" y="88" text-anchor="middle" font-size="8" fill="#991B1B" font-family="system-ui,sans-serif">?</text>' +
                '<rect x="108" y="8" width="72" height="20" rx="10" fill="#FEE2E2"/>' +
                '<text x="144" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#991B1B" font-family="system-ui,sans-serif">Unparsed</text>' +
                '<rect x="336" y="8" width="296" height="172" rx="12" fill="url(#uqc-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Cleaning on</text>' +
                '<text x="484" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="356" y="64" width="100" height="40" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="406" y="82" text-anchor="middle" font-size="10" fill="#334155" font-family="system-ui,sans-serif">LLM JSON</text>' +
                '<text x="406" y="96" text-anchor="middle" font-size="8" fill="#64748B" font-family="monospace">expanded_queries</text>' +
                '<line x1="456" y1="84" x2="472" y2="84" stroke="#007bff" stroke-width="1.5" marker-end="url(#uqc-arrow-blue)"/>' +
                '<rect x="472" y="68" width="72" height="32" rx="6" fill="#007bff"/>' +
                '<text x="508" y="88" text-anchor="middle" font-size="9" font-weight="700" fill="#FFFFFF" font-family="monospace">clean_query</text>' +
                '<line x1="544" y1="84" x2="560" y2="84" stroke="#007bff" stroke-width="1.5" marker-end="url(#uqc-arrow-blue)"/>' +
                '<rect x="380" y="118" width="208" height="52" rx="8" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="396" y="136" font-size="9" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Search list</text>' +
                '<rect x="396" y="142" width="72" height="16" rx="4" fill="#BFDBFE"/><text x="432" y="153" text-anchor="middle" font-size="8" fill="#1E40AF" font-family="system-ui,sans-serif">query 1</text>' +
                '<rect x="474" y="142" width="72" height="16" rx="4" fill="#BFDBFE"/><text x="510" y="153" text-anchor="middle" font-size="8" fill="#1E40AF" font-family="system-ui,sans-serif">query 2</text>' +
                '<rect x="396" y="162" width="72" height="16" rx="4" fill="#BFDBFE" opacity="0.6"/><text x="432" y="173" text-anchor="middle" font-size="8" fill="#1E40AF" font-family="system-ui,sans-serif">query 3</text>' +
                '<rect x="548" y="8" width="76" height="20" rx="10" fill="#DCFCE7"/>' +
                '<text x="586" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Ready</text>' +
                '</svg>'
        },

        'deep-search': {
            caption: 'Turn on when one search is not enough. The app tries your question several ways, then keeps the best articles. Turn off for a quicker, simpler search.',
            svg: '<svg class="flow-help-diagram" viewBox="0 0 640 196" width="100%" height="196" role="img" aria-labelledby="uds-title uds-desc">' +
                '<title id="uds-title">How deep search compares to standard search</title>' +
                '<desc id="uds-desc">Standard search uses one query. Deep search tries several ways to find articles, then picks the best matches.</desc>' +
                '<defs>' +
                '<linearGradient id="uds-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uds-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#94A3B8"/></marker>' +
                '<marker id="uds-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="8" y="8" width="296" height="172" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="156" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Standard search</text>' +
                '<text x="156" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="86" y="64" width="140" height="28" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="156" y="82" text-anchor="middle" font-size="11" fill="#334155" font-family="system-ui,sans-serif">Your question</text>' +
                '<line x1="156" y1="92" x2="156" y2="104" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uds-arrow)"/>' +
                '<circle cx="156" cy="122" r="18" fill="#FFFFFF" stroke="#007bff" stroke-width="2"/>' +
                '<circle cx="151" cy="120" r="5" fill="none" stroke="#007bff" stroke-width="2"/>' +
                '<line x1="155" y1="124" x2="163" y2="130" stroke="#007bff" stroke-width="2" stroke-linecap="round"/>' +
                '<line x1="156" y1="140" x2="156" y2="152" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uds-arrow)"/>' +
                '<rect x="118" y="154" width="76" height="18" rx="4" fill="#FFFFFF" stroke="#CBD5E1"/>' +
                '<rect x="124" y="158" width="14" height="10" rx="1" fill="#CBD5E1"/><rect x="142" y="158" width="14" height="10" rx="1" fill="#CBD5E1"/><rect x="160" y="158" width="14" height="10" rx="1" fill="#CBD5E1"/>' +
                '<rect x="108" y="8" width="58" height="20" rx="10" fill="#DCFCE7"/>' +
                '<text x="137" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Faster</text>' +
                '<rect x="336" y="8" width="296" height="172" rx="12" fill="url(#uds-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Deep search</text>' +
                '<text x="484" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="414" y="64" width="140" height="28" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="484" y="82" text-anchor="middle" font-size="11" fill="#334155" font-family="system-ui,sans-serif">Your question</text>' +
                '<path d="M484 92 L484 100" stroke="#007bff" stroke-width="1.5" fill="none"/>' +
                '<path d="M424 100 L544 100" stroke="#007bff" stroke-width="1.5" fill="none"/>' +
                '<path d="M424 100 L424 112" stroke="#007bff" stroke-width="1.5" fill="none" marker-end="url(#uds-arrow-blue)"/>' +
                '<path d="M484 100 L484 112" stroke="#007bff" stroke-width="1.5" fill="none" marker-end="url(#uds-arrow-blue)"/>' +
                '<path d="M544 100 L544 112" stroke="#007bff" stroke-width="1.5" fill="none" marker-end="url(#uds-arrow-blue)"/>' +
                '<circle cx="424" cy="126" r="14" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<circle cx="484" cy="126" r="14" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<circle cx="544" cy="126" r="14" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="424" y="150" text-anchor="middle" font-size="9" fill="#64748B" font-family="system-ui,sans-serif">Try 1</text>' +
                '<text x="484" y="150" text-anchor="middle" font-size="9" fill="#64748B" font-family="system-ui,sans-serif">Try 2</text>' +
                '<text x="544" y="150" text-anchor="middle" font-size="9" fill="#64748B" font-family="system-ui,sans-serif">Try 3</text>' +
                '<path d="M424 156 L484 168 L544 156" stroke="#007bff" stroke-width="1.5" fill="none" stroke-linejoin="round"/>' +
                '<path d="M484 168 L484 174" stroke="#007bff" stroke-width="1.5" fill="none" marker-end="url(#uds-arrow-blue)"/>' +
                '<rect x="446" y="174" width="76" height="18" rx="4" fill="#FFFFFF" stroke="#93C5FD"/>' +
                '<rect x="452" y="178" width="14" height="10" rx="1" fill="#007bff" opacity="0.35"/>' +
                '<rect x="470" y="178" width="14" height="10" rx="1" fill="#007bff" opacity="0.55"/>' +
                '<rect x="488" y="178" width="14" height="10" rx="1" fill="#007bff" opacity="0.85"/>' +
                '<rect x="548" y="8" width="76" height="20" rx="10" fill="#FEF3C7"/>' +
                '<text x="586" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#92400E" font-family="system-ui,sans-serif">Slower</text>' +
                '</svg>'
        },

        'show-references': {
            caption: 'Turn on to show source links under each answer. If the list stays empty, your Nerd Engine may not be returning citations yet.',
            svg: '<svg class="flow-help-diagram" viewBox="0 0 640 184" width="100%" height="184" role="img" aria-labelledby="uref-title uref-desc">' +
                '<title id="uref-title">How Show References changes the answer page</title>' +
                '<desc id="uref-desc">When off, users only see the answer. When on, a references list appears below the answer with source links.</desc>' +
                '<defs><linearGradient id="uref-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient></defs>' +
                '<rect x="8" y="8" width="296" height="168" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="156" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">References hidden</text>' +
                '<text x="156" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="36" y="64" width="240" height="96" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="52" y="84" font-size="11" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Answer</text>' +
                '<rect x="52" y="92" width="180" height="6" rx="3" fill="#E2E8F0"/><rect x="52" y="104" width="200" height="6" rx="3" fill="#E2E8F0"/>' +
                '<rect x="52" y="116" width="160" height="6" rx="3" fill="#E2E8F0"/><rect x="52" y="128" width="190" height="6" rx="3" fill="#E2E8F0"/>' +
                '<rect x="108" y="8" width="72" height="20" rx="10" fill="#F1F5F9"/>' +
                '<text x="144" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">Answer only</text>' +
                '<rect x="336" y="8" width="296" height="168" rx="12" fill="url(#uref-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">References shown</text>' +
                '<text x="484" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="364" y="58" width="240" height="68" rx="10" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="380" y="76" font-size="11" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Answer</text>' +
                '<rect x="380" y="84" width="160" height="5" rx="2.5" fill="#E2E8F0"/><rect x="380" y="94" width="190" height="5" rx="2.5" fill="#E2E8F0"/>' +
                '<rect x="364" y="132" width="240" height="36" rx="8" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5" stroke-dasharray="4 2" opacity="0.95">' +
                '<animate attributeName="opacity" values="0.85;1;0.85" dur="3s" repeatCount="indefinite"/></rect>' +
                '<text x="380" y="148" font-size="10" font-weight="700" fill="#007bff" font-family="system-ui,sans-serif">References</text>' +
                '<circle cx="388" cy="158" r="7" fill="#007bff"/><text x="388" y="161" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">1</text>' +
                '<rect x="400" y="153" width="120" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<circle cx="388" cy="168" r="7" fill="#007bff" opacity="0.75"/><text x="388" y="171" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">2</text>' +
                '<rect x="400" y="163" width="100" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="548" y="8" width="76" height="20" rx="10" fill="#DCFCE7"/>' +
                '<text x="586" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">With sources</text>' +
                '</svg>'
        },

        'chat-history': {
            caption: 'Turn on to save questions and answers for this Nerd. Users can revisit past chats; you can clear history anytime below.',
            svg: '<svg class="flow-help-diagram" viewBox="0 0 640 184" width="100%" height="184" role="img" aria-labelledby="uch-title uch-desc">' +
                '<title id="uch-title">How Chat History affects the experience</title>' +
                '<desc id="uch-desc">When off, each session starts fresh. When on, past Q and A pairs are stored and shown in history.</desc>' +
                '<defs><linearGradient id="uch-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient></defs>' +
                '<rect x="8" y="8" width="296" height="168" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="156" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">History off</text>' +
                '<text x="156" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="36" y="64" width="240" height="96" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="52" y="84" font-size="11" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">New session</text>' +
                '<rect x="52" y="92" width="200" height="6" rx="3" fill="#E2E8F0"/>' +
                '<text x="52" y="114" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Nothing saved from before</text>' +
                '<rect x="108" y="8" width="72" height="20" rx="10" fill="#F1F5F9"/>' +
                '<text x="144" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">Fresh start</text>' +
                '<rect x="336" y="8" width="296" height="168" rx="12" fill="url(#uch-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="484" y="34" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">History on</text>' +
                '<text x="484" y="50" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="364" y="58" width="72" height="108" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="400" y="74" text-anchor="middle" font-size="9" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">History</text>' +
                '<rect x="372" y="80" width="56" height="22" rx="4" fill="#BFDBFE" opacity="0.5"/>' +
                '<rect x="372" y="106" width="56" height="22" rx="4" fill="#BFDBFE"/>' +
                '<rect x="372" y="132" width="56" height="22" rx="4" fill="#BFDBFE" opacity="0.7"/>' +
                '<rect x="444" y="58" width="160" height="108" rx="10" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="460" y="78" font-size="10" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Q: What is…?</text>' +
                '<rect x="460" y="84" width="120" height="5" rx="2.5" fill="#E2E8F0"/>' +
                '<text x="460" y="102" font-size="10" font-weight="700" fill="#007bff" font-family="system-ui,sans-serif">A: Saved answer</text>' +
                '<rect x="460" y="108" width="132" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="460" y="118" width="100" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="548" y="8" width="76" height="20" rx="10" fill="#DCFCE7"/>' +
                '<text x="586" y="22" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Saved</text>' +
                '</svg>'
        }
    };

    function renderDiagram(key) {
        var entry = DIAGRAMS[key];
        if (!entry) return '';
        return entry.svg + '<p class="flow-help-caption">' + entry.caption + '</p>';
    }

    function initUserFlowDiagrams() {
        document.querySelectorAll('[data-user-flow-diagram]').forEach(function (el) {
            var key = el.getAttribute('data-user-flow-diagram');
            var html = renderDiagram(key);
            if (html) {
                el.classList.add('flow-help');
                el.innerHTML = html;
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUserFlowDiagrams);
    } else {
        initUserFlowDiagrams();
    }
})();
