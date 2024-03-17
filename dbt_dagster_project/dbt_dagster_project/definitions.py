# first version was built according to Udemy course
# import os

# from dagster import Definitions
# from dagster_dbt import DbtCliResource

# from .assets import dbtlearn_dbt_assets
# from .constants import dbt_project_dir
# from .schedules import schedules

# defs = Definitions(
#     assets=[dbtlearn_dbt_assets],
#     schedules=schedules,
#     resources={
#         "dbt": DbtCliResource(project_dir=os.fspath(dbt_project_dir)),
#     },
# )

# this new version was built to implement webhook for Elementary data
import os
import hmac
import requests
from dagster import solid, pipeline, repository, make_values_resource, RunRequest
from dagster_dbt import dbt_cli_resource
from .assets import dbtlearn_dbt_assets
from .constants import dbt_project_dir
from .schedules import schedules

# Here's the new solid definition
@solid(required_resource_keys={"dbt"})
def trigger_elementary_sync(context):
    secret = os.environ.get("ELEMENTARY_SECRET").encode()  # Storing the secret in an environment variable is safer
    webhook_url = os.environ.get("ELEMENTARY_WEBHOOK_URL")  # Get the webhook URL from environment variable
    request_body = b""

    # Generating the signature
    signature = hmac.new(secret, request_body, "sha256").hexdigest()

    # Making the POST request to the webhook URL
    response = requests.post(webhook_url, headers={"Authorization": signature}, data=request_body)

    if response.ok:
        context.log.info("Webhook triggered successfully.")
    else:
        context.log.error(f"Webhook trigger failed with status code: {response.status_code}")
        raise Exception(f"Webhook trigger failed with status code: {response.status_code}")

# Defining the pipeline
@pipeline
def dbt_dagster_pipeline():
    dbtlearn_dbt_assets()
    trigger_elementary_sync()

# Defining resources for dbt
dbt_resources = {
    "dbt": dbt_cli_resource.configured({"project_dir": os.fspath(dbt_project_dir)}),
}

# Wrap everything in a repository
@repository
def my_repository():
    return [
        dbt_dagster_pipeline,
        schedules,
        make_values_resource(dbt_resources)
    ]
