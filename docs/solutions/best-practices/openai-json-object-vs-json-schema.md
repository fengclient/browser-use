---
title: OpenAI JSON Object vs JSON Schema Structured Outputs
date: 2026-06-11
category: best-practices
module: llm/openai
problem_type: best_practice
component: assistant
severity: low
applies_when:
  - "Adding structured-output support for OpenAI-compatible providers"
  - "Choosing between json_schema, json_object, and prompt-only structured output"
  - "Debugging providers that reject response_format type json_schema"
tags: [openai, structured-output, json-schema, json-object, llm-compatibility, pydantic]
---

# OpenAI JSON Object vs JSON Schema Structured Outputs

## Context

`ChatOpenAI` currently treats Pydantic `output_format` as a strict structured-output request. It builds an optimized JSON Schema, sends it through OpenAI `response_format` with `type='json_schema'`, and validates the model response locally with `output_format.model_validate_json(...)`.

Some OpenAI-compatible providers support `response_format={"type": "json_object"}` but not `json_schema`. That raises the question of whether Browser Use should fall back to JSON object mode for compatibility.

## Guidance

Keep `json_schema` as the default structured-output mode. Use `json_object` only as an explicit compatibility fallback for providers that reject `json_schema`.

Recommended behavior if adding fallback support:

```python
structured_output_mode: Literal["json_schema", "json_object", "none"] = "json_schema"
```

- `json_schema`: current default. Send strict schema through `response_format`.
- `json_object`: send `response_format={"type": "json_object"}`, also inject the schema into the system prompt, then validate locally with Pydantic.
- `none`: do not send `response_format`; rely on prompt instructions and local validation.

Do not silently downgrade from `json_schema` to `json_object` for all OpenAI-compatible providers. JSON object mode only guarantees a valid JSON object, not adherence to the requested schema.

Existing schema-cleanup flags still matter whenever the schema is generated. For example, `remove_min_items_from_schema=True` affects the schema injected into the prompt when `add_schema_to_system_prompt=True`, even if the API request does not send `json_schema`.

## Why This Matters

OpenAI's structured-output history explains the tradeoff:

- Early JSON workflows relied on prompt instructions and post-parse retries.
- Function calling introduced model outputs shaped around declared tool/function parameters.
- JSON mode (`json_object`) improved syntactic reliability by requesting valid JSON.
- Structured Outputs (`json_schema`) tightened the contract by constraining output to match a schema.

The practical difference is important for Browser Use:

- `json_object` answers: "Is this valid JSON?"
- `json_schema` answers: "Does this valid JSON match the expected fields, types, required properties, enums, and nested structure?"

Browser Use action outputs and agent structured outputs depend on predictable Pydantic models. A response can be valid JSON and still be unusable if it omits `action`, changes field names, or uses the wrong nested shape. That is why strict schema mode is the safer default.

The difference is partly model training and partly decoding/runtime enforcement. OpenAI describes Structured Outputs as combining model training for schema understanding with constrained decoding so only schema-valid tokens remain available at each generation step. Many OpenAI-compatible providers implement only the cheaper JSON object behavior because full JSON Schema support requires schema-subset handling, grammar compilation, and token-level constraints.

## When to Apply

- Use `json_schema` for official OpenAI models and providers that support strict structured outputs.
- Use `json_object` when a provider supports JSON mode but rejects `type='json_schema'`.
- Use prompt-only mode only when the provider rejects both structured response formats.
- Always keep local Pydantic validation for non-`json_schema` modes.
- Prefer explicit provider configuration over automatic downgrade, because fallback changes reliability semantics.

## Examples

Current strict path:

```python
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "agent_output",
        "strict": True,
        "schema": optimized_schema,
    },
}
```

Compatibility fallback path:

```python
response_format = {"type": "json_object"}
```

When using the fallback path, also add the schema to the prompt and keep the existing validation step:

```python
parsed = output_format.model_validate_json(choice.message.content)
```

## Related

- OpenAI function calling announcement: https://openai.com/index/function-calling-and-other-api-updates/
- OpenAI Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs
- OpenAI Structured Outputs announcement: https://openai.com/index/introducing-structured-outputs-in-the-api/
- Local implementation: `browser_use/llm/openai/chat.py`
- Thin OpenAI-compatible subclass: `browser_use/llm/openai/like.py`
