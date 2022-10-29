"""Logs into Platform hosting Kubernetes to generate a kubeconfig for Helm to install charts."""

from logging import Logger
import timeit
import traceback

from datetime import timedelta
from rich.console import Console

from chart.builder.modules.arguments import get_parser
from chart.builder.modules.clusteroperations import ManagedClusterOperationsFactory
from chart.builder.modules.clusterservices import ManagedClusterServicesFactory
from chart.builder.modules.packagemanager import PackageManagerFactory
from chart.builder.modules.reportingservices import ReportingServicesFactory


def main(args: object, console: object, reporter: object) -> None:
    """
    Logs into platform hosting kubernetes, generates a kubeconfig, and installs a helm chart.

    :param args: An instantiated 'argparse.Namespace' class.
    :type args: object

    :param console: An instantiated 'rich.console' class
    :type console: object

    :param log: An instantiated 'Reporter' class
    :type reporter: object

    return None
    """

    try:

        # Start Timer
        start_time = timeit.default_timer()

        # Print Console
        console.print("Running [italic bold]chart-builder[white]...")
        
        # Cluster Operations
        managed_cluster_operations = ManagedClusterOperationsFactory().get("azure")
        managed_cluster_operations.build_cluster_admin_credentials(
            args.resource_group,
            args.cluster,
            args.tenant_id,
            args.client_id,
            args.client_secret)

        # Cluster Services - build namespace, build registry credentials
        managed_cluster_services = ManagedClusterServicesFactory().get("azure")
        managed_cluster_services.build_namespace(args.helm_namespace)
        managed_cluster_services.build_registery_credentials(
            name=args.pull_secret_name,
            registry=args.docker_registry,
            username=args.docker_username,
            password=args.docker_password,
            namespace=args.helm_namespace)

        # # Package Manager - build package, deploy package
        package_manager = PackageManagerFactory().get("helm")
        package = package_manager.build(
            release=args.helm_release,
            chart=args.helm_chart,
            namespace=args.helm_namespace,
            version=args.helm_version,
            repository=args.helm_repository,
            values=args.helm_values,
            sets=args.helm_sets,
            atomic=args.helm_atomic,
            timeout=args.helm_timeout,
            wait=args.helm_wait)     
        package_manager.deploy(package)

        # Post event to reporter
        reporter.post_event(service=args.app_name, env=args.environment, version=args.app_version, team=args.app_team)

        # Record elapsed time
        elapsed_time = timeit.default_timer() - start_time
        console.print(f"[white]Summary:[/] [bright_green]{timedelta(seconds=elapsed_time)}[/]")

    except Exception: # pylint: disable=broad-except
        
        # Record elapsed time
        elapsed_time = timeit.default_timer() - start_time
        console.print(f"[white]Summary:[/] [bright_green]{timedelta(seconds=elapsed_time)}[/]")

        # Post error to reporter
        event_message = f'An operation failed:\n{traceback.format_exc()}'
        reporter.post_event(
            service=args.app_name,
            env=args.environment,
            event_message=event_message,
            version=args.app_version,
            team=args.app_team,
            event_status="error")

if __name__ == "__main__":

    # Get Logger
    console = Console(color_system="standard")

    # Get Arguments
    args, unknown_args = get_parser().parse_known_args()
    if unknown_args:
        console.print(f"[yellow]Unrecognized arguments:[/] [white italic]{unknown_args}[/]")

    # Get Reporter
    reporter = ReportingServicesFactory().get(args.reporting_platform)

    # Run Main
    main(args, console, reporter)