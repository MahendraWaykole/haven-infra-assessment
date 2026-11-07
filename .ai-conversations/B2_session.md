
Prompt-1
Lets implement scripts/cost_tag_check.py . It needs to read terraform plan JSON file and check if resources being created or updated have the correct billing tag. Look at fixture/plan.json to see how the tag are structured, If they are missing the tag, return exit code 1 and print the resource address. If all have it, return 0.

Output:
Implemented cost_tag_check.py to check create/update actions for a non-empty landlord_account_id tag, print each offending resource address once, and return a nonzero exit code when tags are missing. Invalid or unreadable plan files also report an error and fail.

Added tests for missing tags, all-tags-present success, and repeatable output in test_cost_tag_check.py. All 3 tests pass; Pylance reports no diagnostics.

scripts\cost_tag_check.py

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
    seen_addresses: set[str] = set()

    for index, resource in enumerate(plan["resource_changes"]):
        if not isinstance(resource, dict) or not isinstance(resource.get("change"), dict):
            print(f"Invalid Terraform plan: malformed resource change at index {index}.", file=sys.stderr)
            return 1

        change = resource["change"]
        actions = change.get("actions")
        if not isinstance(actions, list) or not all(isinstance(action, str) for action in actions):
            print(f"Invalid Terraform plan: malformed actions at resource index {index}.", file=sys.stderr)
            return 1

        if not any(action in {"create", "update"} for action in actions):
            continue

        address = resource.get("address")
        if not isinstance(address, str) or not address:
            print(f"Invalid Terraform plan: missing address at resource index {index}.", file=sys.stderr)
            return 1

        after = change.get("after")
        tags = after.get("tags") if isinstance(after, dict) else None
        landlord_account_id = tags.get("landlord_account_id") if isinstance(tags, dict) else None
        if not isinstance(landlord_account_id, str) or not landlord_account_id.strip():
            if address not in seen_addresses:
                missing_tag_addresses.append(address)
                seen_addresses.add(address)

    for address in missing_tag_addresses:
        print(address)

    return 1 if missing_tag_addresses else 0


    -----------------------------------

    tests\test_cost_tag_check.py

    
PLAN_PATH = Path(__file__).parents[1] / "fixtures" / "plan.json"


def test_plan_check_reports_resources_missing_landlord_account_tag(capsys):
    assert check_plan(str(PLAN_PATH)) == 1

    output = capsys.readouterr().out.splitlines()
    assert output == [
        "aws_s3_bucket.listing_media",
        "aws_lambda_function.mls_feed_sync",
    ]


def test_plan_check_is_idempotent(capsys):
    first_result = check_plan(str(PLAN_PATH))
    first_output = capsys.readouterr().out

    second_result = check_plan(str(PLAN_PATH))
    second_output = capsys.readouterr().out

    assert first_result == second_result == 1
    assert first_output == second_output

    ------------------------

prompt 2 >> Correction

wait this is incorrect . You looked at the corrent stae of plan.json and used tenant_id , but the README explicitly states that LandlordAccount is the real billing unit. The script must strictly enforce landlord_account_id, not tenant_id. also the assignment requires the script to be idempotent. you need to deduplicate the output so if the same resource address is processed twice in a single run, it doesnt print twice, Use the resource address as the idempotency key. Please rewrite the script with these fixes.


output


scripts\cost_tag_check.py

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

        --------------------

tests\test_cost_tag_check.py

        def test_tenant_tag_does_not_satisfy_billing_tag_and_duplicate_address_prints_once(
    tmp_path, capsys
):
    address = "aws_s3_bucket.listing_media"
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "resource_changes": [
                    {
                        "address": address,
                        "change": {
                            "actions": ["create"],
                            "after": {"tags": {"tenant_id": "ten-001"}},
                        },
                    },
                    {
                        "address": address,
                        "change": {
                            "actions": ["update"],
                            "after": {"tags": {"tenant_id": "ten-001"}},
                        },
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    assert check_plan(str(plan_path)) == 1
    assert capsys.readouterr().out.splitlines() == [address]