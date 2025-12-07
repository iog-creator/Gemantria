# REALITY_GREEN_SUMMARY

**Generated**: 2025-12-07T19:20:06.049917+00:00
**Source**: `REALITY_GREEN_SUMMARY.json`

---

- **reality_green**: `false`
- **checks**:
  1. Item:
    - **name**: `DB Health`
    - **passed**: `false`
    - **message**:

```
DB health check failed: Traceback (most recent call last):
  File "/home/mccoy/Projects/Gemantria.v2/scripts/guards/guard_ci_empty_db.py", line 1, in <module>
    from scripts.config.env import get_rw_dsn
ModuleNotFoundError: No module named 'scripts'
```

    - **details**:
      - **exit_code**: `1`
  2. Item:
    - **name**: `Control-Plane Health`
    - **passed**: `false`
    - **message**:

```
Control-plane health check failed: Traceback (most recent call last):
  File "/home/mccoy/Projects/Gemantria.v2/scripts/guards/guard_control_plane_health.py", line 1, in <module>
    from scripts.config.env import get_rw_dsn
ModuleNotFoundError: No module named 'scripts'
```

    - **details**:
      - **exit_code**: `1`
  3. Item:
    - **name**: `AGENTS.md Sync`
    - **passed**: `false`
    - **message**:

```
AGENTS.md sync check failed - files may be stale: [check_agents_md_sync] POTENTIAL SYNC ISSUES DETECTED:

  ⚠️  scripts/AGENTS.md: Code updated 2025-12-07 10:46 but AGENTS.md last updated 2025-12-07 08:06

💡 HINT: Update AGENTS.md files to reflect code changes per Rule 006 & Rule 027
   Run: python scripts/create_agents_md.py --dry-run  # Check for missing files
```

    - **details**:
      - **exit_code**: `1`
  4. Item:
    - **name**: `Share Sync & Exports`
    - **passed**: `true`
    - **message**: `All required exports present`
    - **details**:
  5. Item:
    - **name**: `Ledger Verification`
    - **passed**: `false`
    - **message**: `1 stale: AGENTS.md`
    - **details**:
      - **summary**:
        - **ok**: `false`
        - **total**: `9`
        - **current**: `8`
        - **stale**:
          1. `AGENTS.md`
        - **missing**:
        - **results**:
          1. Item:
            - **name**: `AGENTS.md`
            - **source_of_truth**: `root`
            - **status**: `stale`
            - **ledger_hash**: `2903a587830a9eea...`
            - **current_hash**: `c2cad8174aa6a0ce...`
          2. Item:
            - **name**: `MASTER_PLAN.md`
            - **source_of_truth**: `docs/SSOT`
            - **status**: `current`
            - **ledger_hash**: `7267134e5e14bb7d...`
            - **current_hash**: `7267134e5e14bb7d...`
          3. Item:
            - **name**: `DB_HEALTH.md`
            - **source_of_truth**: `docs/runbooks`
            - **status**: `current`
            - **ledger_hash**: `7b351351aaaf7321...`
            - **current_hash**: `7b351351aaaf7321...`
          4. Item:
            - **name**: `PM_SNAPSHOT_CURRENT.md`
            - **source_of_truth**: `docs/runbooks`
            - **status**: `current`
            - **ledger_hash**: `6c51be1d31e4250e...`
            - **current_hash**: `6c51be1d31e4250e...`
          5. Item:
            - **name**: `RULES_INDEX.md`
            - **source_of_truth**: `root`
            - **status**: `current`
            - **ledger_hash**: `df01a6ca8e43a79b...`
            - **current_hash**: `df01a6ca8e43a79b...`
          6. Item:
            - **name**: `system_health.json`
            - **source_of_truth**: `share/atlas/control_plane`
            - **status**: `current`
            - **ledger_hash**: `9c634ea5601204f4...`
            - **current_hash**: `9c634ea5601204f4...`
          7. Item:
            - **name**: `lm_indicator.json`
            - **source_of_truth**: `share/atlas/control_plane`
            - **status**: `current`
            - **ledger_hash**: `0c8d7f9de6b933f5...`
            - **current_hash**: `0c8d7f9de6b933f5...`
          8. Item:
            - **name**: `canonical.json`
            - **source_of_truth**: `share/exports/docs-control`
            - **status**: `current`
            - **ledger_hash**: `c7ca48f2888fb60a...`
            - **current_hash**: `c7ca48f2888fb60a...`
          9. Item:
            - **name**: `summary.json`
            - **source_of_truth**: `share/exports/docs-control`
            - **status**: `current`
            - **ledger_hash**: `fd4f7625bcefe9fb...`
            - **current_hash**: `fd4f7625bcefe9fb...`
      - **stale**:
        1. `AGENTS.md`
      - **missing**:
  6. Item:
    - **name**: `Ketiv-Primary Policy`
    - **passed**: `true`
    - **message**: `Ketiv-primary policy enforced (gematria uses written form per ADR-002)`
    - **details**:
      - **output**:

