from aspose_pdf_cloud_mcp.errors import (
    AsposePdfToolError,
    error_payload,
    sanitize_message,
)


def test_sanitize_message_redacts_configured_and_inline_secrets(monkeypatch):
    monkeypatch.setenv("ASPOSE_CLIENT_SECRET", "super-secret-value")

    result = sanitize_message(
        "secret=super-secret-value client_secret=inline-value "
        "Authorization: Bearer bearer-value? access_token=query-value"
    )

    assert "super-secret-value" not in result
    assert "inline-value" not in result
    assert "bearer-value" not in result
    assert "query-value" not in result
    assert "<redacted>" in result


def test_structured_error_payload_includes_stable_code_and_details():
    error = AsposePdfToolError(
        "Missing file",
        code="not_found",
        details={"status": 404},
    )

    assert error_payload(error) == {
        "code": "not_found",
        "message": "Missing file",
        "details": {"status": 404},
    }


def test_unexpected_error_payload_does_not_expose_message():
    result = error_payload(RuntimeError("client_secret=should-not-leak"))

    assert result == {
        "code": "internal_error",
        "message": "Unexpected internal error.",
    }
