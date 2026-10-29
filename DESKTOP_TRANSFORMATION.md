# SAGE 8.0 — desktop visual transformation

This phase builds on the current, approved mobile project. It adds a desktop design system for the existing Flask/Jinja application and a compact local date/time display at the requested position on the mobile dashboard. The ZIP is a patch for this project, not a replacement application.

## Applying the patch

Extract `sage_8.0_desktop_visual_transformation.zip` over the current SAGE project, retaining its directory structure, then restart SAGE and refresh the browser. All generated desktop CSS is included; deployment needs no CSS build step or new runtime dependency. No database migration is required.

The archive contains only files added or changed during this desktop phase. Existing mobile improvements, approved source stylesheets, database files, configuration secrets, installed dependencies and QA screenshots are excluded. Keep the existing project assets and scripts in place.

## Architecture and maintenance

- `static/css/sage_desktop.css` owns desktop tokens, shell, identity, cards, registers, filters, workflow families, settings, dialogs, search, notifications and responsive refinements. Its component rules apply from **901px**. It introduces no `!important` declarations.
- The current source CSS had many legacy priority declarations. `tools/build_desktop_styles.py` compiles those exact current files into two normal cascade layers, `sage-foundation` and `sage-foundation-priority`; the new `sage-desktop` layer comes after them. This retains foundation precedence while allowing maintainable component rules. Nothing is imported from an older build.
- Four generated foundations cover the application, authentication, owner registration and developer console. Their `.sources.json` files record SHA-256 hashes of the current source files. Rebuild them with `python tools/build_desktop_styles.py` after changing a source stylesheet. **tinycss2 is a development/build dependency only.**
- `templates/partials/workspace_styles.html` loads the appropriate foundation before first paint. A cold phone loads the original mobile sources, not the desktop foundation. Crossing the breakpoint fetches the other foundation once; each link has an explicit media condition.
- `desktop_workspace.html` supplies business identity, role scope, local page-open time, section shortcuts and saved filters. The shared `page_content.html` wrapper is rendered during full and partial navigation. The only `app.py` change is selecting that wrapper for partial HTML rendering.
- `static/js/desktop_ui.js` binds to explicit page/style lifecycle events. Saved filters are stored on the device, scoped to account, organization and page; they reuse the existing input/change handlers. They do not change business records or server permissions. A filter bar appears only when the workspace has usable filters.
- Existing mobile decorators remain available. Desktop avoids redundant legacy visual markers and pointer-following effects. New desktop code adds no continuous animation loop, polling interval, global subtree observer or frontend framework. Submit-state observation is limited to button disabled attributes.
- Chart labels inherit the selected desktop font. Axes/grid colors use the desktop palette. Mobile chart styling follows the existing branch.
- `sage_clock.css`, `dashboard_mobile_clock.html` and the clock initializer in `vision.js` implement the requested phone addition. The display has fixed dimensions and tabular figures, uses the device's local time zone, updates digital text on minute boundaries and pauses while hidden. The existing desktop analog clock remains; it updates with one timer rather than an animation-frame loop. Navigation clears the previous timer.

No accounting calculations, posting flows, models, schemas, API permissions, tenant isolation, invitation logic, approval rules or export routes were changed. Existing owner/staff/individual permissions remain the authority for visible actions.

## Implemented refinements by logical page family

The lists below describe implemented presentation or interaction changes. Existing business capabilities are not presented as new features. Shared components are reused where that improves consistency; workflow-specific treatments are listed separately.

### Dashboard — 20 refinements

1. Preserved the four main summary-card desktop proportions and responsive grid.
2. Replaced competing legacy decoration with a single executive page hierarchy.
3. Added a compact business/family context row.
4. Made the current management/individual/role scope visible in that row.
5. Added a local **Viewed** timestamp, explicitly describing page-open time.
6. Added a shortcut menu for the dashboard's real content sections.
7. Added controlled layered summary surfaces with inset highlights.
8. Added thin financial-state accents instead of large ornamental overlays.
9. Unified main amount weight, spacing and tabular figures.
10. Differentiated positive revenue, expenditure and negative position values.
11. Improved secondary explanatory text hierarchy and contrast.
12. Refined pending versus clear approval chips.
13. Unified summary footer links, dividers and chevrons.
14. Refined the compact receivables/payables/inventory/budget strip.
15. Brought request funding/balance tiles into the same surface system.
16. Improved attention and management-alert card hierarchy.
17. Refined chart surfaces, legends and theme-aware axes.
18. Refined activity/report/feed rows and timestamps.
19. Made floating AI/Finance utilities compact icon controls with labels on hover/focus, reducing content obstruction.
20. Preserved the desktop analog clock and added the stable digital date/time to owner and staff mobile dashboards.

