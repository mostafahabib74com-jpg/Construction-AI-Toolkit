# Estimation Agent workflow catalog

## Recommended sequence

| Sequence | Workflow | Primary output | Required before final bid |
|---:|---|---|---|
| 1 | `rfp-analysis` | RFP requirement and document-control report | Yes |
| 2 | `scope-extraction` | Controlled scope matrix | Yes |
| 3 | `information-gap-analysis` | Missing/conflicting information register | Yes |
| 4 | `rfi-generation` | Technical RFI register | When required |
| 5 | `commercial-query-generation` | Commercial query register | When required |
| 6 | `design-basis-report` | Tender design basis | For design responsibility |
| 7 | `boq-development` | BOQ and quantity-basis report | Yes |
| 8 | `cbs-development` | CBS and mapping matrix | Yes |
| 9 | `excel-cost-model` | Workbook-generation specification and verified workbook | Yes |
| 10 | `quotation-comparison` | Normalized technical-commercial comparison | For quoted packages |
| 11 | `pricing-risk-assessment` | Pricing risk and opportunity register | Yes |
| 12 | `technical-proposal` | Technical proposal | If requested by RFP |
| 13 | `commercial-proposal` | Commercial proposal | Yes |
| 14 | `final-bid-package` | Bid manifest and readiness decision | Yes |

## Gate behavior

Workflows may iterate. A late addendum can reopen RFP analysis, scope, queries, BOQ, pricing, risk, proposals, and final reconciliation. Final-bid readiness requires the approved output version of every applicable upstream workflow.
