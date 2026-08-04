# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Upgrade the server to the MCP Python SDK 2.x `MCPServer` API.
- Advertise the generated SCM package version in the MCP server identity.

## [1.0.0] - 2026-08-03

### Added

- MCP (Model Context Protocol) server for AI-powered PDF operations
- Agent skill installer for bundled `aspose-pdf-cloud-mcp` integration
- Support for extracting images from PDF pages with page range filtering
- Support for extracting tables as JSON with page range filtering
- Support for PDF/A version and type selection in conversion
- Comprehensive live smoke tests for Aspose Cloud operations
- Documentation for MCP configuration and agent integration
- Storage file download with local path support
- Storage folder listing and traversal
- PDF text extraction command
- PDF image listing command
- PDF merge operation with folder merge support
- PDF split operation with custom page range selection
- PDF to PDF/A conversion with version/type selection
- Configuration system with environment variable support
- Project documentation and examples