### Finance & Control — 24 refinements

Applies to Requests, Income, Expenses, Finance, Debtors, Imprest and Daily Close, with the dashboard refinements above.

1. Revenue uses restrained green identity; spend uses coral; treasury uses the selected financial accent.
2. Added a distinct, bounded title surface and contextual description for each workspace.
3. Preserved and refined existing export actions rather than adding new export logic.
4. Standardized Today/Week/Month/Year money-card hierarchy.
5. Used container-aware amount sizing for long period totals.
6. Made Visible Entries a compact full-width summary below the period cards.
7. Refined average/largest entry insight cards.
8. Improved evidence-coverage and current-scope text wrapping.
9. Refined the revenue-versus-budget surface and progress treatment.
10. Gave Finance KPI cards readable standalone liquidity/position values and retained semantic icons.
11. Removed duplicate generic Finance glyphs that competed with those icons.
12. Unified the treasury account, budget and forecast card system.
13. Refined liquidity/position/cash-flow/reconciliation navigation states.
14. Grouped native filter controls into bounded workbenches.
15. Added device-local saved filter views, apply and reset on supported registers.
16. Kept the filter-view toolbar reachable beneath the fixed header.
17. Added numbered rows where the register did not already have numbers.
18. Added sticky, legible table headers inside scrolling registers.
19. Distinguished references, descriptions, counterparties and supporting metadata through weight and spacing.
20. Right-aligned money columns with stable numeric figures and intact currency values.
21. Refined evidence, payment-method, category and transaction-state treatments.
22. Refined request cards/history, funding ledgers and acquisition handoff surfaces while retaining their workflow.
23. Differentiated debtor overdue/over-30-day summary bands and emphasized existing overdue date markers.
24. Gave Imprest and Daily Close ledger surfaces, clearer empty records, detail accents and coherent form/modal actions.

### Departments & Operations — 24 refinements

Applies to Workspace, Catalogue, Operations, Acquisition, Procurement, Inventory, Assets, Events and Advanced Stock.

1. Added a restrained operational accent across workspace identity surfaces.
2. Refined role/department hero cards and scope descriptions.
3. Standardized compact catalogue/custom-item/inventory/request metric cards.
4. Refined job-tool cards and consistent semantic icon tiles.
5. Added steady background/border hover feedback to tools instead of movement.
6. Refined operational-action controls and their grouping.
7. Refined catalogue group headings and section dividers.
8. Refined catalogue item cards, secondary units and request actions.
9. Refined active catalogue filter-chip states.
10. Improved owner catalogue-coverage tiles, labels, counts and icon spacing.
11. Added section shortcuts for operational sections that actually exist on the page.
12. Added saved native search/filter views where controls exist.
13. Removed unusable saved-view bars from pages without filters.
14. Unified Procurement's process, supplier and purchase-trace surfaces.
15. Refined requested/approved/released/actual acquisition summary blocks.
16. Refined the Acquisition Financial Pulse and its four numeric readouts.
17. Refined acquisition funding/balance ledgers and evidence controls.
18. Kept Inventory columns at a readable desktop minimum width with contained horizontal scrolling.
19. Kept Operations' multi-field register readable through its own scroll region.
20. Gave Assets wider identity/serial/department/custodian columns and intact value/action columns.
21. Refined item icon tiles, custodian emphasis and movement-history rows.
22. Emphasized existing low-stock labels and warning/danger stock-health states.
23. Gave Events a restrained amber identity and a readable three-column KPI layout instead of cramped six-column labels.
24. Refined event detail sections and operational empty states without adding unauthorized creation actions.

### Organization, people and accountability — 24 refinements

Applies to Customers, Suppliers, Branches, Departments, Staff, Reports, Audit and Payroll.

1. Gave relationship/people workspaces a controlled violet accent.
2. Added business and permission context above their main page identities.
3. Added section shortcuts and saved filters on supported directories/registers.
4. Added compact initials marks to existing customer/supplier record links.
5. Preserved full names and separated supporting contact metadata typographically.
6. Refined CRM metric and contact/detail surfaces.
7. Refined invoice/sales and outstanding-value table hierarchy.
8. Refined supplier identity, payable and acquisition-history surfaces.
9. Arranged Branch management disclosures in a two-column desktop grid.
10. Kept branch search and performance registers full width.
11. Refined department cards, department icons and summary strips.
12. Kept department-card hover states stationary.
13. Refined staff KPI bands and directory hierarchy.
14. Arranged staff search/department/role/status filters in a compact desktop row.
15. Preserved readable staff identity/contact/department column boundaries.
16. Refined staff avatars, roles, statuses and archive presentation.
17. Refined staff selection/bulk-action states without changing the actions.
18. Refined invitation, editing, removal and staff-activity dialog surfaces.
19. Gave Reports real analytical summary cards, rather than tiny unstructured readouts.
20. Refined report inbox filters, period controls and export matrices.
21. Gave Audit a controlled governance identity and compact native filters.
22. Refined chronological audit rows, actor/reference metadata, state comparison and exception surfaces.
23. Kept Payroll financial profiles/runs/payslips visually distinct with treasury accents and clear detail divisions.
24. Made owner delegation guidance a compact management banner, with no new operational permissions.

