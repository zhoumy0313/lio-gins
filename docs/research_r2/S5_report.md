# S5 — full evidence-bound review manuscript

STATUS: completed Mode B deliverables, with independent validation unavailable. Complete English r01/r02/r03 versions are retained; r03 is the six-page review candidate, not formal submission ready.

REAL_COMMANDS: `paper_tables.py paper/versions/r2_r02` via recorded run `20261011T183146350309Z_S5_bb6b793b`, exit 0, 0.064s; `make_review_figures.py outputs_r2/20261011T181349420151Z_S3_991cd0d6` final run `20261011T190131223958Z_S5_b7f87fe0`, exit 0, 2.169s; `build_paper.py paper/versions/r2_r03` final run `20261011T190343810586Z_S5_c338cbf5`, exit 0, 1.417s. Numeric/font review `20261011T190429267151Z_S6_2fe85c8c`, exit 0, 0.115s. Exact argv, source/input SHA and timing are in each run receipt.

NUMERIC_EVIDENCE: six pages, 285 table-cell bindings, 19 policies across both seen routes/three caches, all long waits/strict NIS/ablations and censoring reported. Figure 1 has editable TikZ source, Figures 2–3 vector PDF/SVG and complete raw CSV points. Ten claim groups map to run/config/cache/reference/input/evaluator SHA. Final PDF SHA256 `34e6850bd5b1e08c8fc169373ba5e5914d20e9b7ee831295920e132e24ea8d70`.

FAILURES: retained r02 compile succeeded but visual review found a 38pt equation overflow and small plot labels. r03 corrects layout; final review shows zero overfull boxes, compile errors or undefined references. Underfull-box warnings are nonfatal. No independent route or novelty was invented, and all intermediate outputs remain retained.

NEXT: critical scientific/venue review, Chinese author decision brief and final archive. GIT_SHA: `artifacts/r2/checkpoints/S5.json` after checkpoint. Full source and PDF: `paper/versions/r2_r03/`; visual inspection: `visual_audit.md`; numeric audit: `artifacts/r2/S6/manuscript_audit.json`.
