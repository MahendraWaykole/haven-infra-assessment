"""
B2, part 2 — implement the cost-tagging check.

Read fixtures/plan.json for the shape of a `terraform show -json` plan: a `resource_changes`
list, where each entry has a `type`, an `address`, and `change.after.tags`.

Implement check_plan() so it:
  - Looks at every resource being created or updated (skip anything whose change.actions
    isn't "create" or "update" — a "no-op"/"read" change, or a "delete" with no `after`
    block at all).
  - Fails (returns a non-zero exit code) if the resource is missing the tag that identifies
    the real billing unit, per README.md's domain model — not whatever tag the resource
    happens to already carry.
  - Is idempotent: running this twice against the same plan file produces the same result,
    with no duplicate output and no flipped pass/fail. This is about a single run being
    stable and repeatable — it does not require remembering anything between runs.
  - Prints which specific resource address(es) are missing the tag.

Run manually: python scripts/cost_tag_check.py fixtures/plan.json
"""
import json
import sys


def check_plan(plan_path: str) -> int:
    """
    Returns an exit code: 0 if every resource being created or updated has
    `landlord_account_id`, non-zero otherwise.
    """
    try:
        with open(plan_path, encoding="utf-8") as plan_file:
            plan = json.load(plan_file)
    except OSError as error:
        print(f"Error reading plan file {plan_path!r}: {error}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"Error parsing plan file {plan_path!r}: {error}", file=sys.stderr)
        return 1

    if not isinstance(plan, dict) or not isinstance(plan.get("resource_changes"), list):
        print("Invalid Terraform plan: expected a resource_changes list.", file=sys.stderr)
        return 1

    missing_tag_addresses: list[str] = []
    seen_missing_addresses: set[str] = set()

    for index, resource in enumerate(plan["resource_changes"]):
        if not isinstance(resource, dict) or not isinstance(resource.get("change"), dict):
            print(
                f"Invalid Terraform plan: malformed resource change at index {index}.",
                file=sys.stderr,
            )
            return 1

        change = resource["change"]
        actions = change.get("actions")
        if not isinstance(actions, list) or not all(isinstance(action, str) for action in actions):
            print(
                f"Invalid Terraform plan: malformed actions at resource index {index}.",
                file=sys.stderr,
            )
            return 1

        if not any(action in {"create", "update"} for action in actions):
            continue

        address = resource.get("address")
        if not isinstance(address, str) or not address:
            print(
                f"Invalid Terraform plan: missing address at resource index {index}.",
                file=sys.stderr,
            )
            return 1

        after = change.get("after")
        tags = after.get("tags") if isinstance(after, dict) else None
        landlord_account_id = (
            tags.get("landlord_account_id") if isinstance(tags, dict) else None
        )
        if not isinstance(landlord_account_id, str) or not landlord_account_id.strip():
            if address not in seen_missing_addresses:
                missing_tag_addresses.append(address)
                seen_missing_addresses.add(address)

    for address in missing_tag_addresses:
        print(address)

    return 1 if missing_tag_addresses else 0


if __name__ == "__main__":
    sys.exit(check_plan(sys.argv[1]))
