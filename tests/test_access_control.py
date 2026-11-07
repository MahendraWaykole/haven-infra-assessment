"""
Write tests here proving:
  1. A PropertyManager scoped to la-001 (pm-001) is DENIED access to la-002's tenant's
     screening report (rep-002).
  2. The same PropertyManager (pm-001) IS allowed access to their own account's screening
     report (rep-001).

Use the `property_managers`, `properties`, `tenants`, and `screening_reports` fixtures from
conftest.py — don't re-invent the seed data here.
"""
from dataclasses import replace

from app.access_control import can_access_screening_report


def test_property_manager_cannot_access_another_landlord_account_report(
    property_managers, properties, tenants, screening_reports
):
    assert not can_access_screening_report(
        property_managers[0],
        screening_reports[1],
        properties=properties,
        tenants=tenants,
    )


def test_property_manager_can_access_report_for_their_landlord_account(
    property_managers, properties, tenants, screening_reports
):
    assert can_access_screening_report(
        property_managers[0],
        screening_reports[0],
        properties=properties,
        tenants=tenants,
    )


def test_missing_tenant_fails_closed(
    property_managers, properties, tenants, screening_reports
):
    report_without_tenant = replace(screening_reports[0], tenant_id="missing-tenant")

    assert not can_access_screening_report(
        property_managers[0],
        report_without_tenant,
        properties=properties,
        tenants=tenants,
    )
