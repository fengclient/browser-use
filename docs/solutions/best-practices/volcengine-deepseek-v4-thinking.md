---
title: Volcengine Ark DeepSeek V4 Thinking Mode
date: 2026-07-22
category: best-practices
module: llm/openai
problem_type: provider-compatibility
component: assistant
severity: low
applies_when:
  - "Using DeepSeek V4 models through Volcengine Ark's OpenAI-compatible chat API"
  - "Tuning thinking depth, latency, and token cost for Browser Use Agent runs"
  - "Passing provider-specific OpenAI-compatible request extensions"
tags: [volcengine, ark, deepseek, thinking, reasoning-effort, openai-compatible]
---

# Volcengine Ark DeepSeek V4 Thinking Mode

## Context

Volcengine Ark exposes DeepSeek V4 models through an OpenAI-compatible chat completions API. The provider also supports thinking-mode controls documented in the Volcengine deep-thinking guide and the DeepSeek thinking-mode guide.

Useful references:

- Volcengine deep-thinking guide: https://docs.volcengine.com/docs/82379/1449737?lang=zh
- Volcengine Ark chat API parameters: https://api.volcengine.com/api-docs/view?action=ContextChatCompletions&serviceCode=ark&version=2024-01-01
- DeepSeek thinking-mode guide: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode

`ChatOpenAI` should not hard-code every new provider model name. Provider-specific controls such as `thinking` are better passed through the OpenAI SDK's `extra_body` request option.

## Live Validation

Validation date: 2026-07-22

Provider: Volcengine Ark

Model: `deepseek-v4-flash-260425`

Prompt shape: a short multi-step logic question with a constrained final answer.

| Case | Result | Elapsed | Reasoning content | Completion tokens | Reasoning tokens |
| --- | --- | ---: | --- | ---: | ---: |
| No thinking parameter | Passed | 18.43s | yes | 647 | 644 |
| `thinking={"type": "disabled"}` | Passed | 1.74s | no | 3 | 0 |
| `thinking={"type": "enabled"}` | Passed | 20.54s | yes | 718 | 715 |
| `thinking={"type": "enabled"}, reasoning_effort="low"` | Passed | 25.15s | yes | 934 | 931 |
| `thinking={"type": "enabled"}, reasoning_effort="high"` | Passed | 19.26s | yes | 690 | 687 |
| `thinking={"type": "enabled"}, reasoning_effort="max"` | Passed | 15.55s | yes | 578 | 575 |
| `reasoning_effort="max"` without explicit thinking | Passed | 19.74s | yes | 719 | 716 |

The same model was also validated through Browser Use's `ChatOpenAI` wrapper:

| Case | Result | Elapsed | Completion tokens |
| --- | --- | ---: | ---: |
| `ChatOpenAI` default | Passed | 16.67s | 649 |
| `reasoning_models=[model], reasoning_effort="max"` | Passed | 18.60s | 744 |
| `reasoning_models=[model], reasoning_effort="high"` | Passed | 17.13s | 653 |

After adding `ChatOpenAI.extra_body`, the provider-specific path was validated directly through Browser Use:

| Case | Result | Elapsed | Total tokens |
| --- | --- | ---: | ---: |
| `extra_body={"thinking": {"type": "disabled"}}` | Passed, exact sentinel returned | 1.32s | 36 |
| `extra_body={"thinking": {"type": "enabled"}, "reasoning_effort": "max"}` | Passed, exact sentinel returned | 2.51s | 144 |

## Findings

DeepSeek V4 Flash on Volcengine Ark appears to enable thinking by default. A request without any thinking parameter returned `reasoning_content` and hundreds of `reasoning_tokens`.

Explicitly disabling thinking had the largest cost and latency impact in the validation run: completion tokens dropped from hundreds to 3, and latency dropped from about 18 seconds to under 2 seconds.

`reasoning_effort="high"` and `reasoning_effort="max"` were accepted by Ark for this model. On this small prompt, `max` did not consume more tokens than `high`; treat the setting as a reasoning-policy request, not as a deterministic token budget.

The OpenAI SDK accepts `reasoning_effort` as a standard chat completion parameter, but provider-specific fields such as `thinking` need the SDK's `extra_body` parameter.

## Recommended Browser Use Configurations

For lower latency and lower token cost:

```python
llm = ChatOpenAI(
	model="deepseek-v4-flash-260425",
	api_key=api_key,
	base_url="https://ark.cn-beijing.volces.com/api/v3",
	extra_body={"thinking": {"type": "disabled"}},
)
```

For deeper reasoning on complex Browser Use Agent tasks:

```python
llm = ChatOpenAI(
	model="deepseek-v4-flash-260425",
	api_key=api_key,
	base_url="https://ark.cn-beijing.volces.com/api/v3",
	extra_body={
		"thinking": {"type": "enabled"},
		"reasoning_effort": "max",
	},
	add_schema_to_system_prompt=True,
	dont_force_structured_output=True,
	remove_min_items_from_schema=True,
)
```

If using `reasoning_effort` through Browser Use's existing standard parameter path, include the model in `reasoning_models` so `ChatOpenAI` sends it:

```python
llm = ChatOpenAI(
	model="deepseek-v4-flash-260425",
	api_key=api_key,
	base_url="https://ark.cn-beijing.volces.com/api/v3",
	reasoning_models=["deepseek-v4-flash-260425"],
	reasoning_effort="max",
)
```

Prefer `extra_body` when using Ark/DeepSeek-specific thinking controls, because it handles both `thinking` and non-OpenAI `reasoning_effort` values without expanding Browser Use's default model-name list.

## Environment Note

When a global proxy is enabled, local Browser Use Agent runs may accidentally route local CDP or test HTTP server traffic through that proxy. Use localhost bypass variables for local verification:

```bash
NO_PROXY=localhost,127.0.0.1,::1 no_proxy=localhost,127.0.0.1,::1 uv run pytest tests/ci/models/test_openai_extra_body.py
```

This is an environment-level workaround and does not require Browser Use source changes.

## Related

- Local implementation: `browser_use/llm/openai/chat.py`
- Regression tests: `tests/ci/models/test_openai_extra_body.py`
- Structured-output compatibility note: `docs/solutions/best-practices/openai-json-object-vs-json-schema.md`
