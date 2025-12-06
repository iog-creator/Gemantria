TOOL_BUS_ENABLED = False  # OFF by default
TOOL_RPC_ENABLED = False  # P1 optional
CAP_MAX_TOOLS = 3
POR_TTL_MIN = 30
POLICY_DEFAULT = "STRICT"
BUDGETS_STRICT = {
    "max_calls_per_tool": 3,
    "max_total_calls": 6,
    "max_tokens_in": 3500,
    "max_tokens_out": 2500,
    "max_runtime_sec": 60,
}
