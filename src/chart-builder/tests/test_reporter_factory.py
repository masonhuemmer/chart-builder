from chart.builder.modules.reportingservices import ReportingServicesFactory, ReportingServices

def test_datadog_reporter_factory(reporting_platform="datadog"):

    reporter_client = ReportingServicesFactory().get(reporting_platform)
    assert isinstance(reporter_client, ReportingServices)

def test_newrelic_reporter_factory(reporting_platform="newrelic"):

    reporter_client = ReportingServicesFactory().get(reporting_platform)
    assert isinstance(reporter_client, ReportingServices)

def test_local_reporter_factory(reporting_platform="local"):

    reporter_client = ReportingServicesFactory().get(reporting_platform)
    assert isinstance(reporter_client, ReportingServices)

def test_invalid_reporter_factory(reporting_platform=None):

    reporter_client = ReportingServicesFactory().get(reporting_platform)
    assert isinstance(reporter_client, ReportingServices)