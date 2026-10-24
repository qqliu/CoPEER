KaTeX 0.16.22 (MIT), vendored from the npm package katex@0.16.22: katex.min.css, katex.min.js, contrib/auto-render.min.js, fonts/*.woff2 only (the CSS also lists woff and ttf fallbacks, which are not shipped; every current browser uses woff2).

CSS adaptation: the `.woff` and `.ttf` fallback `src` entries were removed from `katex.min.css` because only the `.woff2` files are shipped; nothing else in the file was changed.
