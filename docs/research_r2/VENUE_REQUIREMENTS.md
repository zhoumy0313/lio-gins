# Official venue requirements and remaining uncertainty

Checked October12,2026 Asia/Shanghai (October11 UTC). Sources: [conference homepage](https://upinlbs2026.com/), [submission page](https://upinlbs2026.com/submission). Initial HTTP200 responses were a1172-byte app shell rather than the rendered instructions. A subsequent bounded read of the public same-origin JavaScript bundle recovered the actual submission content without executing scripts, logging in or opening CMT. Retain both audits; the initial UNVERIFIED fields are historical, superseded only for items established by the bundle.

| Requirement | Finding |
|---|---|
| Full-paper deadline | VERIFIED official application content:2026-10-15. This is the submission deadline, not the later final-paper date. |
| Full paper | VERIFIED: original PDF in conference format, up to6pages. |
| Template | VERIFIED official link to [IEEE conference template selector](https://template-selector.ieee.org/secure/templateSelector/articleType?publicationTypeId=3&titleId=1). Exact variant/downloaded template and final conformance remain UNVERIFIED. Current IEEEtran conference layout is provisional pending that check. |
| CMT entry | VERIFIED official link to [UPINLBS2026 CMT](https://cmt3.research.microsoft.com/UPINLBS2026). Not opened/logged in/uploaded. |
| Submission types | VERIFIED: Full Paper and Abstract-only; abstract-only length1–2pages. Human must choose. |
| Anonymity | UNVERIFIED. The JavaScript networking attribute `anonymous` is not a review-anonymity rule. |
| Exact deadline time/timezone | UNVERIFIED. Generic timezone library code is not conference guidance. |
| Publisher/AI policy | UNVERIFIED conference-specific applicability. IEEE template linkage and EI eligibility do not establish a publication contract. |

Conditional reference: [IEEE guidance on AI-generated text](https://open.ieee.org/author-guidelines-for-artificial-intelligence-ai-generated-text/) calls for disclosure of the tool, affected sections and extent when applicable. The paper discloses actual OpenAI Codex(GPT-6) assistance in orchestration/evaluation/plot code/evidence and manuscript text; human authors must check the venue's policy. Numeric figures use retained data, not generated artwork.

Evidence: `artifacts/r2/S6/venue_access_audit.json`, `venue_bundle_access_audit.json`, `venue_requirements_interpretation.json`; recorded official-bundle run `20261011T190239109372Z_S6_4d2b0716`, exit0/1.423s. Full public responses remain in that local sealed run. No acceptance/indexing guarantee follows from a formatting check. Authorship, original-content approval, copyright, accounts, fees and Submit remain human actions.
