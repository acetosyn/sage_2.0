# SAGE mobile redesign — implementation and QA report

Completed in the existing Flask/Jinja application. No frontend framework, schema migration, API change, role-policy change or new production dependency was introduced. Extract the companion ZIP into the SAGE project root, preserving paths. Restart SAGE after replacing the files.

## Audit findings

The audit covered 48 HTML/Jinja templates, all original static CSS and JavaScript files, the shared shell, the independent authentication and Developer Console shells, page-context routes, partial navigation, modal controllers and owner/staff/individual permissions. The duplicate UI files under models/ are not the Flask template/static roots. sage6.css/js and sage7.css/js are not loaded by the active shell. They remain unreferenced.

The observed inconsistencies had several concrete causes:

- The typography picker cached computed pixel sizes in data-sage-base-font-size, then wrote inline !important sizes. Its cached desktop/mobile values could outlive the breakpoint and be captured before later decoration.
- Eight active stylesheets contained 161 separate mobile media blocks, including competing table/card conversions, multiple minimum heights, microscopic table/filter text and different modal viewport limits.
- The shell loaded only the previous mobile ledger patch; authentication and the Developer Console did not share a complete mobile system.
- SAGE 5 added a grid, gaps, label letter-spacing and card decoration after the page had painted. Premium/market decoration also added layout-bearing content.
- A toast container retained its desktop top position while also receiving a mobile bottom position. The resulting empty stretched container intercepted taps.
- Backdrops, modal cards and nested modal bodies could all own vertical scrolling. The operational disclosure controller also used a different mobile breakpoint.

## Final architecture

- Mobile layout is owned by static/css/sage_mobile.css and static/css/sage_mobile_ledger.css at widths up to 900px, with narrower rules at 600px and 390px. The old <=900px blocks were removed from the active desktop stylesheets.
- The named sage-mobile cascade layer gives necessary mobile !important declarations a predictable priority over the existing unlayered desktop !important rules. It avoids increasingly specific selectors. All mobile rules remain inside mobile media queries.
- Authored font-size declarations now multiply by --sage-text-scale. The saved font/size still initializes before paint. The picker sets the preference only; it never measures/caches element fonts or writes inline sizes.
- Mobile card geometry, label weights, icon space and page flow are present in initial CSS. Financial values use tabular figures, a readable minimum, full-width value rows and wrapping instead of ellipsis.
- static/js/mobile_ui.js handles interaction and accessibility: drawer focus/inert state, the More menu, the compact floating action menu, scroll-region metadata and passive edge feedback. It does not choose card sizes or typography.
- Desktop media rules, sidebar dimensions, icons, typography hierarchy, tables and modal layouts retain their original default dimensions. The typography preference still works at every breakpoint.

The workspace CSS payload is 888,979 bytes versus 914,941 bytes before this change, despite adding the complete shared mobile treatment. There is no additional framework bundle.

## Mobile refinements implemented

1. Stable 60px phone header, plus the top safe-area inset.
2. Search icon opens the existing command search.
3. Compact More menu retains typography, all appearance palettes, accent controls and SAGE Guide.
4. Icon-only SAGE AI and role-specific Quick Add / Quick Record / Finance View controls have accessible names.
5. An 86vw drawer, capped at 320px, retains strong 24px navigation icons and readable labels.
6. Drawer focus is contained, the background becomes inert, Escape closes it, and desktop state is restored on resize.
7. Two-column KPI layouts reserve a separate label/icon zone and allow complete long amounts to wrap.
8. Finance uses a compact two-plus-one summary layout.
9. Filters form a swipe shelf with deliberate search/date/select widths and 36px controls.
10. Clear is a compact 76px action.
11. Mini-ledgers retain native table/row/cell semantics, planned columns, full-precision amounts and horizontal scrolling.
12. Ledger headers and first identity columns have opaque sticky surfaces and correct stacking.
13. Table regions support keyboard scrolling, column header scope and swipe guidance.
14. Scroll-edge feedback indicates additional columns.
15. Table text, badges, evidence controls and pagination use readable compact sizes.
16. Request metadata wraps; breakdowns use a small swipeable item/quantity/price/total flow.
17. Request amounts, funding, balance and approval actions remain visible in compact cards.
18. Owner oversight notices are concise on phones.
19. Modals have one card scroll owner, an opaque sticky header, reachable flow-based footer actions and safe viewport bounds.
20. Forms use 44px controls and 16px input text to avoid focus zoom; narrow grids become one column.
21. Staff invitation delivery choices and generated-link fields fit narrow dialogs.
22. Operational disclosure forms remain inline throughout the mobile breakpoint and accessible to assistive technology.
23. Floating actions collapse into one 44px button, expand on demand and hide behind workflow overlays.
24. Safe-area padding and bottom content clearance protect the last controls and rows.
25. Notifications, search, AI, Guide, appearance menus and evidence viewers fit the viewport.
26. Empty toast space no longer captures taps; status updates have polite live announcements.
27. Mobile registration uses a compact four-step rail, native business pickers, logo preview and correctly sized department choices.
28. Welcome/setup/handoff scenes show one stage at a time on phones.
29. The Developer Console has its own compact header, app drawer, semantic ledgers and palette-aware table surfaces.
30. Mobile hover lift, magnetic effects and pointer spotlight updates are disabled; reduced-motion drawer transitions are respected.

