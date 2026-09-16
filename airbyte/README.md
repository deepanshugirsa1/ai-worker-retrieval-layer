# Airbyte-compatible sync notes

Custom TypeScript connectors implement the same read/cursor contract as Airbyte sources.
Export JSONL + state files to `data/raw` for the Python orchestrator (destination handoff).

Production path: run Airbyte with Salesforce/HubSpot sources into ClickHouse, or keep these connectors.
