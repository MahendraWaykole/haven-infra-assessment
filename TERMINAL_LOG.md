
1. Manual cost tag check run 1 (Showing non-zero exit on missing tags)
terminal output: 
(.venv) PS D:\Mahendra\Assignments\haven-infra-assessment> python scripts/cost_tag_check.py fixtures/plan.json
aws_s3_bucket.listing_media
aws_lambda_function.mls_feed_sync
(.venv) PS D:\Mahendra\Assignments\haven-infra-assessment> echo $LASTEXITCODE
1

2. manual cost tag check run 2 (proving idempotency)
Teminal output:
(.venv) PS D:\Mahendra\Assignments\haven-infra-assessment> python scripts/cost_tag_check.py fixtures/plan.json
aws_s3_bucket.listing_media
aws_lambda_function.mls_feed_sync
(.venv) PS D:\Mahendra\Assignments\haven-infra-assessment> echo $LASTEXITCODE                             
1   

3. Pytest execution
Terminal output:
(.venv) PS D:\Mahendra\Assignments\haven-infra-assessment> pytest -v                                      
========================================== test session starts ==========================================
platform win32 -- Python 3.13.1, pytest-9.2.0, pluggy-1.7.0 -- D:\Mahendra\Assignments\haven-infra-assessment\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Mahendra\Assignments\haven-infra-assessment
collected 7 items                                                                                        

tests/test_access_control.py::test_property_manager_cannot_access_another_landlord_account_report PASSED [ 14%]
tests/test_access_control.py::test_property_manager_can_access_report_for_their_landlord_account PASSED [28%]
tests/test_access_control.py::test_missing_tenant_fails_closed PASSED                              [ 42%]
tests/test_cost_tag_check.py::test_plan_check_passes_when_all_changed_resources_have_billing_tag PASSED [57%]
tests/test_cost_tag_check.py::test_tenant_tag_does_not_satisfy_billing_tag_and_duplicate_address_prints_once PASSED [ 71%]
tests/test_cost_tag_check.py::test_plan_check_reports_resources_missing_landlord_account_tag PASSED [ 85%]
tests/test_cost_tag_check.py::test_plan_check_is_idempotent PASSED                                 [100%]

=========================================== 7 passed in 0.30s ===========================================
(.venv) PS D:\Mahendra\Assignments\haven-infra-assessment> 