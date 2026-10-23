# Square direct-client payment path

2026-10-22: owner reports an existing U.S. Square Retail account with successful payments and transfers. This satisfies an important prerequisite by owner attestation; no dashboard, bank details or transaction records were accessed. Square plugin discovery returned no match; no connector or API key was installed.

For a directly acquired client, use the existing account's invoice or payment link after agreeing a narrow scope and price. No custom checkout or new subscription is required by the proposed route. The owner must confirm the account permits the service, current plan rate and any account-specific hold before sending an invoice. Keep platform-origin work on its required payment rails.

Workflow: owner authorizes one contact → buyer confirms current need → agree scope, price, deadline and acceptance/refund terms → owner sends a Square invoice or payment link → verify paid status in Square (not a buyer screenshot) → deliver accepted scope → record gross, fees, refunds, net and transfer status. Never mark an invoice draft, sent invoice or pending card authorization as collected revenue. Preserve only redacted transaction references and settlement evidence, not card/bank details.

Illustrative U.S. online rate from current Square documentation: 3.3% + USD 0.30; actual account/legacy plan rates may differ. A USD 100 domestic card payment at that rate yields USD 96.40 before taxes, refunds and other costs; after 2–3h at assumed USD 25/hour, modeled labor-adjusted contribution is USD 21.40–46.40. International-card surcharge can reduce this; transfer fees/holds may also apply. These are scenarios, not income or an account quote.

Sources accessed 2026-10-22:
- https://squareup.com/us/en/payment-links (payment links without upfront fee)
- https://squareup.com/help/us/en/article/5068-what-are-square-s-fees (plan-dependent rates and international surcharge)
- https://squareup.com/help/us/en/article/5085-accepted-cards (international cards/country/currency boundaries)
- https://api.squareup.com/help/us/en/article/3807-deposit-options-with-square (transfer options and limits)

No invoice/link was created or sent, no payment collected, and no bank settings changed. Account readiness is owner-confirmed, not independently verified. Next customer step is a single approved qualification message, not payment configuration.
