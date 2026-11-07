# Design Notes

## B2 — idempotency key

State exactly what key your `cost_tag_check.py` uses to decide whether two resources in the
same run are "the same" for dedup purposes, and why running it twice against an unchanged
plan file produces identical output and exit code without the script keeping any record
between runs. Use the word "idempotency" in your explanation.

The checker uses each Terraform resource's `address` as its idempotency key. During one run,
addresses missing `landlord_account_id` are recorded in a set before being printed, so repeated
entries for the same resource produce only one finding. The script reads the plan and builds this
result from scratch each time; for an unchanged plan, the same addresses are found in the same
order, producing identical output and exit code without storing state between runs.

## Any other decision with a non-obvious alternative

The checker strictly requires a non-empty `landlord_account_id` tag rather than accepting
`tenant_id`. The README defines `LandlordAccount` as the billing unit, and properties, tenants,
and their resources roll up to that account. A tenant ID identifies an individual tenant, not
the account responsible for the cost, so it cannot reliably support billing attribution. Even
though some existing resources in the plan are tagged with `tenant_id`, treating that as a valid
substitute would hide missing billing ownership; those resources should be updated to include
`landlord_account_id`.
