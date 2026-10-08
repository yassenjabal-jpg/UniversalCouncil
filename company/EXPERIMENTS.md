# Experiments

Each experiment declares hypothesis, buyer, alternative, price, channel, qualification, success/failure/inconclusive rules, time/cash/tool/owner-minute caps, liabilities, and invalidators.

Default planning ceiling: 14 days, up to 20 qualified first contacts, at most one follow-up after 5 business days. These are not permissions or statistical proof.

Twenty contacts with no replies can be INCONCLUSIVE_CHANNEL_OR_TARGETING rather than automatic market rejection.

No strategy change during a live experiment except a declared gate, owner instruction, or genuinely invalidating evidence.


## Channel diagnosis before market interpretation
A non-response is not automatically a rejection.

Before counting NO_REPLY as negative market evidence, test:
- delivery;
- channel fit;
- contact/person fit;
- timing;
- offer/message fit.

Allowed diagnostic states include:
INSUFFICIENT_EVIDENCE / DELIVERY_FAILURE / CHANNEL_FAILURE / CONTACT_FAILURE / TIMING_FAILURE / OFFER_FAILURE / NOT_INTERESTED.

Only NOT_INTERESTED counts as an explicit rejection. Repeated silence may still be evidence, but only after channel/contact/timing assumptions are supported.

## Founder-mode experiment rule
When collected revenue is zero, every proposed experiment must justify why it deserves the next operating block relative to alternatives, state Cost of Delay, and include a default KILL/PIVOT/REJECT/HOLD action if its declared gate is missed.
