# Memory Snapshot — project / revenuesystem

> Generated from append-only memory events. Do not edit manually.

## revenuesystem.audit.baseline_2026_10_06
- **Event:** `MEM-20261012-194151-83a063`
- **Level:** `L3_CANONICAL`
- **Kind:** `evidence`
- **Confidence:** `verified`
- **Updated:** `2026-10-12T19:41:51+03:00`
- **Summary:** Historical source-only audit closure at RevenueSystem SHA 7c6e5d4 remained incomplete and NO-GO for comprehensive closure/remediation planning; it is preserved as a dated audit baseline, not as a claim about current main.
- **Details:**
  - `capabilities_with_scoped_assertion_source`: 54
  - `coverage_states`: {"blocked": 4, "partial": 155, "source_only": 32, "verified": 0}
  - `current_main_revalidation_required`: true
  - `financial_invariants`: 20
  - `historical_only`: true
  - `major_holds`: ["H-01 live vs archived difference semantics", "H-02 DB restore/session/cache/pending-write barrier", "H-03 worksheet/date scope", "H-04 modifier-aware keyboard context", "H-05 bank/account/signed-outstanding semantics", "H-06 no-lost-capabilities before UI absorption", "H-07 latest-revision durable handoff"]
  - `mode`: AUDIT-ONLY / SOURCE-ONLY
  - `product_execution_count`: 0
  - `scoped_assertions_reviewed`: 100
  - `source_artifact`: 19_Comprehensive_Audit_Closure_Report.md
  - `source_sha`: 7c6e5d434c9b4ad98f263e02d197e2e7bede6667
  - `total_capabilities`: 191
  - `total_workflows`: 21
  - `verdict`: COMPREHENSIVE AUDIT INCOMPLETE — BLOCKERS REMAIN
- **Tags:** revenuesystem, audit, historical, source-only

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

## revenuesystem.data_management.contract
- **Event:** `MEM-20261012-194151-59b577`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:41:51+03:00`
- **Summary:** RevenueSystem must provide protected data reset plus create/edit/delete management for branches and cashiers, while distinguishing a full reset from deletion of user-entered operational data.
- **Details:**
  - `destructive_action_audit_required`: true
  - `implementation_status`: owner requirement; verify current RevenueSystem5 implementation before claiming complete
  - `required`: ["reset application data", "create branch", "edit branch", "delete/deactivate branch", "create cashier", "edit cashier", "delete/deactivate cashier"]
  - `reset_requires_confirmation`: true
- **Tags:** revenuesystem, data-management, reset, cashiers, branches

## revenuesystem.deployment.contract
- **Event:** `MEM-20261012-194151-7725bd`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:41:51+03:00`
- **Summary:** A final setup executable is a release deliverable only after required updates are merged and hardening/tests pass; installation/database locations must be explicit and the production machine role must not be inferred from chat history alone.
- **Details:**
  - `database_location_must_be_explicit`: true
  - `final_installer_required`: true
  - `hardening_before_release`: true
  - `implementation_status`: release requirement, not proof an installer is currently valid
  - `installation_location_must_be_explicit`: true
  - `merge_before_release`: true
  - `production_machine_identity`: must be verified at execution time
  - `tests_before_release`: true
- **Tags:** revenuesystem, deployment, setup, release

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

## revenuesystem.recovery_precision.contract
- **Event:** `MEM-20261012-194151-603525`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:41:51+03:00`
- **Summary:** As a financial application, RevenueSystem must prioritize exact financial calculations, preserve signed returns, autosave/recover unsaved work where feasible after sudden closure, and diagnose crash paths without silently losing committed or pending state.
- **Details:**
  - `autosave_and_recovery_required`: true
  - `committed_vs_pending_state_must_be_distinguishable`: true
  - `financial_precision_required`: true
  - `implementation_status`: owner requirement; current code/tests/runtime evidence decide completion
  - `signed_negative_returns_supported`: true
  - `sudden_close_diagnostics_required`: true
- **Tags:** revenuesystem, recovery, precision, crash, returns

## revenuesystem.reporting.contract
- **Event:** `MEM-20261012-194151-6f0b36`
- **Level:** `L4_OWNER_DIRECTIVE`
- **Kind:** `requirement`
- **Confidence:** `owner_confirmed`
- **Updated:** `2026-10-12T19:41:51+03:00`
- **Summary:** RevenueSystem reporting should retain daily-revenue review, add matching-difference and cash/electronic summaries, use portrait layouts by default, and keep branch/cashier reports concise and operationally useful.
- **Details:**
  - `branch_summary_goal`: cash and e-payment per branch on one A4 page where feasible
  - `difference_report_goal`: per branch, cashier name and difference only
  - `implementation_status`: owner requirement; verify current report services/artifacts before claiming complete
  - `keep`: ["مراجعة وارد يوم", "تقرير فروقات المطابقة", "ملخص النقدي والالكتروني"]
  - `layout`: portrait
  - `remove_or_deprecate`: ["مجاميع الفروع as a standalone legacy report where superseded"]
- **Tags:** revenuesystem, reports, portrait, matching

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
