# SAGE individual business upgrade

This ZIP contains changed and new files only, preserving their paths under sage_2.0. Back up the application and database, then merge these files into your existing application root. Keep your current .env, uploads and database. Restart the Python application. Two additive tables (solo_records and solo_entries) are created on startup; the database user must have CREATE permission. Existing records are not removed.

Existing individual owners automatically receive My Business navigation. Choose My business setup to change category. Organization navigation remains available for organization accounts. Optional helpers and events reuse the existing permission-controlled screens.

## Included
- Progressive AI responses with provider streaming, stop/retry and word-paced display.
- Compact logo uploader, explicit no-logo option and default user icon.
- 35 named business categories plus a custom category, with tailored starter offerings and labels.
- Dedicated individual overview and 18 tools: offerings, sales, costs, savings, bookings, customers, stock, goals, tasks, debts, startup budget, promotions, pricing calculator, reports, drawings, capital, recurring bills and business profile.
- Editable prices and estimated unit costs, Nigerian food starter names, makeup packages and influencer rate-card ideas. Prices are entered by the owner, not presented as market quotations.
- Savings targets and daily/weekly/monthly contribution plans, deposit/withdrawal history and balance checks. This tracks savings; it does not transfer money.
- Cash-basis profit and period filters, best-selling offerings and CSV export.
- Shared responsive form/modal constraints, compact phone layouts and improved dark-theme text contrast.

## Accounting behavior
Sales and repayments post income once; business spending posts expenses once. Savings, drawings and owner capital are separate transfers. Stock records track quantities; purchase costs must be recorded once in spending. Bookings, promotions, budgets and recurring bills are planning records and do not automatically post payments. Posted money entries are retained; check dates and amounts before saving. Profit is cash-basis, not accrual profit or inventory-adjusted cost of goods sold.

## Validation
43 tests passed, including four new individual-business tests; 25 existing tests failed. The unchanged uploaded code reproduces the same 25 failures (39 passes), principally around organization owner operation restrictions. All templates compile and all 19 individual pages render with a test owner. Modified JavaScript passes Node syntax checks.

Limitations: live provider streaming, cPanel/proxy buffering, real browser layouts and physical devices were not verified in this environment. Proxy buffering may delay network chunks, although the client still renders words progressively. Test on staging before replacing production. No claim is made that every legacy mobile page is visually verified. Legacy helpers, events and preferences retain their existing screens.
