# Memory Snapshot — project / revenuesystem

> Generated from append-only memory events. Do not edit manually.

## revenuesystem.currency_model
- **Event:** `MEM-20261012-192851-eda6d5`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `policy`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Keep Iraqi coarse cash, Iraqi change and USD separated throughout the application; USD is converted to IQD and summed only in matching/comparison logic where required.
- **Details:**
  - `currencies`: ["IQD coarse", "IQD change", "USD"]
  - `financial_precision_required`: true
  - `implementation_status`: requirement; repository remains execution truth
  - `separate_everywhere`: true
  - `usd_conversion_scope`: matching/comparison only
- **Tags:** revenuesystem, currency, financial

## revenuesystem.import_contract
- **Event:** `MEM-20261012-192851-478e5a`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Imported cashier/branch data must preserve and display point of sale, cashier name, meal/shift and branch; negative spreadsheet values are valid returns and must be handled correctly.
- **Details:**
  - `cash_denominations_imported_from_excel`: false
  - `implementation_status`: requirement; verify importer behavior from RevenueSystem5
  - `negative_values_mean_returns`: true
  - `required_display_fields`: ["نقطة البيع", "اسم الكاشير", "الوجبة", "الفرع"]
- **Tags:** revenuesystem, import, excel, returns

## revenuesystem.matching_accounts.contract
- **Event:** `MEM-20261012-192851-5805a3`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Matching is cashier-centric and integrates manual matching, e-payment breakdowns and customer-account transfer; Rafidain and SWITCH bank amounts must remain distributable per cashier for later reconciliation.
- **Details:**
  - `cashier_cards`: true
  - `customer_account_system`: كشف الحساب
  - `customer_account_transfer_integrated`: true
  - `e_payment_banks`: ["Rafidain", "SWITCH"]
  - `implementation_status`: requirement; verify repository state
  - `manual_matching`: true
  - `per_cashier_bank_distribution`: true
  - `usd_conversion_in_matching_only`: true
- **Tags:** revenuesystem, matching, accounts, epayment

## revenuesystem.operational_day.rule
- **Event:** `MEM-20261012-192851-a842ac`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `policy`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Operational days remain open for date differences of 0–2 days; at 3 days or more they become read-only and auto-closure is logged.
- **Details:**
  - `auto_closure_logged`: true
  - `implementation_status`: requirement; verify repository implementation
  - `open_day_difference`: [0, 1, 2]
  - `read_only_from_day_difference`: 3
- **Tags:** revenuesystem, operational-day, policy

## revenuesystem.product_identity
- **Event:** `MEM-20261012-192851-e7b13e`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `decision`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** The desktop revenue application is named «المطابقة» and exists to replace/streamline the legacy daily revenue workflow.
- **Details:**
  - `display_name`: المطابقة
  - `implementation_status`: verify current repository before claiming UI state
  - `platform`: Windows desktop / WPF
- **Tags:** revenuesystem, identity, wpf

## revenuesystem.revenue_entry.contract
- **Event:** `MEM-20261012-192851-84a323`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** Cashier revenue entry must support autosave, direct Iraqi-total input, and arithmetic expressions in denomination fields; cash denominations are entered in-app rather than imported from Excel.
- **Details:**
  - `autosave`: true
  - `denominations`: [25000, 10000, 5000, 50000]
  - `direct_iqd_total`: true
  - `excel_denomination_import`: false
  - `expression_behavior`: evaluate note count expression then multiply by denomination
  - `expression_example`: 80+2
  - `implementation_status`: requirement; verify current code/tests before claiming complete
- **Tags:** revenuesystem, cash-entry, autosave, denominations

## revenuesystem.source_of_truth
- **Event:** `MEM-20261012-182400-e5f6a7`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `policy`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T18:24:00+03:00`
- **Summary:** RevenueSystem execution must use the actual yassenjabal-jpg/RevenueSystem5 repository, current main SHA, governing files, commits/PRs/CI/tests/migrations/artifacts as evidence; chat history is inference only.
- **Details:**
  - `chat_claim_is_not_execution_evidence`: true
  - `repository`: yassenjabal-jpg/RevenueSystem5
- **Tags:** revenuesystem, source-of-truth

## revenuesystem.ui_hardening.contract
- **Event:** `MEM-20261012-192851-879e93`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:28:51+03:00`
- **Summary:** RevenueSystem UI must minimize wasted title-bar space, prevent overlapping text, show popup fields without unnecessary sidebars/scrolling where feasible, keep window controls top-right, and preserve reliable keyboard navigation.
- **Details:**
  - `avoid`: ["duplicate title bars", "text overlap", "wasted header space"]
  - `implementation_status`: historical hardening requirement; current repository must be audited before claiming complete
  - `keyboard_requirements`: ["Enter field flow", "arrow navigation", "PageUp/PageDown cashier navigation", "Home/End where specified", "Ctrl+Z"]
  - `popup_goal`: show all important fields without sidebars when feasible
  - `window_controls`: top-right
- **Tags:** revenuesystem, ui, keyboard, hardening
