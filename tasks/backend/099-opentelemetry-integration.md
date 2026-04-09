# 099: OpenTelemetry Integration

## Phase
All Phases

## Description
Distributed tracing with OpenTelemetry.

## Requirements
- Trace context propagation
- Span creation
- Export to collector
- Correlation IDs

## Acceptance Criteria
- [ ] Traces span requests
- [ ] Context propagates
- [ ] Exported correctly
- [ ] Viewable in UI

## Related Files
- `src/main.py` - OpenTelemetry instrumentation
- `src/config.py` - OTEL exporter config

## Dependencies
- 098: Structured Logging