### Insights and governance — 20 refinements

Applies to Analytics, Bills, Compliance and Business Operations Reports.

1. Gave Analytics/reporting a restrained analytical identity.
2. Gave Bills an amber deadline identity.
3. Gave Compliance a cyan governance identity.
4. Added business/role context and local page-open time.
5. Added section shortcuts for actual analytical/deadline sections.
6. Refined analytical KPI surfaces and supporting descriptions.
7. Improved long nonnumeric KPI messages such as missing prior revenue.
8. Refined chart-card headers and explanatory captions.
9. Refined chart framing, surfaces and legends.
10. Made chart axes/grid colors follow the desktop theme.
11. Made desktop chart labels follow the chosen font.
12. Refined risk/anomaly, category and department-comparison surfaces.
13. Added saved native search views where Bills/Compliance expose filters.
14. Improved deadline register row density, numbering and metadata hierarchy.
15. Emphasized existing Overdue markers with readable semantic ink and an inset marker.
16. Refined existing active/status text and state pills without inventing urgency data.
17. Refined payment, renewal and document/evidence detail sections.
18. Gave the Business Reports period form a full-width, grouped date-control surface.
19. Arranged Business Reports summary metrics into four readable desktop columns and three laptop columns.
20. Refined analytical empty states, export links, table focus/hover and evidence actions.

### System, settings and supporting entry screens — 24 refinements

1. Refined Settings identity and business context.
2. Added section shortcuts for long settings sections.
3. Refined the settings navigation surface and grouping.
4. Gave the active tab a bounded accent and inset marker.
5. Unified settings navigation icon sizing and button height.
6. Improved profile label hierarchy.
7. Gave readonly profile values a consistent surface, font and border.
8. Standardized profile-grid spacing.
9. Refined the display-currency control as a grouped settings row.
10. Improved currency-control explanation typography.
11. Refined the currency selector and rate/status readout.
12. Refined settings health/status strips and subpanels.
13. Refined section titles, rules and smaller descriptions.
14. Standardized keyboard focus across tabs, fields, links and actions.
15. Made disabled controls visibly distinct.
16. Preserved the selected theme/font/text-size controls and pre-paint preference restoration.
17. Added theme-aware desktop authentication canvas and form surfaces.
18. Refined authentication input sizing, labels, borders and focus.
19. Refined authentication submit buttons and the password-dialog surface.
20. Kept registration's existing multi-step workflow while integrating its desktop form surface.
21. Disabled continuous desktop registration orbit movement.
22. Refined developer-console hero/KPI/panel surfaces using the console's own six-theme tokens.
23. Refined console table headers, row hierarchy, scroll shells and active navigation.
24. Removed console header blur while keeping desktop/mobile console behavior and administrative permissions.

### Shared dialogs and utilities — 20 refinements

1. Standardized desktop dialog surface, border and shadow.
2. Retained different widths for simple and complex forms.
3. Bounded dialog height by available space below the header.
4. Kept dialog scrolling inside the intended content area.
5. Refined dialog icon tiles.
6. Refined eyebrow/title/subtitle hierarchy.
7. Refined contextual workflow-step markers.
8. Standardized grouped field gaps and label hierarchy.
9. Refined financial summary and reconciliation blocks.
10. Refined upload/evidence controls.
11. Refined info/warning callouts.
12. Refined close controls with a visible bounded target.
13. Made action footers sticky where the existing modal uses them.
14. Kept native V4 form submit controls reachable in their portals.
15. Observed real submit-button disabled state for `aria-busy` and compact progress feedback.
16. Kept background content sharp when dialogs open.
17. Refined command-search surface, results, keyboard hint and active result.
18. Refined notification icon, title, message, timestamp and unread state.
19. Refined theme/font menus, selection and focus feedback.
20. Placed the bounded desktop live brief near the lower edge, keeping filter actions reachable.

## Page-by-page workflow audit

