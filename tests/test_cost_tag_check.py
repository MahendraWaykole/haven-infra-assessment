"""
Write tests here proving:
  1. Happy path: running the check against fixtures/plan.json correctly flags the resources
     missing `landlord_account_id` (listing_media, mls_feed_sync) and passes the ones that
     have it (landlord_media[0], screening_report_export). The fixture also has a "no-op"
     entry and a "delete" entry with no `after` block at all — neither should appear in the
     output or crash the check.
  2. Idempotency: running the check twice against the same plan file produces the same
     result both times, with no duplicated output.

check_plan() takes a file path, not a dict — for a case that needs its own plan contents
instead of the shared fixture, write one with pytest's `tmp_path` rather than editing
fixtures/plan.json. You don't need to shell out to the real script for every case.
"""
import json
from pathlib import Path

from scripts.cost_tag_check import check_plan


PLAN_PATH = Path(__file__).parents[1] / "fixtures" / "plan.json"


def test_plan_check_passes_when_all_changed_resources_have_billing_tag(
    tmp_path, capsys
):
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "resource_changes": [
                    {
                        "address": "aws_s3_bucket.landlord_media[0]",
                        "change": {
                            "actions": ["create"],
                            "after": {"tags": {"landlord_account_id": "la-001"}},
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert check_plan(str(plan_path)) == 0
    assert capsys.readouterr().out == ""


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
