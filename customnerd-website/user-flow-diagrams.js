/**
 * Inline SVG help diagrams for Configuration → User Flow sections.
 * Injected into elements with data-user-flow-diagram="<key>".
 */
(function () {
    'use strict';

    var DIAGRAMS = {
        'normal-search': {
            caption: 'Turn on to show a database search option on the question page. Users can search your article index alongside their question.',
            svg: '<svg class="flow-help-diagram" viewBox="-16 -12 672 254" width="100%" height="254" role="img" aria-labelledby="ufs-title ufs-desc">' +
                '<title id="ufs-title">Normal Search on the question page</title>' +
                '<desc id="ufs-desc">When off, users only ask a question. When on, a search-articles checkbox appears and queries your database.</desc>' +
                '<defs>' +
                '<linearGradient id="ufs-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="ufs-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#94A3B8"/></marker>' +
                '<marker id="ufs-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="16" y="16" width="288" height="210" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="160" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Hidden</text>' +
                '<text x="160" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="44" y="102" width="240" height="88" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="60" y="122" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Ask a question…</text>' +
                '<rect x="60" y="134" width="200" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="60" y="150" width="72" height="24" rx="6" fill="#E2E8F0"/>' +
                '<text x="96" y="166" text-anchor="middle" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Submit</text>' +
                '<rect x="28" y="28" width="80" height="18" rx="10" fill="#F1F5F9"/>' +
                '<text x="68" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">Question only</text>' +
                '<rect x="368" y="16" width="288" height="210" rx="12" fill="url(#ufs-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="512" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Search enabled</text>' +
                '<text x="512" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="396" y="92" width="240" height="108" rx="10" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="412" y="112" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Ask a question…</text>' +
                '<rect x="412" y="120" width="180" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="412" y="136" width="14" height="14" rx="3" fill="#007bff" stroke="#007bff" stroke-width="1.5"/>' +
                '<path d="M 416 143L 419 146L 424 140" stroke="#FFFFFF" stroke-width="1.5" fill="none" stroke-linecap="round"/>' +
                '<text x="434" y="147" font-size="10" font-weight="600" fill="#334155" font-family="system-ui,sans-serif">Search articles</text>' +
                '<line x1="516" y1="150" x2="516" y2="162" stroke="#007bff" stroke-width="1.5" marker-end="url(#ufs-arrow-blue)"/>' +
                '<circle cx="516" cy="184" r="16" fill="#FFFFFF" stroke="#007bff" stroke-width="2"/>' +
                '<ellipse cx="516" cy="182" rx="8" ry="5" fill="none" stroke="#007bff" stroke-width="1.5"/>' +
                '<rect x="510" y="188" width="12" height="8" rx="1" fill="#007bff" opacity="0.3"/>' +
                '<rect x="484" y="202" width="20" height="14" rx="2" fill="#BFDBFE"/><rect x="508" y="202" width="20" height="14" rx="2" fill="#BFDBFE"/><rect x="532" y="202" width="20" height="14" rx="2" fill="#007bff" opacity="0.6"/>' +
                '<rect x="576" y="28" width="72" height="18" rx="10" fill="#DCFCE7"/>' +
                '<text x="612" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Database</text>' +
                '</svg>'
        },

        'id-specific-search': {
            caption: 'Turn on to let users paste article IDs and fetch those records directly instead of a keyword search.',
            svg: '<svg class="flow-help-diagram" viewBox="-16 -12 672 254" width="100%" height="254" role="img" aria-labelledby="uid-title uid-desc">' +
                '<title id="uid-title">ID Specific Search on the question page</title>' +
                '<desc id="uid-desc">When off, no ID field appears. When on, users enter IDs and the app fetches those articles.</desc>' +
                '<defs>' +
                '<linearGradient id="uid-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uid-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="16" y="16" width="288" height="210" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="160" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Hidden</text>' +
                '<text x="160" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="44" y="102" width="240" height="88" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="60" y="122" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Ask a question…</text>' +
                '<rect x="60" y="134" width="200" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="28" y="28" width="80" height="18" rx="10" fill="#F1F5F9"/>' +
                '<text x="68" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">No ID field</text>' +
                '<rect x="368" y="16" width="288" height="210" rx="12" fill="url(#uid-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="512" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">ID lookup</text>' +
                '<text x="512" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="396" y="92" width="240" height="40" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="408" y="108" font-size="9" font-weight="600" fill="#334155" font-family="system-ui,sans-serif">Article IDs</text>' +
                '<text x="408" y="122" font-size="8" fill="#64748B" font-family="monospace">1042, 8821, 330</text>' +
                '<line x1="516" y1="124" x2="516" y2="136" stroke="#007bff" stroke-width="1.5" marker-end="url(#uid-arrow-blue)"/>' +
                '<rect x="452" y="146" width="128" height="26" rx="6" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="516" y="163" text-anchor="middle" font-size="10" fill="#334155" font-family="system-ui,sans-serif">Fetch by ID</text>' +
                '<line x1="516" y1="164" x2="516" y2="174" stroke="#007bff" stroke-width="1.5" marker-end="url(#uid-arrow-blue)"/>' +
                '<rect x="470" y="186" width="36" height="18" rx="3" fill="#007bff" opacity="0.85"/><text x="488" y="198" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">1042</text>' +
                '<rect x="510" y="186" width="36" height="18" rx="3" fill="#007bff" opacity="0.55"/><text x="528" y="198" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">8821</text>' +
                '<rect x="550" y="186" width="36" height="18" rx="3" fill="#007bff" opacity="0.35"/><text x="568" y="198" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">330</text>' +
                '<rect x="576" y="28" width="72" height="18" rx="10" fill="#DCFCE7"/>' +
                '<text x="612" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Exact match</text>' +
                '</svg>'
        },

        'local-document-search': {
            caption: 'Turn on to let users upload PDFs on the question page. Uploaded text is included when the Nerd answers.',
            svg: '<svg class="flow-help-diagram" viewBox="-16 -12 672 254" width="100%" height="254" role="img" aria-labelledby="uloc-title uloc-desc">' +
                '<title id="uloc-title">Local Document Search on the question page</title>' +
                '<desc id="uloc-desc">When off, no upload option. When on, users attach PDFs that feed into the answer.</desc>' +
                '<defs>' +
                '<linearGradient id="uloc-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uloc-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="16" y="16" width="288" height="210" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="160" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Hidden</text>' +
                '<text x="160" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="44" y="102" width="240" height="88" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="60" y="126" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Question only — no uploads</text>' +
                '<rect x="60" y="138" width="200" height="8" rx="4" fill="#E2E8F0"/>' +
                '<rect x="28" y="28" width="80" height="18" rx="10" fill="#F1F5F9"/>' +
                '<text x="68" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">No PDFs</text>' +
                '<rect x="368" y="16" width="288" height="210" rx="12" fill="url(#uloc-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="512" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">PDF upload</text>' +
                '<text x="512" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="412" y="96" width="88" height="52" rx="6" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5" stroke-dasharray="4 3"/>' +
                '<path d="M 456 108L 456 130M 446 118L 456 108L 466 118" stroke="#007bff" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' +
                '<text x="456" y="142" text-anchor="middle" font-size="9" fill="#64748B" font-family="system-ui,sans-serif">Upload PDF</text>' +
                '<rect x="508" y="102" width="108" height="44" rx="4" fill="#FFFFFF" stroke="#DC2626" stroke-width="1.5"/>' +
                '<text x="520" y="118" font-size="9" font-weight="700" fill="#DC2626" font-family="system-ui,sans-serif">PDF</text>' +
                '<rect x="520" y="124" width="80" height="4" rx="2" fill="#FECACA"/><rect x="520" y="132" width="60" height="4" rx="2" fill="#FECACA"/>' +
                '<line x1="516" y1="146" x2="516" y2="160" stroke="#007bff" stroke-width="1.5" marker-end="url(#uloc-arrow-blue)"/>' +
                '<rect x="396" y="172" width="240" height="36" rx="8" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="412" y="190" font-size="10" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Answer uses your document</text>' +
                '<rect x="412" y="196" width="160" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="576" y="28" width="72" height="18" rx="10" fill="#FEF3C7"/>' +
                '<text x="612" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#92400E" font-family="system-ui,sans-serif">Local files</text>' +
                '</svg>'
        },

        'query-cleaning': {
            caption: 'Turn on to run expanded_queries through clean_query(query_list, max_queries=None) before searching. Parses JSON (or nested lists) into a flat, capped list of search strings for Stack Exchange or other APIs.',
            svg: '<svg class="flow-help-diagram" viewBox="-16 -12 672 254" width="100%" height="254" role="img" aria-labelledby="uqc-title uqc-desc">' +
                '<title id="uqc-title">Query Cleaning in the search pipeline</title>' +
                '<desc id="uqc-desc">When off, raw LLM output may reach search. When on, clean_query normalizes expanded_queries into usable strings.</desc>' +
                '<defs>' +
                '<linearGradient id="uqc-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uqc-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#94A3B8"/></marker>' +
                '<marker id="uqc-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="16" y="16" width="288" height="210" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="160" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Cleaning off</text>' +
                '<text x="160" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="36" y="98" width="120" height="40" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="96" y="116" text-anchor="middle" font-size="10" fill="#334155" font-family="system-ui,sans-serif">LLM output</text>' +
                '<text x="96" y="130" text-anchor="middle" font-size="8" fill="#94A3B8" font-family="monospace">{ messy… }</text>' +
                '<line x1="148" y1="110" x2="168" y2="110" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uqc-arrow)"/>' +
                '<circle cx="208" cy="118" r="18" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="2"/>' +
                '<circle cx="204" cy="116" r="5" fill="none" stroke="#94A3B8" stroke-width="1.5"/>' +
                '<line x1="208" y1="120" x2="216" y2="126" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>' +
                '<line x1="218" y1="110" x2="268" y2="110" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uqc-arrow)"/>' +
                '<rect x="276" y="102" width="28" height="32" rx="3" fill="#FECACA" stroke="#F87171" stroke-width="1" opacity="0.7"/>' +
                '<text x="290" y="122" text-anchor="middle" font-size="8" fill="#991B1B" font-family="system-ui,sans-serif">?</text>' +
                '<rect x="28" y="28" width="80" height="18" rx="10" fill="#FEE2E2"/>' +
                '<text x="68" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#991B1B" font-family="system-ui,sans-serif">Unparsed</text>' +
                '<rect x="368" y="16" width="288" height="210" rx="12" fill="url(#uqc-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="512" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Cleaning on</text>' +
                '<text x="512" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="388" y="98" width="100" height="40" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="438" y="116" text-anchor="middle" font-size="10" fill="#334155" font-family="system-ui,sans-serif">LLM JSON</text>' +
                '<text x="438" y="130" text-anchor="middle" font-size="8" fill="#64748B" font-family="monospace">expanded_queries</text>' +
                '<line x1="456" y1="110" x2="472" y2="110" stroke="#007bff" stroke-width="1.5" marker-end="url(#uqc-arrow-blue)"/>' +
                '<rect x="504" y="102" width="72" height="32" rx="6" fill="#007bff"/>' +
                '<text x="540" y="122" text-anchor="middle" font-size="9" font-weight="700" fill="#FFFFFF" font-family="monospace">clean_query</text>' +
                '<line x1="508" y1="126" x2="508" y2="138" stroke="#007bff" stroke-width="1.5" marker-end="url(#uqc-arrow-blue)"/>' +
                '<rect x="396" y="148" width="240" height="58" rx="8" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="412" y="164" font-size="9" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Search list</text>' +
                '<rect x="408" y="172" width="68" height="14" rx="4" fill="#BFDBFE"/><text x="442" y="182" text-anchor="middle" font-size="8" fill="#1E40AF" font-family="system-ui,sans-serif">query 1</text>' +
                '<rect x="482" y="172" width="68" height="14" rx="4" fill="#BFDBFE"/><text x="516" y="182" text-anchor="middle" font-size="8" fill="#1E40AF" font-family="system-ui,sans-serif">query 2</text>' +
                '<rect x="556" y="172" width="68" height="14" rx="4" fill="#BFDBFE" opacity="0.75"/><text x="590" y="182" text-anchor="middle" font-size="8" fill="#1E40AF" font-family="system-ui,sans-serif">query 3</text>' +
                '<rect x="576" y="28" width="72" height="18" rx="10" fill="#DCFCE7"/>' +
                '<text x="612" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Ready</text>' +
                '</svg>'
        },

        'deep-search': {
            caption: 'Turn on for three-tier cascade retrieval (strict, then title-only, then extended keywords) per expanded query. Tier parameters come from the Nerd code profile; this toggle sets cascade_retrieval.visible. Turn off for a faster single-pass search.',
            svg: '<svg class="flow-help-diagram" viewBox="-16 -12 672 254" width="100%" height="254" role="img" aria-labelledby="uds-title uds-desc">' +
                '<title id="uds-title">How Deep Search cascade retrieval compares to standard search</title>' +
                '<desc id="uds-desc">When off, legacy single-pass search runs once per query. When on, retrieval tries strict, title-only, and extended-keyword tiers in order until enough articles are collected.</desc>' +
                '<defs>' +
                '<linearGradient id="uds-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient>' +
                '<marker id="uds-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#94A3B8"/></marker>' +
                '<marker id="uds-arrow-blue" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#007bff"/></marker>' +
                '</defs>' +
                '<rect x="16" y="16" width="288" height="210" rx="12" fill="#F5F6F8" stroke="#CBD5E1" stroke-width="1.25"/>' +
                '<text x="160" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">Single pass</text>' +
                '<text x="160" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off · legacy</text>' +
                '<rect x="94" y="98" width="140" height="28" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="164" y="116" text-anchor="middle" font-size="11" fill="#334155" font-family="system-ui,sans-serif">Expanded query</text>' +
                '<line x1="164" y1="126" x2="164" y2="138" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uds-arrow)"/>' +
                '<rect x="118" y="142" width="92" height="32" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.25"/>' +
                '<text x="164" y="156" text-anchor="middle" font-size="10" font-weight="600" fill="#334155" font-family="system-ui,sans-serif">One search</text>' +
                '<text x="164" y="168" text-anchor="middle" font-size="8" fill="#64748B" font-family="system-ui,sans-serif">single strictness</text>' +
                '<line x1="164" y1="174" x2="164" y2="186" stroke="#94A3B8" stroke-width="1.5" marker-end="url(#uds-arrow)"/>' +
                '<rect x="126" y="190" width="76" height="18" rx="4" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.25"/>' +
                '<rect x="132" y="194" width="14" height="10" rx="1" fill="#CBD5E1"/><rect x="150" y="194" width="14" height="10" rx="1" fill="#CBD5E1"/><rect x="168" y="194" width="14" height="10" rx="1" fill="#CBD5E1"/>' +
                '<rect x="28" y="28" width="58" height="18" rx="10" fill="#DCFCE7" stroke="#166534" stroke-opacity="0.25" stroke-width="1"/>' +
                '<text x="57" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Faster</text>' +
                '<rect x="368" y="16" width="288" height="210" rx="12" fill="url(#uds-on-bg)" stroke="#93C5FD" stroke-width="1.25"/>' +
                '<text x="512" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Deep search</text>' +
                '<text x="512" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on · cascade</text>' +
                '<rect x="446" y="92" width="140" height="24" rx="8" fill="#FFFFFF" stroke="#BFDBFE" stroke-width="1.25"/>' +
                '<text x="516" y="108" text-anchor="middle" font-size="10" fill="#334155" font-family="system-ui,sans-serif">Expanded query</text>' +
                '<line x1="516" y1="116" x2="516" y2="124" stroke="#007bff" stroke-width="1.5" marker-end="url(#uds-arrow-blue)"/>' +
                '<rect x="422" y="126" width="56" height="34" rx="8" fill="#FFFFFF" stroke="#BFDBFE" stroke-width="1.25"/>' +
                '<text x="450" y="140" text-anchor="middle" font-size="9" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Strict</text>' +
                '<text x="450" y="152" text-anchor="middle" font-size="7" fill="#64748B" font-family="system-ui,sans-serif">plane 1</text>' +
                '<line x1="478" y1="143" x2="486" y2="143" stroke="#007bff" stroke-width="1.5" marker-end="url(#uds-arrow-blue)"/>' +
                '<rect x="488" y="126" width="56" height="34" rx="8" fill="#FFFFFF" stroke="#BFDBFE" stroke-width="1.25"/>' +
                '<text x="516" y="140" text-anchor="middle" font-size="9" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Title</text>' +
                '<text x="516" y="152" text-anchor="middle" font-size="7" fill="#64748B" font-family="system-ui,sans-serif">plane 2</text>' +
                '<line x1="544" y1="143" x2="552" y2="143" stroke="#007bff" stroke-width="1.5" marker-end="url(#uds-arrow-blue)"/>' +
                '<rect x="554" y="126" width="56" height="34" rx="8" fill="#FFFFFF" stroke="#BFDBFE" stroke-width="1.25"/>' +
                '<text x="582" y="140" text-anchor="middle" font-size="9" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">Extended</text>' +
                '<text x="582" y="152" text-anchor="middle" font-size="7" fill="#64748B" font-family="system-ui,sans-serif">plane 3</text>' +
                '<text x="516" y="172" text-anchor="middle" font-size="8" fill="#64748B" font-family="system-ui,sans-serif">try in order until enough articles</text>' +
                '<line x1="516" y1="176" x2="516" y2="184" stroke="#007bff" stroke-width="1.5" marker-end="url(#uds-arrow-blue)"/>' +
                '<rect x="468" y="188" width="96" height="22" rx="4" fill="#FFFFFF" stroke="#BFDBFE" stroke-width="1.25"/>' +
                '<rect x="476" y="194" width="14" height="10" rx="1" fill="#007bff" opacity="0.35"/>' +
                '<rect x="494" y="194" width="14" height="10" rx="1" fill="#007bff" opacity="0.55"/>' +
                '<rect x="512" y="194" width="14" height="10" rx="1" fill="#007bff" opacity="0.85"/>' +
                '<rect x="530" y="194" width="14" height="10" rx="1" fill="#007bff" opacity="0.65"/>' +
                '<text x="516" y="218" text-anchor="middle" font-size="8" fill="#64748B" font-family="system-ui,sans-serif">merged articles</text>' +
                '<rect x="576" y="28" width="72" height="18" rx="10" fill="#FEF3C7" stroke="#92400E" stroke-opacity="0.25" stroke-width="1"/>' +
                '<text x="612" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#92400E" font-family="system-ui,sans-serif">3-tier</text>' +
                '</svg>'
        },

        'show-references': {
            caption: 'Turn on to show source links under each answer. If the list stays empty, your Nerd Engine may not be returning citations yet.',
            svg: '<svg class="flow-help-diagram" viewBox="-16 -12 672 242" width="100%" height="242" role="img" aria-labelledby="uref-title uref-desc">' +
                '<title id="uref-title">How Show References changes the answer page</title>' +
                '<desc id="uref-desc">When off, users only see the answer. When on, a references list appears below the answer with source links.</desc>' +
                '<defs><linearGradient id="uref-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient></defs>' +
                '<rect x="16" y="16" width="288" height="206" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="160" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">References hidden</text>' +
                '<text x="160" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="44" y="98" width="240" height="96" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="60" y="118" font-size="11" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Answer</text>' +
                '<rect x="60" y="126" width="180" height="6" rx="3" fill="#E2E8F0"/><rect x="60" y="138" width="200" height="6" rx="3" fill="#E2E8F0"/>' +
                '<rect x="60" y="150" width="160" height="6" rx="3" fill="#E2E8F0"/><rect x="60" y="162" width="190" height="6" rx="3" fill="#E2E8F0"/>' +
                '<rect x="28" y="28" width="80" height="18" rx="10" fill="#F1F5F9"/>' +
                '<text x="68" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">Answer only</text>' +
                '<rect x="368" y="16" width="288" height="206" rx="12" fill="url(#uref-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="512" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">References shown</text>' +
                '<text x="512" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="396" y="92" width="240" height="58" rx="10" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="412" y="108" font-size="11" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Answer</text>' +
                '<rect x="412" y="114" width="160" height="5" rx="2.5" fill="#E2E8F0"/><rect x="412" y="124" width="190" height="5" rx="2.5" fill="#E2E8F0"/>' +
                '<rect x="412" y="134" width="140" height="5" rx="2.5" fill="#E2E8F0"/>' +
                '<rect x="396" y="156" width="240" height="46" rx="8" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5" stroke-dasharray="4 2" opacity="0.95">' +
                '<animate attributeName="opacity" values="0.85;1;0.85" dur="3s" repeatCount="indefinite"/></rect>' +
                '<text x="412" y="170" font-size="10" font-weight="700" fill="#007bff" font-family="system-ui,sans-serif">References</text>' +
                '<circle cx="420" cy="182" r="6" fill="#007bff"/><text x="420" y="185" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">1</text>' +
                '<rect x="432" y="178" width="120" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<circle cx="420" cy="196" r="6" fill="#007bff" opacity="0.75"/><text x="420" y="199" text-anchor="middle" font-size="8" font-weight="700" fill="#FFFFFF" font-family="system-ui,sans-serif">2</text>' +
                '<rect x="432" y="192" width="100" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="566" y="28" width="82" height="18" rx="10" fill="#DCFCE7"/>' +
                '<text x="607" y="41" text-anchor="middle" font-size="9" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">With sources</text>' +
                '</svg>'
        },

        'chat-history': {
            caption: 'Turn on to save questions and answers for this Nerd. Users can revisit past chats; you can clear history anytime below.',
            svg: '<svg class="flow-help-diagram" viewBox="-16 -12 672 242" width="100%" height="242" role="img" aria-labelledby="uch-title uch-desc">' +
                '<title id="uch-title">How Chat History affects the experience</title>' +
                '<desc id="uch-desc">When off, each session starts fresh. When on, past Q and A pairs are stored and shown in history.</desc>' +
                '<defs><linearGradient id="uch-on-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8F4FD"/><stop offset="100%" stop-color="#F8FBFF"/></linearGradient></defs>' +
                '<rect x="16" y="16" width="288" height="206" rx="12" fill="#F5F6F8" stroke="#E2E8F0" stroke-width="1.5"/>' +
                '<text x="160" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#475569" font-family="system-ui,sans-serif">History off</text>' +
                '<text x="160" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle off</text>' +
                '<rect x="44" y="98" width="240" height="96" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>' +
                '<text x="60" y="118" font-size="11" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">New session</text>' +
                '<rect x="60" y="126" width="200" height="6" rx="3" fill="#E2E8F0"/>' +
                '<text x="60" y="148" font-size="10" fill="#94A3B8" font-family="system-ui,sans-serif">Nothing saved from before</text>' +
                '<rect x="28" y="28" width="80" height="18" rx="10" fill="#F1F5F9"/>' +
                '<text x="68" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#64748B" font-family="system-ui,sans-serif">Fresh start</text>' +
                '<rect x="368" y="16" width="288" height="206" rx="12" fill="url(#uch-on-bg)" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="512" y="64" text-anchor="middle" font-size="13" font-weight="700" fill="#1E40AF" font-family="system-ui,sans-serif">History on</text>' +
                '<text x="512" y="80" text-anchor="middle" font-size="11" fill="#64748B" font-family="system-ui,sans-serif">Toggle on</text>' +
                '<rect x="396" y="92" width="72" height="108" rx="8" fill="#FFFFFF" stroke="#93C5FD" stroke-width="1.5"/>' +
                '<text x="432" y="108" text-anchor="middle" font-size="9" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">History</text>' +
                '<rect x="404" y="114" width="56" height="22" rx="4" fill="#BFDBFE" opacity="0.5"/>' +
                '<rect x="404" y="140" width="56" height="22" rx="4" fill="#BFDBFE"/>' +
                '<rect x="404" y="166" width="56" height="22" rx="4" fill="#BFDBFE" opacity="0.7"/>' +
                '<rect x="476" y="92" width="160" height="108" rx="10" fill="#FFFFFF" stroke="#007bff" stroke-width="1.5"/>' +
                '<text x="492" y="112" font-size="10" font-weight="700" fill="#334155" font-family="system-ui,sans-serif">Q: What is…?</text>' +
                '<rect x="492" y="118" width="120" height="5" rx="2.5" fill="#E2E8F0"/>' +
                '<text x="492" y="136" font-size="10" font-weight="700" fill="#007bff" font-family="system-ui,sans-serif">A: Saved answer</text>' +
                '<rect x="492" y="142" width="132" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="492" y="152" width="100" height="5" rx="2.5" fill="#BFDBFE"/>' +
                '<rect x="576" y="28" width="72" height="18" rx="10" fill="#DCFCE7"/>' +
                '<text x="612" y="41" text-anchor="middle" font-size="10" font-weight="700" fill="#166534" font-family="system-ui,sans-serif">Saved</text>' +
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