Every routed workspace was inspected against its current template, current permissions and populated/empty QA state. Main content remains server-rendered. Creation buttons continue to appear only where the current project permits them; the visual pass does not reinterpret delegation rules.

| Workspace | Main information / workflow | Presentation audited |
|---|---|---|
| Dashboard | Owner executive summary or staff role workspace | Money, approvals, attention, accounts, requests, charts, reports/activity and clocks |
| Requests & Approvals | Requester, department, stage, funding, evidence | Owner decisions, staff requests, history ledger and funding/return dialogs |
| Income & Sales | Posted revenue, period/scope, source and evidence | Period KPIs, insights, budget chart, native filters, export and register |
| Expenses & Expenditure | Posted spend, department, vendor and evidence | Spend KPIs, insights, categories, native filters, export and register |
| Finance | Liquidity, position, cash flow and reconciliation | Accounts, budgets, AR/AP, ledger, recorded-by/status/reference/amount and forms |
| Debtors & Credit Sales | Outstanding, due, overdue and ageing | Exposure bands, customer/invoice ledger and collection/history detail |
| Petty Cash & Imprest | Held, issued, retired and returned money | Fund register, cash-history detail, holder/receipt/approval forms and empty state |
| Daily Sales / POS Close | Expected/count/variance and approval | Reconciliation register/detail, payment methods and empty state |
| Department Workspace | Job scope, catalogue, items and requests | Role hero, compact summaries, focus/actions, tools and request sections |
| Department Catalogue | Industry/department items and custom items | Owner coverage, staff groups, search/chips, request and custom-item dialog |
| Department Operations | Actor, activity, item/quantity, money and time | Role actions, organization/staff stream, register and operation dialog |
| Acquisition Hub | Released versus actual and evidence | Financial pulse, approved queue, balances, final summaries and purchase modal |
| Procurement | Need/approval/vendor/purchase/receipt/evidence | Process cards, trace stages, suppliers, approved queue and catalogue |
| Inventory | Availability, reorder, value and movements | Stock-health states, readable register, search, move/add dialogs and movement feed |
| Assets | Identity, serial, department, custodian and value | Wider register columns, status, search, move/add dialogs and history |
| Events & Campaigns | Schedule, funding and outcomes | Three-column KPIs, event register/detail, outcome report and form portal |
| Advanced Stock Control | Quantities, cost, selling price, margin and reorder | Register, low-stock emphasis, batches, transfers/counts and movement history |
| Customers & CRM | Identity, relationship, sales and balances | Contact rows, initial marks, detail/activity/invoices and permitted forms |
| Suppliers & Vendors | Identity, contact, payables and history | Supplier rows, initial marks, quotation/documents/acquisition/payable detail |
| Branches & Shops | Access, accounts, property and performance | Paired management disclosures, full register, branch department summaries |
| Departments | Department identity, users and scope | Department cards, counts, create dialog and scoped links |
| Staff | Identity, role, department, contact and status | Compact filters, directory, selection/bulk actions, archive and staff dialogs |
| Reports | Staff submissions, periods, comparison and exports | Analytical cards, inbox, charts, report detail/generation and export controls |
| Audit Trail | Time, actor, action, resource and state history | Filters, chronology, before/after rows, references, exceptions and metadata |
| Staff Finance & Payroll | Profiles, runs, payslips, advances and claims | Section hierarchy, sensitive financial rows, approvals/evidence and portals |
| Analytics | Trend, category, risk and department performance | KPIs, comparison charts, legends, themes and empty analytical sections |
| Bills & Renewals | Due/overdue, recurrence, vendor and payments | Deadline register, existing overdue markers, payment history/evidence and forms |
| Compliance Centre | Category, identifier, expiry, responsible party and evidence | Governance register, expiry emphasis, renewal/documents and permitted forms |
| Business Operations Reports | Period summary and operational discovery | Period form, money/count grids, due items, exports and reminder controls |
| Settings | Profile, roles, approval, finance, notifications and security | Tab navigation, readonly fields, currency, status/health, descriptions and controls |

Login, organization registration, individual registration flow, staff invitation registration, developer sign-in/console, global search, notifications, theme/font menus and SAGE AI were also included in the audit. Shared and native form portals retain the existing keyboard/close behavior.

## Verification

QA runs use `tools/qa_desktop.py`, which creates an isolated temporary SQLite database and storage directory with populated owner, responsible staff, finance and individual-owner accounts. Email and push delivery are disabled. It never opens the live project database. Generated test accounts, very large test amounts and test organization names in screenshots are fixture data.

Test programs included in this phase:

