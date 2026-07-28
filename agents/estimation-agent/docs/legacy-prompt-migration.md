# Legacy prompt migration map

The legacy prompt library remains unchanged in this milestone. Relevant content will later be reviewed and migrated into the controlled Estimation Agent workflows.

| Legacy prompt | Target workflow |
|---|---|
| `AI-Prompts/Tendering/01-Tender-Document-Review.md` | `rfp-analysis` |
| `AI-Prompts/Tendering/02-BOQ-Analysis.md` | `boq-development`, `quotation-comparison`, `pricing-risk-assessment` |
| `AI-Prompts/Tendering/03-Technical-Proposal.md` | `technical-proposal` |
| `AI-Prompts/Tendering/04-Commercial-Proposal.md` | `commercial-proposal` |
| `AI-Prompts/Tendering/05-Risk-Assessment.md` | `pricing-risk-assessment` |
| `AI-Prompts/Tendering/06-RFI-Generator.md` | `rfi-generation`, `commercial-query-generation` |
| `AI-Prompts/Tendering/07-Method-Statement.md` | Input to `technical-proposal`; future Construction Management Agent ownership |
| `AI-Prompts/Tendering/08-Execution-Plan.md` | Input to `technical-proposal`; future Project Management Agent ownership |
| `AI-Prompts/Tendering/09-Bid-NoBid-Decision.md` | Future tender-governance extension |
| `AI-Prompts/Tendering/10-Final-Bid-Review.md` | `final-bid-package` |

Migration requires domain review, evaluation cases, and preservation of useful content. A legacy prompt must not be deleted merely because a target workflow exists.
