# SAGE mobile refinements — screenshot follow-up

This update addresses the seven supplied screenshots and adds the 20 interactions listed below. It builds on the first mobile redesign. Desktop chat and navigation section icons were explicitly included in this follow-up; other desktop page layouts retain their prior geometry.

## Screenshot fixes

| Area | Result |
| --- | --- |
| Staff | Separate, explicit column widths prevent long names, emails and departments from overlapping. The staff identity column stays visible during horizontal scrolling. Filters occupy a compact swipe shelf. |
| Audit filters | Search, category, department and dates share a compact horizontal shelf with 36px controls. Presets and Clear stay small. Category summaries become a horizontal shelf instead of a long stack. |
| Audit history | A semantic four-column register replaces the broken phone timeline. It has a sticky date column/header, bounded vertical scrolling and 25/50/100-row pages. Search and filters cover every event loaded by the existing Audit view (up to its current 600-event limit), including events outside the current phone page. Desktop retains its timeline presentation. |
| Workspace | The four operational summaries form a compact 2×2 grid, with aligned labels, values and helper text. |
| SAGE AI | One dedicated stylesheet owns the desktop and mobile panel. The narrower panel sits inside the visible viewport, above the header, with a permanent Close button, independent conversation scrolling, colored role markers, topic icons, safe answer formatting and a visible composer. The page behind it remains sharp. |
| Live Pulse | On phones, the card is at the bottom, beside the quick-action button, with a maximum width of 264px. It can be minimized, expanded or dismissed. |
| Sidebar | The mobile drawer is at most 280px wide. All five section headers have visible icons on mobile and desktop. Account text truncates cleanly. |

## Why the layouts broke

- A later flex rule overrode the Workspace card grid, allowing four cards to collapse into narrow strips. The mobile card layout now has one explicit grid definition.
- Audit used four timeline parts inside a mobile two-column grid. Converting the phone view to native table cells preserves the relationship between each event's date, type, activity and action.
- Staff's flexible identity content could exceed its column. Explicit column plans and bounded wrapping keep each value within its cell.
- AI presentation was scattered across six stylesheets. Its old selectors were removed and the panel now has one layout owner. Fixed grid rows keep the composer in place when suggestions are hidden; visual-viewport handling accommodates an on-screen keyboard.
- Clock text changes triggered repeated decoration scans over the entire Audit page. Observers now respond to structural content changes, date formatters are reused, and mobile Audit retains non-current pages outside the rendered table. Scroll observers are shared and disconnected page wrappers are released after navigation.

## The 20 additional mobile features implemented

1. **Navigation quick search:** search only the pages available to the signed-in account; clear the search or open the first match with Enter.
2. **Recent pages:** three recent permitted pages appear as shortcuts in the drawer, stored separately for each account in the browser session.
3. **Previous page:** the More menu provides a shortcut to the previous app page.
4. **Back restores reading position:** returning through browser history restores the page's vertical position.
5. **Back restores register columns:** horizontal table positions are restored with the page.
6. **Column snapping:** table headers provide proximity snap points during horizontal navigation.
7. **Register navigation controls:** previous/next column arrows plus Left, Right, Home and End keyboard shortcuts on a focused register.
8. **Staff name sorting:** switch between ascending and descending name order.
9. **Staff result count and reset:** see matching versus total accounts and clear directory filters together.
10. **Clear staff selection feedback:** selected rows are highlighted and the bulk-action bar stays accessible while selected rows are present.
11. **Audit pagination:** choose 25, 50 or 100 events per phone page and move between matching pages.
12. **Audit date sorting:** reverse the chronological order from the Date / Time header.
13. **Removable Audit filter chips:** see active filters and remove an individual filter with one tap.
14. **AI latest-message shortcut:** return to the newest reply while preserving your place when reading older messages.
15. **AI draft retention:** an unsent question survives closing or reloading the panel, within the same account/browser session, for up to one hour.
16. **AI retry:** a failed or stopped question can be retried without retyping or duplicating its history context.
17. **AI Stop and request state:** stop waiting for a reply; busy controls prevent duplicate sends, and state feedback shows readiness or failure.
18. **Keyboard-aware composer:** phone Enter inserts a new line, Send submits, and the panel adjusts to the visible viewport when the keyboard opens. Desktop Enter still sends; Shift+Enter inserts a new line.
19. **Readable AI answers:** headings, lists, bold text, inline code and highlighted currency amounts, with HTML escaped before formatting. Copy preserves the original answer text.
20. **Pulse minimize/expand:** collapse the live update to a small summary and restore it when needed.

## Verification

The regression fixture uses a temporary SQLite database, 33 organization accounts with long names/departments, and 600 retained Audit events. AI replies are intercepted locally in Chromium; these tests make no external model calls.

- Staff, Audit and Workspace: 33 layout combinations across 320–900px, including actual row alignment and overflow checks.
- Audit: all-event search, date order, 25/50/100 paging, categories, presets, removable chips, empty results and desktop filtering.
- Navigation: drawer width/icons, search, recents, previous/back behavior, restored scroll/columns and a separate staff-account permission check.
- AI: portrait, landscape, desktop, reduced-height and visual-viewport keyboard cases; visible Close/composer, no blur, drafts, formatting/escaping, copy, retry, Stop, multiline input and focus restoration.
- Pulse: bottom placement, width, separation from the quick-action button, minimize and expand.
- Ten same-content desktop page geometry comparisons passed: Dashboard, Income, Expenses, Finance, Requests, Workspace, Staff, Departments, Audit and Settings.
- The populated Audit sidebar test improved from approximately 6.9 seconds before this follow-up to 0.4–0.8 seconds in repeated local browser runs, including automation overhead. Device performance will vary.
- JavaScript syntax, CSS parsing and whitespace checks passed. No production routes, database schema, accounting rules or authorization policies were changed.

The final sweep passed all 94 permitted account/page combinations across 14 viewport widths (1,316 viewport states, including 940 mobile states), with no mobile document overflow, broken table semantics or overflowing financial values. All 48 shared-menu/dialog interactions and 52 pre-/post-initialization size comparisons also passed. No uncaught JavaScript errors were reported.

The cumulative `sage_mobile_complete_redesign.zip` contains 35 changed/new source, template, documentation and QA-tool files in their project-relative folders. It includes the first redesign plus these refinements, so it can be extracted into the SAGE project directly. No credentials, databases, temporary dependencies or QA output files are included.

## Re-running

Start `python tools/qa_mobile.py` in a development environment with the application dependencies installed. It creates temporary test data and binds only to `127.0.0.1:5016`.

With Playwright and its Chromium browser installed, run:

```text
python tools/qa_mobile_revision.py --mobile-only
python tools/qa_mobile_browser.py --matrix
python tools/qa_mobile_interactions.py
python tools/qa_mobile_stability.py --mobile-only
```

The optional same-content desktop test uses the pre-follow-up template/asset snapshot when it is available in `.qa/revision_before`; that local snapshot is excluded from the deployment ZIP. Screenshots, logs, temporary dependencies and test databases are also excluded. The original redesign report remains in `MOBILE_REDESIGN.md` for its earlier verification and known backend test baseline.
