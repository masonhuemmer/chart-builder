from argparse import ArgumentParser, Action
from typing import Optional, IO
from rich.console import Console
from rich.panel import Panel

import os
import re
import sys

# Global Variables
console = Console(color_system="standard")

class RichParser(ArgumentParser):

    def error(self, message):
            message = message.split(":")
            console.print(f"[bright_red]{message[0]}:[/] [white italic]{message[1]}[/]")
            sys.exit(2)

class EnvDefault(Action):
    def __init__(self, metavar, required=True, default=None, **kwargs):
        if not default and metavar:
            if metavar in os.environ:
                default = os.environ[metavar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(metavar=metavar, default=default, required=required, 
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

def environment(env: str):
    # Get Environment Variable
    list_supported_environments = os.environ["CHART_BUILDER_SUPPORTED_ENVIRONMENTS"].split(",")

    if env.lower() not in list_supported_environments:

        # Create String Value for Printout
        str_supported_environments = ', '.join(list_supported_environments)

        # Printout Error Message
        console.print(f"[bright_red]argument --environment:[/] [white italic] must be one of the following values: {str_supported_environments}[/]")

        # Exit Job
        sys.exit(2)

    return env.lower()

def get_parser():

    # PARSER OBJECT
    parser = RichParser(
        description="Logs into platform hosting kubernetes, generates a kubeconfig, and installs a helm chart."
    )

    # ---------------------------
    # DEFAULT ARGUMENTS
    # ---------------------------
    default = parser.add_argument_group("Default arguments")

    # DEPARTMENT NAME
    default.add_argument("--department-name",
        action=EnvDefault, metavar="DEPARTMENT_NAME", required=False,
        dest="department_name",
        help="The department that owns the application.",
    )

    # DEPARTMENT TEAM
    default.add_argument("--department-team",
        action=EnvDefault, metavar="DEPARTMENT_TEAM", required=False,
        dest="department_team",
        help="The department team who owns the application.",
    )

    # APP NAME
    default.add_argument("--app-name",
        action=EnvDefault, metavar="APP_NAME", required=False,
        dest="app_name",
        help="Name of the application.",
    )

    # APP TEAM
    default.add_argument("--team",
        action=EnvDefault, metavar="APP_TEAM", required=False,
        dest="app_team",
        help="Application Team.",
    )

    # APP VERSION
    default.add_argument("--version", "--app-version",
        action=EnvDefault, metavar="APP_VERSION", required=False,
        dest="app_version",
        help="Version of the application.",
    )

    # ENVIRONMENT
    default.add_argument("--environment",
        action=EnvDefault, metavar="ENVIRONMENT",
        dest="environment", type=environment,
        help="Supported environments: [ eph, dev, test, stage, prod ]",
    )

    default.add_argument("--reporting-platform",
        action=EnvDefault, metavar="REPORTING_PLATFORM", required=False,
        dest="reporting_platform",
        help="The reporting platform where events are posted (Datadog, NewRelic, Local). Do not set this flag within your gitlab job.",
    )

    # ---------------------------
    # AZURE ARGUMENTS
    # ---------------------------
    azure = parser.add_argument_group("Azure arguments")

    # CLUSTER NAME
    azure.add_argument("--clustername", "--aksclustername",
        action=EnvDefault, metavar="AKS_CLUSTER_NAME",
        dest="cluster",
        help="Name of the Managed Kubernetes Cluster.",
    )

    # RESOURCE GROUP
    azure.add_argument("--resource-group", "--aksclusterresourcegroup",
        action=EnvDefault, metavar="AKS_CLUSTER_RESOURCE_GROUP", required=False,
        dest="resource_group",
        help="Name of resource group.",
    )

    # CLIENT ID
    azure.add_argument("--client-id", "--username",
        action=EnvDefault, metavar="AKS_SERVICE_PRINCIPAL_ID",
        dest="client_id",
        help="Service principal ID. Do not set this flag within your gitlab job.",
    )

    # Client Secret
    azure.add_argument("--client-secret", "--password",
        action=EnvDefault, metavar="AKS_SERVICE_PRINCIPAL_PASSWORD",
        dest="client_secret",
        help="Service principal Secret. Do not set this flag within your gitlab job.",
    )

    # Tenant ID
    azure.add_argument("--tenant", "--tenant-id",
        action=EnvDefault, metavar="AZURE_TENANT_ID",
        dest="tenant_id",
        help="The AAD tenant, must provide when using service principals. Do not set this flag within your gitlab job.",
    )

    # ---------------------------
    # DOCKER ARGUMENTS
    # ---------------------------
    docker = parser.add_argument_group("Docker arguments")

    # Docker Registry
    docker.add_argument("--docker-registry", "--container-registry",
        action=EnvDefault, metavar="DOCKER_REGISTRY", required=False,
        dest="docker_registry",
        help="Host where container images are stored.",
    )

    # Docker Username
    docker.add_argument("--docker-username",
        action=EnvDefault, metavar="DOCKER_USERNAME", required=False,
        dest="docker_username",
        help="Username to authenticate to the Container registry.",
    )

    # Docker Password
    docker.add_argument("--docker-password",
        action=EnvDefault, metavar="DOCKER_PASSWORD", required=False,
        dest="docker_password",
        help="Password to authenticate to the Container registry.",
    )

    # PULL SECRET NAME
    docker.add_argument("--pull-secret-name",
        action=EnvDefault, metavar="PULL_SECRET_NAME", required=False,
        dest="pull_secret_name",
        help="Name for Docker Registry Secret.",
    )

    # ---------------------------
    # HELM ARGUMENTS
    # ---------------------------
    helm = parser.add_argument_group("Helm arguments")

    # Helm Repository
    helm.add_argument("--repository", "--helm-repository",
        action=EnvDefault, metavar="HELM_REPOSITORY", required=False,
        dest="helm_repository",
        help="A repository to the chart, packaged, or fully qualified URL.",
    )

    # Helm Chart
    helm.add_argument("--chart", "--helm-chart",
        action=EnvDefault, metavar="HELM_CHART",
        dest="helm_chart",
        help="A path to a chart directory, a packaged chart, or a fully qualified URL.",
    )

    # Helm Release
    helm.add_argument("--release", "--helm-release",
        action=EnvDefault, metavar="RELEASE",
        dest="helm_release",
        help="Release name for a chart instance installed in Kubernetes.",
    )

    # Helm Namespace
    helm.add_argument("--namespace", "--helm-namespace",
        action=EnvDefault, metavar="NAMESPACE",
        dest="helm_namespace",
        help="Namespace scope for this request.",
    )

    # Helm Values
    helm.add_argument("--helm-values",
        action="append", required=False,
        dest="helm_values",
        help="Specify values in a YAML file or a URL (can specify multiple)",
    )

    # Helm Set
    helm.add_argument("--helm-set",
        action="append",required=False,
        dest="helm_sets",
        help="Set values on the command line (can specify multiple or separate values with commas: key1=val1,key2=val2)",
    )

    # Helm Atomic
    helm.add_argument("--helm-atomic",
        dest="helm_atomic", default="True",
        help="If set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used",
    )

    # Helm Timeout
    helm.add_argument("--helm-timeout",
        action=EnvDefault, metavar="HELM_TIMEOUT", required=False,
        dest="helm_timeout",
        help="time to wait for any individual Kubernetes operation (like Jobs for hooks) (default 5m0s)",
    )

    # Helm Wait
    helm.add_argument("--helm-wait",
        dest="helm_wait",
        help="Time to wait for any individual Kubernetes operation (like Jobs for hooks) (default 5m0s)",
    )

    # Helm Version
    helm.add_argument("--helm-version",
        action=EnvDefault, metavar="HELM_VERSION", required=False,
        dest="helm_version",
        help="Specify a version constraint for the chart version to use. This constraint can be a specific tag (e.g. 1.1.1) or it may reference a valid range (e.g. ^2.0.0). If this is not specified, the latest version is used.",
    )

    # ---------------------------
    # DATADOG ARGUMENTS
    # ---------------------------
    datadog = parser.add_argument_group("Datadog arguments")

    datadog.add_argument("--datadog-site",
        action=EnvDefault, metavar="DD_SITE", required=False,
        dest="datadog_site",
        help="Datadog Site.",
    )

    datadog.add_argument("--datadog-api-key",
        action=EnvDefault, metavar="DD_API_KEY", required=False,
        dest="datadog_api_key",
        help="Datadog API Key.",
    )

    datadog.add_argument("--datadog-apo-key",
        action=EnvDefault, metavar="DD_APP_KEY", required=False,
        dest="datadog_app_key",
        help="Datadog APP Key.",
    )

    # ---------------------------
    # LEGACY ARGUMENTS
    # ---------------------------
    legacy = parser.add_argument_group("Legacy arguments")

    # New Relic App Name
    legacy.add_argument("--new-relic-app-name",
        action=EnvDefault, metavar="NEW_RELIC_APP_NAME", required=False,
        dest="newrelic_app_name",
        help="Name of the application to be reported to New Relic.",
    )

    return parser