## Verification

- Chromium browser QA used an isolated temporary SQLite database and local-only QA sessions. The existing vision_dev.db and .env were not modified.
- 94 permitted page/account combinations were exercised across 14 viewport widths: 320, 360, 375, 390, 412, 430, 480, 600, 768, 820, 1024, 1366, 1440 and 1920px. This includes 940 phone/tablet checks with no detected page overflow, card-amount overflow, microscopic KPI values or row-to-card table conversion.
- 154 same-content desktop geometry comparisons passed, including the requested desktop widths. Audit/activity data was held constant for this comparison.
- Desktop 1440x900 screenshot comparisons: Dashboard, Income, Finance and Requests matched pixel for pixel. Expenses differed by 12 pixels out of 1,296,000 (0.00093%).
- 52 mobile initialization comparisons passed at 320, 390, 430 and 768px: server-rendered component geometry matched the initialized application. The comparison preserves the synchronous pre-paint font preference in both cases.
- The functional suite passed 48 checks covering the drawer, appearance controls, all 19 appearance palettes, search, notifications, SAGE AI, Guide, navigation/back/orientation, authentication, Developer Console and workflow dialogs.
- 18 further scenarios passed: both owner onboarding modes with logo upload/native pickers, operational inline forms, 400 amount/width/font-preference combinations at Large text size, exact screenshot dimensions and the floating action menu.
- Screenshots were captured at 390x844, 430x932, 768x1024 and 1440x900. Original 390px and desktop captures were retained for comparison.
- Browser visual comparisons use deterministic offline font fallbacks. The checks cover all ten font preferences; they do not claim a physical-device or live Google Fonts network test.
- JavaScript syntax checks and Python QA-tool compilation passed.

The existing Python regression suite ran 64 tests: 39 passed, 23 failed and 2 errored. Running the original unmodified project from Git produced the same 23 failures and 2 errors. These are existing owner-permission/operational-policy expectation failures in test_business_v4.py; this presentation upgrade does not alter those policies. The owner-control and datetime regression tests passed.

## Page-by-page coverage

O = organization owner, S = organization staff, F = finance staff, I = individual-business owner. A dash indicates the role does not expose that menu in the existing permission-filtered navigation.

| Page | O | S | F | I |
|---|:---:|:---:|:---:|:---:|
| Dashboard | Pass | Pass | Pass | Pass |
| Requests & Approvals | Pass | Pass | Pass | — |
| Income & Sales | Pass | Pass | Pass | Pass |
| Expenses & Expenditure | Pass | — | Pass | Pass |
| Finance | Pass | — | Pass | Pass |
| Debtors & Credit Sales | Pass | Pass | Pass | Pass |
| Petty Cash & Imprest | Pass | — | Pass | Pass |
| Daily Sales / POS Close | Pass | Pass | Pass | Pass |
| Department Workspace | Pass | Pass | Pass | Pass |
| Department Catalogue | Pass | Pass | Pass | Pass |
| Department Operations | Pass | Pass | Pass | Pass |
| Acquisition Hub | Pass | Pass | Pass | Pass |
| Procurement | Pass | — | — | Pass |
| Inventory | Pass | — | — | Pass |
| Assets | Pass | — | — | Pass |
| Events & Campaigns | Pass | Pass | Pass | Pass |
| Advanced Stock Control | Pass | — | — | Pass |
| Customers & CRM | Pass | Pass | Pass | Pass |
| Suppliers & Vendors | Pass | — | — | Pass |
| Branches & Shops | Pass | — | Pass | Pass |
| Departments | Pass | Pass | — | — |
| Staff | Pass | — | — | Pass |
| Reports | Pass | Pass | Pass | Pass |
| Audit Trail | Pass | — | Pass | Pass |
| Staff Finance & Payroll | Pass | — | Pass | Pass |
| Analytics | Pass | — | Pass | Pass |
| Bills & Renewals | Pass | Pass | Pass | Pass |
| Compliance Centre | Pass | — | Pass | Pass |
| Business Operations Reports | Pass | — | Pass | Pass |
| Settings | Pass | — | — | Pass |

Authentication coverage also includes Login, Owner Registration, Staff Registration from a valid invitation, both workspace choices, logo upload and all welcome stages. The separate Developer Console, notification tray, theme/font pickers, command search, SAGE AI, Guide and major finance, request/funding, staff, department, inventory, asset, evidence/report and acquisition dialogs were checked.

## Re-running the QA tools

Install Playwright in a development environment and install its Chromium browser. Start `python tools/qa_mobile.py`; it binds only to 127.0.0.1:5016 and creates temporary test data. In another terminal run:

```text
python tools/qa_mobile_browser.py --matrix
python tools/qa_mobile_interactions.py
python tools/qa_mobile_onboarding.py
python tools/qa_mobile_stability.py --mobile-only
```

For a same-content desktop comparison, provide the original CSS directory with `python tools/qa_mobile_stability.py --original-css PATH_TO_ORIGINAL_CSS`. The browser tools can use a local .qa-deps installation or the normal Python environment. QA screenshots/results are written to .qa and are not included in the deployment ZIP. The ZIP contains only changed/new source files, these QA tools and this report, preserving project-relative paths.
