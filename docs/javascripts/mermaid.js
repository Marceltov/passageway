(() => {
  if (typeof mermaid === "undefined") return;
  const rules = `
    .actor-line { stroke: var(--md-mermaid-sequence-actor-line-color) !important; }
    marker[id$="arrowhead"] path { fill: var(--md-mermaid-sequence-message-line-color) !important; stroke: none !important; }
    marker[id$="crosshead"] path { stroke: var(--md-mermaid-sequence-message-line-color) !important; }
    .cluster rect { fill: var(--md-default-bg-color) !important; stroke: var(--md-mermaid-edge-color) !important; stroke-dasharray: 4 3; }
    .edgeLabel, .edgeLabel p { color: var(--md-mermaid-label-fg-color); }
  `;
  const initialize = mermaid.initialize.bind(mermaid);
  mermaid.initialize = (config = {}) => initialize({ ...config, themeCSS: (config.themeCSS ?? "") + rules });
})();