```
✅ Ketiv-primary guard: PASS (4399/4399 nodes)

```

  7. Item:
    - **name**: `DMS Hint Registry`
    - **passed**: `false`
    - **message**: `Failed to import hint registry: No module named 'typer'`
    - **details**:
      - **error**: `No module named 'typer'`
  8. Item:
    - **name**: `Repo Alignment (Layer 4)`
    - **passed**: `true`
    - **message**: `Plan vs implementation drift detected (HINT mode: warnings only)`
    - **details**:
      - **output**:

```
Layer 4 Alignment Guard: FAIL
  Expected paths: 7
  Actual paths: 4
  Missing: 0
  Integration islands: 2
\nViolations detected:
  - Found 2 files in scripts/code_ingest/ (plan expected scripts/governance/)
  - Update LAYER4_CODE_INGESTION_PLAN.md or migrate code to planned locations
\nEvidence: evidence/repo/guard_layer4_alignment.json
\n⚠️  HINT MODE: Warnings only (exit 0)

```

      - **note**: `Run with --strict to enforce`
  9. Item:
    - **name**: `DMS Alignment`
    - **passed**: `false`
    - **message**:

```
DMS Alignment failed: Traceback (most recent call last):
  File "/home/mccoy/Projects/Gemantria.v2/scripts/ops/preflight_db_check.py", line 28, in <module>
    from scripts.guards.guard_db_health import check_db_health
  File "/home/mccoy/Projects/Gemantria.v2/scripts/guards/guard_db_health.py", line 15, in <module>
    from sqlalchemy import text
ModuleNotFoundError: No module named 'sqlalchemy'
```

    - **details**:
      - **output**: ``
  10. Item:
    - **name**: `DMS Metadata`
    - **passed**: `true`
    - **message**: `DMS metadata sane (low_enabled=0)`
    - **details**:
      - **distribution**:
        - **critical**: `132`
        - **high**: `132`
        - **medium**: `86`
        - **unknown**: `853`
  11. Item:
    - **name**: `AGENTS–DMS Contract`
    - **passed**: `false`
    - **message**: `301 AGENTS metadata violation(s) detected`
    - **details**:
      - **violations**:
        1. `agentpm/adapters/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        2. `agentpm/adapters/AGENTS.md: missing 'ssot' tag`
        3. `agentpm/adapters/AGENTS.md: missing 'agent_framework' tag`
        4. `agentpm/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        5. `agentpm/AGENTS.md: missing 'ssot' tag`
        6. `agentpm/AGENTS.md: missing 'agent_framework' tag`
        7. `agentpm/ai_docs/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        8. `agentpm/ai_docs/AGENTS.md: missing 'ssot' tag`
        9. `agentpm/ai_docs/AGENTS.md: missing 'agent_framework' tag`
        10. `agentpm/atlas/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        11. `agentpm/atlas/AGENTS.md: missing 'ssot' tag`
        12. `agentpm/atlas/AGENTS.md: missing 'agent_framework' tag`
        13. `agentpm/biblescholar/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        14. `agentpm/biblescholar/AGENTS.md: missing 'ssot' tag`
        15. `agentpm/biblescholar/AGENTS.md: missing 'agent_framework' tag`
        16. `agentpm/biblescholar/tests/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        17. `agentpm/biblescholar/tests/AGENTS.md: missing 'ssot' tag`
        18. `agentpm/biblescholar/tests/AGENTS.md: missing 'agent_framework' tag`
        19. `agentpm/bus/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        20. `agentpm/bus/AGENTS.md: missing 'ssot' tag`
        21. `agentpm/bus/AGENTS.md: missing 'agent_framework' tag`
        22. `agentpm/control_plane/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        23. `agentpm/control_plane/AGENTS.md: missing 'ssot' tag`
        24. `agentpm/control_plane/AGENTS.md: missing 'agent_framework' tag`
        25. `agentpm/control_widgets/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        26. `agentpm/control_widgets/AGENTS.md: missing 'ssot' tag`
        27. `agentpm/control_widgets/AGENTS.md: missing 'agent_framework' tag`
        28. `agentpm/db/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        29. `agentpm/db/AGENTS.md: missing 'ssot' tag`
        30. `agentpm/db/AGENTS.md: missing 'agent_framework' tag`
        31. `agentpm/dms/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        32. `agentpm/dms/AGENTS.md: missing 'ssot' tag`
        33. `agentpm/dms/AGENTS.md: missing 'agent_framework' tag`
        34. `agentpm/docs/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        35. `agentpm/docs/AGENTS.md: missing 'ssot' tag`
        36. `agentpm/docs/AGENTS.md: missing 'agent_framework' tag`
        37. `agentpm/exports/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        38. `agentpm/exports/AGENTS.md: missing 'ssot' tag`
        39. `agentpm/exports/AGENTS.md: missing 'agent_framework' tag`
        40. `agentpm/extractors/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        41. `agentpm/extractors/AGENTS.md: missing 'ssot' tag`
        42. `agentpm/extractors/AGENTS.md: missing 'agent_framework' tag`
        43. `agentpm/gatekeeper/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        44. `agentpm/gatekeeper/AGENTS.md: missing 'ssot' tag`
        45. `agentpm/gatekeeper/AGENTS.md: missing 'agent_framework' tag`
        46. `agentpm/governance/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        47. `agentpm/governance/AGENTS.md: missing 'ssot' tag`
        48. `agentpm/governance/AGENTS.md: missing 'agent_framework' tag`
        49. `agentpm/graph/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        50. `agentpm/graph/AGENTS.md: missing 'ssot' tag`
        51. `agentpm/graph/AGENTS.md: missing 'agent_framework' tag`
        52. `agentpm/guard/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        53. `agentpm/guard/AGENTS.md: missing 'ssot' tag`
        54. `agentpm/guard/AGENTS.md: missing 'agent_framework' tag`
        55. `agentpm/guarded/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        56. `agentpm/guarded/AGENTS.md: missing 'ssot' tag`
        57. `agentpm/guarded/AGENTS.md: missing 'agent_framework' tag`
        58. `agentpm/handoff/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        59. `agentpm/handoff/AGENTS.md: missing 'ssot' tag`
        60. `agentpm/handoff/AGENTS.md: missing 'agent_framework' tag`
        61. `agentpm/hints/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        62. `agentpm/hints/AGENTS.md: missing 'ssot' tag`
        63. `agentpm/hints/AGENTS.md: missing 'agent_framework' tag`
        64. `agentpm/kb/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        65. `agentpm/kb/AGENTS.md: missing 'ssot' tag`
        66. `agentpm/kb/AGENTS.md: missing 'agent_framework' tag`
        67. `agentpm/knowledge/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        68. `agentpm/knowledge/AGENTS.md: missing 'ssot' tag`
        69. `agentpm/knowledge/AGENTS.md: missing 'agent_framework' tag`
        70. `agentpm/lm/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        71. `agentpm/lm/AGENTS.md: missing 'ssot' tag`
        72. `agentpm/lm/AGENTS.md: missing 'agent_framework' tag`
        73. `agentpm/lm_widgets/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        74. `agentpm/lm_widgets/AGENTS.md: missing 'ssot' tag`
        75. `agentpm/lm_widgets/AGENTS.md: missing 'agent_framework' tag`
        76. `agentpm/mcp/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        77. `agentpm/mcp/AGENTS.md: missing 'ssot' tag`
        78. `agentpm/mcp/AGENTS.md: missing 'agent_framework' tag`
        79. `agentpm/metrics/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        80. `agentpm/metrics/AGENTS.md: missing 'ssot' tag`
        81. `agentpm/metrics/AGENTS.md: missing 'agent_framework' tag`
        82. `agentpm/modules/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        83. `agentpm/modules/AGENTS.md: missing 'ssot' tag`
        84. `agentpm/modules/AGENTS.md: missing 'agent_framework' tag`
        85. `agentpm/modules/gematria/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        86. `agentpm/modules/gematria/AGENTS.md: missing 'ssot' tag`
        87. `agentpm/modules/gematria/AGENTS.md: missing 'agent_framework' tag`
        88. `agentpm/obs/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        89. `agentpm/obs/AGENTS.md: missing 'ssot' tag`
        90. `agentpm/obs/AGENTS.md: missing 'agent_framework' tag`
        91. `agentpm/plan/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        92. `agentpm/plan/AGENTS.md: missing 'ssot' tag`
        93. `agentpm/plan/AGENTS.md: missing 'agent_framework' tag`
        94. `agentpm/reality/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        95. `agentpm/reality/AGENTS.md: missing 'ssot' tag`
        96. `agentpm/reality/AGENTS.md: missing 'agent_framework' tag`
        97. `agentpm/rpc/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        98. `agentpm/rpc/AGENTS.md: missing 'ssot' tag`
        99. `agentpm/rpc/AGENTS.md: missing 'agent_framework' tag`
        100. `agentpm/runtime/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        101. `agentpm/runtime/AGENTS.md: missing 'ssot' tag`
        102. `agentpm/runtime/AGENTS.md: missing 'agent_framework' tag`
        103. `agentpm/scripts/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        104. `agentpm/scripts/AGENTS.md: missing 'ssot' tag`
        105. `agentpm/scripts/AGENTS.md: missing 'agent_framework' tag`
        106. `agentpm/scripts/state/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        107. `agentpm/scripts/state/AGENTS.md: missing 'ssot' tag`
        108. `agentpm/scripts/state/AGENTS.md: missing 'agent_framework' tag`
        109. `agentpm/server/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        110. `agentpm/server/AGENTS.md: missing 'ssot' tag`
        111. `agentpm/server/AGENTS.md: missing 'agent_framework' tag`
        112. `agentpm/status/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        113. `agentpm/status/AGENTS.md: missing 'ssot' tag`
        114. `agentpm/status/AGENTS.md: missing 'agent_framework' tag`
        115. `agentpm/tests/adapters/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        116. `agentpm/tests/adapters/AGENTS.md: missing 'ssot' tag`
        117. `agentpm/tests/adapters/AGENTS.md: missing 'agent_framework' tag`
        118. `agentpm/tests/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        119. `agentpm/tests/AGENTS.md: missing 'ssot' tag`
        120. `agentpm/tests/AGENTS.md: missing 'agent_framework' tag`
        121. `agentpm/tests/atlas/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        122. `agentpm/tests/atlas/AGENTS.md: missing 'ssot' tag`
        123. `agentpm/tests/atlas/AGENTS.md: missing 'agent_framework' tag`
        124. `agentpm/tests/cli/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        125. `agentpm/tests/cli/AGENTS.md: missing 'ssot' tag`
        126. `agentpm/tests/cli/AGENTS.md: missing 'agent_framework' tag`
        127. `agentpm/tests/db/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        128. `agentpm/tests/db/AGENTS.md: missing 'ssot' tag`
        129. `agentpm/tests/db/AGENTS.md: missing 'agent_framework' tag`
        130. `agentpm/tests/docs/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        131. `agentpm/tests/docs/AGENTS.md: missing 'ssot' tag`
        132. `agentpm/tests/docs/AGENTS.md: missing 'agent_framework' tag`
        133. `agentpm/tests/exports/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        134. `agentpm/tests/exports/AGENTS.md: missing 'ssot' tag`
        135. `agentpm/tests/exports/AGENTS.md: missing 'agent_framework' tag`
        136. `agentpm/tests/extractors/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        137. `agentpm/tests/extractors/AGENTS.md: missing 'ssot' tag`
        138. `agentpm/tests/extractors/AGENTS.md: missing 'agent_framework' tag`
        139. `agentpm/tests/html/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        140. `agentpm/tests/html/AGENTS.md: missing 'ssot' tag`
        141. `agentpm/tests/html/AGENTS.md: missing 'agent_framework' tag`
        142. `agentpm/tests/kb/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        143. `agentpm/tests/kb/AGENTS.md: missing 'ssot' tag`
        144. `agentpm/tests/kb/AGENTS.md: missing 'agent_framework' tag`
        145. `agentpm/tests/knowledge/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        146. `agentpm/tests/knowledge/AGENTS.md: missing 'ssot' tag`
        147. `agentpm/tests/knowledge/AGENTS.md: missing 'agent_framework' tag`
        148. `agentpm/tests/lm/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        149. `agentpm/tests/lm/AGENTS.md: missing 'ssot' tag`
        150. `agentpm/tests/lm/AGENTS.md: missing 'agent_framework' tag`
        151. `agentpm/tests/mcp/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        152. `agentpm/tests/mcp/AGENTS.md: missing 'ssot' tag`
        153. `agentpm/tests/mcp/AGENTS.md: missing 'agent_framework' tag`
        154. `agentpm/tests/phase1/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        155. `agentpm/tests/phase1/AGENTS.md: missing 'ssot' tag`
        156. `agentpm/tests/phase1/AGENTS.md: missing 'agent_framework' tag`
        157. `agentpm/tests/reality/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        158. `agentpm/tests/reality/AGENTS.md: missing 'ssot' tag`
        159. `agentpm/tests/reality/AGENTS.md: missing 'agent_framework' tag`
        160. `agentpm/tests/status/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        161. `agentpm/tests/status/AGENTS.md: missing 'ssot' tag`
        162. `agentpm/tests/status/AGENTS.md: missing 'agent_framework' tag`
        163. `agentpm/tests/system/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        164. `agentpm/tests/system/AGENTS.md: missing 'ssot' tag`
        165. `agentpm/tests/system/AGENTS.md: missing 'agent_framework' tag`
        166. `agentpm/tools/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        167. `agentpm/tools/AGENTS.md: missing 'ssot' tag`
        168. `agentpm/tools/AGENTS.md: missing 'agent_framework' tag`
        169. `AGENTS.md: missing 'agent_framework' tag`
        170. `AGENTS.md: missing 'agent_framework_index' tag for root AGENTS.md`
        171. `archive/docs_legacy/share_scripts_AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        172. `archive/docs_legacy/share_scripts_AGENTS.md: located under archive/ (AGENTS must not be archived)`
        173. `archive/docs_legacy/share_scripts_AGENTS.md: missing 'ssot' tag`
        174. `archive/docs_legacy/share_scripts_AGENTS.md: missing 'agent_framework' tag`
        175. `backup/20251206T011629Z/share/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        176. `backup/20251206T011629Z/share/AGENTS.md: missing 'ssot' tag`
        177. `backup/20251206T011629Z/share/AGENTS.md: missing 'agent_framework' tag`
        178. `backup/20251206T011629Z/share/scripts_AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        179. `backup/20251206T011629Z/share/scripts_AGENTS.md: missing 'ssot' tag`
        180. `backup/20251206T011629Z/share/scripts_AGENTS.md: missing 'agent_framework' tag`
        181. `backup/20251206T044916Z/share/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        182. `backup/20251206T044916Z/share/AGENTS.md: missing 'ssot' tag`
        183. `backup/20251206T044916Z/share/AGENTS.md: missing 'agent_framework' tag`
        184. `backup/20251206T044916Z/share/scripts_AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        185. `backup/20251206T044916Z/share/scripts_AGENTS.md: missing 'ssot' tag`
        186. `backup/20251206T044916Z/share/scripts_AGENTS.md: missing 'agent_framework' tag`
        187. `backup/20251206T050237Z/share/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        188. `backup/20251206T050237Z/share/AGENTS.md: missing 'ssot' tag`
        189. `backup/20251206T050237Z/share/AGENTS.md: missing 'agent_framework' tag`
        190. `backup/20251206T050237Z/share/scripts_AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        191. `backup/20251206T050237Z/share/scripts_AGENTS.md: missing 'ssot' tag`
        192. `backup/20251206T050237Z/share/scripts_AGENTS.md: missing 'agent_framework' tag`
        193. `backup/20251206T051001Z/share/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        194. `backup/20251206T051001Z/share/AGENTS.md: missing 'ssot' tag`
        195. `backup/20251206T051001Z/share/AGENTS.md: missing 'agent_framework' tag`
        196. `backup/20251206T051001Z/share/scripts_AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        197. `backup/20251206T051001Z/share/scripts_AGENTS.md: missing 'ssot' tag`
        198. `backup/20251206T051001Z/share/scripts_AGENTS.md: missing 'agent_framework' tag`
        199. `backup/20251206T051704Z/share/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        200. `backup/20251206T051704Z/share/AGENTS.md: missing 'ssot' tag`
        201. `backup/20251206T051704Z/share/AGENTS.md: missing 'agent_framework' tag`
        202. `backup/20251206T051704Z/share/scripts_AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        203. `backup/20251206T051704Z/share/scripts_AGENTS.md: missing 'ssot' tag`
        204. `backup/20251206T051704Z/share/scripts_AGENTS.md: missing 'agent_framework' tag`
        205. `backup/20251207T032033Z/share/AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        206. `backup/20251207T032033Z/share/AGENTS.md: missing 'ssot' tag`
        207. `backup/20251207T032033Z/share/AGENTS.md: missing 'agent_framework' tag`
        208. `backup/20251207T032033Z/share/scripts_AGENTS.md: importance='unknown' (must be 'critical' or 'high')`
        209. `backup/20251207T032033Z/share/scripts_AGENTS.md: missing 'ssot' tag`
        210. `backup/20251207T032033Z/share/scripts_AGENTS.md: missing 'agent_framework' tag`
        211. `docs/adr/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        212. `docs/adr/AGENTS.md: missing 'ssot' tag`
        213. `docs/adr/AGENTS.md: missing 'agent_framework' tag`
        214. `docs/ADRs/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        215. `docs/ADRs/AGENTS.md: missing 'ssot' tag`
        216. `docs/ADRs/AGENTS.md: missing 'agent_framework' tag`
        217. `docs/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        218. `docs/AGENTS.md: missing 'ssot' tag`
        219. `docs/AGENTS.md: missing 'agent_framework' tag`
        220. `docs/AI_LEARNING_SYSTEM_AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        221. `docs/AI_LEARNING_SYSTEM_AGENTS.md: missing 'ssot' tag`
        222. `docs/AI_LEARNING_SYSTEM_AGENTS.md: missing 'agent_framework' tag`
        223. `docs/analysis/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        224. `docs/analysis/AGENTS.md: missing 'ssot' tag`
        225. `docs/analysis/AGENTS.md: missing 'agent_framework' tag`
        226. `docs/ANALYSIS/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        227. `docs/ANALYSIS/AGENTS.md: missing 'ssot' tag`
        228. `docs/ANALYSIS/AGENTS.md: missing 'agent_framework' tag`
        229. `docs/atlas/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        230. `docs/atlas/AGENTS.md: missing 'ssot' tag`
        231. `docs/atlas/AGENTS.md: missing 'agent_framework' tag`
        232. `docs/audits/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        233. `docs/audits/AGENTS.md: missing 'ssot' tag`
        234. `docs/audits/AGENTS.md: missing 'agent_framework' tag`
        235. `docs/consumers/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        236. `docs/consumers/AGENTS.md: missing 'ssot' tag`
        237. `docs/consumers/AGENTS.md: missing 'agent_framework' tag`
        238. `docs/evidence/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        239. `docs/evidence/AGENTS.md: missing 'ssot' tag`
        240. `docs/evidence/AGENTS.md: missing 'agent_framework' tag`
        241. `docs/forest/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        242. `docs/forest/AGENTS.md: missing 'ssot' tag`
        243. `docs/forest/AGENTS.md: missing 'agent_framework' tag`
        244. `docs/handoff/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        245. `docs/handoff/AGENTS.md: missing 'ssot' tag`
        246. `docs/handoff/AGENTS.md: missing 'agent_framework' tag`
        247. `docs/hints/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        248. `docs/hints/AGENTS.md: missing 'ssot' tag`
        249. `docs/hints/AGENTS.md: missing 'agent_framework' tag`
        250. `docs/ingestion/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        251. `docs/ingestion/AGENTS.md: missing 'ssot' tag`
        252. `docs/ingestion/AGENTS.md: missing 'agent_framework' tag`
        253. `docs/ops/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        254. `docs/ops/AGENTS.md: missing 'ssot' tag`
        255. `docs/ops/AGENTS.md: missing 'agent_framework' tag`
        256. `docs/OPS/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        257. `docs/OPS/AGENTS.md: missing 'ssot' tag`
        258. `docs/OPS/AGENTS.md: missing 'agent_framework' tag`
        259. `docs/phase10/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        260. `docs/phase10/AGENTS.md: missing 'ssot' tag`
        261. `docs/phase10/AGENTS.md: missing 'agent_framework' tag`
        262. `docs/phase9/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        263. `docs/phase9/AGENTS.md: missing 'ssot' tag`
        264. `docs/phase9/AGENTS.md: missing 'agent_framework' tag`
        265. `docs/plan-074/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        266. `docs/plan-074/AGENTS.md: missing 'ssot' tag`
        267. `docs/plan-074/AGENTS.md: missing 'agent_framework' tag`
        268. `docs/plans/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        269. `docs/plans/AGENTS.md: missing 'ssot' tag`
        270. `docs/plans/AGENTS.md: missing 'agent_framework' tag`
        271. `docs/projects/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        272. `docs/projects/AGENTS.md: missing 'ssot' tag`
        273. `docs/projects/AGENTS.md: missing 'agent_framework' tag`
        274. `docs/projects/storymaker/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        275. `docs/projects/storymaker/AGENTS.md: missing 'ssot' tag`
        276. `docs/projects/storymaker/AGENTS.md: missing 'agent_framework' tag`
        277. `docs/rfcs/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        278. `docs/rfcs/AGENTS.md: missing 'ssot' tag`
        279. `docs/rfcs/AGENTS.md: missing 'agent_framework' tag`
        280. `docs/runbooks/AGENTS.md: missing 'ssot' tag`
        281. `docs/runbooks/AGENTS.md: missing 'agent_framework' tag`
        282. `docs/runbooks/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        283. `docs/runbooks/AGENTS.md: missing 'ssot' tag`
        284. `docs/runbooks/AGENTS.md: missing 'agent_framework' tag`
        285. `docs/schema/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        286. `docs/schema/AGENTS.md: missing 'ssot' tag`
        287. `docs/schema/AGENTS.md: missing 'agent_framework' tag`
        288. `docs/schemas/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        289. `docs/schemas/AGENTS.md: missing 'ssot' tag`
        290. `docs/schemas/AGENTS.md: missing 'agent_framework' tag`
        291. `docs/sql/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        292. `docs/sql/AGENTS.md: missing 'ssot' tag`
        293. `docs/sql/AGENTS.md: missing 'agent_framework' tag`
        294. `docs/SSOT/AGENTS.md: missing 'agent_framework' tag`
        295. `docs/SSOT/AGENTS.md: missing 'agent_framework' tag`
        296. `docs/tickets/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        297. `docs/tickets/AGENTS.md: missing 'ssot' tag`
        298. `docs/tickets/AGENTS.md: missing 'agent_framework' tag`
        299. `docs/vendor/AGENTS.md: importance='medium' (must be 'critical' or 'high')`
        300. `docs/vendor/AGENTS.md: missing 'ssot' tag`
        301. `docs/vendor/AGENTS.md: missing 'agent_framework' tag`
      - **rows**: `233`
  12. Item:
    - **name**: `Bootstrap Consistency`
    - **passed**: `true`
    - **message**: `Bootstrap state matches SSOT`
    - **details**:
      - **output**:

