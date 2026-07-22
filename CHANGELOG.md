# Changelog

## 0.13.7 - 2026-07-22

### Added

- Added `ChatOpenAI.extra_body` passthrough for OpenAI-compatible provider extensions. This enables Volcengine Ark and DeepSeek-style request controls such as `thinking={"type": "enabled"}` / `thinking={"type": "disabled"}` and provider-specific reasoning parameters without hard-coding new model names.
- Added regression coverage to verify that `extra_body` fields are included in both plain and structured `ChatOpenAI` chat completion requests.
- Documented the live Volcengine Ark validation for `deepseek-v4-flash-260425` thinking mode, reasoning token usage, latency impact, and recommended Browser Use configuration.

### Notes

- For DeepSeek V4 Flash on Volcengine Ark, live validation showed that thinking is enabled by default. Use `extra_body={"thinking": {"type": "disabled"}}` when low latency and low token cost are more important than deeper reasoning.
- For complex Browser Use Agent tasks with this model, prefer prompt-only structured output compatibility with `add_schema_to_system_prompt=True`, `dont_force_structured_output=True`, and the existing schema cleanup flags.

## 0.13.6 - 2026-07-22

### Added

- Published the upstream 0.13.6 baseline as the `browser-use-volcengine` fork package.
- Recorded the fork release flow, including the local PyPI publishing script and annotated tag convention `browser-use-volcengine-<version>`.
- Recorded the fork rule that upstream upgrades must preserve and explicitly verify Volcengine-specific features.
