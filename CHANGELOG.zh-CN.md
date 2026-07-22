# 更新日志

## 0.13.7 - 2026-07-22

### 新增

- 为 `ChatOpenAI` 增加 `extra_body` 透传能力，用于 OpenAI 兼容服务商的扩展参数。它可以支持火山方舟和 DeepSeek 风格的请求控制，例如 `thinking={"type": "enabled"}` / `thinking={"type": "disabled"}`，以及服务商特有的推理参数，同时不需要在源码里硬编码新模型名。
- 增加回归测试，验证普通文本输出和结构化输出两条 `ChatOpenAI` 请求路径都会把 `extra_body` 字段写入最终 chat completion 请求体。
- 记录 `deepseek-v4-flash-260425` 在火山方舟上的 thinking 模式 live 验证结果，包括 reasoning token、延迟影响和推荐的 Browser Use 配置。

### 说明

- 针对火山方舟上的 DeepSeek V4 Flash，live 验证显示 thinking 默认已开启。如果更重视低延迟和低 token 成本，可以使用 `extra_body={"thinking": {"type": "disabled"}}` 显式关闭。
- 针对该模型的复杂 Browser Use Agent 任务，建议继续使用 prompt-only 结构化输出兼容路径：`add_schema_to_system_prompt=True`、`dont_force_structured_output=True`，并配合现有 schema 清理参数。

## 0.13.6 - 2026-07-22

### 新增

- 将 upstream 0.13.6 基线发布为 `browser-use-volcengine` fork 包。
- 记录本 fork 的发布流程，包括本地 PyPI 发布脚本，以及 `browser-use-volcengine-<version>` 的 annotated tag 规则。
- 记录本 fork 的核心规则：跟进 upstream 升级时必须保留并显式验证火山相关的 fork-specific feature。