- `qa_desktop_browser.py`: before/after captures, allowed role/page combinations, requested desktop/mobile widths, overflow, figures and headings.
- `qa_desktop_same_content.py`: old/new mobile comparisons using the same current fixture records, with only clock/live-time text masked for image comparison.
- `qa_desktop_interactions.py`: saved-view persistence/account isolation, SPA navigation, section shortcuts, hover stability, adaptive loading, clocks, appearance controls, search/notification/AI and modal surfaces.
- `qa_desktop_entrypoints.py`: login/register/staff/developer screens and console palettes, responsive bounds and original mobile appearance comparison.
- `qa_desktop_contrast.py`: browser-resolved foreground/background contrast of shared desktop body, muted, accent, semantic and action tokens.
- `qa_desktop_fonts.py`: hosted-font rendering and amount bounds, separate from deterministic fallback-font screenshots.

The fixture helper uses the existing `tools/qa_mobile.py`. Browser QA requires Playwright/Chromium; paired screenshots also use Pillow. These are QA dependencies, not application runtime dependencies. The local pre-phase snapshot under `.qa/desktop_before` is needed only to reproduce comparisons and is excluded from the patch ZIP.

### Release results

- **30 workspace routes / 95 permitted account-page combinations**, covering organization owner, staff, finance and individual-owner modes.
- **570 desktop states** at 1024×768, 1280×720, 1366×768, 1440×900, 1536×864 and 1920×1080. The last sweep identified staff/finance Catalogue overflow; its parent minimum width and KPI/chip layout were corrected and both roles then passed all six sizes. No remaining overflow, clipped sampled KPI amount, hidden main heading or uncaught JavaScript error.
- **190 mobile geometry states** at 390×844 and 430×932. Static-baseline differences were confined to live Dashboard/Audit content. A final **32 old/new comparisons using identical current records** passed, including affected roles, catalogue pages and desktop-to-mobile resizing. In 12 owner-page image comparisons, masked changes were 0–16 pixels per 329,160-pixel screenshot (at most 0.0049%); clock/live-time text was excluded from the image diff.
- **Six original-versus-new shell comparisons** preserve the responsive sidebar and 82px header footprint: sidebar 252px at 1024, 264px at the other requested widths.
- **9/9 interaction groups** pass: saved-view apply/reset/persistence/account isolation/SPA navigation; section navigation; stationary hover; adaptive styles; clock behavior; palettes; fonts; utilities; and dialogs/JavaScript errors. A follow-up also confirms exact mobile foundation order after repeated breakpoint changes.
- **40 modal/native form-portal surfaces** checked, including funding, acquisition, staff, inventory/assets, money entries and operational forms. Bounds include the reachable lower edge, not just modal height.
- **152 theme/page states** across the 19 existing palettes, and **608 sampled shared-token foreground/background contrast pairs** across four page families; all sampled pairs reach at least 4.5:1. This is a targeted contrast audit, not a claim of a formal application-wide accessibility certification.
- **All ten actual hosted fonts loaded**, with **60 font/size/width cases** passing money-figure bounds. The deterministic screenshot suite separately tests the same choices with hosted fonts blocked.
- **Three time zones**, midnight rollover, fixed clock dimensions, no per-second digital text writes and repeated partial navigation verified.
- **40 responsive auth/console states**, four registration-step states including the initial step, and six console palettes checked. Login, owner registration, staff registration and developer sign-in have **zero changed mobile pixels** against their original styles. Console comparison differs only by a small live-content area; its template body and source mobile CSS are unchanged.
- **18/18 existing mobile onboarding/form/stress checks** pass, including organization/individual registration, native pickers, logo preview, welcome stages, operational fields, large money values and the compact AI action menu.
- A cold phone downloads **zero desktop foundation/design CSS files**. Each foundation is fetched once as needed across breakpoint changes.
- CSS parsing, Python/JavaScript syntax, source hashes and unchanged original CSS/auth-console template bodies verified. The one backend-file diff is the UI partial-wrapper rendering line.

All workflow screenshots were reviewed by page family; the final corrections include asset-column wrapping, staff filter density, branch action layout, event KPI spacing, empty-row numbering, semantic deadline ink and catalogue layout. Production posting, email delivery and destructive administrative actions were deliberately not exercised; their existing implementations were not changed.

### Archive contents

The patch contains **37 files**: 11 CSS/manifest files, four JavaScript files, 12 templates/partials, `app.py`, eight build/QA tools and this report. Generated desktop foundations are included. Original source CSS, existing mobile scripts, images, catalogue seed data, service worker/manifest, QA databases and screenshots are excluded because they were not modified in this phase.