```
{
  "ok": true,
  "mode": "STRICT",
  "bootstrap_current_phase": "24",
  "ssot_current_phase": "24",
  "mismatches": []
}
```

  13. Item:
    - **name**: `Root Surface`
    - **passed**: `true`
    - **message**: `No unexpected files in repository root`
    - **details**:
      - **output**: `[root-surface] OK: no unexpected files in repo root`
  14. Item:
    - **name**: `Share Sync Policy`
    - **passed**: `false`
    - **message**: `Check failed: Error: DB not available.`
    - **details**:
      - **output**: ``
  15. Item:
    - **name**: `Backup System`
    - **passed**: `false`
    - **message**: `No recent backup found: `
    - **details**:
      - **output**:

```
❌ No backup found within the last 5 minutes.
   Run: make backup.surfaces
   Before running destructive operations.

🛑 STRICT MODE: Blocking execution.

```

  16. Item:
    - **name**: `WebUI Shell Sanity`
    - **passed**: `true`
    - **message**: `WebUI shell files present`
    - **details**:
  17. Item:
    - **name**: `Handoff Kernel`
    - **passed**: `true`
    - **message**: `Handoff kernel is consistent with bootstrap/SSOT/reality.green`
    - **details**:
      - **output**:

```
{
  "ok": true,
  "mode": "STRICT",
  "mismatches": []
}
```

- **timestamp**: `2025-12-07T19:13:42Z`
