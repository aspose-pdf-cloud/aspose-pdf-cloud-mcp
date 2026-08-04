from importlib.metadata import version

import aspose_pdf_cloud_mcp


def test_runtime_version_matches_distribution_metadata():
    assert aspose_pdf_cloud_mcp.__version__ == version("aspose-pdf-cloud-mcp")
