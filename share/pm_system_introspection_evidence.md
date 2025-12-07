# PM System Introspection — Raw Evidence Bundle

This file aggregates raw evidence about how the pmagent + AGENTS + share +
planning + KB + tracking/self-healing systems currently behave. It is NOT a
designed doc; it is an evidence pack for the PM to read and interpret.

**Generated**: 2025-12-07T19:19:56.416020+00:00

## 1. Repo / branch / status

```
## feat/phase27l-agents-dms-contract
 M AGENTS.md
 M docs/SSOT/DOC_STRATEGY.md
 M docs/SSOT/PM_CONTRACT_STRICT_SSOT_DMS.md
 M docs/SSOT/SHARE_FOLDER_ANALYSIS.md
 M pmagent/AGENTS.md
 M scripts/governance/ingest_docs_to_db.py
 M scripts/guards/guard_reality_green.py
 M share/HANDOFF_KERNEL.json
 M share/REALITY_GREEN_SUMMARY.json
 M share/agents_md.head.json
 M share/doc_registry.json
 M share/doc_sync_state.json
 M share/doc_version.json
 M share/governance_freshness.json
 M share/hint_registry.json
 M share/kb_registry.json
 M share/live_posture.json
 M share/next_steps.head.json
 M share/planning_lane_status.json
 M share/pm_contract.head.json
 M share/pm_snapshot.json
 M share/schema_snapshot.json
?? docs/analysis/DOC_STRATEGY.md
?? scripts/governance/dms_doc_cleanup.py

```

## 2. pmagent commands (help text)

### pmagent

```
                                                                                
 Usage: pmagent [OPTIONS] COMMAND [ARGS]...                                     
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ health          Health check commands                                        │
│ graph           Graph operations                                             │
│ control         Control-plane operations                                     │
│ ask             Ask questions using SSOT documentation                       │
│ reality-check   Reality checks for automated bring-up                        │
│ reality         Reality validation commands                                  │
│ bringup         System bring-up commands                                     │
│ mcp             MCP server commands                                          │
│ lm              LM (Language Model) operations                               │
│ status          System status helpers                                        │
│ docs            Documentation search operations                              │
│ models          Model introspection commands                                 │
│ state           System state ledger operations                               │
│ kb              Knowledge-base document registry operations                  │
│ plan            Planning workflows powered by KB registry                    │
│ report          Reporting commands                                           │
│ tools           External planning/tool helpers (Gemini, Codex)               │
│ autopilot       Autopilot backend operations                                 │
│ repo            Repository introspection and git workflow commands.          │
│ handoff         Handoff service commands                                     │
│ hints           Hint generation and management                               │
│ dms             DMS governance operations                                    │
│ bible           Bible operations                                             │
│ rerank          Rerank operations                                            │
│ extract         Extract operations                                           │
│ embed           Embed operations                                             │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent plan

```
                                                                                
 Usage: pmagent plan [OPTIONS] COMMAND [ARGS]...                                
                                                                                
 Planning workflows powered by KB registry                                      
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ next           Suggest next work items from MASTER_PLAN + NEXT_STEPS         │
│ open           Open a NEXT_STEPS item as a capability_session envelope       │
│ reality-loop   Run a single plan+posture loop and persist a                  │
│                capability_session envelope                                   │
│ history        List recent capability_session envelopes (read-only)          │
│ kb             KB-powered planning commands                                  │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent kb

```
                                                                                
 Usage: pmagent kb [OPTIONS] COMMAND [ARGS]...                                  
                                                                                
 Knowledge-base document registry operations                                    
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ registry   KB document registry commands                                     │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent status

```
                                                                                
 Usage: pmagent status [OPTIONS] COMMAND [ARGS]...                              
                                                                                
 System status helpers                                                          
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ explain   Explain current DB + LM health in plain language                   │
│ kb        KB registry status view for PM/AgentPM planning                    │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent status snapshot

```

```

### pmagent status kb

```
                                                                                
 Usage: pmagent status kb [OPTIONS]                                             
                                                                                
 KB registry status view for PM/AgentPM planning                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --json-only                  Print only JSON                                 │
│ --registry-path        TEXT  Path to registry JSON file                      │
│ --help                       Show this message and exit.                     │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent status explain

```
                                                                                
 Usage: pmagent status explain [OPTIONS]                                        
                                                                                
 Explain current DB + LM health in plain language                               
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --json-only          Return JSON instead of text                             │
│ --no-lm              Skip LM enhancement, use rule-based only                │
│ --help               Show this message and exit.                             │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent hints

```
                                                                                
 Usage: pmagent hints [OPTIONS] COMMAND [ARGS]...                               
                                                                                
 Hint generation and management                                                 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ generate   Generate a hint from an error message and context.                │
│ batch      Batch-generate hints from a session error log.                    │
│ list       List hints from the registry.                                     │
│ export     Export all hints to markdown documentation.                       │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent health

```
                                                                                
 Usage: pmagent health [OPTIONS] COMMAND [ARGS]...                              
                                                                                
 Health check commands                                                          
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ system   Aggregate system health (DB + LM + Graph)                           │
│ db       Check database health                                               │
│ lm       Check LM Studio health                                              │
│ graph    Check graph overview                                                │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent health system

```
                                                                                
 Usage: pmagent health system [OPTIONS]                                         
                                                                                
 Aggregate system health (DB + LM + Graph)                                      
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --json-only          Print only JSON                                         │
│ --help               Show this message and exit.                             │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent reality-check

```
                                                                                
 Usage: pmagent reality-check [OPTIONS] COMMAND [ARGS]...                       
                                                                                
 Reality checks for automated bring-up                                          
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ 1       Run Reality Check #1 automated bring-up                              │
│ live    Run Reality Check #1 LIVE (DB + LM + pipeline)                       │
│ check   Run comprehensive reality check (env + DB + LM + exports + eval)     │
╰──────────────────────────────────────────────────────────────────────────────╯


```

### pmagent reality-check check

```
                                                                                
 Usage: pmagent reality-check check [OPTIONS]                                   
                                                                                
 Run comprehensive reality check (env + DB + LM + exports + eval)               
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --mode                 TEXT  Mode: hint (default) or strict [default: hint]  │
│ --json-only                  Print only JSON                                 │
│ --no-dashboards              Skip exports/eval checks                        │
│ --help                       Show this message and exit.                     │
╰──────────────────────────────────────────────────────────────────────────────╯


```

## 3. Current planning state

### plan_next_with_status

```
{
  "available": true,
  "master_plan_path": "/home/mccoy/Projects/Gemantria.v2/docs/SSOT/MASTER_PLAN.md",
  "next_steps_path": "/home/mccoy/Projects/Gemantria.v2/NEXT_STEPS.md",
  "current_focus": "Phase 8 temporal analytics completion and Phase 11 unified envelope stabilization.",
  "next_milestone": "Phase 12 advanced pattern mining capabilities.",
  "candidates": [
    {
      "id": "NEXT_STEPS:1",
      "title": "\u2705 All 5 tab components present and functional (SearchTab, SemanticSearchTab, LexiconTab, InsightsTab, CrossLanguageTab)",
      "source": "NEXT_STEPS",
      "priority": 1,
      "raw_line": "- \u2705 All 5 tab components present and functional (SearchTab, SemanticSearchTab, LexiconTab, InsightsTab, CrossLanguageTab)"
    },
    {
      "id": "NEXT_STEPS:2",
      "title": "\u2705 All 6 export scripts operational (`export_biblescholar_{summary,search,semantic_search,lexicon,insights,cross_language}.py`)",
      "source": "NEXT_STEPS",
      "priority": 2,
      "raw_line": "- \u2705 All 6 export scripts operational (`export_biblescholar_{summary,search,semantic_search,lexicon,insights,cross_language}.py`)"
    },
    {
      "id": "NEXT_STEPS:3",
      "title": "\u2705 All static JSON exports present in `share/exports/biblescholar/`",
      "source": "NEXT_STEPS",
      "priority": 3,
      "raw_line": "- \u2705 All static JSON exports present in `share/exports/biblescholar/`"
    }
  ],
  "posture": {
    "mode": "live",
    "reality": {
      "command": "reality.check",
      "mode": "HINT",
      "timestamp": "2025-12-07T19:20:00.560434+00:00",
      "env": {
        "ok": true,
        "dsn_ok": true,
        "details": {
          "dsns": {
            "rw": true,
            "ro": true,
            "bible": true
          }
        }
      },
      "db": {
        "ok": true,
        "control_schema": "control",
        "tables_expected": 0,
        "tables_present": 0,
        "generated_at": "2025-12-07T19:20:00.560454+00:00",
        "components": {
          "status": {
            "ok": true,
            "mode": "ready",
            "reason": null,
            "tables": {
              "public.ai_interactions": {
                "present": true,
                "row_count": 1,
                "latest_created_at": "2025-11-07T11:11:49.732991-08:00"
              },
              "public.governance_artifacts": {
                "present": true,
                "row_count": 134,
                "latest_created_at": "2025-12-07T09:56:28.527430-08:00"
              },
              "control.agent_run": {
                "present": true,
                "row_count": 2270,
                "latest_created_at": "2025-11-30T09:02:28.655100-08:00"
              },
              "control.agent_run_cli": {
                "present": true,
                "row_count": 141,
                "latest_created_at": "2025-12-07T11:20:00.547860-08:00"
              },
              "control.kb_document": {
                "present": true,
                "row_count": 4238,
                "latest_created_at": "2025-11-27T10:39:03.026669-08:00"
              },
              "control.doc_registry": {
                "present": true,
                "row_count": 1203,
                "latest_created_at": "2025-12-07T10:46:19.978008-08:00"
              },
              "control.doc_version": {
                "present": true,
                "row_count": 8808,
                "latest_created_at": null
              },
              "control.tool_catalog": {
                "present": true,
                "row_count": 7,
                "latest_created_at": "2025-11-26T09:05:34.616631-08:00"
              },
              "gematria.graph_stats_snapshots": {
                "present": true,
                "row_count": 0,
                "latest_created_at": null
              }
            }
          },
          "tables": {
            "ok": true,
            "mode": "db_on",
            "error": null,
            "tables": {
              "control.agent_run": 2270,
              "control.agent_run_cli": 141,
              "control.capability_rule": 5,
              "control.capability_session": 5,
              "control.doc_embedding": 245898,
              "control.doc_fragment": 245903,
              "control.doc_registry": 1203,
              "control.doc_sync_state": 0,
              "control.doc_version": 8808,
              "control.guard_definition": 0,
              "control.hint_registry": 25,
              "control.kb_document": 4238,
              "control.rule_definition": 69,
              "control.rule_source": 138,
              "control.system_state_ledger": 462,
              "control.tool_catalog": 7,
              "gematria.ai_embeddings": 1,
              "gematria.checkpoints": 4,
              "gematria.concept_centrality": 0,
              "gematria.concept_relations": 0,
              "gematria.concepts": 0,
              "gematria.edges": 1,
              "gematria.enrichment_crossrefs": 0,
              "gematria.graph_stats_snapshots": 0,
              "gematria.nodes": 2,
              "gematria.nouns": 0,
              "gematria.runs": 2,
              "gematria.runs_ledger": 115,
              "gematria.schema_migrations": 2,
              "gematria.word_cache": 0,
              "mcp.endpoints": 10,
              "mcp.logs": 0,
              "mcp.tools": 6,
              "ops.job_queue": 0,
              "public.ai_enrichment_log": 13857,
              "public.ai_interactions": 1,
              "public.ai_performance_insights": 0,
              "public.books": 35,
              "public.checkpointer_state": 64,
              "public.checkpointer_writes": 2,
              "public.checkpoints": 22,
              "public.cluster_metrics": 0,
              "public.code_generation_events": 0,
              "public.code_generation_patterns": 0,
              "public.concept_centrality": 0,
              "public.concept_clusters": 1,
              "public.concept_metadata": 4399,
              "public.concept_metrics": 0,
              "public.concept_network": 4399,
              "public.concept_relations": 14330,
              "public.concept_rerank_cache": 0,
              "public.concepts": 4399,
              "public.confidence_validation_log": 35,
              "public.connections": 0,
              "public.context_awareness_events": 0,
              "public.context_success_patterns": 0,
              "public.cross_references": 0,
              "public.doctrinal_links": 0,
              "public.document_access_log": 1,
              "public.document_sections": 398,
              "public.governance_artifacts": 134,
              "public.governance_compliance_log": 243,
              "public.hint_emissions": 818,
              "public.hypotheses": 0,
              "public.integration_log": 0,
              "public.isolation_patterns": 0,
              "public.learning_events": 2,
              "public.metrics_log": 7969,
              "public.model_performance_metrics": 0,
              "public.network_metrics": 0,
              "public.pattern_occurrences": 9,
              "public.patterns": 9,
              "public.prime_factors": 0,
              "public.qwen_health_log": 15,
              "public.runs": 25,
              "public.satisfaction_metrics": 0,
              "public.share_manifest_items": 40,
              "public.share_manifest_metadata": 1,
              "public.tool_usage_analytics": 0,
              "public.twin_patterns": 0,
              "public.user_feedback": 0,
              "public.verse_noun_occurrences": 116960,
              "staging.concept_metadata_norm": 0,
              "staging.concept_relations_norm": 1855,
              "staging.concepts_norm": 710,
              "telemetry.ai_interactions": 0,
              "telemetry.checkpointer_state": 0,
              "telemetry.metrics_log": 0
            }
          },
          "schema": {
            "ok": true,
            "mode": "db_on",
            "reason": null,
            "tables": {
              "control.agent_run": {
                "columns": [
                  {
                    "name": "id",
                    "data_type": "uuid",
                    "is_nullable": false,
                    "default": "gen_random_uuid()"
                  },
                  {
                    "name": "project_id",
                    "data_type": "bigint",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "session_id",
                    "data_type": "uuid",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "tool",
                    "data_type": "text",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "args_json",
                    "data_type": "jsonb",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "result_json",
                    "data_type": "jsonb",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "violations_json",
                    "data_type": "jsonb",
                    "is_nullable": false,
                    "default": "'[]'::jsonb"
                  },
                  {
                    "name": "created_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": false,
                    "default": "now()"
                  }
                ],
                "primary_key": [
                  "id"
                ],
                "indexes": [
                  {
                    "name": "idx_agent_run_created",
                    "columns": [
                      "created_at"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_agent_run_project",
                    "columns": [
                      "project_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_agent_run_session",
                    "columns": [
                      "session_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_agent_run_tool",
                    "columns": [
                      "tool"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_agent_run_violations",
                    "columns": [
                      "violations_json"
                    ],
                    "unique": false
                  }
                ]
              },
              "control.tool_catalog": {
                "columns": [
                  {
                    "name": "id",
                    "data_type": "uuid",
                    "is_nullable": false,
                    "default": "gen_random_uuid()"
                  },
                  {
                    "name": "project_id",
                    "data_type": "bigint",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "name",
                    "data_type": "text",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "ring",
                    "data_type": "integer",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "io_schema",
                    "data_type": "jsonb",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "enabled",
                    "data_type": "boolean",
                    "is_nullable": false,
                    "default": "true"
                  },
                  {
                    "name": "created_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": false,
                    "default": "now()"
                  }
                ],
                "primary_key": [
                  "id"
                ],
                "indexes": [
                  {
                    "name": "idx_tool_catalog_enabled",
                    "columns": [
                      "enabled"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_tool_catalog_project",
                    "columns": [
                      "project_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_tool_catalog_ring",
                    "columns": [
                      "ring"
                    ],
                    "unique": false
                  },
                  {
                    "name": "tool_catalog_project_id_name_key",
                    "columns": [
                      "project_id",
                      "name"
                    ],
                    "unique": true
                  }
                ]
              },
              "control.capability_rule": {
                "columns": [
                  {
                    "name": "id",
                    "data_type": "uuid",
                    "is_nullable": false,
                    "default": "gen_random_uuid()"
                  },
                  {
                    "name": "project_id",
                    "data_type": "bigint",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "name",
                    "data_type": "text",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "ring",
                    "data_type": "integer",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "allowlist",
                    "data_type": "ARRAY",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "denylist",
                    "data_type": "ARRAY",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "budgets",
                    "data_type": "jsonb",
                    "is_nullable": false,
                    "default": "'{}'::jsonb"
                  },
                  {
                    "name": "created_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": false,
                    "default": "now()"
                  }
                ],
                "primary_key": [
                  "id"
                ],
                "indexes": [
                  {
                    "name": "capability_rule_project_id_name_key",
                    "columns": [
                      "project_id",
                      "name"
                    ],
                    "unique": true
                  },
                  {
                    "name": "idx_capability_rule_project",
                    "columns": [
                      "project_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_capability_rule_ring",
                    "columns": [
                      "ring"
                    ],
                    "unique": false
                  }
                ]
              },
              "control.doc_fragment": {
                "columns": [
                  {
                    "name": "id",
                    "data_type": "uuid",
                    "is_nullable": false,
                    "default": "gen_random_uuid()"
                  },
                  {
                    "name": "project_id",
                    "data_type": "bigint",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "src",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "anchor",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "sha256",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "created_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": false,
                    "default": "now()"
                  },
                  {
                    "name": "doc_id",
                    "data_type": "uuid",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "version_id",
                    "data_type": "bigint",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "fragment_index",
                    "data_type": "integer",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "fragment_type",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "content",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "updated_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": true,
                    "default": "now()"
                  },
                  {
                    "name": "meta",
                    "data_type": "jsonb",
                    "is_nullable": true,
                    "default": "'{}'::jsonb"
                  },
                  {
                    "name": "content_tsvector",
                    "data_type": "tsvector",
                    "is_nullable": true,
                    "default": null
                  }
                ],
                "primary_key": [
                  "id"
                ],
                "indexes": [
                  {
                    "name": "doc_fragment_project_id_src_anchor_key",
                    "columns": [
                      "project_id",
                      "src",
                      "anchor"
                    ],
                    "unique": true
                  },
                  {
                    "name": "idx_doc_fragment_content_tsvector",
                    "columns": [
                      "content_tsvector"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_doc_fragment_content_unique",
                    "columns": [
                      "doc_id",
                      "version_id",
                      "fragment_index"
                    ],
                    "unique": true
                  },
                  {
                    "name": "idx_doc_fragment_doc_id",
                    "columns": [
                      "doc_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_doc_fragment_meta",
                    "columns": [
                      "meta"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_doc_fragment_project",
                    "columns": [
                      "project_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_doc_fragment_sha256",
                    "columns": [
                      "sha256"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_doc_fragment_src",
                    "columns": [
                      "src"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_doc_fragment_type",
                    "columns": [
                      "fragment_type"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_doc_fragment_version_id",
                    "columns": [
                      "version_id"
                    ],
                    "unique": false
                  }
                ]
              },
              "control.capability_session": {
                "columns": [
                  {
                    "name": "id",
                    "data_type": "uuid",
                    "is_nullable": false,
                    "default": "gen_random_uuid()"
                  },
                  {
                    "name": "project_id",
                    "data_type": "bigint",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "rule_id",
                    "data_type": "uuid",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "por_json",
                    "data_type": "jsonb",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "tiny_menu",
                    "data_type": "ARRAY",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "ttl_s",
                    "data_type": "integer",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "created_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": false,
                    "default": "now()"
                  }
                ],
                "primary_key": [
                  "id"
                ],
                "indexes": [
                  {
                    "name": "idx_capability_session_created",
                    "columns": [
                      "created_at"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_capability_session_project",
                    "columns": [
                      "project_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_capability_session_rule",
                    "columns": [
                      "rule_id"
                    ],
                    "unique": false
                  }
                ]
              },
              "public.ai_interactions": {
                "columns": [
                  {
                    "name": "id",
                    "data_type": "integer",
                    "is_nullable": false,
                    "default": "nextval('ai_interactions_id_seq'::regclass)"
                  },
                  {
                    "name": "session_id",
                    "data_type": "character varying",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "interaction_type",
                    "data_type": "character varying",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "user_query",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "ai_response",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "tools_used",
                    "data_type": "ARRAY",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "context_provided",
                    "data_type": "jsonb",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "execution_time_ms",
                    "data_type": "integer",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "success",
                    "data_type": "boolean",
                    "is_nullable": true,
                    "default": "true"
                  },
                  {
                    "name": "error_details",
                    "data_type": "text",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "created_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": true,
                    "default": "now()"
                  }
                ],
                "primary_key": [
                  "id"
                ],
                "indexes": [
                  {
                    "name": "idx_ai_interactions_created",
                    "columns": [
                      "created_at"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_ai_interactions_session",
                    "columns": [
                      "session_id"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_ai_interactions_type",
                    "columns": [
                      "interaction_type"
                    ],
                    "unique": false
                  }
                ]
              },
              "public.governance_artifacts": {
                "columns": [
                  {
                    "name": "id",
                    "data_type": "integer",
                    "is_nullable": false,
                    "default": "nextval('governance_artifacts_id_seq'::regclass)"
                  },
                  {
                    "name": "artifact_type",
                    "data_type": "character varying",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "artifact_name",
                    "data_type": "character varying",
                    "is_nullable": false,
                    "default": null
                  },
                  {
                    "name": "file_path",
                    "data_type": "character varying",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "rule_references",
                    "data_type": "ARRAY",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "agent_references",
                    "data_type": "ARRAY",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "last_updated",
                    "data_type": "timestamp with time zone",
                    "is_nullable": true,
                    "default": "now()"
                  },
                  {
                    "name": "checksum",
                    "data_type": "character varying",
                    "is_nullable": true,
                    "default": null
                  },
                  {
                    "name": "validation_status",
                    "data_type": "character varying",
                    "is_nullable": true,
                    "default": "'pending'::character varying"
                  },
                  {
                    "name": "created_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": true,
                    "default": "now()"
                  },
                  {
                    "name": "updated_at",
                    "data_type": "timestamp with time zone",
                    "is_nullable": true,
                    "default": "now()"
                  }
                ],
                "primary_key": [
                  "id"
                ],
                "indexes": [
                  {
                    "name": "governance_artifacts_artifact_type_artifact_name_key",
                    "columns": [
                      "artifact_type",
                      "artifact_name"
                    ],
                    "unique": true
                  },
                  {
                    "name": "idx_governance_agent_refs",
                    "columns": [
                      "agent_references"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_governance_rule_refs",
                    "columns": [
                      "rule_references"
                    ],
                    "unique": false
                  },
                  {
                    "name": "idx_governance_type",
                    "columns": [
                      "artifact_type"
                    ],
                    "unique": false
                  }
                ]
              }
            }
          },
          "pipeline_status": {
            "ok": true,
            "mode": "db_on",
            "reason": null,
            "window_hours": 24,
            "summary": {
              "total_runs": 0,
              "pipelines": {}
            }
          }
        }
      },
      "lm": {
        "ok": true,
        "provider": "unknown",
        "slots": [
          {
            "slot": "local_agent",
            "provider": "lmstudio",
            "model": "ibm/granite-4-h-tiny",
            "service_status": "OK"
          },
          {
            "slot": "embedding",
            "provider": "lmstudio",
            "model": "text-embedding-bge-m3",
            "service_status": "OK"
          },
          {
            "slot": "reranker",
            "provider": "lmstudio",
            "model": "ibm/granite-4-h-tiny (embedding_only)",
            "service_status": "OK"
          },
          {
            "slot": "theology",
            "provider": "lmstudio",
            "model": "christian-bible-expert-v2.0-12b",
            "service_status": "OK"
          }
        ],
        "mode": "lm_ready",
        "details": {
          "endpoint": "http://127.0.0.1:9994/v1",
          "provider": "lmstudio",
          "errors": []
        }
      },
      "exports": {
        "ok": true,
        "lm_indicator": {
          "status": "unknown",
          "lm_available": true,
          "note": "Recreated after share/ disaster; regenerate from LM health scripts when available."
        },
        "compliance_head": null,
        "kb_docs_head": null,
        "mcp_catalog": null
      },
      "eval_smoke": {
        "ok": true,
        "targets": [
          "ci.exports.smoke",
          "eval.graph.calibrate.adv"
        ],
        "messages": [
          "ci.exports.smoke: OK",
          "eval.graph.calibrate.adv: OK"
        ]
      },
      "hints": [
        "DMS-REQUIRED: reality.green STRICT must pass all required checks before declaring system ready.",
        "KB: KB registry references 316 missing file(s)",
        "KB: KB registry validation issue: Registry validation failed: 318 errors",
        "KB: KB registry validation issue: Registry has 3 warnings",
        "KB: 9 document(s) are stale (exceed refresh interval)",
        "KB: Doc freshness: 9 stale, 0 out-of-sync"
      ],
      "kb_hints": [
        {
          "level": "WARN",
          "code": "KB_MISSING_DOCS",
          "message": "KB registry references 316 missing file(s)",
          "missing_count": 316,
          "missing_files": [
            "agentpm/adapters/AGENTS.md (ID",
            "agentpm/AGENTS.md (ID",
            "agentpm/ai_docs/AGENTS.md (ID",
            "agentpm/atlas/AGENTS.md (ID",
            "agentpm/biblescholar/AGENTS.md (ID",
            "agentpm/biblescholar/tests/AGENTS.md (ID",
            "agentpm/bus/AGENTS.md (ID",
            "agentpm/control_plane/AGENTS.md (ID",
            "agentpm/control_widgets/AGENTS.md (ID",
            "agentpm/db/AGENTS.md (ID"
          ]
        },
        {
          "level": "WARN",
          "code": "KB_VALIDATION_ISSUES",
          "message": "KB registry validation issue: Registry validation failed: 318 errors"
        },
        {
          "level": "WARN",
          "code": "KB_VALIDATION_ISSUES",
          "message": "KB registry validation issue: Registry has 3 warnings"
        },
        {
          "level": "WARN",
          "code": "KB_DOC_STALE",
          "message": "9 document(s) are stale (exceed refresh interval)",
          "stale_count": 9,
          "stale_docs": [
            {
              "id": "ssot::docs/ssot/data-flow-visual.md",
              "path": "docs/SSOT/data_flow_visual.md",
              "title": "SSOT::docs/SSOT/data_flow_visual.md"
            },
            {
              "id": "ssot::docs/ssot/epoch-ledger.md",
              "path": "docs/SSOT/EPOCH_LEDGER.md",
              "title": "SSOT::docs/SSOT/EPOCH_LEDGER.md"
            },
            {
              "id": "ssot::docs/ssot/graph-metrics-api.md",
              "path": "docs/SSOT/graph-metrics-api.md",
              "title": "SSOT::docs/SSOT/graph-metrics-api.md"
            },
            {
              "id": "ssot::docs/ssot/graph-stats-api.md",
              "path": "docs/SSOT/graph-stats-api.md",
              "title": "SSOT::docs/SSOT/graph-stats-api.md"
            },
            {
              "id": "ssot::docs/ssot/jsonld-schema.md",
              "path": "docs/SSOT/jsonld-schema.md",
              "title": "SSOT::docs/SSOT/jsonld-schema.md"
            }
          ]
        }
      ],
      "overall_ok": true,
      "required_hints": [
        {
          "logical_name": "reality.green.required_checks",
          "injection_mode": "PRE_PROMPT",
          "payload": {
            "text": "reality.green STRICT must pass all required checks before declaring system ready.",
            "commands": [
              "make reality.green STRICT"
            ],
            "metadata": {
              "source": "Rule-050",
              "section": "5"
            },
            "constraints": {
              "rule_ref": "050",
              "required_before": "PR"
            }
          },
          "priority": 10
        }
      ],
      "suggested_hints": []
    },
    "status": {
      "level": "OK",
      "headline": "All systems nominal",
      "details": "Everything looks good with the system right now! The database is fully ready and working properly. All four language model slots (local_agent, embedding, reranker, theology) are active and functioning as expected. So overall, everything is running smoothly without any issues detected.",
      "documentation": {
        "available": true,
        "total": 1185,
        "by_subsystem": {
          "ops": 555,
          "gematria": 38,
          "pm": 227,
          "general": 227,
          "docs": 5,
          "root": 48,
          "webui": 51,
          "biblescholar": 34
        },
        "by_type": {
          "other": 1023,
          "ssot": 129,
          "runbook": 33
        },
        "hints": [
          {
            "level": "WARN",
            "code": "KB_MISSING_DOCS",
            "message": "KB registry references 316 missing file(s)",
            "missing_count": 316,
            "missing_files": [
              "agentpm/adapters/AGENTS.md (ID",
              "agentpm/AGENTS.md (ID",
              "agentpm/ai_docs/AGENTS.md (ID",
              "agentpm/atlas/AGENTS.md (ID",
              "agentpm/biblescholar/AGENTS.md (ID",
              "agentpm/biblescholar/tests/AGENTS.md (ID",
              "agentpm/bus/AGENTS.md (ID",
              "agentpm/control_plane/AGENTS.md (ID",
              "agentpm/control_widgets/AGENTS.md (ID",
              "agentpm/db/AGENTS.md (ID"
            ]
          },
          {
            "level": "WARN",
            "code": "KB_VALIDATION_ISSUES",
            "message": "KB registry validation issue: Registry validation failed: 318 errors"
          },
          {
            "level": "WARN",
            "code": "KB_VALIDATION_ISSUES",
            "message": "KB registry validation issue: Registry has 3 warnings"
          },
          {
            "level": "WARN",
            "code": "KB_DOC_STALE",
            "message": "9 document(s) are stale (exceed refresh interval)",
            "stale_count": 9,
            "stale_docs": [
              {
                "id": "ssot::docs/ssot/data-flow-visual.md",
                "path": "docs/SSOT/data_flow_visual.md",
                "title": "SSOT::docs/SSOT/data_flow_visual.md"
              },
              {
                "id": "ssot::docs/ssot/epoch-ledger.md",
                "path": "docs/SSOT/EPOCH_LEDGER.md",
                "title": "SSOT::docs/SSOT/EPOCH_LEDGER.md"
              },
              {
                "id": "ssot::docs/ssot/graph-metrics-api.md",
                "path": "docs/SSOT/graph-metrics-api.md",
                "title": "SSOT::docs/SSOT/graph-metrics-api.md"
              },
              {
                "id": "ssot::docs/ssot/graph-stats-api.md",
                "path": "docs/SSOT/graph-stats-api.md",
                "title": "SSOT::docs/SSOT/graph-stats-api.md"
              },
              {
                "id": "ssot::docs/ssot/jsonld-schema.md",
                "path": "docs/SSOT/jsonld-schema.md",
                "title": "SSOT::docs/SSOT/jsonld-schema.md"
              }
            ]
          }
        ],
        "key_docs": [
          {
            "id": "master-plan",
            "title": "MASTER_PLAN",
            "path": "MASTER_PLAN.md",
            "type": "ssot"
          },
          {
            "id": "rules-index",
            "title": "RULES_INDEX",
            "path": "RULES_INDEX.md",
            "type": "ssot"
          },
          {
            "id": "ssot::docs/ssot/agentpm-gematria-module-plan.md",
            "title": "SSOT::docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md",
            "path": "docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md",
            "type": "ssot"
          }
        ],
        "freshness": {
          "total": 1185,
          "stale_count": 9,
          "missing_count": 316,
          "out_of_sync_count": 0,
          "fresh_count": 860
        }
      }
    }
  }
}

```

### plan_history

```
{
  "count": 7,
  "sessions": [
    {
      "id": "NEXT_STEPS:1",
      "title": "[ ] **Schema Migration**: Create SQL migration for `patterns` and `pattern_occurrences` tables.",
      "source": "NEXT_STEPS",
      "envelope_path": "/home/mccoy/Projects/Gemantria.v2/evidence/pmagent/capability_session-2025-11-26T03-20-37+00-00.json",
      "timestamp": "2025-11-26T03:20:37.331126+00:00",
      "dry_run_command": null,
      "posture_mode": "live",
      "reality_overall_ok": true,
      "status_level": "OK"
    },
    {
      "id": "NEXT_STEPS:1",
      "title": "[ ] **Schema Migration**: Create SQL migration for `patterns` and `pattern_occurrences` tables.",
      "source": "NEXT_STEPS",
      "envelope_path": "/home/mccoy/Projects/Gemantria.v2/evidence/pmagent/capability_session-2025-11-26T03-19-25+00-00.json",
      "timestamp": "2025-11-26T03:19:25.973637+00:00",
      "dry_run_command": null,
      "posture_mode": "live",
      "reality_overall_ok": true,
      "status_level": "OK"
    },
    {
      "id": "NEXT_STEPS:1",
      "title": "[ ] **Schema Migration**: Create SQL migration for `patterns` and `pattern_occurrences` tables.",
      "source": "NEXT_STEPS",
      "envelope_path": "/home/mccoy/Projects/Gemantria.v2/evidence/pmagent/capability_session-2025-11-26T03-16-49+00-00.json",
      "timestamp": "2025-11-26T03:16:49.372682+00:00",
      "dry_run_command": null,
      "posture_mode": "live",
      "reality_overall_ok": true,
      "status_level": "OK"
    },
    {
      "id": "NEXT_STEPS:1",
      "title": "[ ] **Draft Phase 12 Plan**: Create `docs/plans/PHASE_12_PATTERN_MINING.md` detailing the objectives, deliverables, and architecture.",
      "source": "NEXT_STEPS",
      "envelope_path": "/home/mccoy/Projects/Gemantria.v2/evidence/pmagent/capability_session-2025-11-26T03-06-25+00-00.json",
      "timestamp": "2025-11-26T03:06:25.704162+00:00",
      "dry_run_command": null,
      "posture_mode": "live",
      "reality_overall_ok": true,
      "status_level": "OK"
    },
    {
      "id": "NEXT_STEPS:1",
      "title": "[ ] **Draft Phase 12 Plan**: Create `docs/plans/PHASE_12_PATTERN_MINING.md` detailing the objectives, deliverables, and architecture.",
      "source": "NEXT_STEPS",
      "envelope_path": "/home/mccoy/Projects/Gemantria.v2/evidence/pmagent/capability_session-2025-11-26T03-06-10+00-00.json",
      "timestamp": "2025-11-26T03:06:10.368657+00:00",
      "dry_run_command": null,
      "posture_mode": "live",
      "reality_overall_ok": true,
      "status_level": "OK"
    },
    {
      "id": "NEXT_STEPS:1",
      "title": "Test task for dry-run command demonstration",
      "source": "NEXT_STEPS",
      "envelope_path": "/home/mccoy/Projects/Gemantria.v2/evidence/pmagent/capability_session-2025-11-22T02-37-10+00-00.json",
      "timestamp": "2025-11-22T02:37:10.084921+00:00",
      "dry_run_command": "make book.go",
      "posture_mode": "live",
      "reality_overall_ok": true,
      "status_level": "OK"
    },
    {
      "id": "NEXT_STEPS:1",
      "title": "Test task for reality loop demonstration",
      "source": "NEXT_STEPS",
      "envelope_path": "/home/mccoy/Projects/Gemantria.v2/evidence/pmagent/capability_session-2025-11-22T02-34-25+00-00.json",
      "timestamp": "2025-11-22T02:34:25.143268+00:00",
      "dry_run_command": null,
      "posture_mode": "live",
      "reality_overall_ok": true,
      "status_level": "OK"
    }
  ]
}

```

### plan_next_json

```
{
  "available": true,
  "master_plan_path": "/home/mccoy/Projects/Gemantria.v2/docs/SSOT/MASTER_PLAN.md",
  "next_steps_path": "/home/mccoy/Projects/Gemantria.v2/NEXT_STEPS.md",
  "current_focus": "Phase 8 temporal analytics completion and Phase 11 unified envelope stabilization.",
  "next_milestone": "Phase 12 advanced pattern mining capabilities.",
  "candidates": [
    {
      "id": "NEXT_STEPS:1",
      "title": "\u2705 All 5 tab components present and functional (SearchTab, SemanticSearchTab, LexiconTab, InsightsTab, CrossLanguageTab)",
      "source": "NEXT_STEPS",
      "priority": 1,
      "raw_line": "- \u2705 All 5 tab components present and functional (SearchTab, SemanticSearchTab, LexiconTab, InsightsTab, CrossLanguageTab)"
    },
    {
      "id": "NEXT_STEPS:2",
      "title": "\u2705 All 6 export scripts operational (`export_biblescholar_{summary,search,semantic_search,lexicon,insights,cross_language}.py`)",
      "source": "NEXT_STEPS",
      "priority": 2,
      "raw_line": "- \u2705 All 6 export scripts operational (`export_biblescholar_{summary,search,semantic_search,lexicon,insights,cross_language}.py`)"
    },
    {
      "id": "NEXT_STEPS:3",
      "title": "\u2705 All static JSON exports present in `share/exports/biblescholar/`",
      "source": "NEXT_STEPS",
      "priority": 3,
      "raw_line": "- \u2705 All static JSON exports present in `share/exports/biblescholar/`"
    }
  ]
}

```

## 4. Status snapshots (JSON)

### status_kb

```json
{
  "available": true,
  "total": 1185,
  "by_subsystem": {
    "ops": 555,
    "gematria": 38,
    "pm": 227,
    "general": 227,
    "docs": 5,
    "root": 48,
    "webui": 51,
    "biblescholar": 34
  },
  "by_type": {
    "other": 1023,
    "ssot": 129,
    "runbook": 33
  },
  "missing_files": [
    "agentpm/adapters/AGENTS.md (ID",
    "agentpm/AGENTS.md (ID",
    "agentpm/ai_docs/AGENTS.md (ID",
    "agentpm/atlas/AGENTS.md (ID",
    "agentpm/biblescholar/AGENTS.md (ID",
    "agentpm/biblescholar/tests/AGENTS.md (ID",
    "agentpm/bus/AGENTS.md (ID",
    "agentpm/control_plane/AGENTS.md (ID",
    "agentpm/control_widgets/AGENTS.md (ID",
    "agentpm/db/AGENTS.md (ID",
    "agentpm/dms/AGENTS.md (ID",
    "agentpm/docs/AGENTS.md (ID",
    "agentpm/exports/AGENTS.md (ID",
    "agentpm/extractors/AGENTS.md (ID",
    "agentpm/gatekeeper/AGENTS.md (ID",
    "agentpm/governance/AGENTS.md (ID",
    "agentpm/graph/AGENTS.md (ID",
    "agentpm/guard/AGENTS.md (ID",
    "agentpm/guarded/AGENTS.md (ID",
    "agentpm/handoff/AGENTS.md (ID",
    "agentpm/hints/AGENTS.md (ID",
    "agentpm/kb/AGENTS.md (ID",
    "agentpm/knowledge/AGENTS.md (ID",
    "agentpm/lm/AGENTS.md (ID",
    "agentpm/lm_widgets/AGENTS.md (ID",
    "agentpm/mcp/AGENTS.md (ID",
    "agentpm/metrics/AGENTS.md (ID",
    "agentpm/modules/AGENTS.md (ID",
    "agentpm/modules/gematria/AGENTS.md (ID",
    "agentpm/obs/AGENTS.md (ID",
    "agentpm/plan/AGENTS.md (ID",
    "agentpm/reality/AGENTS.md (ID",
    "agentpm/rpc/AGENTS.md (ID",
    "agentpm/runtime/AGENTS.md (ID",
    "agentpm/scripts/AGENTS.md (ID",
    "agentpm/scripts/state/AGENTS.md (ID",
    "agentpm/server/AGENTS.md (ID",
    "agentpm/status/AGENTS.md (ID",
    "agentpm/tests/adapters/AGENTS.md (ID",
    "agentpm/tests/AGENTS.md (ID",
    "agentpm/tests/atlas/AGENTS.md (ID",
    "agentpm/tests/cli/AGENTS.md (ID",
    "agentpm/tests/db/AGENTS.md (ID",
    "agentpm/tests/docs/AGENTS.md (ID",
    "agentpm/tests/exports/AGENTS.md (ID",
    "agentpm/tests/extractors/AGENTS.md (ID",
    "agentpm/tests/html/AGENTS.md (ID",
    "agentpm/tests/kb/AGENTS.md (ID",
    "agentpm/tests/knowledge/AGENTS.md (ID",
    "agentpm/tests/lm/AGENTS.md (ID",
    "agentpm/tests/mcp/AGENTS.md (ID",
    "agentpm/tests/phase1/AGENTS.md (ID",
    "agentpm/tests/reality/AGENTS.md (ID",
    "agentpm/tests/status/AGENTS.md (ID",
    "agentpm/tests/system/AGENTS.md (ID",
    "agentpm/tools/AGENTS.md (ID",
    "archive/docs/codebase-cleanup/docs-analysis/AGENTS.snapshot.md (ID",
    "archive/docs_legacy/share_scripts_AGENTS.md (ID",
    "backup/20251206T011629Z/share/AGENTS.md (ID",
    "backup/20251206T011629Z/share/scripts_AGENTS.md (ID",
    "backup/20251206T044916Z/share/AGENTS.md (ID",
    "backup/20251206T044916Z/share/scripts_AGENTS.md (ID",
    "backup/20251206T050237Z/share/AGENTS.md (ID",
    "backup/20251206T050237Z/share/scripts_AGENTS.md (ID",
    "backup/20251206T051001Z/share/AGENTS.md (ID",
    "backup/20251206T051001Z/share/scripts_AGENTS.md (ID",
    "backup/20251206T051704Z/share/AGENTS.md (ID",
    "backup/20251206T051704Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T032033Z/share/AGENTS.md (ID",
    "backup/20251207T032033Z/share/scripts_AGENTS.md (ID",
    "docs/analysis/phase7_governance/AGENTS.snapshot.md (ID",
    "agentpm/adapters/codex_cli.py (ID",
    "agentpm/adapters/gemini_cli.py (ID",
    "agentpm/adapters/lm_studio.py (ID",
    "agentpm/adapters/mcp_db.py (ID",
    "agentpm/adapters/ollama.py (ID",
    "agentpm/adapters/planning_common.py (ID",
    "agentpm/adapters/planning.py (ID",
    "agentpm/adapters/theology.py (ID",
    "agentpm/ai_docs/reality_check_ai_notes.py (ID",
    "agentpm/atlas/drilldowns.py (ID",
    "agentpm/atlas/generate.py (ID",
    "agentpm/atlas/reranker_badges.py (ID",
    "agentpm/atlas/screenshots.py (ID",
    "agentpm/atlas/webproof.py (ID",
    "agentpm/biblescholar/bible_db_adapter.py (ID",
    "agentpm/biblescholar/bible_passage_flow.py (ID",
    "agentpm/biblescholar/cross_language_flow.py (ID",
    "agentpm/biblescholar/cross_language_semantic_flow.py (ID",
    "agentpm/biblescholar/gematria_adapter.py (ID",
    "agentpm/biblescholar/gematria_flow.py (ID",
    "agentpm/biblescholar/insights_flow.py (ID",
    "agentpm/biblescholar/lexicon_adapter.py (ID",
    "agentpm/biblescholar/lexicon_flow.py (ID",
    "agentpm/biblescholar/passage.py (ID",
    "agentpm/biblescholar/reference_parser.py (ID",
    "agentpm/biblescholar/reference_slice.py (ID",
    "agentpm/biblescholar/relationship_adapter.py (ID",
    "agentpm/biblescholar/search_flow.py (ID",
    "agentpm/biblescholar/semantic_search_flow.py (ID",
    "agentpm/biblescholar/tests/test_bible_db_adapter.py (ID",
    "agentpm/biblescholar/tests/test_bible_passage_flow.py (ID",
    "agentpm/biblescholar/tests/test_cross_language_flow.py (ID",
    "agentpm/biblescholar/tests/test_cross_language.py (ID",
    "agentpm/biblescholar/tests/test_gematria_adapter.py (ID",
    "agentpm/biblescholar/tests/test_gematria_flow.py (ID",
    "agentpm/biblescholar/tests/test_insights_flow.py (ID",
    "agentpm/biblescholar/tests/test_lexicon_adapter.py (ID",
    "agentpm/biblescholar/tests/test_lexicon_flow.py (ID",
    "agentpm/biblescholar/tests/test_reference_parser.py (ID",
    "agentpm/biblescholar/tests/test_reference_slice.py (ID",
    "agentpm/biblescholar/tests/test_relationship_adapter.py (ID",
    "agentpm/biblescholar/tests/test_search_flow.py (ID",
    "agentpm/biblescholar/tests/test_vector_adapter.py (ID",
    "agentpm/biblescholar/tests/test_vector_flow.py (ID",
    "agentpm/biblescholar/vector_adapter.py (ID",
    "agentpm/biblescholar/vector_flow.py (ID",
    "agentpm/control_plane/doc_fragments.py (ID",
    "agentpm/control_plane/exports.py (ID",
    "agentpm/control_plane.py (ID",
    "agentpm/control_plane/sessions.py (ID",
    "agentpm/control_widgets/adapter.py (ID",
    "agentpm/db/loader.py (ID",
    "agentpm/db/models_graph_stats.py (ID",
    "agentpm/docs/search.py (ID",
    "agentpm/exports/generate.py (ID",
    "agentpm/extractors/provenance.py (ID",
    "agentpm/gatekeeper/impl.py (ID",
    "agentpm/gatekeeper/__init__.py (ID",
    "agentpm/gatekeeper.py (ID",
    "agentpm/graph/assembler.py (ID",
    "agentpm/guarded/autopilot_adapter.py (ID",
    "agentpm/guarded/gatekeeper.py (ID",
    "agentpm/guarded/guard_shim.py (ID",
    "agentpm/guarded/violations.py (ID",
    "agentpm/guard/impl.py (ID",
    "agentpm/guard/__init__.py (ID",
    "agentpm/hints/registry.py (ID",
    "agentpm/kb/classify.py (ID",
    "agentpm/kb/registry.py (ID",
    "agentpm/kb/search.py (ID",
    "agentpm/knowledge/qa_docs.py (ID",
    "agentpm/knowledge/retrieval.py (ID",
    "agentpm/lm/lm_status.py (ID",
    "agentpm/lm/router.py (ID",
    "agentpm/lm_widgets/adapter.py (ID",
    "agentpm/mcp/ingest.py (ID",
    "agentpm/metrics/graph_rollup.py (ID",
    "agentpm/modules/gematria/core.py (ID",
    "agentpm/modules/gematria/hebrew.py (ID",
    "agentpm/modules/gematria/nouns.py (ID",
    "agentpm/modules/gematria/osis.py (ID",
    "agentpm/modules/gematria/tests/test_core.py (ID",
    "agentpm/modules/gematria/tests/test_hebrew.py (ID",
    "agentpm/modules/gematria/verification.py (ID",
    "agentpm/obs/logger.py (ID",
    "agentpm/obs/tv.py (ID",
    "agentpm/plan/fix.py (ID",
    "agentpm/plan/kb.py (ID",
    "agentpm/plan/next.py (ID",
    "agentpm/reality/capability_envelope_validator.py (ID",
    "agentpm/reality/capability_envelope_writer.py (ID",
    "agentpm/reality/check.py (ID",
    "agentpm/reality/sessions_summary.py (ID",
    "agentpm/router.py (ID",
    "agentpm/runtime/lm_budget.py (ID",
    "agentpm/runtime/lm_helpers.py (ID",
    "agentpm/runtime/lm_logging.py (ID",
    "agentpm/runtime/lm_routing.py (ID",
    "agentpm/scripts/cleanup_codebase.py (ID",
    "agentpm/scripts/cleanup_root.py (ID",
    "agentpm/scripts/docs_archive_apply.py (ID",
    "agentpm/scripts/docs_archive_dryrun.py (ID",
    "agentpm/scripts/docs_classify_direct.py (ID",
    "agentpm/scripts/docs_dashboard_refresh.py (ID",
    "agentpm/scripts/docs_dm002_preview.py (ID",
    "agentpm/scripts/docs_dm002_summary.py (ID",
    "agentpm/scripts/docs_dm002_sync.py (ID",
    "agentpm/scripts/docs_duplicates_report.py (ID",
    "agentpm/scripts/docs_inventory.py (ID",
    "agentpm/scripts/generate_tool_embeddings.py (ID",
    "agentpm/scripts/ingest_docs.py (ID",
    "agentpm/scripts/reality_check_1_live.py (ID",
    "agentpm/scripts/reality_check_1.py (ID",
    "agentpm/scripts/state/ledger_sync.py (ID",
    "agentpm/scripts/state/ledger_verify.py (ID",
    "agentpm/scripts/system_bringup.py (ID",
    "agentpm/server/autopilot_api.py (ID",
    "agentpm/status/eval_exports.py (ID",
    "agentpm/status/explain.py (ID",
    "agentpm/status/kb_metrics.py (ID",
    "agentpm/status/snapshot.py (ID",
    "agentpm/status/system.py (ID",
    "agentpm/tests/adapters/test_lm_studio_adapter.py (ID",
    "agentpm/tests/atlas/test_atlas_accessibility_e38_e40.py (ID",
    "agentpm/tests/atlas/test_atlas_auditjump_e29_e31.py (ID",
    "agentpm/tests/atlas/test_atlas_download_backlinks_e32_e34.py (ID",
    "agentpm/tests/atlas/test_atlas_filters_breadcrumbs_sitemap_e44_e46.py (ID",
    "agentpm/tests/atlas/test_atlas_filters_contrast_sitemap_e47_e49.py (ID",
    "agentpm/tests/atlas/test_atlas_links_e26_e28.py (ID",
    "agentpm/tests/atlas/test_atlas_rawproof_e35_e37.py (ID",
    "agentpm/tests/atlas/test_atlas_search_microdata_guard_e50_e52.py (ID",
    "agentpm/tests/atlas/test_atlas_search_title_aria_e41_e43.py (ID",
    "agentpm/tests/atlas/test_atlas_smoke_e23_e25.py (ID",
    "agentpm/tests/atlas/test_e100_tagproof_phase2.py (ID",
    "agentpm/tests/atlas/test_e86_compliance_summary.py (ID",
    "agentpm/tests/atlas/test_e87_compliance_timeseries.py (ID",
    "agentpm/tests/atlas/test_e91_guard_receipts_index.py (ID",
    "agentpm/tests/atlas/test_e92_screenshot_manifest_guard.py (ID",
    "agentpm/tests/atlas/test_e93_browser_verification_guard.py (ID",
    "agentpm/tests/atlas/test_e94_tagproof_screenshots_guard.py (ID",
    "agentpm/tests/atlas/test_e95_atlas_links_guard.py (ID",
    "agentpm/tests/atlas/test_e96_tv_coverage_guard.py (ID",
    "agentpm/tests/atlas/test_e97_gatekeeper_coverage_guard.py (ID",
    "agentpm/tests/atlas/test_e98_regenerate_all_guard.py (ID",
    "agentpm/tests/atlas/test_e99_browser_screenshot_integrated.py (ID",
    "agentpm/tests/atlas/test_lm_dashboards_config.py (ID",
    "agentpm/tests/atlas/test_lm_indicator_export.py (ID",
    "agentpm/tests/atlas/test_lm_insights_exports.py (ID",
    "agentpm/tests/atlas/test_lm_metrics_exports.py (ID",
    "agentpm/tests/atlas/test_lm_status_page_insights.py (ID",
    "agentpm/tests/atlas/test_phase6p_biblescholar_reference_guard.py (ID",
    "agentpm/tests/atlas/test_phase_d_autopilot_summary.py (ID",
    "agentpm/tests/cli/test_phase3b_pmagent_control_pipeline_status_cli.py (ID",
    "agentpm/tests/cli/test_phase3b_pmagent_control_schema_cli.py (ID",
    "agentpm/tests/cli/test_phase3b_pmagent_control_status_cli.py (ID",
    "agentpm/tests/cli/test_phase3b_pmagent_control_summary_cli.py (ID",
    "agentpm/tests/cli/test_phase3b_pmagent_control_tables_cli.py (ID",
    "agentpm/tests/cli/test_phase3b_pmagent_graph_cli.py (ID",
    "agentpm/tests/cli/test_phase3b_pmagent_health_cli.py (ID",
    "agentpm/tests/cli/test_pmagent_health_lm.py (ID",
    "agentpm/tests/cli/test_pmagent_lm_router_status.py (ID",
    "agentpm/tests/cli/test_pmagent_plan_kb_fix.py (ID",
    "agentpm/tests/cli/test_pmagent_plan_kb.py (ID",
    "agentpm/tests/cli/test_pmagent_plan_next.py (ID",
    "agentpm/tests/cli/test_pmagent_reality_check_cli.py (ID",
    "agentpm/tests/cli/test_pmagent_report_kb.py (ID",
    "agentpm/tests/cli/test_pmagent_status_kb.py (ID",
    "agentpm/tests/control_widgets/test_adapter.py (ID",
    "agentpm/tests/control_widgets/test_m2_visualization.py (ID",
    "agentpm/tests/db/test_phase3a_db_health_guard.py (ID",
    "agentpm/tests/db/test_phase3a_db_health_smoke.py (ID",
    "agentpm/tests/db/test_phase3a_db_health_snapshot.py (ID",
    "agentpm/tests/db/test_phase3a_db_loader.py (ID",
    "agentpm/tests/db/test_phase3a_graph_stats_import.py (ID",
    "agentpm/tests/db/test_phase3b_graph_overview.py (ID",
    "agentpm/tests/docs/test_dms_guards.py (ID",
    "agentpm/tests/exports/test_graph_export_e20_e22.py (ID",
    "agentpm/tests/extractors/test_extraction_correctness.py (ID",
    "agentpm/tests/extractors/test_extraction_determinism_e11_e13.py (ID",
    "agentpm/tests/extractors/test_extraction_graph_propagation_e14_e16.py (ID",
    "agentpm/tests/extractors/test_extraction_provenance_e06_e10.py (ID",
    "agentpm/tests/extractors/test_graph_rollups_e17_e19.py (ID",
    "agentpm/tests/guarded/test_autopilot_adapter.py (ID",
    "agentpm/tests/html/test_lm_status_page.py (ID",
    "agentpm/tests/kb/test_freshness.py (ID",
    "agentpm/tests/kb/test_registry.py (ID",
    "agentpm/tests/knowledge/test_kb_ingest_and_export.py (ID",
    "agentpm/tests/knowledge/test_qa_docs.py (ID",
    "agentpm/tests/lm/test_phase3b_lm_health_guard.py (ID",
    "agentpm/tests/lm/test_phase6_lm_budgets.py (ID",
    "agentpm/tests/lm/test_phase6_lm_enablement.py (ID",
    "agentpm/tests/lm_widgets/test_adapter.py (ID",
    "agentpm/tests/mcp/test_m2_e21_e25.py (ID",
    "agentpm/tests/mcp/test_mcp_catalog_e01_e05.py (ID",
    "agentpm/tests/mcp/test_mcp_m10_e46_e50.py (ID",
    "agentpm/tests/mcp/test_mcp_m11_e51_e55.py (ID",
    "agentpm/tests/mcp/test_mcp_m12_e56_e60.py (ID",
    "agentpm/tests/mcp/test_mcp_m13_e61_e65.py (ID",
    "agentpm/tests/mcp/test_mcp_m14_e66_e70.py (ID",
    "agentpm/tests/mcp/test_mcp_m2_e06_e10.py (ID",
    "agentpm/tests/mcp/test_mcp_m3_e11_e15.py (ID",
    "agentpm/tests/mcp/test_mcp_m4_e16_e20.py (ID",
    "agentpm/tests/mcp/test_mcp_m5_e21_e25.py (ID",
    "agentpm/tests/mcp/test_mcp_m6_e26_e30.py (ID",
    "agentpm/tests/mcp/test_mcp_m7_e31_e35.py (ID",
    "agentpm/tests/mcp/test_mcp_m8_e36_e40.py (ID",
    "agentpm/tests/mcp/test_mcp_m9_e41_e45.py (ID",
    "agentpm/tests/phase1/test_tv01_missing_por.py (ID",
    "agentpm/tests/phase1/test_tv02_arg_schema_invalid.py (ID",
    "agentpm/tests/phase1/test_tv03_ring_violation.py (ID",
    "agentpm/tests/phase1/test_tv04_provenance_mismatch.py (ID",
    "agentpm/tests/phase1/test_tv05_forbidden_tool.py (ID",
    "agentpm/tests/pipelines/test_enrich_nouns_lm_routing.py (ID",
    "agentpm/tests/reality/test_capability_envelope_validator.py (ID",
    "agentpm/tests/reality/test_capability_envelope_writer.py (ID",
    "agentpm/tests/reality/test_reality_check.py (ID",
    "agentpm/tests/reality/test_sessions_summary.py (ID",
    "agentpm/tests/runtime/test_lm_logging.py (ID",
    "agentpm/tests/runtime/test_lm_routing.py (ID",
    "agentpm/tests/runtime/test_pm_snapshot.py (ID",
    "agentpm/tests/server/test_autopilot_api.py (ID",
    "agentpm/tests/status/test_eval_exports.py (ID",
    "agentpm/tests/status/test_explain_kb.py (ID",
    "agentpm/tests/status/test_kb_hints.py (ID",
    "agentpm/tests/system/test_phase3b_system_health.py (ID",
    "agentpm/tests/test_guarded_calls_tv.py (ID",
    "agentpm/tests/tools/test_system_reality_check.py (ID",
    "agentpm/tools/bible.py (ID",
    "agentpm/tools/embed.py (ID",
    "agentpm/tools/extract.py (ID",
    "agentpm/tools/rerank.py (ID",
    "agentpm/tools/system.py (ID",
    "archive/docs/codebase-cleanup/scripts/tmp_patch_samples.py (ID",
    "archive/_quarantine/p2-scaffold/envelope.py (ID",
    "archive/_quarantine/p2-scaffold/graph.py (ID",
    "archive/_quarantine/p2-scaffold/nodes.py (ID",
    "archive/run_pipeline.py (ID",
    "archive/test_graph.py (ID",
    "archive/ui_legacy_phase10/scripts/export_noun_index.py (ID",
    "conftest.py (ID",
    "rules_guard.py (ID",
    "test_bi_encoder_rerank.py (ID",
    "test_mcp_server.py (ID",
    "docs/runbooks/CPU_PERFORMANCE_FIX.md (ID",
    "docs/runbooks/SYSTEM_OPTIMIZATION_AI.md (ID"
  ],
  "notes": [
    "Registry validation failed: 318 errors",
    "Registry has 3 warnings"
  ],
  "freshness": {
    "total": 1185,
    "stale_count": 9,
    "missing_count": 316,
    "out_of_sync_count": 0,
    "fresh_count": 860
  },
  "freshness_details": {
    "stale_docs": [
      {
        "id": "ssot::docs/ssot/data-flow-visual.md",
        "path": "docs/SSOT/data_flow_visual.md",
        "title": "SSOT::docs/SSOT/data_flow_visual.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/epoch-ledger.md",
        "path": "docs/SSOT/EPOCH_LEDGER.md",
        "title": "SSOT::docs/SSOT/EPOCH_LEDGER.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/graph-metrics-api.md",
        "path": "docs/SSOT/graph-metrics-api.md",
        "title": "SSOT::docs/SSOT/graph-metrics-api.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/graph-stats-api.md",
        "path": "docs/SSOT/graph-stats-api.md",
        "title": "SSOT::docs/SSOT/graph-stats-api.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/jsonld-schema.md",
        "path": "docs/SSOT/jsonld-schema.md",
        "title": "SSOT::docs/SSOT/jsonld-schema.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/rdf-ontology.md",
        "path": "docs/SSOT/rdf-ontology.md",
        "title": "SSOT::docs/SSOT/rdf-ontology.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/references.md",
        "path": "docs/SSOT/REFERENCES.md",
        "title": "SSOT::docs/SSOT/REFERENCES.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/visualization-config.md",
        "path": "docs/SSOT/visualization-config.md",
        "title": "SSOT::docs/SSOT/visualization-config.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      },
      {
        "id": "ssot::docs/ssot/webui-contract.md",
        "path": "docs/SSOT/webui-contract.md",
        "title": "SSOT::docs/SSOT/webui-contract.md",
        "type": "ssot",
        "last_refreshed_at": null,
        "refresh_interval_days": 30
      }
    ],
    "missing_docs": [
      {
        "id": "agents::agentpm/adapters/agents.md",
        "path": "agentpm/adapters/AGENTS.md",
        "title": "AGENTS::agentpm/adapters/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/agents.md",
        "path": "agentpm/AGENTS.md",
        "title": "AGENTS::agentpm/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/ai-docs/agents.md",
        "path": "agentpm/ai_docs/AGENTS.md",
        "title": "AGENTS::agentpm/ai_docs/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/atlas/agents.md",
        "path": "agentpm/atlas/AGENTS.md",
        "title": "AGENTS::agentpm/atlas/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/biblescholar/agents.md",
        "path": "agentpm/biblescholar/AGENTS.md",
        "title": "AGENTS::agentpm/biblescholar/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/biblescholar/tests/agents.md",
        "path": "agentpm/biblescholar/tests/AGENTS.md",
        "title": "AGENTS::agentpm/biblescholar/tests/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/bus/agents.md",
        "path": "agentpm/bus/AGENTS.md",
        "title": "AGENTS::agentpm/bus/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/control-plane/agents.md",
        "path": "agentpm/control_plane/AGENTS.md",
        "title": "AGENTS::agentpm/control_plane/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/control-widgets/agents.md",
        "path": "agentpm/control_widgets/AGENTS.md",
        "title": "AGENTS::agentpm/control_widgets/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/db/agents.md",
        "path": "agentpm/db/AGENTS.md",
        "title": "AGENTS::agentpm/db/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/dms/agents.md",
        "path": "agentpm/dms/AGENTS.md",
        "title": "AGENTS::agentpm/dms/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/docs/agents.md",
        "path": "agentpm/docs/AGENTS.md",
        "title": "AGENTS::agentpm/docs/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/exports/agents.md",
        "path": "agentpm/exports/AGENTS.md",
        "title": "AGENTS::agentpm/exports/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/extractors/agents.md",
        "path": "agentpm/extractors/AGENTS.md",
        "title": "AGENTS::agentpm/extractors/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/gatekeeper/agents.md",
        "path": "agentpm/gatekeeper/AGENTS.md",
        "title": "AGENTS::agentpm/gatekeeper/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/governance/agents.md",
        "path": "agentpm/governance/AGENTS.md",
        "title": "AGENTS::agentpm/governance/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/graph/agents.md",
        "path": "agentpm/graph/AGENTS.md",
        "title": "AGENTS::agentpm/graph/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/guard/agents.md",
        "path": "agentpm/guard/AGENTS.md",
        "title": "AGENTS::agentpm/guard/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/guarded/agents.md",
        "path": "agentpm/guarded/AGENTS.md",
        "title": "AGENTS::agentpm/guarded/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/handoff/agents.md",
        "path": "agentpm/handoff/AGENTS.md",
        "title": "AGENTS::agentpm/handoff/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/hints/agents.md",
        "path": "agentpm/hints/AGENTS.md",
        "title": "AGENTS::agentpm/hints/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/kb/agents.md",
        "path": "agentpm/kb/AGENTS.md",
        "title": "AGENTS::agentpm/kb/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/knowledge/agents.md",
        "path": "agentpm/knowledge/AGENTS.md",
        "title": "AGENTS::agentpm/knowledge/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/lm/agents.md",
        "path": "agentpm/lm/AGENTS.md",
        "title": "AGENTS::agentpm/lm/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/lm-widgets/agents.md",
        "path": "agentpm/lm_widgets/AGENTS.md",
        "title": "AGENTS::agentpm/lm_widgets/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/mcp/agents.md",
        "path": "agentpm/mcp/AGENTS.md",
        "title": "AGENTS::agentpm/mcp/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/metrics/agents.md",
        "path": "agentpm/metrics/AGENTS.md",
        "title": "AGENTS::agentpm/metrics/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/modules/agents.md",
        "path": "agentpm/modules/AGENTS.md",
        "title": "AGENTS::agentpm/modules/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/modules/gematria/agents.md",
        "path": "agentpm/modules/gematria/AGENTS.md",
        "title": "AGENTS::agentpm/modules/gematria/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/obs/agents.md",
        "path": "agentpm/obs/AGENTS.md",
        "title": "AGENTS::agentpm/obs/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/plan/agents.md",
        "path": "agentpm/plan/AGENTS.md",
        "title": "AGENTS::agentpm/plan/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/reality/agents.md",
        "path": "agentpm/reality/AGENTS.md",
        "title": "AGENTS::agentpm/reality/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/rpc/agents.md",
        "path": "agentpm/rpc/AGENTS.md",
        "title": "AGENTS::agentpm/rpc/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/runtime/agents.md",
        "path": "agentpm/runtime/AGENTS.md",
        "title": "AGENTS::agentpm/runtime/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/scripts/agents.md",
        "path": "agentpm/scripts/AGENTS.md",
        "title": "AGENTS::agentpm/scripts/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/scripts/state/agents.md",
        "path": "agentpm/scripts/state/AGENTS.md",
        "title": "AGENTS::agentpm/scripts/state/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/server/agents.md",
        "path": "agentpm/server/AGENTS.md",
        "title": "AGENTS::agentpm/server/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/status/agents.md",
        "path": "agentpm/status/AGENTS.md",
        "title": "AGENTS::agentpm/status/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/adapters/agents.md",
        "path": "agentpm/tests/adapters/AGENTS.md",
        "title": "AGENTS::agentpm/tests/adapters/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/agents.md",
        "path": "agentpm/tests/AGENTS.md",
        "title": "AGENTS::agentpm/tests/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/atlas/agents.md",
        "path": "agentpm/tests/atlas/AGENTS.md",
        "title": "AGENTS::agentpm/tests/atlas/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/cli/agents.md",
        "path": "agentpm/tests/cli/AGENTS.md",
        "title": "AGENTS::agentpm/tests/cli/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/db/agents.md",
        "path": "agentpm/tests/db/AGENTS.md",
        "title": "AGENTS::agentpm/tests/db/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/docs/agents.md",
        "path": "agentpm/tests/docs/AGENTS.md",
        "title": "AGENTS::agentpm/tests/docs/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/exports/agents.md",
        "path": "agentpm/tests/exports/AGENTS.md",
        "title": "AGENTS::agentpm/tests/exports/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/extractors/agents.md",
        "path": "agentpm/tests/extractors/AGENTS.md",
        "title": "AGENTS::agentpm/tests/extractors/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/html/agents.md",
        "path": "agentpm/tests/html/AGENTS.md",
        "title": "AGENTS::agentpm/tests/html/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/kb/agents.md",
        "path": "agentpm/tests/kb/AGENTS.md",
        "title": "AGENTS::agentpm/tests/kb/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/knowledge/agents.md",
        "path": "agentpm/tests/knowledge/AGENTS.md",
        "title": "AGENTS::agentpm/tests/knowledge/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/lm/agents.md",
        "path": "agentpm/tests/lm/AGENTS.md",
        "title": "AGENTS::agentpm/tests/lm/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/mcp/agents.md",
        "path": "agentpm/tests/mcp/AGENTS.md",
        "title": "AGENTS::agentpm/tests/mcp/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/phase1/agents.md",
        "path": "agentpm/tests/phase1/AGENTS.md",
        "title": "AGENTS::agentpm/tests/phase1/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/reality/agents.md",
        "path": "agentpm/tests/reality/AGENTS.md",
        "title": "AGENTS::agentpm/tests/reality/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/status/agents.md",
        "path": "agentpm/tests/status/AGENTS.md",
        "title": "AGENTS::agentpm/tests/status/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tests/system/agents.md",
        "path": "agentpm/tests/system/AGENTS.md",
        "title": "AGENTS::agentpm/tests/system/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::agentpm/tools/agents.md",
        "path": "agentpm/tools/AGENTS.md",
        "title": "AGENTS::agentpm/tools/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::archive/docs/codebase-cleanup/docs-analysis/agents.snapshot.md",
        "path": "archive/docs/codebase-cleanup/docs-analysis/AGENTS.snapshot.md",
        "title": "AGENTS::archive/docs/codebase-cleanup/docs-analysis/AGENTS.snapshot.md",
        "type": "other"
      },
      {
        "id": "agents::archive/docs-legacy/share-scripts-agents.md",
        "path": "archive/docs_legacy/share_scripts_AGENTS.md",
        "title": "AGENTS::archive/docs_legacy/share_scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t011629z/share/agents.md",
        "path": "backup/20251206T011629Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251206T011629Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t011629z/share/scripts-agents.md",
        "path": "backup/20251206T011629Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251206T011629Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t044916z/share/agents.md",
        "path": "backup/20251206T044916Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251206T044916Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t044916z/share/scripts-agents.md",
        "path": "backup/20251206T044916Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251206T044916Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t050237z/share/agents.md",
        "path": "backup/20251206T050237Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251206T050237Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t050237z/share/scripts-agents.md",
        "path": "backup/20251206T050237Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251206T050237Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t051001z/share/agents.md",
        "path": "backup/20251206T051001Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251206T051001Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t051001z/share/scripts-agents.md",
        "path": "backup/20251206T051001Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251206T051001Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t051704z/share/agents.md",
        "path": "backup/20251206T051704Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251206T051704Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251206t051704z/share/scripts-agents.md",
        "path": "backup/20251206T051704Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251206T051704Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t032033z/share/agents.md",
        "path": "backup/20251207T032033Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T032033Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t032033z/share/scripts-agents.md",
        "path": "backup/20251207T032033Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T032033Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::docs/analysis/phase7-governance/agents.snapshot.md",
        "path": "docs/analysis/phase7_governance/AGENTS.snapshot.md",
        "title": "AGENTS::docs/analysis/phase7_governance/AGENTS.snapshot.md",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/codex-cli.py",
        "path": "agentpm/adapters/codex_cli.py",
        "title": "CODE::agentpm/adapters/codex_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/gemini-cli.py",
        "path": "agentpm/adapters/gemini_cli.py",
        "title": "CODE::agentpm/adapters/gemini_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/lm-studio.py",
        "path": "agentpm/adapters/lm_studio.py",
        "title": "CODE::agentpm/adapters/lm_studio.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/mcp-db.py",
        "path": "agentpm/adapters/mcp_db.py",
        "title": "CODE::agentpm/adapters/mcp_db.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/ollama.py",
        "path": "agentpm/adapters/ollama.py",
        "title": "CODE::agentpm/adapters/ollama.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/planning-common.py",
        "path": "agentpm/adapters/planning_common.py",
        "title": "CODE::agentpm/adapters/planning_common.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/planning.py",
        "path": "agentpm/adapters/planning.py",
        "title": "CODE::agentpm/adapters/planning.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/adapters/theology.py",
        "path": "agentpm/adapters/theology.py",
        "title": "CODE::agentpm/adapters/theology.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/ai-docs/reality-check-ai-notes.py",
        "path": "agentpm/ai_docs/reality_check_ai_notes.py",
        "title": "CODE::agentpm/ai_docs/reality_check_ai_notes.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/atlas/drilldowns.py",
        "path": "agentpm/atlas/drilldowns.py",
        "title": "CODE::agentpm/atlas/drilldowns.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/atlas/generate.py",
        "path": "agentpm/atlas/generate.py",
        "title": "CODE::agentpm/atlas/generate.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/atlas/reranker-badges.py",
        "path": "agentpm/atlas/reranker_badges.py",
        "title": "CODE::agentpm/atlas/reranker_badges.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/atlas/screenshots.py",
        "path": "agentpm/atlas/screenshots.py",
        "title": "CODE::agentpm/atlas/screenshots.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/atlas/webproof.py",
        "path": "agentpm/atlas/webproof.py",
        "title": "CODE::agentpm/atlas/webproof.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/bible-db-adapter.py",
        "path": "agentpm/biblescholar/bible_db_adapter.py",
        "title": "CODE::agentpm/biblescholar/bible_db_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/bible-passage-flow.py",
        "path": "agentpm/biblescholar/bible_passage_flow.py",
        "title": "CODE::agentpm/biblescholar/bible_passage_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/cross-language-flow.py",
        "path": "agentpm/biblescholar/cross_language_flow.py",
        "title": "CODE::agentpm/biblescholar/cross_language_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/cross-language-semantic-flow.py",
        "path": "agentpm/biblescholar/cross_language_semantic_flow.py",
        "title": "CODE::agentpm/biblescholar/cross_language_semantic_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/gematria-adapter.py",
        "path": "agentpm/biblescholar/gematria_adapter.py",
        "title": "CODE::agentpm/biblescholar/gematria_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/gematria-flow.py",
        "path": "agentpm/biblescholar/gematria_flow.py",
        "title": "CODE::agentpm/biblescholar/gematria_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/insights-flow.py",
        "path": "agentpm/biblescholar/insights_flow.py",
        "title": "CODE::agentpm/biblescholar/insights_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/lexicon-adapter.py",
        "path": "agentpm/biblescholar/lexicon_adapter.py",
        "title": "CODE::agentpm/biblescholar/lexicon_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/lexicon-flow.py",
        "path": "agentpm/biblescholar/lexicon_flow.py",
        "title": "CODE::agentpm/biblescholar/lexicon_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/passage.py",
        "path": "agentpm/biblescholar/passage.py",
        "title": "CODE::agentpm/biblescholar/passage.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/reference-parser.py",
        "path": "agentpm/biblescholar/reference_parser.py",
        "title": "CODE::agentpm/biblescholar/reference_parser.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/reference-slice.py",
        "path": "agentpm/biblescholar/reference_slice.py",
        "title": "CODE::agentpm/biblescholar/reference_slice.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/relationship-adapter.py",
        "path": "agentpm/biblescholar/relationship_adapter.py",
        "title": "CODE::agentpm/biblescholar/relationship_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/search-flow.py",
        "path": "agentpm/biblescholar/search_flow.py",
        "title": "CODE::agentpm/biblescholar/search_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/semantic-search-flow.py",
        "path": "agentpm/biblescholar/semantic_search_flow.py",
        "title": "CODE::agentpm/biblescholar/semantic_search_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-bible-db-adapter.py",
        "path": "agentpm/biblescholar/tests/test_bible_db_adapter.py",
        "title": "CODE::agentpm/biblescholar/tests/test_bible_db_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-bible-passage-flow.py",
        "path": "agentpm/biblescholar/tests/test_bible_passage_flow.py",
        "title": "CODE::agentpm/biblescholar/tests/test_bible_passage_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-cross-language-flow.py",
        "path": "agentpm/biblescholar/tests/test_cross_language_flow.py",
        "title": "CODE::agentpm/biblescholar/tests/test_cross_language_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-cross-language.py",
        "path": "agentpm/biblescholar/tests/test_cross_language.py",
        "title": "CODE::agentpm/biblescholar/tests/test_cross_language.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-gematria-adapter.py",
        "path": "agentpm/biblescholar/tests/test_gematria_adapter.py",
        "title": "CODE::agentpm/biblescholar/tests/test_gematria_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-gematria-flow.py",
        "path": "agentpm/biblescholar/tests/test_gematria_flow.py",
        "title": "CODE::agentpm/biblescholar/tests/test_gematria_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-insights-flow.py",
        "path": "agentpm/biblescholar/tests/test_insights_flow.py",
        "title": "CODE::agentpm/biblescholar/tests/test_insights_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-lexicon-adapter.py",
        "path": "agentpm/biblescholar/tests/test_lexicon_adapter.py",
        "title": "CODE::agentpm/biblescholar/tests/test_lexicon_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-lexicon-flow.py",
        "path": "agentpm/biblescholar/tests/test_lexicon_flow.py",
        "title": "CODE::agentpm/biblescholar/tests/test_lexicon_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-reference-parser.py",
        "path": "agentpm/biblescholar/tests/test_reference_parser.py",
        "title": "CODE::agentpm/biblescholar/tests/test_reference_parser.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-reference-slice.py",
        "path": "agentpm/biblescholar/tests/test_reference_slice.py",
        "title": "CODE::agentpm/biblescholar/tests/test_reference_slice.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-relationship-adapter.py",
        "path": "agentpm/biblescholar/tests/test_relationship_adapter.py",
        "title": "CODE::agentpm/biblescholar/tests/test_relationship_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-search-flow.py",
        "path": "agentpm/biblescholar/tests/test_search_flow.py",
        "title": "CODE::agentpm/biblescholar/tests/test_search_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-vector-adapter.py",
        "path": "agentpm/biblescholar/tests/test_vector_adapter.py",
        "title": "CODE::agentpm/biblescholar/tests/test_vector_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/tests/test-vector-flow.py",
        "path": "agentpm/biblescholar/tests/test_vector_flow.py",
        "title": "CODE::agentpm/biblescholar/tests/test_vector_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/vector-adapter.py",
        "path": "agentpm/biblescholar/vector_adapter.py",
        "title": "CODE::agentpm/biblescholar/vector_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/biblescholar/vector-flow.py",
        "path": "agentpm/biblescholar/vector_flow.py",
        "title": "CODE::agentpm/biblescholar/vector_flow.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/control-plane/doc-fragments.py",
        "path": "agentpm/control_plane/doc_fragments.py",
        "title": "CODE::agentpm/control_plane/doc_fragments.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/control-plane/exports.py",
        "path": "agentpm/control_plane/exports.py",
        "title": "CODE::agentpm/control_plane/exports.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/control-plane.py",
        "path": "agentpm/control_plane.py",
        "title": "CODE::agentpm/control_plane.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/control-plane/sessions.py",
        "path": "agentpm/control_plane/sessions.py",
        "title": "CODE::agentpm/control_plane/sessions.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/control-widgets/adapter.py",
        "path": "agentpm/control_widgets/adapter.py",
        "title": "CODE::agentpm/control_widgets/adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/db/loader.py",
        "path": "agentpm/db/loader.py",
        "title": "CODE::agentpm/db/loader.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/db/models-graph-stats.py",
        "path": "agentpm/db/models_graph_stats.py",
        "title": "CODE::agentpm/db/models_graph_stats.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/docs/search.py",
        "path": "agentpm/docs/search.py",
        "title": "CODE::agentpm/docs/search.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/exports/generate.py",
        "path": "agentpm/exports/generate.py",
        "title": "CODE::agentpm/exports/generate.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/extractors/provenance.py",
        "path": "agentpm/extractors/provenance.py",
        "title": "CODE::agentpm/extractors/provenance.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/gatekeeper/impl.py",
        "path": "agentpm/gatekeeper/impl.py",
        "title": "CODE::agentpm/gatekeeper/impl.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/gatekeeper/--init--.py",
        "path": "agentpm/gatekeeper/__init__.py",
        "title": "CODE::agentpm/gatekeeper/__init__.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/gatekeeper.py",
        "path": "agentpm/gatekeeper.py",
        "title": "CODE::agentpm/gatekeeper.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/graph/assembler.py",
        "path": "agentpm/graph/assembler.py",
        "title": "CODE::agentpm/graph/assembler.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/guarded/autopilot-adapter.py",
        "path": "agentpm/guarded/autopilot_adapter.py",
        "title": "CODE::agentpm/guarded/autopilot_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/guarded/gatekeeper.py",
        "path": "agentpm/guarded/gatekeeper.py",
        "title": "CODE::agentpm/guarded/gatekeeper.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/guarded/guard-shim.py",
        "path": "agentpm/guarded/guard_shim.py",
        "title": "CODE::agentpm/guarded/guard_shim.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/guarded/violations.py",
        "path": "agentpm/guarded/violations.py",
        "title": "CODE::agentpm/guarded/violations.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/guard/impl.py",
        "path": "agentpm/guard/impl.py",
        "title": "CODE::agentpm/guard/impl.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/guard/--init--.py",
        "path": "agentpm/guard/__init__.py",
        "title": "CODE::agentpm/guard/__init__.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/hints/registry.py",
        "path": "agentpm/hints/registry.py",
        "title": "CODE::agentpm/hints/registry.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/kb/classify.py",
        "path": "agentpm/kb/classify.py",
        "title": "CODE::agentpm/kb/classify.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/kb/registry.py",
        "path": "agentpm/kb/registry.py",
        "title": "CODE::agentpm/kb/registry.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/kb/search.py",
        "path": "agentpm/kb/search.py",
        "title": "CODE::agentpm/kb/search.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/knowledge/qa-docs.py",
        "path": "agentpm/knowledge/qa_docs.py",
        "title": "CODE::agentpm/knowledge/qa_docs.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/knowledge/retrieval.py",
        "path": "agentpm/knowledge/retrieval.py",
        "title": "CODE::agentpm/knowledge/retrieval.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/lm/lm-status.py",
        "path": "agentpm/lm/lm_status.py",
        "title": "CODE::agentpm/lm/lm_status.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/lm/router.py",
        "path": "agentpm/lm/router.py",
        "title": "CODE::agentpm/lm/router.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/lm-widgets/adapter.py",
        "path": "agentpm/lm_widgets/adapter.py",
        "title": "CODE::agentpm/lm_widgets/adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/mcp/ingest.py",
        "path": "agentpm/mcp/ingest.py",
        "title": "CODE::agentpm/mcp/ingest.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/metrics/graph-rollup.py",
        "path": "agentpm/metrics/graph_rollup.py",
        "title": "CODE::agentpm/metrics/graph_rollup.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/modules/gematria/core.py",
        "path": "agentpm/modules/gematria/core.py",
        "title": "CODE::agentpm/modules/gematria/core.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/modules/gematria/hebrew.py",
        "path": "agentpm/modules/gematria/hebrew.py",
        "title": "CODE::agentpm/modules/gematria/hebrew.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/modules/gematria/nouns.py",
        "path": "agentpm/modules/gematria/nouns.py",
        "title": "CODE::agentpm/modules/gematria/nouns.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/modules/gematria/osis.py",
        "path": "agentpm/modules/gematria/osis.py",
        "title": "CODE::agentpm/modules/gematria/osis.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/modules/gematria/tests/test-core.py",
        "path": "agentpm/modules/gematria/tests/test_core.py",
        "title": "CODE::agentpm/modules/gematria/tests/test_core.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/modules/gematria/tests/test-hebrew.py",
        "path": "agentpm/modules/gematria/tests/test_hebrew.py",
        "title": "CODE::agentpm/modules/gematria/tests/test_hebrew.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/modules/gematria/verification.py",
        "path": "agentpm/modules/gematria/verification.py",
        "title": "CODE::agentpm/modules/gematria/verification.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/obs/logger.py",
        "path": "agentpm/obs/logger.py",
        "title": "CODE::agentpm/obs/logger.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/obs/tv.py",
        "path": "agentpm/obs/tv.py",
        "title": "CODE::agentpm/obs/tv.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/plan/fix.py",
        "path": "agentpm/plan/fix.py",
        "title": "CODE::agentpm/plan/fix.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/plan/kb.py",
        "path": "agentpm/plan/kb.py",
        "title": "CODE::agentpm/plan/kb.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/plan/next.py",
        "path": "agentpm/plan/next.py",
        "title": "CODE::agentpm/plan/next.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/reality/capability-envelope-validator.py",
        "path": "agentpm/reality/capability_envelope_validator.py",
        "title": "CODE::agentpm/reality/capability_envelope_validator.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/reality/capability-envelope-writer.py",
        "path": "agentpm/reality/capability_envelope_writer.py",
        "title": "CODE::agentpm/reality/capability_envelope_writer.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/reality/check.py",
        "path": "agentpm/reality/check.py",
        "title": "CODE::agentpm/reality/check.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/reality/sessions-summary.py",
        "path": "agentpm/reality/sessions_summary.py",
        "title": "CODE::agentpm/reality/sessions_summary.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/router.py",
        "path": "agentpm/router.py",
        "title": "CODE::agentpm/router.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/runtime/lm-budget.py",
        "path": "agentpm/runtime/lm_budget.py",
        "title": "CODE::agentpm/runtime/lm_budget.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/runtime/lm-helpers.py",
        "path": "agentpm/runtime/lm_helpers.py",
        "title": "CODE::agentpm/runtime/lm_helpers.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/runtime/lm-logging.py",
        "path": "agentpm/runtime/lm_logging.py",
        "title": "CODE::agentpm/runtime/lm_logging.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/runtime/lm-routing.py",
        "path": "agentpm/runtime/lm_routing.py",
        "title": "CODE::agentpm/runtime/lm_routing.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/cleanup-codebase.py",
        "path": "agentpm/scripts/cleanup_codebase.py",
        "title": "CODE::agentpm/scripts/cleanup_codebase.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/cleanup-root.py",
        "path": "agentpm/scripts/cleanup_root.py",
        "title": "CODE::agentpm/scripts/cleanup_root.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-archive-apply.py",
        "path": "agentpm/scripts/docs_archive_apply.py",
        "title": "CODE::agentpm/scripts/docs_archive_apply.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-archive-dryrun.py",
        "path": "agentpm/scripts/docs_archive_dryrun.py",
        "title": "CODE::agentpm/scripts/docs_archive_dryrun.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-classify-direct.py",
        "path": "agentpm/scripts/docs_classify_direct.py",
        "title": "CODE::agentpm/scripts/docs_classify_direct.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-dashboard-refresh.py",
        "path": "agentpm/scripts/docs_dashboard_refresh.py",
        "title": "CODE::agentpm/scripts/docs_dashboard_refresh.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-dm002-preview.py",
        "path": "agentpm/scripts/docs_dm002_preview.py",
        "title": "CODE::agentpm/scripts/docs_dm002_preview.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-dm002-summary.py",
        "path": "agentpm/scripts/docs_dm002_summary.py",
        "title": "CODE::agentpm/scripts/docs_dm002_summary.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-dm002-sync.py",
        "path": "agentpm/scripts/docs_dm002_sync.py",
        "title": "CODE::agentpm/scripts/docs_dm002_sync.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-duplicates-report.py",
        "path": "agentpm/scripts/docs_duplicates_report.py",
        "title": "CODE::agentpm/scripts/docs_duplicates_report.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/docs-inventory.py",
        "path": "agentpm/scripts/docs_inventory.py",
        "title": "CODE::agentpm/scripts/docs_inventory.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/generate-tool-embeddings.py",
        "path": "agentpm/scripts/generate_tool_embeddings.py",
        "title": "CODE::agentpm/scripts/generate_tool_embeddings.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/ingest-docs.py",
        "path": "agentpm/scripts/ingest_docs.py",
        "title": "CODE::agentpm/scripts/ingest_docs.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/reality-check-1-live.py",
        "path": "agentpm/scripts/reality_check_1_live.py",
        "title": "CODE::agentpm/scripts/reality_check_1_live.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/reality-check-1.py",
        "path": "agentpm/scripts/reality_check_1.py",
        "title": "CODE::agentpm/scripts/reality_check_1.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/state/ledger-sync.py",
        "path": "agentpm/scripts/state/ledger_sync.py",
        "title": "CODE::agentpm/scripts/state/ledger_sync.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/state/ledger-verify.py",
        "path": "agentpm/scripts/state/ledger_verify.py",
        "title": "CODE::agentpm/scripts/state/ledger_verify.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/scripts/system-bringup.py",
        "path": "agentpm/scripts/system_bringup.py",
        "title": "CODE::agentpm/scripts/system_bringup.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/server/autopilot-api.py",
        "path": "agentpm/server/autopilot_api.py",
        "title": "CODE::agentpm/server/autopilot_api.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/status/eval-exports.py",
        "path": "agentpm/status/eval_exports.py",
        "title": "CODE::agentpm/status/eval_exports.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/status/explain.py",
        "path": "agentpm/status/explain.py",
        "title": "CODE::agentpm/status/explain.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/status/kb-metrics.py",
        "path": "agentpm/status/kb_metrics.py",
        "title": "CODE::agentpm/status/kb_metrics.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/status/snapshot.py",
        "path": "agentpm/status/snapshot.py",
        "title": "CODE::agentpm/status/snapshot.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/status/system.py",
        "path": "agentpm/status/system.py",
        "title": "CODE::agentpm/status/system.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/adapters/test-lm-studio-adapter.py",
        "path": "agentpm/tests/adapters/test_lm_studio_adapter.py",
        "title": "CODE::agentpm/tests/adapters/test_lm_studio_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-accessibility-e38-e40.py",
        "path": "agentpm/tests/atlas/test_atlas_accessibility_e38_e40.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_accessibility_e38_e40.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-auditjump-e29-e31.py",
        "path": "agentpm/tests/atlas/test_atlas_auditjump_e29_e31.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_auditjump_e29_e31.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-download-backlinks-e32-e34.py",
        "path": "agentpm/tests/atlas/test_atlas_download_backlinks_e32_e34.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_download_backlinks_e32_e34.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-filters-breadcrumbs-sitemap-e44-e46.py",
        "path": "agentpm/tests/atlas/test_atlas_filters_breadcrumbs_sitemap_e44_e46.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_filters_breadcrumbs_sitemap_e44_e46.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-filters-contrast-sitemap-e47-e49.py",
        "path": "agentpm/tests/atlas/test_atlas_filters_contrast_sitemap_e47_e49.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_filters_contrast_sitemap_e47_e49.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-links-e26-e28.py",
        "path": "agentpm/tests/atlas/test_atlas_links_e26_e28.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_links_e26_e28.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-rawproof-e35-e37.py",
        "path": "agentpm/tests/atlas/test_atlas_rawproof_e35_e37.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_rawproof_e35_e37.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-search-microdata-guard-e50-e52.py",
        "path": "agentpm/tests/atlas/test_atlas_search_microdata_guard_e50_e52.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_search_microdata_guard_e50_e52.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-search-title-aria-e41-e43.py",
        "path": "agentpm/tests/atlas/test_atlas_search_title_aria_e41_e43.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_search_title_aria_e41_e43.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-atlas-smoke-e23-e25.py",
        "path": "agentpm/tests/atlas/test_atlas_smoke_e23_e25.py",
        "title": "CODE::agentpm/tests/atlas/test_atlas_smoke_e23_e25.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e100-tagproof-phase2.py",
        "path": "agentpm/tests/atlas/test_e100_tagproof_phase2.py",
        "title": "CODE::agentpm/tests/atlas/test_e100_tagproof_phase2.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e86-compliance-summary.py",
        "path": "agentpm/tests/atlas/test_e86_compliance_summary.py",
        "title": "CODE::agentpm/tests/atlas/test_e86_compliance_summary.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e87-compliance-timeseries.py",
        "path": "agentpm/tests/atlas/test_e87_compliance_timeseries.py",
        "title": "CODE::agentpm/tests/atlas/test_e87_compliance_timeseries.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e91-guard-receipts-index.py",
        "path": "agentpm/tests/atlas/test_e91_guard_receipts_index.py",
        "title": "CODE::agentpm/tests/atlas/test_e91_guard_receipts_index.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e92-screenshot-manifest-guard.py",
        "path": "agentpm/tests/atlas/test_e92_screenshot_manifest_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_e92_screenshot_manifest_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e93-browser-verification-guard.py",
        "path": "agentpm/tests/atlas/test_e93_browser_verification_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_e93_browser_verification_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e94-tagproof-screenshots-guard.py",
        "path": "agentpm/tests/atlas/test_e94_tagproof_screenshots_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_e94_tagproof_screenshots_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e95-atlas-links-guard.py",
        "path": "agentpm/tests/atlas/test_e95_atlas_links_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_e95_atlas_links_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e96-tv-coverage-guard.py",
        "path": "agentpm/tests/atlas/test_e96_tv_coverage_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_e96_tv_coverage_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e97-gatekeeper-coverage-guard.py",
        "path": "agentpm/tests/atlas/test_e97_gatekeeper_coverage_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_e97_gatekeeper_coverage_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e98-regenerate-all-guard.py",
        "path": "agentpm/tests/atlas/test_e98_regenerate_all_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_e98_regenerate_all_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-e99-browser-screenshot-integrated.py",
        "path": "agentpm/tests/atlas/test_e99_browser_screenshot_integrated.py",
        "title": "CODE::agentpm/tests/atlas/test_e99_browser_screenshot_integrated.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-lm-dashboards-config.py",
        "path": "agentpm/tests/atlas/test_lm_dashboards_config.py",
        "title": "CODE::agentpm/tests/atlas/test_lm_dashboards_config.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-lm-indicator-export.py",
        "path": "agentpm/tests/atlas/test_lm_indicator_export.py",
        "title": "CODE::agentpm/tests/atlas/test_lm_indicator_export.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-lm-insights-exports.py",
        "path": "agentpm/tests/atlas/test_lm_insights_exports.py",
        "title": "CODE::agentpm/tests/atlas/test_lm_insights_exports.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-lm-metrics-exports.py",
        "path": "agentpm/tests/atlas/test_lm_metrics_exports.py",
        "title": "CODE::agentpm/tests/atlas/test_lm_metrics_exports.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-lm-status-page-insights.py",
        "path": "agentpm/tests/atlas/test_lm_status_page_insights.py",
        "title": "CODE::agentpm/tests/atlas/test_lm_status_page_insights.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-phase6p-biblescholar-reference-guard.py",
        "path": "agentpm/tests/atlas/test_phase6p_biblescholar_reference_guard.py",
        "title": "CODE::agentpm/tests/atlas/test_phase6p_biblescholar_reference_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/atlas/test-phase-d-autopilot-summary.py",
        "path": "agentpm/tests/atlas/test_phase_d_autopilot_summary.py",
        "title": "CODE::agentpm/tests/atlas/test_phase_d_autopilot_summary.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-phase3b-pmagent-control-pipeline-status-cli.py",
        "path": "agentpm/tests/cli/test_phase3b_pmagent_control_pipeline_status_cli.py",
        "title": "CODE::agentpm/tests/cli/test_phase3b_pmagent_control_pipeline_status_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-phase3b-pmagent-control-schema-cli.py",
        "path": "agentpm/tests/cli/test_phase3b_pmagent_control_schema_cli.py",
        "title": "CODE::agentpm/tests/cli/test_phase3b_pmagent_control_schema_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-phase3b-pmagent-control-status-cli.py",
        "path": "agentpm/tests/cli/test_phase3b_pmagent_control_status_cli.py",
        "title": "CODE::agentpm/tests/cli/test_phase3b_pmagent_control_status_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-phase3b-pmagent-control-summary-cli.py",
        "path": "agentpm/tests/cli/test_phase3b_pmagent_control_summary_cli.py",
        "title": "CODE::agentpm/tests/cli/test_phase3b_pmagent_control_summary_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-phase3b-pmagent-control-tables-cli.py",
        "path": "agentpm/tests/cli/test_phase3b_pmagent_control_tables_cli.py",
        "title": "CODE::agentpm/tests/cli/test_phase3b_pmagent_control_tables_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-phase3b-pmagent-graph-cli.py",
        "path": "agentpm/tests/cli/test_phase3b_pmagent_graph_cli.py",
        "title": "CODE::agentpm/tests/cli/test_phase3b_pmagent_graph_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-phase3b-pmagent-health-cli.py",
        "path": "agentpm/tests/cli/test_phase3b_pmagent_health_cli.py",
        "title": "CODE::agentpm/tests/cli/test_phase3b_pmagent_health_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-health-lm.py",
        "path": "agentpm/tests/cli/test_pmagent_health_lm.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_health_lm.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-lm-router-status.py",
        "path": "agentpm/tests/cli/test_pmagent_lm_router_status.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_lm_router_status.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-plan-kb-fix.py",
        "path": "agentpm/tests/cli/test_pmagent_plan_kb_fix.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_plan_kb_fix.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-plan-kb.py",
        "path": "agentpm/tests/cli/test_pmagent_plan_kb.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_plan_kb.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-plan-next.py",
        "path": "agentpm/tests/cli/test_pmagent_plan_next.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_plan_next.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-reality-check-cli.py",
        "path": "agentpm/tests/cli/test_pmagent_reality_check_cli.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_reality_check_cli.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-report-kb.py",
        "path": "agentpm/tests/cli/test_pmagent_report_kb.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_report_kb.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/cli/test-pmagent-status-kb.py",
        "path": "agentpm/tests/cli/test_pmagent_status_kb.py",
        "title": "CODE::agentpm/tests/cli/test_pmagent_status_kb.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/control-widgets/test-adapter.py",
        "path": "agentpm/tests/control_widgets/test_adapter.py",
        "title": "CODE::agentpm/tests/control_widgets/test_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/control-widgets/test-m2-visualization.py",
        "path": "agentpm/tests/control_widgets/test_m2_visualization.py",
        "title": "CODE::agentpm/tests/control_widgets/test_m2_visualization.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/db/test-phase3a-db-health-guard.py",
        "path": "agentpm/tests/db/test_phase3a_db_health_guard.py",
        "title": "CODE::agentpm/tests/db/test_phase3a_db_health_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/db/test-phase3a-db-health-smoke.py",
        "path": "agentpm/tests/db/test_phase3a_db_health_smoke.py",
        "title": "CODE::agentpm/tests/db/test_phase3a_db_health_smoke.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/db/test-phase3a-db-health-snapshot.py",
        "path": "agentpm/tests/db/test_phase3a_db_health_snapshot.py",
        "title": "CODE::agentpm/tests/db/test_phase3a_db_health_snapshot.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/db/test-phase3a-db-loader.py",
        "path": "agentpm/tests/db/test_phase3a_db_loader.py",
        "title": "CODE::agentpm/tests/db/test_phase3a_db_loader.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/db/test-phase3a-graph-stats-import.py",
        "path": "agentpm/tests/db/test_phase3a_graph_stats_import.py",
        "title": "CODE::agentpm/tests/db/test_phase3a_graph_stats_import.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/db/test-phase3b-graph-overview.py",
        "path": "agentpm/tests/db/test_phase3b_graph_overview.py",
        "title": "CODE::agentpm/tests/db/test_phase3b_graph_overview.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/docs/test-dms-guards.py",
        "path": "agentpm/tests/docs/test_dms_guards.py",
        "title": "CODE::agentpm/tests/docs/test_dms_guards.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/exports/test-graph-export-e20-e22.py",
        "path": "agentpm/tests/exports/test_graph_export_e20_e22.py",
        "title": "CODE::agentpm/tests/exports/test_graph_export_e20_e22.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/extractors/test-extraction-correctness.py",
        "path": "agentpm/tests/extractors/test_extraction_correctness.py",
        "title": "CODE::agentpm/tests/extractors/test_extraction_correctness.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/extractors/test-extraction-determinism-e11-e13.py",
        "path": "agentpm/tests/extractors/test_extraction_determinism_e11_e13.py",
        "title": "CODE::agentpm/tests/extractors/test_extraction_determinism_e11_e13.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/extractors/test-extraction-graph-propagation-e14-e16.py",
        "path": "agentpm/tests/extractors/test_extraction_graph_propagation_e14_e16.py",
        "title": "CODE::agentpm/tests/extractors/test_extraction_graph_propagation_e14_e16.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/extractors/test-extraction-provenance-e06-e10.py",
        "path": "agentpm/tests/extractors/test_extraction_provenance_e06_e10.py",
        "title": "CODE::agentpm/tests/extractors/test_extraction_provenance_e06_e10.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/extractors/test-graph-rollups-e17-e19.py",
        "path": "agentpm/tests/extractors/test_graph_rollups_e17_e19.py",
        "title": "CODE::agentpm/tests/extractors/test_graph_rollups_e17_e19.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/guarded/test-autopilot-adapter.py",
        "path": "agentpm/tests/guarded/test_autopilot_adapter.py",
        "title": "CODE::agentpm/tests/guarded/test_autopilot_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/html/test-lm-status-page.py",
        "path": "agentpm/tests/html/test_lm_status_page.py",
        "title": "CODE::agentpm/tests/html/test_lm_status_page.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/kb/test-freshness.py",
        "path": "agentpm/tests/kb/test_freshness.py",
        "title": "CODE::agentpm/tests/kb/test_freshness.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/kb/test-registry.py",
        "path": "agentpm/tests/kb/test_registry.py",
        "title": "CODE::agentpm/tests/kb/test_registry.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/knowledge/test-kb-ingest-and-export.py",
        "path": "agentpm/tests/knowledge/test_kb_ingest_and_export.py",
        "title": "CODE::agentpm/tests/knowledge/test_kb_ingest_and_export.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/knowledge/test-qa-docs.py",
        "path": "agentpm/tests/knowledge/test_qa_docs.py",
        "title": "CODE::agentpm/tests/knowledge/test_qa_docs.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/lm/test-phase3b-lm-health-guard.py",
        "path": "agentpm/tests/lm/test_phase3b_lm_health_guard.py",
        "title": "CODE::agentpm/tests/lm/test_phase3b_lm_health_guard.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/lm/test-phase6-lm-budgets.py",
        "path": "agentpm/tests/lm/test_phase6_lm_budgets.py",
        "title": "CODE::agentpm/tests/lm/test_phase6_lm_budgets.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/lm/test-phase6-lm-enablement.py",
        "path": "agentpm/tests/lm/test_phase6_lm_enablement.py",
        "title": "CODE::agentpm/tests/lm/test_phase6_lm_enablement.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/lm-widgets/test-adapter.py",
        "path": "agentpm/tests/lm_widgets/test_adapter.py",
        "title": "CODE::agentpm/tests/lm_widgets/test_adapter.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-m2-e21-e25.py",
        "path": "agentpm/tests/mcp/test_m2_e21_e25.py",
        "title": "CODE::agentpm/tests/mcp/test_m2_e21_e25.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-catalog-e01-e05.py",
        "path": "agentpm/tests/mcp/test_mcp_catalog_e01_e05.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_catalog_e01_e05.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m10-e46-e50.py",
        "path": "agentpm/tests/mcp/test_mcp_m10_e46_e50.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m10_e46_e50.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m11-e51-e55.py",
        "path": "agentpm/tests/mcp/test_mcp_m11_e51_e55.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m11_e51_e55.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m12-e56-e60.py",
        "path": "agentpm/tests/mcp/test_mcp_m12_e56_e60.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m12_e56_e60.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m13-e61-e65.py",
        "path": "agentpm/tests/mcp/test_mcp_m13_e61_e65.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m13_e61_e65.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m14-e66-e70.py",
        "path": "agentpm/tests/mcp/test_mcp_m14_e66_e70.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m14_e66_e70.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m2-e06-e10.py",
        "path": "agentpm/tests/mcp/test_mcp_m2_e06_e10.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m2_e06_e10.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m3-e11-e15.py",
        "path": "agentpm/tests/mcp/test_mcp_m3_e11_e15.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m3_e11_e15.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m4-e16-e20.py",
        "path": "agentpm/tests/mcp/test_mcp_m4_e16_e20.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m4_e16_e20.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m5-e21-e25.py",
        "path": "agentpm/tests/mcp/test_mcp_m5_e21_e25.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m5_e21_e25.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m6-e26-e30.py",
        "path": "agentpm/tests/mcp/test_mcp_m6_e26_e30.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m6_e26_e30.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m7-e31-e35.py",
        "path": "agentpm/tests/mcp/test_mcp_m7_e31_e35.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m7_e31_e35.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m8-e36-e40.py",
        "path": "agentpm/tests/mcp/test_mcp_m8_e36_e40.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m8_e36_e40.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/mcp/test-mcp-m9-e41-e45.py",
        "path": "agentpm/tests/mcp/test_mcp_m9_e41_e45.py",
        "title": "CODE::agentpm/tests/mcp/test_mcp_m9_e41_e45.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/phase1/test-tv01-missing-por.py",
        "path": "agentpm/tests/phase1/test_tv01_missing_por.py",
        "title": "CODE::agentpm/tests/phase1/test_tv01_missing_por.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/phase1/test-tv02-arg-schema-invalid.py",
        "path": "agentpm/tests/phase1/test_tv02_arg_schema_invalid.py",
        "title": "CODE::agentpm/tests/phase1/test_tv02_arg_schema_invalid.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/phase1/test-tv03-ring-violation.py",
        "path": "agentpm/tests/phase1/test_tv03_ring_violation.py",
        "title": "CODE::agentpm/tests/phase1/test_tv03_ring_violation.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/phase1/test-tv04-provenance-mismatch.py",
        "path": "agentpm/tests/phase1/test_tv04_provenance_mismatch.py",
        "title": "CODE::agentpm/tests/phase1/test_tv04_provenance_mismatch.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/phase1/test-tv05-forbidden-tool.py",
        "path": "agentpm/tests/phase1/test_tv05_forbidden_tool.py",
        "title": "CODE::agentpm/tests/phase1/test_tv05_forbidden_tool.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/pipelines/test-enrich-nouns-lm-routing.py",
        "path": "agentpm/tests/pipelines/test_enrich_nouns_lm_routing.py",
        "title": "CODE::agentpm/tests/pipelines/test_enrich_nouns_lm_routing.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/reality/test-capability-envelope-validator.py",
        "path": "agentpm/tests/reality/test_capability_envelope_validator.py",
        "title": "CODE::agentpm/tests/reality/test_capability_envelope_validator.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/reality/test-capability-envelope-writer.py",
        "path": "agentpm/tests/reality/test_capability_envelope_writer.py",
        "title": "CODE::agentpm/tests/reality/test_capability_envelope_writer.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/reality/test-reality-check.py",
        "path": "agentpm/tests/reality/test_reality_check.py",
        "title": "CODE::agentpm/tests/reality/test_reality_check.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/reality/test-sessions-summary.py",
        "path": "agentpm/tests/reality/test_sessions_summary.py",
        "title": "CODE::agentpm/tests/reality/test_sessions_summary.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/runtime/test-lm-logging.py",
        "path": "agentpm/tests/runtime/test_lm_logging.py",
        "title": "CODE::agentpm/tests/runtime/test_lm_logging.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/runtime/test-lm-routing.py",
        "path": "agentpm/tests/runtime/test_lm_routing.py",
        "title": "CODE::agentpm/tests/runtime/test_lm_routing.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/runtime/test-pm-snapshot.py",
        "path": "agentpm/tests/runtime/test_pm_snapshot.py",
        "title": "CODE::agentpm/tests/runtime/test_pm_snapshot.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/server/test-autopilot-api.py",
        "path": "agentpm/tests/server/test_autopilot_api.py",
        "title": "CODE::agentpm/tests/server/test_autopilot_api.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/status/test-eval-exports.py",
        "path": "agentpm/tests/status/test_eval_exports.py",
        "title": "CODE::agentpm/tests/status/test_eval_exports.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/status/test-explain-kb.py",
        "path": "agentpm/tests/status/test_explain_kb.py",
        "title": "CODE::agentpm/tests/status/test_explain_kb.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/status/test-kb-hints.py",
        "path": "agentpm/tests/status/test_kb_hints.py",
        "title": "CODE::agentpm/tests/status/test_kb_hints.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/system/test-phase3b-system-health.py",
        "path": "agentpm/tests/system/test_phase3b_system_health.py",
        "title": "CODE::agentpm/tests/system/test_phase3b_system_health.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/test-guarded-calls-tv.py",
        "path": "agentpm/tests/test_guarded_calls_tv.py",
        "title": "CODE::agentpm/tests/test_guarded_calls_tv.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tests/tools/test-system-reality-check.py",
        "path": "agentpm/tests/tools/test_system_reality_check.py",
        "title": "CODE::agentpm/tests/tools/test_system_reality_check.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tools/bible.py",
        "path": "agentpm/tools/bible.py",
        "title": "CODE::agentpm/tools/bible.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tools/embed.py",
        "path": "agentpm/tools/embed.py",
        "title": "CODE::agentpm/tools/embed.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tools/extract.py",
        "path": "agentpm/tools/extract.py",
        "title": "CODE::agentpm/tools/extract.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tools/rerank.py",
        "path": "agentpm/tools/rerank.py",
        "title": "CODE::agentpm/tools/rerank.py",
        "type": "other"
      },
      {
        "id": "code::agentpm/tools/system.py",
        "path": "agentpm/tools/system.py",
        "title": "CODE::agentpm/tools/system.py",
        "type": "other"
      },
      {
        "id": "code::archive/docs/codebase-cleanup/scripts/tmp-patch-samples.py",
        "path": "archive/docs/codebase-cleanup/scripts/tmp_patch_samples.py",
        "title": "CODE::archive/docs/codebase-cleanup/scripts/tmp_patch_samples.py",
        "type": "other"
      },
      {
        "id": "code::archive/-quarantine/p2-scaffold/envelope.py",
        "path": "archive/_quarantine/p2-scaffold/envelope.py",
        "title": "CODE::archive/_quarantine/p2-scaffold/envelope.py",
        "type": "other"
      },
      {
        "id": "code::archive/-quarantine/p2-scaffold/graph.py",
        "path": "archive/_quarantine/p2-scaffold/graph.py",
        "title": "CODE::archive/_quarantine/p2-scaffold/graph.py",
        "type": "other"
      },
      {
        "id": "code::archive/-quarantine/p2-scaffold/nodes.py",
        "path": "archive/_quarantine/p2-scaffold/nodes.py",
        "title": "CODE::archive/_quarantine/p2-scaffold/nodes.py",
        "type": "other"
      },
      {
        "id": "code::archive/run-pipeline.py",
        "path": "archive/run_pipeline.py",
        "title": "CODE::archive/run_pipeline.py",
        "type": "other"
      },
      {
        "id": "code::archive/test-graph.py",
        "path": "archive/test_graph.py",
        "title": "CODE::archive/test_graph.py",
        "type": "other"
      },
      {
        "id": "code::archive/ui-legacy-phase10/scripts/export-noun-index.py",
        "path": "archive/ui_legacy_phase10/scripts/export_noun_index.py",
        "title": "CODE::archive/ui_legacy_phase10/scripts/export_noun_index.py",
        "type": "other"
      },
      {
        "id": "code::conftest.py",
        "path": "conftest.py",
        "title": "CODE::conftest.py",
        "type": "other"
      },
      {
        "id": "code::rules-guard.py",
        "path": "rules_guard.py",
        "title": "CODE::rules_guard.py",
        "type": "other"
      },
      {
        "id": "code::test-bi-encoder-rerank.py",
        "path": "test_bi_encoder_rerank.py",
        "title": "CODE::test_bi_encoder_rerank.py",
        "type": "other"
      },
      {
        "id": "code::test-mcp-server.py",
        "path": "test_mcp_server.py",
        "title": "CODE::test_mcp_server.py",
        "type": "other"
      },
      {
        "id": "runbook::docs/runbooks/cpu-performance-fix.md",
        "path": "docs/runbooks/CPU_PERFORMANCE_FIX.md",
        "title": "RUNBOOK::docs/runbooks/CPU_PERFORMANCE_FIX.md",
        "type": "runbook"
      },
      {
        "id": "runbook::docs/runbooks/system-optimization-ai.md",
        "path": "docs/runbooks/SYSTEM_OPTIMIZATION_AI.md",
        "title": "RUNBOOK::docs/runbooks/SYSTEM_OPTIMIZATION_AI.md",
        "type": "runbook"
      }
    ],
    "out_of_sync_docs": []
  }
}

```

### status_explain

```json
{
  "level": "OK",
  "headline": "All systems nominal",
  "details": "Everything looks good with the system right now! The database is fully ready and working properly. All four language model slots (local_agent, embedding, reranker, theology) are active and functioning as expected. So overall, everything is running smoothly without any issues detected.",
  "documentation": {
    "available": true,
    "total": 1185,
    "by_subsystem": {
      "ops": 555,
      "gematria": 38,
      "pm": 227,
      "general": 227,
      "docs": 5,
      "root": 48,
      "webui": 51,
      "biblescholar": 34
    },
    "by_type": {
      "other": 1023,
      "ssot": 129,
      "runbook": 33
    },
    "hints": [
      {
        "level": "WARN",
        "code": "KB_MISSING_DOCS",
        "message": "KB registry references 316 missing file(s)",
        "missing_count": 316,
        "missing_files": [
          "agentpm/adapters/AGENTS.md (ID",
          "agentpm/AGENTS.md (ID",
          "agentpm/ai_docs/AGENTS.md (ID",
          "agentpm/atlas/AGENTS.md (ID",
          "agentpm/biblescholar/AGENTS.md (ID",
          "agentpm/biblescholar/tests/AGENTS.md (ID",
          "agentpm/bus/AGENTS.md (ID",
          "agentpm/control_plane/AGENTS.md (ID",
          "agentpm/control_widgets/AGENTS.md (ID",
          "agentpm/db/AGENTS.md (ID"
        ]
      },
      {
        "level": "WARN",
        "code": "KB_VALIDATION_ISSUES",
        "message": "KB registry validation issue: Registry validation failed: 318 errors"
      },
      {
        "level": "WARN",
        "code": "KB_VALIDATION_ISSUES",
        "message": "KB registry validation issue: Registry has 3 warnings"
      },
      {
        "level": "WARN",
        "code": "KB_DOC_STALE",
        "message": "9 document(s) are stale (exceed refresh interval)",
        "stale_count": 9,
        "stale_docs": [
          {
            "id": "ssot::docs/ssot/data-flow-visual.md",
            "path": "docs/SSOT/data_flow_visual.md",
            "title": "SSOT::docs/SSOT/data_flow_visual.md"
          },
          {
            "id": "ssot::docs/ssot/epoch-ledger.md",
            "path": "docs/SSOT/EPOCH_LEDGER.md",
            "title": "SSOT::docs/SSOT/EPOCH_LEDGER.md"
          },
          {
            "id": "ssot::docs/ssot/graph-metrics-api.md",
            "path": "docs/SSOT/graph-metrics-api.md",
            "title": "SSOT::docs/SSOT/graph-metrics-api.md"
          },
          {
            "id": "ssot::docs/ssot/graph-stats-api.md",
            "path": "docs/SSOT/graph-stats-api.md",
            "title": "SSOT::docs/SSOT/graph-stats-api.md"
          },
          {
            "id": "ssot::docs/ssot/jsonld-schema.md",
            "path": "docs/SSOT/jsonld-schema.md",
            "title": "SSOT::docs/SSOT/jsonld-schema.md"
          }
        ]
      }
    ],
    "key_docs": [
      {
        "id": "master-plan",
        "title": "MASTER_PLAN",
        "path": "MASTER_PLAN.md",
        "type": "ssot"
      },
      {
        "id": "rules-index",
        "title": "RULES_INDEX",
        "path": "RULES_INDEX.md",
        "type": "ssot"
      },
      {
        "id": "ssot::docs/ssot/agentpm-gematria-module-plan.md",
        "title": "SSOT::docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md",
        "path": "docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md",
        "type": "ssot"
      }
    ],
    "freshness": {
      "total": 1185,
      "stale_count": 9,
      "missing_count": 316,
      "out_of_sync_count": 0,
      "fresh_count": 860
    }
  }
}

```

### health_system

```json
{
  "ok": true,
  "db": {
    "ok": true,
    "mode": "ready",
    "checks": {
      "driver_available": true,
      "connection_ok": true,
      "graph_stats_ready": true
    },
    "details": {
      "errors": []
    }
  },
  "lm": {
    "ok": true,
    "mode": "lm_ready",
    "details": {
      "endpoint": "http://127.0.0.1:9994/v1",
      "provider": "lmstudio",
      "errors": []
    }
  },
  "graph": {
    "ok": true,
    "mode": "db_on",
    "stats": {
      "nodes": null,
      "edges": null,
      "avg_degree": null,
      "snapshot_count": null,
      "last_import_at": null
    },
    "reason": "no snapshots found"
  },
  "system": {
    "ok": true,
    "components": {
      "db": {
        "ok": true,
        "mode": "ready",
        "checks": {
          "driver_available": true,
          "connection_ok": true,
          "graph_stats_ready": true
        },
        "details": {
          "errors": []
        }
      },
      "lm": {
        "ok": true,
        "mode": "lm_ready",
        "details": {
          "endpoint": "http://127.0.0.1:9994/v1",
          "provider": "lmstudio",
          "errors": []
        }
      },
      "graph": {
        "ok": true,
        "mode": "db_on",
        "stats": {
          "nodes": null,
          "edges": null,
          "avg_degree": null,
          "snapshot_count": null,
          "last_import_at": null
        },
        "reason": "no snapshots found"
      }
    }
  }
}

```

### reality_check_hint

```json
{
  "command": "reality.check",
  "mode": "HINT",
  "timestamp": "2025-12-07T19:20:05.411735+00:00",
  "env": {
    "ok": true,
    "dsn_ok": true,
    "details": {
      "dsns": {
        "rw": true,
        "ro": true,
        "bible": true
      }
    }
  },
  "db": {
    "ok": true,
    "control_schema": "control",
    "tables_expected": 0,
    "tables_present": 0,
    "generated_at": "2025-12-07T19:20:05.411755+00:00",
    "components": {
      "status": {
        "ok": true,
        "mode": "ready",
        "reason": null,
        "tables": {
          "public.ai_interactions": {
            "present": true,
            "row_count": 1,
            "latest_created_at": "2025-11-07T11:11:49.732991-08:00"
          },
          "public.governance_artifacts": {
            "present": true,
            "row_count": 134,
            "latest_created_at": "2025-12-07T09:56:28.527430-08:00"
          },
          "control.agent_run": {
            "present": true,
            "row_count": 2270,
            "latest_created_at": "2025-11-30T09:02:28.655100-08:00"
          },
          "control.agent_run_cli": {
            "present": true,
            "row_count": 143,
            "latest_created_at": "2025-12-07T11:20:05.398287-08:00"
          },
          "control.kb_document": {
            "present": true,
            "row_count": 4238,
            "latest_created_at": "2025-11-27T10:39:03.026669-08:00"
          },
          "control.doc_registry": {
            "present": true,
            "row_count": 1203,
            "latest_created_at": "2025-12-07T10:46:19.978008-08:00"
          },
          "control.doc_version": {
            "present": true,
            "row_count": 8808,
            "latest_created_at": null
          },
          "control.tool_catalog": {
            "present": true,
            "row_count": 7,
            "latest_created_at": "2025-11-26T09:05:34.616631-08:00"
          },
          "gematria.graph_stats_snapshots": {
            "present": true,
            "row_count": 0,
            "latest_created_at": null
          }
        }
      },
      "tables": {
        "ok": true,
        "mode": "db_on",
        "error": null,
        "tables": {
          "control.agent_run": 2270,
          "control.agent_run_cli": 143,
          "control.capability_rule": 5,
          "control.capability_session": 5,
          "control.doc_embedding": 245898,
          "control.doc_fragment": 245903,
          "control.doc_registry": 1203,
          "control.doc_sync_state": 0,
          "control.doc_version": 8808,
          "control.guard_definition": 0,
          "control.hint_registry": 25,
          "control.kb_document": 4238,
          "control.rule_definition": 69,
          "control.rule_source": 138,
          "control.system_state_ledger": 462,
          "control.tool_catalog": 7,
          "gematria.ai_embeddings": 1,
          "gematria.checkpoints": 4,
          "gematria.concept_centrality": 0,
          "gematria.concept_relations": 0,
          "gematria.concepts": 0,
          "gematria.edges": 1,
          "gematria.enrichment_crossrefs": 0,
          "gematria.graph_stats_snapshots": 0,
          "gematria.nodes": 2,
          "gematria.nouns": 0,
          "gematria.runs": 2,
          "gematria.runs_ledger": 115,
          "gematria.schema_migrations": 2,
          "gematria.word_cache": 0,
          "mcp.endpoints": 10,
          "mcp.logs": 0,
          "mcp.tools": 6,
          "ops.job_queue": 0,
          "public.ai_enrichment_log": 13857,
          "public.ai_interactions": 1,
          "public.ai_performance_insights": 0,
          "public.books": 35,
          "public.checkpointer_state": 64,
          "public.checkpointer_writes": 2,
          "public.checkpoints": 22,
          "public.cluster_metrics": 0,
          "public.code_generation_events": 0,
          "public.code_generation_patterns": 0,
          "public.concept_centrality": 0,
          "public.concept_clusters": 1,
          "public.concept_metadata": 4399,
          "public.concept_metrics": 0,
          "public.concept_network": 4399,
          "public.concept_relations": 14330,
          "public.concept_rerank_cache": 0,
          "public.concepts": 4399,
          "public.confidence_validation_log": 35,
          "public.connections": 0,
          "public.context_awareness_events": 0,
          "public.context_success_patterns": 0,
          "public.cross_references": 0,
          "public.doctrinal_links": 0,
          "public.document_access_log": 1,
          "public.document_sections": 398,
          "public.governance_artifacts": 134,
          "public.governance_compliance_log": 243,
          "public.hint_emissions": 818,
          "public.hypotheses": 0,
          "public.integration_log": 0,
          "public.isolation_patterns": 0,
          "public.learning_events": 2,
          "public.metrics_log": 7969,
          "public.model_performance_metrics": 0,
          "public.network_metrics": 0,
          "public.pattern_occurrences": 9,
          "public.patterns": 9,
          "public.prime_factors": 0,
          "public.qwen_health_log": 15,
          "public.runs": 25,
          "public.satisfaction_metrics": 0,
          "public.share_manifest_items": 40,
          "public.share_manifest_metadata": 1,
          "public.tool_usage_analytics": 0,
          "public.twin_patterns": 0,
          "public.user_feedback": 0,
          "public.verse_noun_occurrences": 116960,
          "staging.concept_metadata_norm": 0,
          "staging.concept_relations_norm": 1855,
          "staging.concepts_norm": 710,
          "telemetry.ai_interactions": 0,
          "telemetry.checkpointer_state": 0,
          "telemetry.metrics_log": 0
        }
      },
      "schema": {
        "ok": true,
        "mode": "db_on",
        "reason": null,
        "tables": {
          "control.agent_run": {
            "columns": [
              {
                "name": "id",
                "data_type": "uuid",
                "is_nullable": false,
                "default": "gen_random_uuid()"
              },
              {
                "name": "project_id",
                "data_type": "bigint",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "session_id",
                "data_type": "uuid",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "tool",
                "data_type": "text",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "args_json",
                "data_type": "jsonb",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "result_json",
                "data_type": "jsonb",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "violations_json",
                "data_type": "jsonb",
                "is_nullable": false,
                "default": "'[]'::jsonb"
              },
              {
                "name": "created_at",
                "data_type": "timestamp with time zone",
                "is_nullable": false,
                "default": "now()"
              }
            ],
            "primary_key": [
              "id"
            ],
            "indexes": [
              {
                "name": "idx_agent_run_created",
                "columns": [
                  "created_at"
                ],
                "unique": false
              },
              {
                "name": "idx_agent_run_project",
                "columns": [
                  "project_id"
                ],
                "unique": false
              },
              {
                "name": "idx_agent_run_session",
                "columns": [
                  "session_id"
                ],
                "unique": false
              },
              {
                "name": "idx_agent_run_tool",
                "columns": [
                  "tool"
                ],
                "unique": false
              },
              {
                "name": "idx_agent_run_violations",
                "columns": [
                  "violations_json"
                ],
                "unique": false
              }
            ]
          },
          "control.tool_catalog": {
            "columns": [
              {
                "name": "id",
                "data_type": "uuid",
                "is_nullable": false,
                "default": "gen_random_uuid()"
              },
              {
                "name": "project_id",
                "data_type": "bigint",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "name",
                "data_type": "text",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "ring",
                "data_type": "integer",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "io_schema",
                "data_type": "jsonb",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "enabled",
                "data_type": "boolean",
                "is_nullable": false,
                "default": "true"
              },
              {
                "name": "created_at",
                "data_type": "timestamp with time zone",
                "is_nullable": false,
                "default": "now()"
              }
            ],
            "primary_key": [
              "id"
            ],
            "indexes": [
              {
                "name": "idx_tool_catalog_enabled",
                "columns": [
                  "enabled"
                ],
                "unique": false
              },
              {
                "name": "idx_tool_catalog_project",
                "columns": [
                  "project_id"
                ],
                "unique": false
              },
              {
                "name": "idx_tool_catalog_ring",
                "columns": [
                  "ring"
                ],
                "unique": false
              },
              {
                "name": "tool_catalog_project_id_name_key",
                "columns": [
                  "project_id",
                  "name"
                ],
                "unique": true
              }
            ]
          },
          "control.capability_rule": {
            "columns": [
              {
                "name": "id",
                "data_type": "uuid",
                "is_nullable": false,
                "default": "gen_random_uuid()"
              },
              {
                "name": "project_id",
                "data_type": "bigint",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "name",
                "data_type": "text",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "ring",
                "data_type": "integer",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "allowlist",
                "data_type": "ARRAY",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "denylist",
                "data_type": "ARRAY",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "budgets",
                "data_type": "jsonb",
                "is_nullable": false,
                "default": "'{}'::jsonb"
              },
              {
                "name": "created_at",
                "data_type": "timestamp with time zone",
                "is_nullable": false,
                "default": "now()"
              }
            ],
            "primary_key": [
              "id"
            ],
            "indexes": [
              {
                "name": "capability_rule_project_id_name_key",
                "columns": [
                  "project_id",
                  "name"
                ],
                "unique": true
              },
              {
                "name": "idx_capability_rule_project",
                "columns": [
                  "project_id"
                ],
                "unique": false
              },
              {
                "name": "idx_capability_rule_ring",
                "columns": [
                  "ring"
                ],
                "unique": false
              }
            ]
          },
          "control.doc_fragment": {
            "columns": [
              {
                "name": "id",
                "data_type": "uuid",
                "is_nullable": false,
                "default": "gen_random_uuid()"
              },
              {
                "name": "project_id",
                "data_type": "bigint",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "src",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "anchor",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "sha256",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "created_at",
                "data_type": "timestamp with time zone",
                "is_nullable": false,
                "default": "now()"
              },
              {
                "name": "doc_id",
                "data_type": "uuid",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "version_id",
                "data_type": "bigint",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "fragment_index",
                "data_type": "integer",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "fragment_type",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "content",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "updated_at",
                "data_type": "timestamp with time zone",
                "is_nullable": true,
                "default": "now()"
              },
              {
                "name": "meta",
                "data_type": "jsonb",
                "is_nullable": true,
                "default": "'{}'::jsonb"
              },
              {
                "name": "content_tsvector",
                "data_type": "tsvector",
                "is_nullable": true,
                "default": null
              }
            ],
            "primary_key": [
              "id"
            ],
            "indexes": [
              {
                "name": "doc_fragment_project_id_src_anchor_key",
                "columns": [
                  "project_id",
                  "src",
                  "anchor"
                ],
                "unique": true
              },
              {
                "name": "idx_doc_fragment_content_tsvector",
                "columns": [
                  "content_tsvector"
                ],
                "unique": false
              },
              {
                "name": "idx_doc_fragment_content_unique",
                "columns": [
                  "doc_id",
                  "version_id",
                  "fragment_index"
                ],
                "unique": true
              },
              {
                "name": "idx_doc_fragment_doc_id",
                "columns": [
                  "doc_id"
                ],
                "unique": false
              },
              {
                "name": "idx_doc_fragment_meta",
                "columns": [
                  "meta"
                ],
                "unique": false
              },
              {
                "name": "idx_doc_fragment_project",
                "columns": [
                  "project_id"
                ],
                "unique": false
              },
              {
                "name": "idx_doc_fragment_sha256",
                "columns": [
                  "sha256"
                ],
                "unique": false
              },
              {
                "name": "idx_doc_fragment_src",
                "columns": [
                  "src"
                ],
                "unique": false
              },
              {
                "name": "idx_doc_fragment_type",
                "columns": [
                  "fragment_type"
                ],
                "unique": false
              },
              {
                "name": "idx_doc_fragment_version_id",
                "columns": [
                  "version_id"
                ],
                "unique": false
              }
            ]
          },
          "control.capability_session": {
            "columns": [
              {
                "name": "id",
                "data_type": "uuid",
                "is_nullable": false,
                "default": "gen_random_uuid()"
              },
              {
                "name": "project_id",
                "data_type": "bigint",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "rule_id",
                "data_type": "uuid",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "por_json",
                "data_type": "jsonb",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "tiny_menu",
                "data_type": "ARRAY",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "ttl_s",
                "data_type": "integer",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "created_at",
                "data_type": "timestamp with time zone",
                "is_nullable": false,
                "default": "now()"
              }
            ],
            "primary_key": [
              "id"
            ],
            "indexes": [
              {
                "name": "idx_capability_session_created",
                "columns": [
                  "created_at"
                ],
                "unique": false
              },
              {
                "name": "idx_capability_session_project",
                "columns": [
                  "project_id"
                ],
                "unique": false
              },
              {
                "name": "idx_capability_session_rule",
                "columns": [
                  "rule_id"
                ],
                "unique": false
              }
            ]
          },
          "public.ai_interactions": {
            "columns": [
              {
                "name": "id",
                "data_type": "integer",
                "is_nullable": false,
                "default": "nextval('ai_interactions_id_seq'::regclass)"
              },
              {
                "name": "session_id",
                "data_type": "character varying",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "interaction_type",
                "data_type": "character varying",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "user_query",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "ai_response",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "tools_used",
                "data_type": "ARRAY",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "context_provided",
                "data_type": "jsonb",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "execution_time_ms",
                "data_type": "integer",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "success",
                "data_type": "boolean",
                "is_nullable": true,
                "default": "true"
              },
              {
                "name": "error_details",
                "data_type": "text",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "created_at",
                "data_type": "timestamp with time zone",
                "is_nullable": true,
                "default": "now()"
              }
            ],
            "primary_key": [
              "id"
            ],
            "indexes": [
              {
                "name": "idx_ai_interactions_created",
                "columns": [
                  "created_at"
                ],
                "unique": false
              },
              {
                "name": "idx_ai_interactions_session",
                "columns": [
                  "session_id"
                ],
                "unique": false
              },
              {
                "name": "idx_ai_interactions_type",
                "columns": [
                  "interaction_type"
                ],
                "unique": false
              }
            ]
          },
          "public.governance_artifacts": {
            "columns": [
              {
                "name": "id",
                "data_type": "integer",
                "is_nullable": false,
                "default": "nextval('governance_artifacts_id_seq'::regclass)"
              },
              {
                "name": "artifact_type",
                "data_type": "character varying",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "artifact_name",
                "data_type": "character varying",
                "is_nullable": false,
                "default": null
              },
              {
                "name": "file_path",
                "data_type": "character varying",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "rule_references",
                "data_type": "ARRAY",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "agent_references",
                "data_type": "ARRAY",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "last_updated",
                "data_type": "timestamp with time zone",
                "is_nullable": true,
                "default": "now()"
              },
              {
                "name": "checksum",
                "data_type": "character varying",
                "is_nullable": true,
                "default": null
              },
              {
                "name": "validation_status",
                "data_type": "character varying",
                "is_nullable": true,
                "default": "'pending'::character varying"
              },
              {
                "name": "created_at",
                "data_type": "timestamp with time zone",
                "is_nullable": true,
                "default": "now()"
              },
              {
                "name": "updated_at",
                "data_type": "timestamp with time zone",
                "is_nullable": true,
                "default": "now()"
              }
            ],
            "primary_key": [
              "id"
            ],
            "indexes": [
              {
                "name": "governance_artifacts_artifact_type_artifact_name_key",
                "columns": [
                  "artifact_type",
                  "artifact_name"
                ],
                "unique": true
              },
              {
                "name": "idx_governance_agent_refs",
                "columns": [
                  "agent_references"
                ],
                "unique": false
              },
              {
                "name": "idx_governance_rule_refs",
                "columns": [
                  "rule_references"
                ],
                "unique": false
              },
              {
                "name": "idx_governance_type",
                "columns": [
                  "artifact_type"
                ],
                "unique": false
              }
            ]
          }
        }
      },
      "pipeline_status": {
        "ok": true,
        "mode": "db_on",
        "reason": null,
        "window_hours": 24,
        "summary": {
          "total_runs": 0,
          "pipelines": {}
        }
      }
    }
  },
  "lm": {
    "ok": true,
    "provider": "unknown",
    "slots": [
      {
        "slot": "local_agent",
        "provider": "lmstudio",
        "model": "ibm/granite-4-h-tiny",
        "service_status": "OK"
      },
      {
        "slot": "embedding",
        "provider": "lmstudio",
        "model": "text-embedding-bge-m3",
        "service_status": "OK"
      },
      {
        "slot": "reranker",
        "provider": "lmstudio",
        "model": "ibm/granite-4-h-tiny (embedding_only)",
        "service_status": "OK"
      },
      {
        "slot": "theology",
        "provider": "lmstudio",
        "model": "christian-bible-expert-v2.0-12b",
        "service_status": "OK"
      }
    ],
    "mode": "lm_ready",
    "details": {
      "endpoint": "http://127.0.0.1:9994/v1",
      "provider": "lmstudio",
      "errors": []
    }
  },
  "exports": {
    "ok": true,
    "lm_indicator": {
      "status": "unknown",
      "lm_available": true,
      "note": "Recreated after share/ disaster; regenerate from LM health scripts when available."
    },
    "compliance_head": null,
    "kb_docs_head": null,
    "mcp_catalog": null
  },
  "eval_smoke": {
    "ok": true,
    "targets": [
      "ci.exports.smoke",
      "eval.graph.calibrate.adv"
    ],
    "messages": [
      "ci.exports.smoke: OK",
      "eval.graph.calibrate.adv: OK"
    ]
  },
  "hints": [
    "DMS-REQUIRED: reality.green STRICT must pass all required checks before declaring system ready.",
    "KB: KB registry references 316 missing file(s)",
    "KB: KB registry validation issue: Registry validation failed: 318 errors",
    "KB: KB registry validation issue: Registry has 3 warnings",
    "KB: 9 document(s) are stale (exceed refresh interval)",
    "KB: Doc freshness: 9 stale, 0 out-of-sync"
  ],
  "kb_hints": [
    {
      "level": "WARN",
      "code": "KB_MISSING_DOCS",
      "message": "KB registry references 316 missing file(s)",
      "missing_count": 316,
      "missing_files": [
        "agentpm/adapters/AGENTS.md (ID",
        "agentpm/AGENTS.md (ID",
        "agentpm/ai_docs/AGENTS.md (ID",
        "agentpm/atlas/AGENTS.md (ID",
        "agentpm/biblescholar/AGENTS.md (ID",
        "agentpm/biblescholar/tests/AGENTS.md (ID",
        "agentpm/bus/AGENTS.md (ID",
        "agentpm/control_plane/AGENTS.md (ID",
        "agentpm/control_widgets/AGENTS.md (ID",
        "agentpm/db/AGENTS.md (ID"
      ]
    },
    {
      "level": "WARN",
      "code": "KB_VALIDATION_ISSUES",
      "message": "KB registry validation issue: Registry validation failed: 318 errors"
    },
    {
      "level": "WARN",
      "code": "KB_VALIDATION_ISSUES",
      "message": "KB registry validation issue: Registry has 3 warnings"
    },
    {
      "level": "WARN",
      "code": "KB_DOC_STALE",
      "message": "9 document(s) are stale (exceed refresh interval)",
      "stale_count": 9,
      "stale_docs": [
        {
          "id": "ssot::docs/ssot/data-flow-visual.md",
          "path": "docs/SSOT/data_flow_visual.md",
          "title": "SSOT::docs/SSOT/data_flow_visual.md"
        },
        {
          "id": "ssot::docs/ssot/epoch-ledger.md",
          "path": "docs/SSOT/EPOCH_LEDGER.md",
          "title": "SSOT::docs/SSOT/EPOCH_LEDGER.md"
        },
        {
          "id": "ssot::docs/ssot/graph-metrics-api.md",
          "path": "docs/SSOT/graph-metrics-api.md",
          "title": "SSOT::docs/SSOT/graph-metrics-api.md"
        },
        {
          "id": "ssot::docs/ssot/graph-stats-api.md",
          "path": "docs/SSOT/graph-stats-api.md",
          "title": "SSOT::docs/SSOT/graph-stats-api.md"
        },
        {
          "id": "ssot::docs/ssot/jsonld-schema.md",
          "path": "docs/SSOT/jsonld-schema.md",
          "title": "SSOT::docs/SSOT/jsonld-schema.md"
        }
      ]
    }
  ],
  "overall_ok": true,
  "required_hints": [
    {
      "logical_name": "reality.green.required_checks",
      "injection_mode": "PRE_PROMPT",
      "payload": {
        "text": "reality.green STRICT must pass all required checks before declaring system ready.",
        "commands": [
          "make reality.green STRICT"
        ],
        "metadata": {
          "source": "Rule-050",
          "section": "5"
        },
        "constraints": {
          "rule_ref": "050",
          "required_before": "PR"
        }
      },
      "priority": 10
    }
  ],
  "suggested_hints": []
}

```

## 5. AGENTS docs (core and samples)

### AGENTS.md_head

```
# AGENTS.md — Gemantria Agent Framework
<!-- alwaysapply.sentinel: 050,051,052 source=ai_interactions -->

> **AGENT REGISTRY ROLE: CANONICAL_GLOBAL**  
> Source of truth for the Gemantria agent roster (IDs, roles, subsystems, tools, workflows, governance).  
> Derived views: `pmagent/kb/AGENTS.md` (PM-focused), `pmagent/tests/*/AGENTS.md` (test-specific), other subsystem-specific summaries.  
> Last reviewed: 2025-12-03

> **Always-Apply Triad**: We operate under **Rule-050 (LOUD FAIL)**, **Rule-051 (CI gating)**, and **Rule-052 (tool-priority)**. The guards ensure this 050/051/052 triad is present in docs and mirrored in DB checks.

## Doc Strategy & DMS Hierarchy (Gemantria-Specific)

**Architecture Clarification:**

pmagent is the governance and control-plane engine for the Gemantria project.
All documentation lifecycle, classification, metadata, and structural enforcement
are handled by pmagent's control-plane DMS (`control.doc_registry`).
Gemantria is the domain project being governed, not the system performing
the governance. AGENTS.md surfaces define the agent-facing worldview of both
Gemantria and pmagent; the DMS records that worldview in structured form.

In Gemantria, documentation and metadata are layered. The hierarchy for truth is:

1. **Orchestrator (human)** — ultimate source of product and governance intent.

2. **Contracts & SSOT docs** (`docs/SSOT/**`, PHASE index docs, OPS/PM contracts).

3. **AGENTS surfaces** (`AGENTS.md` at root and subsystem levels) — canonical map of agents, tools, and doc surfaces.

4. **pmagent control-plane DMS** (`control.doc_registry` in Postgres) — structured inventory and lifecycle metadata for docs (paths, importance, tags, owner_component, enabled/archived), which must reflect (not override) the above.

5. **Filesystem layout** — implementation detail that must be kept in sync with the registry.

**AGENTS.md is privileged:**

- Root `AGENTS.md` is the **global agent registry** (`CANONICAL_GLOBAL`) and must never be archived or demoted.

- Subsystem-level `AGENTS.md` files are local views that inherit from this global registry.

- Any automated doc lifecycle (archive/cleanup/moves) must treat `AGENTS.md` as **core SSOT**, not as regular documentation.

**pmagent control-plane DMS responsibilities:**

- Tracks **which docs exist**, where they live (`repo_path`), their lifecycle (`enabled`, archive path), and their metadata (`importance`, `tags`, `owner_component`).

- Must not propose or apply moves that contradict the AGENTS contract (e.g., archiving `AGENTS.md`).

- Housekeeping scripts (`scripts/governance/ingest_docs_to_db.py` and related) populate the pmagent control-plane DMS with `importance`, `tags`, and `owner_component` but **never downgrade AGENTS docs**.

In short: **AGENTS.md defines the world; the pmagent control-plane DMS records and enforces that definition.**

## Canonical Agents Table (Draft from KB Registry)

The following table was generated from **share/AGENTS_REGISTRY_SNAPSHOT.json** to reflect the currently registered agents in the pmagent control-plane DMS.

<!-- BEGIN: AUTO-GENERATED AGENTS TABLE -->
| Agent ID | Path | Subsystem | Tags |
|----------|------|-----------|------|
| agents::agentpm/kb/agents.md | agentpm/kb/AGENTS.md | ops | ssot, agent_framework |
| agents::agentpm/knowledge/agents.md | agentpm/knowledge/AGENTS.md | ops | ssot, agent_framework |
| agents::agentpm/metrics/agents.md | agentpm/metrics/AGENTS.md | ops | ssot, agent_framework |
| agents::agentpm/rpc/agents.md | agentpm/rpc/AGENTS.md | ops | ssot, agent_framework |
| agents::agentpm/tests/kb/agents.md | agentpm/tests/kb/AGENTS.md | general | ssot, agent_framework |
| agents::agentpm/tests/status/agents.md | agentpm/tests/status/AGENTS.md | ops | ssot, agent_framework |
| agents::docs/audits/agents.md | docs/audits/AGENTS.md | ops | ssot, agent_framework |
| agents::src/gemantria.egg-info/agents.md | src/gemantria.egg-info/AGENTS.md | gematria | ssot, agent_framework |
<!-- END: AUTO-GENERATED AGENTS TABLE -->

## Directory Purpose

The root `AGENTS.md` serves as the primary agent framework documentation for the Gemantria repository, defining mission, priorities, environment, workflows, and governance for all agentic operations across the codebase.

## Mission
Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts.

## Priorities
1) Correctness: **Code gematria > bible_db > LLM (LLM = metadata only)**.
2) Determinism: content_hash identity; uuidv7 surrogate; fixed seeds; position_index.
3) Safety: **bible_db is READ-ONLY**; parameterized SQL only; **fail-closed if <50 nouns** (ALLOW_PARTIAL=1 is explicit).
- **pmagent control-plane DMS Lifecycle Policy**:
    - **Exclusive SSOT**: `control.doc_registry` (pmagent control-plane DMS) is the ONLY authority for document existence and status.
    - **Lifecycle**: `importance` and `enabled` columns determine if a doc is Core, Helpful, or Archived.
    - **Pathing**: Filesystem locations must reflect pmagent control-plane DMS `repo_path`.

## pmagent Status

See `docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md` for current vs intended state of pmagent commands and capabilities.

See `docs/SSOT/PMAGENT_REALITY_CHECK_DESIGN.md` for reality.check implementation design and validation schema.

## PM DMS Integration (Rule-053) ⭐ NEW

**Phase 9.1**: PM must query **pmagent control-plane DMS (Postgres `control.doc_registry`)** BEFORE file searching.

**DMS-First Workflow**:
1. **Documentation**: `pmagent kb registry by-subsystem --owning-subsystem=<project>`
2. **Tool Catalog**: `SELECT * FROM control.mcp_tool_catalog WHERE tags @> '{<project>}'`
3. **Project Status**: `pmagent status kb` and `pmagent plan kb list`
4. **File Search** (LAST RESORT): Only if content not in DMS

**Feature Registration**:
- After building new tool/module: Create MCP envelope → `make mcp.ingest` → Update KB registry
- PM learns capabilities automatically through DMS registration
- **Goal**: PM and project develop together

See `.cursor/rules/053-pm-dms-integration.mdc` and `docs/SSOT/PM_CONTRACT.md` Section 2.6 for full workflow.

## Environment
- venv: `python -m venv .venv && source .venv/bin/activate`
- install: `make deps`
- Databases:
  - `BIBLE_DB_DSN` — read-only Bible database (RO adapter denies writes pre-connection)
  - `GEMATRIA_DSN` — read/write application database
- **DSN Access**: All DSN access must go through centralized loaders:
  - **Preferred**: `scripts.config.env` (`get_rw_dsn()`, `get_ro_dsn()`, `get_bible_db_dsn()`)
  - **Legacy**: `src.gemantria.dsn` (`dsn_rw()`, `dsn_ro()`, `dsn_atlas()`)
  - Never use `os.getenv("GEMATRIA_DSN")` directly - enforced by `guard.dsn.centralized`

### 3-Role DB Contract (OPS v6.2.3)
**Extraction DB**: `GEMATRIA_DSN` → database `gematria`  
**SSOT DB**: `BIBLE_DB_DSN` → database `bible_db` (read-only)  
**AI Tracking**: **lives in `gematria` DB**, `public` schema; `AI_AUTOMATION_DSN` **must equal** `GEMATRIA_DSN`.  
Guards: `guard.rules.alwaysapply.dbmirror` (triad), `guard.ai.tracking` (tables `public.ai_interactions`, `public.governance_artifacts`).  
CI posture: HINT on PRs; STRICT on tags behind `vars.STRICT_DB_MIRROR_CI == '1'`.
- Batch & overrides:
  - `BATCH_SIZE=50` (default noun batch size)
  - `ALLOW_PARTIAL=0|1` (if 1, manifest must capture reason)
  - `PARTIAL_REASON=<string>` (required when ALLOW_PARTIAL=1)
- Checkpointer: `CHECKPOINTER=postgres|memory` (default: memory for CI/dev)
- LLM: Local inference providers (LM Studio or Ollama) when enabled; confidence is metadata only.
  - **Inference Providers** (Phase-7E): Supports both LM Studio and Ollama via `INFERENCE_PROVIDER`:
    - `lmstudio`: OpenAI-compatible API (`OPENAI_BASE_URL`) - **Granite models available in LM Studio**
    - `ollama`: Native HTTP API (`OLLAMA_BASE_URL`) - **Granite models also available via Ollama**
  - **Setup**: See `docs/runbooks/LM_STUDIO_SETUP.md` for LM Studio setup or `docs/runbooks/OLLAMA_ALTERNATIVE.md` for Ollama
  - **Quick Start (LM Studio)**: Set `INFERENCE_PROVIDER=lmstudio`, `LM_STUDIO_ENABLED=1`, `OPENAI_BASE_URL=http://127.0.0.1:9994/v1`
  - **Quick Start (Ollama)**: Set `INFERENCE_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://127.0.0.1:11434`, then `ollama pull ibm/granite4.0-preview:tiny`
  - **Health Check**: `pmagent health lm` verifies inference provider availability
  - **Default Models (Phase-7F)**: 
    - **Default stack**: Granite embedding + Granite reranker + Granite local agent.
      - `LOCAL_AGENT_MODEL=granite4:tiny-h` (Ollama)
      - `EMBEDDING_MODEL=granite-embedding:278m` (Granite)
      - `RERANKER_MODEL=granite4:tiny-h` (Granite)
    - **Bible lane**: BGE embedding + theology model; BGE is not the general default.
      - `BIBLE_EMBEDDING_MODEL=bge-m3:latest` (Ollama: `qllama/bge-m3`) - for Bible/multilingual tasks only
    - **Qwen reranker**: fallback only, not the primary reranker.
    - `THEOLOGY_MODEL=Christian-Bible-Expert-v2.0-12B` (via theology adapter)
  - **Retrieval Profile (Phase-7C)**: `RETRIEVAL_PROFILE=DEFAULT` (default) uses Granite stack. Setting `RETRIEVAL_PROFILE=GRANITE` or `BIBLE` switches retrieval embeddings/rerankers accordingly. Granite IDs are resolved via `GRANITE_EMBEDDING_MODEL`, `GRANITE_RERANKER_MODEL`, and `GRANITE_LOCAL_AGENT_MODEL`. Misconfigured Granite profiles emit a `HINT` and fall back to DEFAULT for hermetic runs.
  - **Planning Lane (Gemini CLI + Codex)**: pmagent exposes a **planning slot** for backend planning, coding refactors, and math-heavy reasoning. This lane is intentionally **non-theology** and never substitutes for gematria/theology slots.
    - Configure via `PLANNING_PROVIDER` (`gemini`, `codex`, `lmstudio`, `ollama`) and `PLANNING_MODEL`. Optional toggles: `GEMINI_ENABLED`, `CODEX_ENABLED`, `GEMINI_CLI_PATH`, `CODEX_CLI_PATH`.
    - pmagent calls CLI adapters (`agentpm/adapters/gemini_cli.py`, `agentpm/adapters/codex_cli.py`) with structured prompts, logs runs through `agentpm.runtime.lm_logging`, and records outcomes in `control.agent_run`.
    - If the selected CLI is unavailable, pmagent fails closed with `mode="lm_off"` and optionally falls back to the Granite local_agent slot—never to theology.
    - Multi-agent planning is permitted: pmagent may spin up multiple planning calls (Gemini/Codex instances) for decomposition tasks, each tracked with its own agent_run row. Context windows are large, but prompts must still cite SSOT docs; no theology, scripture exegesis, or gematria scoring is delegated to these tools.
    - Planning lane usage is opt-in per operator; CI remains hermetic (planning CLIs disabled unless explicitly allowed).
    - **Runbooks**: See `docs/runbooks/GEMINI_CLI.md` and `docs/runbooks/CODEX_CLI.md` for setup and usage details.

### LM Status Command

- Command: `pmagent lm.status`
- Purpose: Show current LM configuration and local service health:
  - Per-slot provider and model (local_agent, embedding, reranker, theology)
  - Ollama health (local only)
  - LM Studio/theology_lmstudio health (local only)
- Notes:
  - No LangChain/LangGraph; this is a thin status/introspection layer.
  - All checks use localhost URLs (127.0.0.1); no internet calls.

### System Status UI & TVs

- JSON endpoint:
  - Path: `/api/status/system` (DB + LM health snapshot; reuses DB + LM health helpers)
- HTML status page:
  - Path: `/status`
  - Shows:
    - DB health mode (`ready`, `db_off`, or `partial`)
    - LM slots (local_agent, embedding, reranker, theology) with provider, model, and service status
- TVs:
  - `TV-LM-HEALTH-01`: LM stack local health snapshot (Ollama + LM Studio per-slot status)
  - `TV-DB-HEALTH-01`: DB health mode snapshot (ready/db_off/partial) based on db health guard
- Notes:
  - All checks are local-only (Postgres + LM providers on 127.0.0.1).
  - No LangChain/LangGraph in this path; thin status layer over existing adapters and guards.

### Status Explanation Skill

- Command: `pmagent status.explain`
- Purpose:
  - Read the combined DB + LM system status snapshot.
  - Produce a plain-language explanation of current health:
    - Database mode (ready/db_off/partial) and what it means.
    - LM slots (local_agent, embedding, reranker, theology) and their service states.
- Behavior:
  - Uses rule-based summaries by default.
  - May call the local LM provider stack (Granite/Ollama/LM Studio) to refine wording if available.
  - Never fails if LM is down; always returns a best-effort explanation.
- Options:
  - `--json-only`: Return JSON instead of formatted text.
  - `--no-lm`: Skip LM enhancement, use rule-based explanation only.
- Notes:
  - No external internet calls; only local DB and LM services (127.0.0.1).
  - Exit code 0 always (explanations are best-effort snapshots).
```

## 6. Tracking / self-healing references (rg outputs)

### tracking_agent_refs

```
scripts/util/export_pm_introspection_evidence.py:145:        ("tracking agent", "tracking_agent_refs"),

```

### envelope_refs

```
pmagent/hints/registry.py:1:"""Hint Registry - DMS-backed hint loading and embedding for envelopes."""
pmagent/hints/registry.py:92:def embed_hints_in_envelope(
pmagent/hints/registry.py:93:    envelope: dict[str, Any],
pmagent/hints/registry.py:97:    Embed hints into an envelope structure.
pmagent/hints/registry.py:99:    Adds "required_hints" and "suggested_hints" sections to the envelope.
pmagent/hints/registry.py:103:        envelope: Existing envelope dict
pmagent/hints/registry.py:110:    result = envelope.copy()
docs/phase10/UI_SPEC.md:10:**Input**: `/tmp/p9-ingest-envelope.json` (built via `make ingest.local.envelope`)  
docs/phase10/UI_SPEC.md:11:Schema (draft): `docs/phase9/ingest_envelope.schema.draft.json`.
docs/phase10/UI_SPEC.md:41:  Copy the envelope into your dev server's static root and fetch it:
docs/phase10/UI_SPEC.md:45:  OUT_FILE=/tmp/p9-ingest-envelope.json make ingest.local.envelope
docs/phase10/UI_SPEC.md:46:  cp /tmp/p9-ingest-envelope.json ui/public/envelope.json
docs/phase10/UI_SPEC.md:47:  # UI fetches /envelope.json at dev-time
docs/phase10/UI_SPEC.md:50:  Do not hardwire absolute `/tmp/...` in fetch; use `/envelope.json`.
docs/phase10/UI_SPEC.md:54:  GET `/api/envelope` → Envelope (we'll provide later). Keep adapter boundary.
docs/phase10/UI_SPEC.md:71:  constructor(private url = "/envelope.json") {}
docs/phase10/UI_SPEC.md:91:* `envelopeLoaded`: `{ nodeCount, edgeCount, meta }`
docs/phase10/UI_SPEC.md:109:  public/              # (optional) envelope.json for dev fetch
docs/phase10/UI_SPEC.md:126:* [ ] Loads via file picker (and/or `/envelope.json`) with **no network/DB**.
docs/phase10/UI_SPEC.md:127:* [ ] Renders meta + counts deterministically with our sample envelope.
docs/phase10/DASHBOARD_PLAN.md:5:- Visualize local ingestion envelopes (Phase-9) without network/DB.
docs/phase10/DASHBOARD_PLAN.md:10:- Input: /tmp/p9-ingest-envelope.json (built locally via `make ingest.local.envelope`).
docs/phase10/DASHBOARD_PLAN.md:22:- P10-B: JSON loader + minimal graph view reading envelope nodes/edges.
docs/phase10/STRUCTURE.md:10:* `ui/src/lib/` helpers (envelope loader)
docs/phase10/STRUCTURE.md:15:1. Build envelope locally: `make ingest.local.envelope`
docs/phase10/STRUCTURE.md:17:3. Load `/tmp/p9-ingest-envelope.json` for views
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:6:Move hints from hardcoded strings in agent code to a DMS-backed registry (`control.hint_registry`) with REQUIRED vs SUGGESTED semantics. Envelope generators (handoff, capability_session, reality_check, status) will query the registry and embed hints into their outputs. A guard (`guard.hints.required`) will enforce that REQUIRED hints are present in envelopes.
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:12:3. **Ensure envelopes always carry required hints** – fail if they don't
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:66:- `embed_hints_in_envelope(envelope: dict, hints: dict[str, list]) -> dict`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:67:  - Adds `required_hints`, `suggested_hints` sections to envelope
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:80:- Add `required_hints` and `suggested_hints` arrays to capability_session envelope
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:90:- Add hints section to status snapshot envelope
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:96:Function: `guard_hints_required(flow_name: str, envelope_path: Path, mode: str = "HINT") -> dict[str, Any]`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:100:1. Load envelope from `envelope_path`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:102:3. Check that all REQUIRED hints appear in envelope's `required_hints` array
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:135:- No behavior changes yet (envelopes still work without DMS hints)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:139:- Update envelope generators to query DMS and include hints
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:147:- Ensure all envelope generators pass guard
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:169:- `pmagent/plan/next.py` - Add hints to capability_session envelopes
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:179:2. ✅ All envelope generators query DMS and embed `required_hints` / `suggested_hints`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:190:4. **Step 3**: Wire envelope generators (parallel behavior, non-breaking)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:198:- **Idempotent**: Registry queries are read-only; envelope generation remains deterministic
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:199:- **Hermetic-friendly**: Guard and envelope generators must work when DB unavailable (HINT mode)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:207:- [ ] Implement pmagent/hints/registry.py with load_hints_for_flow() and embed_hints_in_envelope() functions
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:208:- [ ] Wire envelope generators to query DMS and embed hints: scripts/prepare_handoff.py, pmagent/plan/next.py, pmagent/reality/check.py, pmagent/status/snapshot.py (parallel behavior, non-breaking)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:209:- [ ] Implement scripts/guards/hints_required.py guard that checks envelopes contain all REQUIRED hints, wire into make reality.green STRICT
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:210:- [ ] Fix any flows that fail guard.hints.required until all envelope generators pass in STRICT mode
docs/phase10/AGENTS.md:38:5. **Integration** - Backend data integration and envelope loading
docs/phase10/AGENTS.md:61:- **Envelope loading**: Load data from `/tmp/p9-ingest-envelope.json` or `share/exports/`
docs/phase10/AGENTS.md:75:- **scripts/extract/extract_all.py**: Unified envelope extraction
docs/phase10/AGENTS.md:76:- **make ui.extract.all**: Extract envelope for UI consumption
.cursor/plans/ui-enhancement-18696d49.plan.md:11:- Generate unified envelope format with integrated attributes
.cursor/plans/ui-enhancement-18696d49.plan.md:128:- IndexedDB storage for large envelopes
docs/PHASE11_PLAN.md:5:* **1d**: Unified pipeline (graph + temporal + correlations → single envelope)
docs/PHASE11_PLAN.md:12:* Extract stub generates `unified_envelope_SIZE.json` in <2 sec for SIZE=10,000
docs/PHASE11_PLAN.md:21:* Include schema version in envelope header
docs/PHASE11_PLAN.md:25:See AGENTS.md section "Data Extraction Lineage" for complete flow: graph_latest → temporal_export → correlation_weights → unified_envelope
scripts/ingest/validate_ingest_envelope_schema.py:32:        error("usage: python3 scripts/ingest/validate_ingest_envelope_schema.py <envelope.json>")
scripts/ingest/validate_ingest_envelope_schema.py:42:        errs.append("envelope must be an object")
scripts/ingest/show_meta.py:18:    out = os.getenv("OUT_FILE", "/tmp/p9-ingest-envelope.json")
scripts/ingest/show_meta.py:21:        print(f"ERR[ingest.meta]: envelope not found: {p}", file=sys.stderr)
scripts/ingest/validate_snapshot.py:53:    envelope = {
scripts/ingest/validate_snapshot.py:63:    print(json.dumps(envelope, indent=2))
scripts/ingest/validate_envelope_schema.py:22:def validate_envelope(env: dict) -> list[str]:
scripts/ingest/validate_envelope_schema.py:60:            "usage: python3 scripts/ingest/validate_envelope_schema.py <envelope.json>",
scripts/ingest/validate_envelope_schema.py:69:    errs = validate_envelope(env)
scripts/ingest/build_envelope.py:21:        print(f"ERR[p9.envelope]: snapshot not found: {p}", file=sys.stderr)
scripts/ingest/build_envelope.py:28:        print("HINT[p9.envelope]: CI detected; noop (hermetic).")
scripts/ingest/build_envelope.py:35:    out_path = os.getenv("OUT_FILE", "/tmp/p9-ingest-envelope.json")
scripts/ingest/build_envelope.py:44:    envelope = {
scripts/ingest/build_envelope.py:47:            "source": "p9-envelope-local",
scripts/ingest/build_envelope.py:55:    s = json.dumps(envelope, indent=2)
.cursor/rules/058-auto-housekeeping.mdc:119:- **Rule 061**: AI learning tracking (hint envelope detection)
scripts/governance_docs_hints.py:7:hints envelope for auditability.
scripts/governance_docs_hints.py:85:def emit_hints_envelope(modified_files: list[str], recent_files: list[str]) -> dict:
scripts/governance_docs_hints.py:86:    """Create a hints envelope for governance docs/rule changes."""
scripts/governance_docs_hints.py:122:    envelope = {
scripts/governance_docs_hints.py:123:        "type": "hints_envelope",
scripts/governance_docs_hints.py:133:    return envelope
scripts/governance_docs_hints.py:137:    """Main function: check for changes and emit hints envelope."""
scripts/governance_docs_hints.py:141:    envelope = emit_hints_envelope(modified, recent)
scripts/governance_docs_hints.py:143:    # Write hints envelope to evidence directory
scripts/governance_docs_hints.py:146:        json.dump(envelope, f, indent=2, ensure_ascii=False)
scripts/governance_docs_hints.py:149:    if envelope["count"] > 0:
scripts/governance_docs_hints.py:150:        for hint in envelope["items"]:
scripts/governance_docs_hints.py:153:            f"HINT: governance.docs: Wrote {envelope['count']} hint(s) → {HINTS_FILE}",
.cursor/rules/054-reuse-first.mdc:14:  - src/**/{*pipeline*,*graph*,*envelope*,*rerank*}
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:154:Test that hints appear in generated envelopes:
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:156:# Test handoff envelope
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:160:# Test capability_session envelope
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:164:# Test reality_check envelope
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:170:- All REQUIRED hints appear in their respective envelopes
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:176:Test guard with actual envelope files:
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:181:    --envelope share/handoff_latest.md \
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:187:    --envelope evidence/pmagent/reality_check_latest.json \
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:224:python scripts/guards/hints_required.py --flow handoff.generate --envelope share/handoff_latest.md --mode STRICT
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:225:python scripts/guards/hints_required.py --flow reality_check --envelope evidence/pmagent/reality_check_latest.json --mode STRICT
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:253:3. ✅ All hints appear in their respective envelopes
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:261:### Risk: Removing hardcoded hints breaks envelope generation
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:263:- Verify hints in envelopes before removing hardcoded copies

```

### housekeeping_refs

```
pmagent/ai_docs/reality_check_ai_notes.py:68:    prompt = f"""You are the Granite housekeeping AI for the Gemantria project.
pmagent/control_plane/sessions.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/control_plane/doc_fragments.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/control_plane/exports.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:92:- After generating diagrams, MUST run `make housekeeping` before committing
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:95:  1. Run housekeeping: `make housekeeping`
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:184:8. **Run housekeeping** (Rule 058)
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:185:   - Execute `make housekeeping` after all changes
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:216:8. Run `make housekeeping`
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:272:- Housekeeping: `make housekeeping` runs after diagram generation
.cursor/plans/plan-e3abd805.plan.md:34:- Every execution brief includes required SSOT references, guard/tests, and housekeeping/reality.green expectations per OPS v6.2.3.
.cursor/plans/plan-e3abd805.plan.md:50:- [ ] Specify final repo-wide gates (ruff, focused smokes, housekeeping, optionally reality.green) to run after the E-step.
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:144:### Step 5: Integrate doc registry ingestion into housekeeping
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:150:- Add `governance.ingest.docs` as a dependency to `housekeeping` target (before `share.sync`)
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:176:7. Run `make housekeeping` and verify it completes successfully
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:209:- [ ] Add governance.ingest.docs as dependency to housekeeping target in Makefile (before share.sync)
docs/hints/HINT-DB-002-postgres-not-running.md:85:- ❌ Cannot run housekeeping or regenerate KB
scripts/ingest/validate_ingest_envelope_schema.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/show_meta.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/__init__.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/validate_snapshot.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/validate_envelope_schema.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/build_envelope.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/check_env.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
docs/BACKUP_STRATEGY_AUDIT.md:45:- Part of housekeeping (`make housekeeping`)
docs/BACKUP_STRATEGY_AUDIT.md:130:- Run during housekeeping
scripts/ingest/mappers.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/stub_ingest.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/book_policy_check.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
.cursor/rules/058-auto-housekeeping.mdc:2:description: Mandatory run `make housekeeping` after every change/PR. Fail-closed if skipped—critical error log/CI fail. Includes share.sync, governance, ADRs, rules audit, forest regen, and evidence archiving.
.cursor/rules/058-auto-housekeeping.mdc:14:**CRITICAL CURSOR ENFORCEMENT**: After ANY file edit in this repository, Cursor MUST automatically run `make housekeeping` before committing. This is non-negotiable. Do not proceed without running housekeeping.
.cursor/rules/058-auto-housekeeping.mdc:16:**AUTOMATIC DOCUMENTATION UPDATES**: The housekeeping pipeline now **automatically** updates:
.cursor/rules/058-auto-housekeeping.mdc:20:**You should NOT need to manually update these files** — they are updated automatically by `scripts/auto_update_agents_md.py` and `scripts/auto_update_changelog.py` as part of `make housekeeping`. If you find yourself manually editing AGENTS.md or CHANGELOG.md, that indicates the auto-update scripts need enhancement, not that manual updates are required.
.cursor/rules/058-auto-housekeeping.mdc:24:Mandatory run `make housekeeping` after every change/PR. Fail-closed if skipped—critical error log/CI fail.
.cursor/rules/058-auto-housekeeping.mdc:31:# Unified housekeeping command (runs all steps)
.cursor/rules/058-auto-housekeeping.mdc:32:make housekeeping
.cursor/rules/058-auto-housekeeping.mdc:35:The `make housekeeping` target executes:
.cursor/rules/058-auto-housekeeping.mdc:37:2. **ADR housekeeping** (`adr.housekeeping`) — ADR validation and updates
.cursor/rules/058-auto-housekeeping.mdc:38:3. **Governance housekeeping** (`governance.housekeeping`) — runs `scripts/governance_housekeeping.py` for database compliance + docs
.cursor/rules/058-auto-housekeeping.mdc:56:python3 scripts/governance_housekeeping.py   # Governance compliance
.cursor/rules/058-auto-housekeeping.mdc:62:**FAIL-CLOSED DESIGN**: If housekeeping skipped, operations fail with critical error logs:
.cursor/rules/058-auto-housekeeping.mdc:65:Evidence: Modified files detected without housekeeping completion
.cursor/rules/058-auto-housekeeping.mdc:71:- **Pre-commit hooks**: Block commits without housekeeping completion
.cursor/rules/058-auto-housekeeping.mdc:72:- **PR checks**: Require housekeeping evidence in PR descriptions  
.cursor/rules/058-auto-housekeeping.mdc:73:- **Branch protection**: Enforce housekeeping completion for merges
.cursor/rules/058-auto-housekeeping.mdc:76:- **IDE integration**: Automatic housekeeping prompts after saves
.cursor/rules/058-auto-housekeeping.mdc:77:- **Git hooks**: Pre-commit validation of housekeeping status
.cursor/rules/058-auto-housekeeping.mdc:78:- **Status indicators**: Clear visual feedback on housekeeping state
.cursor/rules/058-auto-housekeeping.mdc:97:  - **No manual intervention required** — runs as part of `make housekeeping`
.cursor/rules/058-auto-housekeeping.mdc:102:  - **No manual intervention required** — runs as part of `make housekeeping`
.cursor/rules/058-auto-housekeeping.mdc:114:- **Rule 027**: Docs sync gate (housekeeping includes docs sync)
.cursor/rules/058-auto-housekeeping.mdc:116:- **Rule 055**: Auto-docs sync pass (housekeeping enforces this)
.cursor/rules/058-auto-housekeeping.mdc:117:- **Rule 017**: Agent docs presence (housekeeping validates coverage)
scripts/docs/apply_ops_header.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/docs/apply_ops_header.py:7:HEADER = """# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/exports_smoke.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/temporal_analytics.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/verify_enrichment_prompts.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/housekeeping_gpu/__init__.py:4:Purpose: Performance-optimized housekeeping operations using GPU acceleration when available.
scripts/echo_env.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/AGENTS.md:182:  - Run `make housekeeping` (or at least `make share.sync governance.housekeeping`) after changes to ensure docs and share/ are updated.
scripts/housekeeping_gpu/gpu_classifier.py:7:Provide GPU-accelerated batch classification for housekeeping operations.
.cursor/rules/README.md:5:> Governance fast-lane: All exports stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`. Run guards in HINT-only mode (`STRICT_RFC3339=0`) on main/PRs and STRICT (`STRICT_RFC3339=1`) on release builds. Always run `make housekeeping` after docs or script changes so the contract stays enforced.
scripts/goldens_status.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/housekeeping_gpu/classify_fragments_gpu.py:18:    python scripts/housekeeping_gpu/classify_fragments_gpu.py [--dry-run] [--limit N]
scripts/housekeeping_gpu/classify_fragments_gpu.py:36:from scripts.housekeeping_gpu.gpu_classifier import classify_batch_gpu
scripts/ingest_bible_db_morphology.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/governance_housekeeping.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/governance_housekeeping.py:7:governance_housekeeping.py — Automated governance maintenance per Rule-058.
scripts/governance_housekeeping.py:9:Integrates with existing housekeeping workflow to ensure governance artifacts
scripts/governance_housekeeping.py:10:stay current and compliant. Called automatically by make housekeeping targets.
scripts/governance_housekeeping.py:22:    python scripts/governance_housekeeping.py  # Run full housekeeping cycle
scripts/governance_housekeeping.py:61:        print("   DB is SSOT - housekeeping cannot proceed without DB connectivity.")
scripts/governance_housekeeping.py:93:    # For initial housekeeping runs, be more lenient about stale artifacts
scripts/governance_housekeeping.py:94:    # This allows housekeeping to succeed even with stale artifacts on first run
scripts/governance_housekeeping.py:109:    # Document hints are informational and should not fail housekeeping
scripts/governance_housekeeping.py:160:                        "housekeeping",
scripts/governance_housekeeping.py:163:                        "housekeeping_script",
scripts/governance_housekeeping.py:172:    """Run complete governance housekeeping cycle."""
scripts/governance_housekeeping.py:206:    log_compliance_status(all_success, "full_housekeeping_cycle")
scripts/sandbox_smoke_check.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/gematria_verify.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/governance_tracker.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/governance_tracker.py:293:        return True  # Return success to allow housekeeping to pass
scripts/governance_tracker.py:329:        return True  # Return success to allow housekeeping to pass
scripts/backfill_bge_embeddings.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/repo_audit.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ai_enrichment.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ontology_compat.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
.cursor/rules/006-agents-md-governance.mdc:13:- **MANDATORY**: Run `make housekeeping` after ANY changes to docs, scripts, rules, or database
.cursor/rules/006-agents-md-governance.mdc:50:- **Rule 058**: Auto-housekeeping (mandatory after any modifications)
scripts/document_management_hints.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/math_verifier.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ai_session_monitor.py:3:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
.cursor/rules/010-task-brief.mdc:23:- **MANDATORY**: Include `make housekeeping` in Tests/checks for any doc/script/rule changes
.cursor/rules/010-task-brief.mdc:38:- **Rule 058**: Auto-housekeeping (mandatory after modifications)
scripts/audit_genesis_db.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/repo/logic.py:147:        "Run 'make share.sync' or housekeeping to generate the KB registry."
scripts/ci/check_pr_model_usage.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/guarded/guard_shim.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

```

### pm_snapshot_refs

```
.cursor/rules/070-gotchas-check.mdc:136:- All command execution wrappers (e.g., `scripts/pm_snapshot.py::run()`, `scripts/prepare_handoff.py::run_cmd()`)
.cursor/rules/058-auto-housekeeping.mdc:48:13. **PM snapshot** (`pm.snapshot`) — generates PM-facing status snapshot
.cursor/rules/071-portable-json-not-plan-ssot.mdc:3:* The `share/*.json` portable bundle (e.g. `pm_snapshot.json`,
pmagent/AGENTS.md:68:  - **Snapshot integration (KB-Reg:M2)**: Registry summary included in `pm.snapshot` via `pmagent.status.snapshot.get_system_snapshot()` (advisory-only, non-gating)
pmagent/AGENTS.md:89:## pm.snapshot Integration (AgentPM-First:M3 + M4)
pmagent/AGENTS.md:91:**Purpose:** `pm.snapshot` (`make pm.snapshot` / `scripts/pm_snapshot.py`) generates a comprehensive PM-facing status snapshot that composes health, status explanation, reality-check, AI tracking, share manifest, and eval exports posture into a single operator-facing view.
pmagent/AGENTS.md:95:- **Shared by**: `pm.snapshot` script and WebUI APIs (`/api/status/system`) for consistency
pmagent/AGENTS.md:104:- **Markdown snapshot**: `share/pm.snapshot.md` — Human-readable PM snapshot with all component statuses
pmagent/AGENTS.md:105:- **JSON snapshot**: `evidence/pm_snapshot/snapshot.json` — Machine-readable comprehensive snapshot with:
pmagent/AGENTS.md:118:    - `db_health`: DB health snapshot (from `evidence/pm_snapshot/db_health.json`)
pmagent/AGENTS.md:128:- **DB health JSON** (backward compatibility): `evidence/pm_snapshot/db_health.json`
pmagent/AGENTS.md:131:- **Local operator command**: `make pm.snapshot` — Run after bring-up or DSN changes to generate current system posture snapshot
pmagent/AGENTS.md:132:- **CI usage**: CI may run `pm.snapshot` but should not fail if DB/LM are offline (hermetic behavior)
pmagent/AGENTS.md:141:- **KB hints (KB-Reg:M4 + M6)**: KB registry health is surfaced as structured hints in `pm.snapshot` and `pmagent reality-check`; hints include missing docs, low coverage subsystems, validation issues, stale docs (`KB_DOC_STALE`), and out-of-sync docs (`KB_DOC_OUT_OF_SYNC`); all hints are advisory-only and never affect `overall_ok`
docs/BACKUP_STRATEGY_AUDIT.md:32:- `Makefile` lines 187-189 (`pm.snapshot` target)
docs/BACKUP_STRATEGY_AUDIT.md:33:- `scripts/pm_snapshot.py`
docs/BACKUP_STRATEGY_AUDIT.md:34:- Output: `evidence/pm_snapshot/run.txt`
docs/BACKUP_STRATEGY_AUDIT.md:38:make pm.snapshot  # Generate PM health snapshot
docs/BACKUP_STRATEGY_AUDIT.md:128:**PM Snapshots** (`pm.snapshot`):
pmagent/status/snapshot.py:5:AgentPM-First:M3: Unified system snapshot helper for pm.snapshot and WebUI APIs.
pmagent/status/snapshot.py:458:    """Get unified system snapshot (pm.snapshot + API contract).
pmagent/status/eval_exports.py:24:DB_HEALTH_PATH = REPO_ROOT / "evidence" / "pm_snapshot" / "db_health.json"
pmagent/status/eval_exports.py:121:    """Load DB health snapshot (from pm.snapshot evidence).
pmagent/status/eval_exports.py:136:                "note": "DB health snapshot not available (file missing; run `make pm.snapshot`)",
.cursor/rules/AGENTS.md:2076:13. **PM snapshot** (`pm.snapshot`) — generates PM-facing status snapshot
pmagent/status/AGENTS.md:9:- `snapshot.py`: Unified system snapshot helpers used by `pm.snapshot` and `/api/status/system`. Now includes advisory `kb_doc_health` metrics (AgentPM-Next:M3).
pmagent/status/AGENTS.md:10:- `kb_metrics.py`: KB documentation health metrics helper (AgentPM-Next:M3) that aggregates KB registry freshness + M2 fix manifests into doc-health metrics for reporting surfaces (`pmagent report kb`, `pm.snapshot`, and future status integration).
scripts/util/export_pm_snapshot_json.py:5:Exports pm.snapshot as JSON format by calling get_system_snapshot() directly.
scripts/util/export_pm_snapshot_json.py:6:This is the JSON version of the markdown snapshot generated by make pm.snapshot.
scripts/util/export_pm_snapshot_json.py:9:    python scripts/util/export_pm_snapshot_json.py [--output <path>]
scripts/util/export_pm_snapshot_json.py:24:OUT_FILE = OUT_DIR / "pm_snapshot.json"
scripts/util/export_pm_snapshot_json.py:30:    parser.add_argument("--output", type=Path, help="Output JSON file path (default: share/pm_snapshot.json)")
scripts/util/export_pm_snapshot_json.py:67:            "schema": "pm_snapshot.v1",
scripts/util/export_pm_introspection_evidence.py:148:        ("pm.snapshot", "pm_snapshot_refs"),
scripts/AGENTS.md:1349:- `share/pm.snapshot.md`
scripts/pm_snapshot.py:12:doc_path = share_dir / "pm.snapshot.md"
scripts/pm_snapshot.py:14:evid_dir = root / "evidence" / "pm_snapshot"
scripts/pm_snapshot.py:237:entry = {"src": "share/pm.snapshot.md", "dst": "share/pm.snapshot.md"}
scripts/pm_snapshot.py:279:    "**Now**\n- Keep GemantriaV.2 as the active project.\n- Use `STRICT` posture when DSNs present; otherwise HINT mode is allowed for hermetic tests.\n- Regenerate this PM Snapshot on each bring-up or DSN change (`make pm.snapshot`).\n"
scripts/guard_pm_snapshot.sh:3:SNAPSHOT_PATH="${1:-share/pm.snapshot.md}"
pmagent/kb/AGENTS.md:77:- **pm.snapshot**: Registry is included in system snapshots (KB-Reg:M2) — advisory-only, non-gating
pmagent/kb/AGENTS.md:85:The KB registry is integrated into `pm.snapshot` via `pmagent.status.snapshot.get_system_snapshot()`:
pmagent/kb/AGENTS.md:185:KB registry health is surfaced as structured hints in `pm.snapshot` and `pmagent reality-check`:
pmagent/kb/AGENTS.md:197:- **pm.snapshot**: KB hints included in `evidence/pm_snapshot/snapshot.json` and rendered in `share/pm.snapshot.md` under "KB Hints (Advisory)" section
scripts/kb/seed_registry.py:108:            id="runbook-pm-snapshot",
scripts/guards/guard_snapshot_drift.py:78:        "pm_snapshot": ROOT / "share" / "pm.snapshot.md",
docs/runbooks/LM_HEALTH.md:156:make pm.snapshot
docs/runbooks/DB_HEALTH.md:134:make pm.snapshot
docs/runbooks/DSN_SECRETS.md:21:  **Used in:** `pm-snapshot.yml` (release tags), `tagproof.yml` (release tags)
docs/runbooks/DSN_SECRETS.md:27:  **Used in:** `pm-snapshot.yml` (release tags), `tagproof.yml` (release tags)
docs/runbooks/DSN_SECRETS.md:29:> CI uses these secrets only on **release tags** and regenerates `share/pm.snapshot.md`
docs/runbooks/DSN_SECRETS.md:35:- PM Snapshot exists in `share/pm.snapshot.md`
docs/runbooks/DSN_SECRETS.md:50:3. Confirm Actions jobs **tagproof** and **pm-snapshot** are green.
docs/forest/overview.md:99:- pm-snapshot.yml
pmagent/tests/db/test_phase3a_db_health_snapshot.py:2:Tests for Phase-3A Step-5: DB health integration in pm.snapshot.
pmagent/tests/db/test_phase3a_db_health_snapshot.py:4:Verifies that pm.snapshot calls guard.db.health and embeds JSON correctly.
pmagent/tests/db/test_phase3a_db_health_snapshot.py:18:    """Test DB health integration in pm.snapshot."""
pmagent/tests/db/test_phase3a_db_health_snapshot.py:20:    @patch("scripts.pm_snapshot.check_db_health")
pmagent/tests/db/test_phase3a_db_health_snapshot.py:22:        """Test that pm.snapshot includes DB health JSON in output."""
pmagent/tests/db/test_phase3a_db_health_snapshot.py:23:        from scripts import pm_snapshot
pmagent/tests/db/test_phase3a_db_health_snapshot.py:39:            patch("scripts.pm_snapshot.pathlib.Path.write_text"),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:40:            patch("scripts.pm_snapshot.pathlib.Path.exists", return_value=True),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:41:            patch("scripts.pm_snapshot.pathlib.Path.read_text", return_value='{"items": []}'),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:42:            patch("scripts.pm_snapshot.pathlib.Path.mkdir"),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:47:            with patch("scripts.pm_snapshot.share_dir", mock_share_dir):
pmagent/tests/db/test_phase3a_db_health_snapshot.py:56:                        pm_snapshot.now_iso = "2024-01-01T00:00:00+00:00"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:57:                        pm_snapshot.BIBLE_DB_DSN = "postgresql://test/bible_db"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:58:                        pm_snapshot.GEMATRIA_DSN = "postgresql://test/gematria"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:59:                        pm_snapshot.CHECKPOINTER = "postgres"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:60:                        pm_snapshot.ENFORCE_STRICT = "1"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:61:                        pm_snapshot.ro_probe = "ok"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:62:                        pm_snapshot.rw_probe = "ok"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:70:    @patch("scripts.pm_snapshot.check_db_health")
pmagent/tests/db/test_phase3a_db_health_snapshot.py:72:        """Test that pm.snapshot handles DB health check errors gracefully."""
pmagent/tests/db/test_phase3a_db_health_snapshot.py:73:        from scripts import pm_snapshot
pmagent/tests/db/test_phase3a_db_health_snapshot.py:80:            patch("scripts.pm_snapshot.pathlib.Path.write_text"),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:81:            patch("scripts.pm_snapshot.pathlib.Path.exists", return_value=True),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:82:            patch("scripts.pm_snapshot.pathlib.Path.read_text", return_value='{"items": []}'),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:83:            patch("scripts.pm_snapshot.pathlib.Path.mkdir"),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:88:                pm_snapshot.now_iso = "2024-01-01T00:00:00+00:00"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:89:                pm_snapshot.BIBLE_DB_DSN = "postgresql://test/bible_db"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:90:                pm_snapshot.GEMATRIA_DSN = "postgresql://test/gematria"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:99:        """Test that pm.snapshot writes DB health JSON to evidence directory."""
pmagent/tests/db/test_phase3a_db_health_snapshot.py:100:        from scripts import pm_snapshot
pmagent/tests/db/test_phase3a_db_health_snapshot.py:115:            patch("scripts.pm_snapshot.check_db_health", return_value=mock_db_health),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:116:            patch("scripts.pm_snapshot.pathlib.Path.write_text"),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:117:            patch("scripts.pm_snapshot.pathlib.Path.exists", return_value=True),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:118:            patch("scripts.pm_snapshot.pathlib.Path.read_text", return_value='{"items": []}'),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:119:            patch("scripts.pm_snapshot.pathlib.Path.mkdir"),
pmagent/tests/db/test_phase3a_db_health_snapshot.py:122:            mock_evid_dir = tmp_path / "evidence" / "pm_snapshot"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:124:            with patch("scripts.pm_snapshot.evid_dir", mock_evid_dir):
pmagent/tests/db/test_phase3a_db_health_snapshot.py:127:                    pm_snapshot.now_iso = "2024-01-01T00:00:00+00:00"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:128:                    pm_snapshot.BIBLE_DB_DSN = "postgresql://test/bible_db"
pmagent/tests/db/test_phase3a_db_health_snapshot.py:129:                    pm_snapshot.GEMATRIA_DSN = "postgresql://test/gematria"
docs/plans/PLAN-080-Verification-Sweep-and-Tagproof.md:96:**M4 - UI Integration (pm.snapshot kb_doc_health):**
pmagent/tests/runtime/test_pm_snapshot.py:2:Tests for pm.snapshot integration (AgentPM-First:M3).
pmagent/tests/runtime/test_pm_snapshot.py:4:Verifies that pm.snapshot composes health, status explain, reality-check,
pmagent/tests/runtime/test_pm_snapshot.py:8:executing the full pm_snapshot.py script (which runs at module import time).
pmagent/tests/runtime/test_pm_snapshot.py:21:    """Test pm.snapshot integration with pmagent commands."""
docs/SSOT/PHASE15_WAVE3_STEP2_OPS_BLOCK.md:27:| **Gate 1 (DMS Ingestion)** | ✅ COMPLETE | 65,243 fragments, 65,238 embeddings (1024-D) | `share/pm_snapshot.md`, `docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md` |

```

### planning_context_refs

```
scripts/util/export_pm_introspection_evidence.py:149:        ("planning_context", "planning_context_refs"),
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:147:**Fix**: Consider including `pmagent plan next --json-only` output in share folder as `planning_context.json` (full, not head).
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:154:- Add `planning_context.json` to share folder (from `pmagent plan next`)
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:184:**Fix**: Include `planning_context` in `pm_snapshot.json` by calling `pmagent plan next --json-only`.
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:233:4. **Add planning context to share folder** - include `pmagent plan next --json-only` output as `share/planning_context.json`
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:245:2. **Automate planning context updates** - ensure `share/planning_context.json` is always fresh
scripts/pm/generate_pm_boot_surface.py:30:        (SHARE / "planning_context.json", PM_BOOT / "planning_context.json"),
docs/SSOT/PHASE27_INDEX.md:370:  - Treats planning_context.json as optional
scripts/guards/guard_pm_boot_surface.py:33:    "planning_context.json",
docs/SSOT/PHASE15_RECON.md:48:- Multiple `share/` files (doc_registry, kb_registry, planning_context, etc.)
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:69:2. **Planning Context** (`share/planning_context.json`)
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:128:* `make pm.share.planning_context` - Export planning context only
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:183:2. **Use planning context** from `share/planning_context.json` for current focus
scripts/guards/guard_share_sync_policy.py:82:    "share/planning_context.json",  # planning pipeline output for agents (not a managed doc)
scripts/guards/guard_dms_share_alignment.py:83:    "planning_context.json",  # planning pipeline output for agents (not a managed doc)
docs/SSOT/SHARE_FOLDER_STRUCTURE.md:35:* `planning_context.md` - Full planning output from `pmagent plan next`
docs/SSOT/SHARE_FOLDER_STRUCTURE.md:88:* `share/planning_context.md` - Full planning output from `pmagent plan next` (converted from JSON)

```

### kb_registry_refs

```
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:12:- KB registry system (file-based `share/kb_registry.json`) may need restoration after PR #579
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:34:   - Check if `share/kb_registry.json` exists and is valid (KB registry from PR #579)
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:45:   - Check if KB registry (`share/kb_registry.json`) is missing or corrupted
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:129:**Files**: `share/kb_registry.json`, `scripts/kb/seed_registry.py`
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:133:- If `share/kb_registry.json` is missing or corrupted:
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:194:- `share/kb_registry.json` - KB registry file (may need restoration)
pmagent/cli.py:2029:def kb_registry_list(
pmagent/cli.py:2055:def kb_registry_show(
pmagent/cli.py:2090:def kb_registry_by_subsystem(
pmagent/cli.py:2119:def kb_registry_by_tag(
pmagent/cli.py:2145:def kb_registry_summary(
pmagent/cli.py:2204:def kb_registry_validate(
pmagent/AGENTS.md:66:  - **SSOT**: Registry entries live in `share/kb_registry.json` (read-only in CI per Rule-044)
pmagent/AGENTS.md:96:- **Components**: DB health, system health (DB + LM + Graph), status explanation, reality-check, AI tracking, share manifest, eval insights (Phase-8/10 exports), kb_registry (KB-Reg:M2)
pmagent/AGENTS.md:121:  - `kb_registry`: KB registry summary (KB-Reg:M2) — **advisory only, read-only in CI**:
pmagent/repo/logic.py:70:      - share/kb_registry.json (JSON export from DMS)
pmagent/repo/logic.py:73:      - If kb_registry.json is missing but doc_registry.md exists, fall back
pmagent/repo/logic.py:81:    kb_json_path = Path("share/kb_registry.json")
pmagent/repo/logic.py:85:    # Primary: Use kb_registry.json if available
pmagent/repo/logic.py:96:                f"Unrecognized kb_registry.json structure: expected dict with 'documents' key or list, got {type(data)}"
scripts/AGENTS.md:1048:### `kb/build_kb_registry.py` — KB Registry Builder from DMS
scripts/AGENTS.md:1055:- **Files Modified**: `scripts/kb/build_kb_registry.py` (3 query locations), `scripts/governance/classify_fragments.py` (1 query location)
scripts/AGENTS.md:1061:python scripts/kb/build_kb_registry.py
scripts/AGENTS.md:1064:python scripts/kb/build_kb_registry.py --dry-run
scripts/AGENTS.md:1068:- `share/kb_registry.json` (curated subset, <50KB target)
pmagent/status/snapshot.py:131:def get_kb_registry_summary(registry_path: Path | None = None) -> dict[str, Any]:
pmagent/status/snapshot.py:135:        registry_path: Path to kb_registry.json (defaults to share/kb_registry.json)
pmagent/status/snapshot.py:150:        registry_path = repo_root / "share" / "kb_registry.json"
pmagent/status/snapshot.py:181:        registry_path: Path to kb_registry.json (defaults to share/kb_registry.json)
pmagent/status/snapshot.py:196:        registry_path = repo_root / "share" / "kb_registry.json"
pmagent/status/snapshot.py:218:        # If registry is at share/kb_registry.json, repo_root is parent of share/
pmagent/status/snapshot.py:220:        if registry_path.name == "kb_registry.json" and registry_path.parent.name == "share":
pmagent/status/snapshot.py:452:    include_kb_registry: bool = True,
pmagent/status/snapshot.py:465:        include_kb_registry: Whether to include KB registry summary (advisory-only)
pmagent/status/snapshot.py:483:            "kb_registry": {...} (if included) - optional, advisory-only, read-only in CI
pmagent/status/snapshot.py:562:    kb_registry_summary = {}
pmagent/status/snapshot.py:563:    if include_kb_registry:
pmagent/status/snapshot.py:565:            kb_registry_summary = get_kb_registry_summary()
pmagent/status/snapshot.py:567:            kb_registry_summary = {
pmagent/status/snapshot.py:589:    # NOTE: eval_insights and kb_registry are advisory only and do NOT affect overall_ok
pmagent/status/snapshot.py:617:    if include_kb_registry:
pmagent/status/snapshot.py:618:        snapshot["kb_registry"] = kb_registry_summary
pmagent/status/explain.py:202:                registry_path = repo_root / "share" / "kb_registry.json"
pmagent/status/AGENTS.md:24:    include_kb_registry: bool = True,
pmagent/status/AGENTS.md:42:    registry_path: str = "share/kb_registry.json"
.cursor/rules/068-gpt-docs-sync.mdc:99:The KB document registry (`share/kb_registry.json`) serves as the SSOT for document coverage and freshness:
.cursor/rules/AGENTS.md:2998:The KB document registry (`share/kb_registry.json`) serves as the SSOT for document coverage and freshness:
scripts/util/export_pm_snapshot_json.py:45:            include_kb_registry=True,
scripts/util/export_pm_introspection_evidence.py:150:        ("kb_registry", "kb_registry_refs"),
scripts/kb/build_kb_registry.py:8:SSOT: share/kb_registry.json (read-only in CI per Rule-044).
scripts/kb/build_kb_registry.py:48:def build_kb_registry_from_dms(dry_run: bool = False) -> KBDocumentRegistry:
scripts/kb/build_kb_registry.py:293:        registry = build_kb_registry_from_dms(dry_run=args.dry_run)
scripts/guards/guard_repo_layer4_alignment.py:58:        "scripts/kb/build_kb_registry.py",
scripts/guards/guard_dms_share_alignment.py:52:    "kb_registry.json",
scripts/pm_snapshot.py:95:        include_kb_registry=True,  # Include KB registry summary (KB-Reg:M2)
scripts/pm_snapshot.py:108:    kb_registry_summary = snapshot.get("kb_registry", {})
scripts/pm_snapshot.py:193:    kb_registry_summary = {
scripts/pm_snapshot.py:204:            get_kb_registry_summary,
scripts/pm_snapshot.py:209:        kb_registry_summary = get_kb_registry_summary()
scripts/pm_snapshot.py:217:        kb_registry_summary = {
scripts/pm_snapshot.py:324:    "kb_registry": kb_registry_summary,
scripts/pm_snapshot.py:417:kb_available = kb_registry_summary.get("available", False)
scripts/pm_snapshot.py:418:kb_total = kb_registry_summary.get("total", 0)
scripts/pm_snapshot.py:419:kb_valid = kb_registry_summary.get("valid", False)
scripts/pm_snapshot.py:420:kb_errors = kb_registry_summary.get("errors_count", 0)
scripts/pm_snapshot.py:421:kb_warnings = kb_registry_summary.get("warnings_count", 0)
scripts/pm_snapshot.py:431:    lines.append(f"- Note: {kb_registry_summary.get('note', 'KB registry file not found')}")
scripts/guards/guard_share_sync_policy.py:66:    "share/kb_registry.json",
pmagent/kb/__init__.py:8:SSOT: Registry entries live in share/kb_registry.json (read-only in CI per Rule-044).
scripts/pm/generate_pm_bootstrap_state.py:41:REGISTRY_PATH = SHARE / "kb_registry.json"
scripts/pm/generate_pm_bootstrap_state.py:100:def load_kb_registry() -> dict[str, Any] | None:
scripts/pm/generate_pm_bootstrap_state.py:261:    registry = load_kb_registry()
scripts/pm/generate_pm_bootstrap_state.py:303:            "kb_registry": optional("share/kb_registry.json"),
scripts/pm/generate_pm_bootstrap_state.py:308:            "kb_registry_path": "share/kb_registry.json",
scripts/pm/generate_pm_bootstrap_state.py:348:                    optional("share/kb_registry.json"),
pmagent/kb/AGENTS.md:21:- **Registry file**: `share/kb_registry.json` (JSON format)
pmagent/kb/AGENTS.md:125:**Seeding Script**: `scripts/kb/seed_registry.py` — Populates `share/kb_registry.json` with initial document entries. Respects CI write guards (Rule-044) — only runs in local/dev environments.
pmagent/kb/AGENTS.md:223:The KB registry builder (`scripts/kb/build_kb_registry.py`) has been optimized for PostgreSQL performance:
pmagent/kb/AGENTS.md:236:- `scripts/kb/build_kb_registry.py` (3 query locations optimized)
pmagent/kb/registry.py:9:SSOT: Registry entries live in share/kb_registry.json (read-only in CI per Rule-044).
pmagent/kb/registry.py:25:REGISTRY_PATH = REPO_ROOT / "share" / "kb_registry.json"
pmagent/kb/registry.py:169:        registry_path: Path to registry JSON file (defaults to share/kb_registry.json)
pmagent/kb/registry.py:205:        registry_path: Path to registry JSON file (defaults to share/kb_registry.json)
docs/SSOT/LAYERS_AND_PHASES.md:29:  - **Artifact:** `share/kb_registry.json` (generated from DMS)
docs/SSOT/LAYERS_AND_PHASES.md:30:  - **Builder:** `scripts/kb/build_kb_registry.py`
docs/SSOT/LAYER4_CODE_INGESTION_PLAN.md:108:- `scripts/kb/build_kb_registry.py` - Extended to include code files (already supports CODE::*)
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:18:- **Already implemented**: Code updated in `build_kb_registry.py`
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:88:- Only used in one query (`build_kb_registry.py` line 130)
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:169:**Is `build_kb_registry.py` slow?**
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:198:2. ⚠️ **Test partial index** if `build_kb_registry.py` is slow
docs/SSOT/PHASE15_WAVE3_STEP2_OPS_BLOCK.md:29:| **Gate 3 (KB Curation)** | ✅ COMPLETE | 40KB registry, 50 documents | `share/kb_registry.json`, `docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md` |
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:24:   - Data exists: `kb_registry.json` is 40KB (31KB actual), 50 documents
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:40:- **kb_registry**:
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:46:**`share/kb_registry.json`**:
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:78:6. Checked `kb_registry.json` for Gate 3 evidence
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:92:**Source**: `pm_snapshot.md`, `kb_registry.json`, schema inspection
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:135:- ✅ `share/kb_registry.json` is <50KB (31KB actual)
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:158:    # Check kb_registry size
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:167:3. Checks `share/kb_registry.json` size
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:196:- `share/kb_registry.json` - KB registry (Gate 3 evidence)

```

### hint_registry_refs

```
pmagent/hints/__init__.py:78:            typer.echo("✓ Inserted to control.hint_registry")
pmagent/hints/__init__.py:102:            typer.echo(f"\n✓ Inserted {len(hints)} hints to control.hint_registry")
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:6:Move hints from hardcoded strings in agent code to a DMS-backed registry (`control.hint_registry`) with REQUIRED vs SUGGESTED semantics. Envelope generators (handoff, capability_session, reality_check, status) will query the registry and embed hints into their outputs. A guard (`guard.hints.required`) will enforce that REQUIRED hints are present in envelopes.
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:19:**Migration**: `migrations/052_control_hint_registry.sql`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:21:Create `control.hint_registry` table:
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:24:CREATE TABLE IF NOT EXISTS control.hint_registry (
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:38:CREATE INDEX idx_hint_registry_scope ON control.hint_registry (scope) WHERE enabled = TRUE;
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:39:CREATE INDEX idx_hint_registry_applies_to ON control.hint_registry USING GIN (applies_to) WHERE enabled = TRUE;
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:40:CREATE INDEX idx_hint_registry_kind ON control.hint_registry (kind, priority) WHERE enabled = TRUE;
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:63:  - Queries `control.hint_registry` for matching hints
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:123:**Migration**: `migrations/052_control_hint_registry.sql`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:131:**Script**: `scripts/governance/seed_hint_registry.py` (new)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:134:- Insert hints into `control.hint_registry`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:159:- `migrations/052_control_hint_registry.sql` - Schema migration
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:163:- `scripts/governance/seed_hint_registry.py` - Registry seeding
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:178:1. ✅ `control.hint_registry` table exists and is populated with initial hints
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:206:- [ ] Create migration 052_control_hint_registry.sql with hint_registry table schema, then seed initial REQUIRED hints (docs.dms_only, status.local_gates_first, share.dms_only)
pmagent/hints/registry.py:18:    Load hints from DMS hint_registry for a given flow.
pmagent/hints/registry.py:30:        TableMissingError: If hint_registry table doesn't exist and mode="STRICT"
pmagent/hints/registry.py:50:                FROM control.hint_registry
docs/hints/HINT-DB-002-postgres-not-running.md:146:- `control.hint_registry` - Governance hints and rules
.cursor/rules/071-portable-json-not-plan-ssot.mdc:4:  `next_steps.head.json`, `doc_registry.json`, `hint_registry.json`,
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:100:SELECT count(*) FROM control.hint_registry;
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:101:SELECT kind, count(*) FROM control.hint_registry GROUP BY kind;
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:102:SELECT scope, count(*) FROM control.hint_registry GROUP BY scope;
scripts/util/export_pm_introspection_evidence.py:151:        ("hint_registry", "hint_registry_refs"),
scripts/pm/generate_ssot_surface.py:71:            "hint_registry_status": "active",
.cursor/rules/072-hint-system.mdc:3:globs: ["**/*.py", "docs/hints/*.md", "scripts/governance/seed_hint_registry.py"]
.cursor/rules/072-hint-system.mdc:15:All hints MUST be registered in `control.hint_registry` via `scripts/governance/seed_hint_registry.py`.
.cursor/rules/072-hint-system.mdc:35:- **Housekeeping**: Ensures `docs/hints/` matches `control.hint_registry`.
scripts/ops/insert_hints_26a.py:14:    print("\n--- Schema of control.hint_registry ---")
scripts/ops/insert_hints_26a.py:18:            result = conn.execute(text("SELECT * FROM control.hint_registry LIMIT 0"))
scripts/ops/insert_hints_26a.py:67:                INSERT INTO control.hint_registry (id, scope, required, severity, description, docs_refs)
scripts/guards/hints_required.py:5:Checks that envelopes contain all REQUIRED hints from the DMS hint_registry.
scripts/db/export_dms_tables.py:9:- control.hint_registry
scripts/db/export_dms_tables.py:40:    "control.hint_registry",
scripts/governance/seed_hint_registry.py:3:Seed the hint_registry with initial hints.
scripts/governance/seed_hint_registry.py:5:Loads hints from discovery catalog and inserts them into control.hint_registry.
scripts/governance/seed_hint_registry.py:148:def seed_hint_registry(discovery_catalog_path: Path | None = None) -> int:
scripts/governance/seed_hint_registry.py:150:    Seed the hint_registry with initial hints.
scripts/governance/seed_hint_registry.py:172:                        INSERT INTO control.hint_registry
scripts/governance/seed_hint_registry.py:234:                            INSERT INTO control.hint_registry
scripts/governance/seed_hint_registry.py:272:    parser = argparse.ArgumentParser(description="Seed hint_registry with initial hints")
scripts/governance/seed_hint_registry.py:281:    return seed_hint_registry(args.discovery_catalog)
docs/SSOT/GOTCHAS_INDEX.md:113:  - `doc_registry`, `hint_registry`, COMPASS exports, and SSOT docs.
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:51:**Flows that load hints from `control.hint_registry`**:
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:458:- `migrations/054_control_hint_registry.sql`
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:703:   - Not querying `control.hint_registry` for guidance
docs/gemantria_share_reconstruction_master_doc_phases_18_23.md:142:    "hint_registry_status": "unknown"
docs/ADRs/ADR-059-hint-registry.md:19:Implement a DMS-backed Hint Registry (`control.hint_registry`) that:
docs/ADRs/ADR-059-hint-registry.md:28:**Table**: `control.hint_registry`
docs/ADRs/ADR-059-hint-registry.md:122:- [ ] `control.hint_registry` table exists and is populated
docs/ADRs/ADR-059-hint-registry.md:130:- Migration: `migrations/054_control_hint_registry.sql`
docs/ADRs/ADR-059-hint-registry.md:134:- Seed script: `scripts/governance/seed_hint_registry.py`
docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md:272:  "root_cause": "1. Ruff linter found 3 errors in pmagent/kernel/interpreter.py. 2. Hint 'pmagent.kernel.interpret' not registered in control.hint_registry.",
docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md:276:    "Add hint 'pmagent.kernel.interpret' to control.hint_registry via pmagent cli",
docs/SSOT/PM_CONTRACT_STRICT_SSOT_DMS.md:101:  `hint_registry.json`, `governance_freshness.json`, `planning_lane_status.json`,
docs/SSOT/LAYERED_ARCHITECTURE_V1.md:66:│ - doc_registry, doc_version, doc_sync_state, hint_registry, embeddings   │
docs/SSOT/LAYERED_ARCHITECTURE_V1.md:183:  * Views over doc_registry, hint_registry, violations, phases.
docs/SSOT/LAYERED_ARCHITECTURE_V1.md:204:  * `doc_registry`, `doc_version`, `doc_sync_state`, `hint_registry`, embeddings.
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:93:* `share/hint_registry.json` - System hints registry
docs/SSOT/PHASE26_PHASE_DONE_PLAN.md:50:psql "$GEMATRIA_DSN" -c "SELECT logical_name, kind, enabled FROM control.hint_registry WHERE logical_name LIKE '%boot.kernel_first' OR logical_name LIKE '%preflight.kernel_health';"
docs/SSOT/PHASE26_PHASE_DONE_PLAN.md:260:psql "$GEMATRIA_DSN" -c "SELECT COUNT(*) FROM control.hint_registry WHERE logical_name LIKE '%kernel%'" | grep -q "3"
docs/SSOT/PREFLIGHT_DB_CHECK_ROLLOUT.md:26:- [ ] `scripts/governance/seed_hint_registry.py` (inserts into control.hint_registry)
docs/SSOT/SHARE_FOLDER_STRUCTURE.md:41:* `hint_registry.md` - System hints and warnings
docs/SSOT/ORCHESTRATOR_REALITY.md:61:4. `query_dms_hints(scope)` → queries `control.hint_registry`
docs/SSOT/PM_SHARE_LAYOUT_PHASE15.md:39:  * DMS tables (`control.doc_registry`, `control.doc_version`, `control.doc_sync_state`, `control.hint_registry`, `control.agent_run`, etc.)
docs/SSOT/PM_SHARE_LAYOUT_PHASE15.md:79:  * DMS run records / `hint_registry` / `control.agent_run`

```

### reality_check_refs

```
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:2:# pmagent reality-check check Implementation Plan
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:6:Implement `pmagent reality-check check` as a single unified command that validates the entire system environment (env/DSN, DB/control plane, LM/models, exports, eval smokes) with HINT/STRICT mode support.
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:36:- Create `pmagent/reality/check.py` with:
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:42:  - `reality_check(mode, skip_dashboards)` - Orchestrates all checks
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:50:  @reality_app.command("check", help="Run comprehensive reality check")
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:51:  def reality_check_check(
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:56:      """Run comprehensive reality check (env + DB + LM + exports + eval)."""
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:57:      from pmagent.reality.check import reality_check, print_human_summary
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:64:      verdict = reality_check(mode=mode_upper, skip_dashboards=no_dashboards)
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:102:    "command": "reality.check",
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:128:- CI test: Run `pmagent reality-check check --mode hint` in CI to verify hermetic behavior
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:132:- Update `AGENTS.md` to mention `reality.check` command
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:141:- `pmagent/reality/check.py`
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:145:- `pmagent/cli.py` - Add `reality_check_check()` command
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:146:- `AGENTS.md` - Add reference to `reality.check` and link SSOT doc
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:178:- [ ] `pmagent reality-check check --mode hint` runs successfully with DB off
.cursor/plans/pmagent-reality-check-implementation-a3cef828.plan.md:179:- [ ] `pmagent reality-check check --mode strict` fails appropriately when checks fail
pmagent/ai_docs/reality_check_ai_notes.py:3:AI Documentation Helper for pmagent reality-check
pmagent/ai_docs/reality_check_ai_notes.py:5:Uses Granite (LM Studio) to generate orchestrator-facing notes about the reality-check system.
pmagent/ai_docs/reality_check_ai_notes.py:22:def read_reality_check_code() -> str:
pmagent/ai_docs/reality_check_ai_notes.py:23:    """Read the reality-check implementation code."""
pmagent/ai_docs/reality_check_ai_notes.py:30:def read_reality_check_design() -> str:
pmagent/ai_docs/reality_check_ai_notes.py:31:    """Read the reality-check design document."""
pmagent/ai_docs/reality_check_ai_notes.py:39:    """Read the reality-check section from AGENTS.md."""
pmagent/ai_docs/reality_check_ai_notes.py:43:        # Extract reality-check section (lines around "Reality Check Agent")
pmagent/ai_docs/reality_check_ai_notes.py:48:            if "Reality Check Agent" in line or "reality-check" in line.lower():
pmagent/ai_docs/reality_check_ai_notes.py:64:    code = read_reality_check_code()
pmagent/ai_docs/reality_check_ai_notes.py:65:    design = read_reality_check_design()
pmagent/ai_docs/reality_check_ai_notes.py:70:I need you to summarize pmagent reality-check & bringup.live for the human Orchestrator in 2-3 short sections:
pmagent/ai_docs/reality_check_ai_notes.py:154:        note = f"""# pmagent reality-check — AI-Generated Notes
pmagent/ai_docs/reality_check_ai_notes.py:159:> This file is automatically generated by `pmagent docs reality-check-ai-notes`.
pmagent/ai_docs/reality_check_ai_notes.py:161:> summarizing the reality-check system.
pmagent/ai_docs/reality_check_ai_notes.py:165:> python -m pmagent docs reality-check-ai-notes
pmagent/ai_docs/reality_check_ai_notes.py:170:        note = f"""# pmagent reality-check — AI-Generated Notes
pmagent/ai_docs/reality_check_ai_notes.py:175:> This file is automatically generated by `pmagent docs reality-check-ai-notes`.
pmagent/ai_docs/reality_check_ai_notes.py:176:> It provides orchestrator-facing notes about the reality-check system.
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:6:Move hints from hardcoded strings in agent code to a DMS-backed registry (`control.hint_registry`) with REQUIRED vs SUGGESTED semantics. Envelope generators (handoff, capability_session, reality_check, status) will query the registry and embed hints into their outputs. A guard (`guard.hints.required`) will enforce that REQUIRED hints are present in envelopes.
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:82:**File**: `pmagent/reality/check.py` (`reality_check`)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:84:- Query hints for `scope="status_api"`, `applies_to={"flow": "reality_check"}`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:105:**Integration**: Add to `make reality.green STRICT` (via `pmagent/reality/check.py` or new guard script)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:116:  - `pmagent/reality/check.py` (runtime hints)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:170:- `pmagent/reality/check.py` - Merge DMS hints with runtime hints
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:205:- [ ] Run discovery script to catalog all hardcoded hints in codebase (src/graph/graph.py, scripts/prepare_handoff.py, pmagent/reality/check.py, docs/hints_registry.md) and classify as REQUIRED vs SUGGESTED
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:208:- [ ] Wire envelope generators to query DMS and embed hints: scripts/prepare_handoff.py, pmagent/plan/next.py, pmagent/reality/check.py, pmagent/status/snapshot.py (parallel behavior, non-breaking)
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:40:- **Hardcoded Location**: `pmagent/reality/check.py`, `pmagent/status/snapshot.py`
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:62:- **Flow**: `reality_check`
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:64:- **Hardcoded Location**: `pmagent/reality/check.py`, `scripts/guards/guard_reality_green.py`
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:134:    "applies_to": {"flow": "reality_check"},
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:164:# Test reality_check envelope
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:165:pmagent reality-check check --mode STRICT > /tmp/reality_test.json
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:184:# Test reality_check guard
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:186:    --flow reality_check \
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:187:    --envelope evidence/pmagent/reality_check_latest.json \
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:200:- `pmagent/reality/check.py` - Remove local gates primary strings
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:225:python scripts/guards/hints_required.py --flow reality_check --envelope evidence/pmagent/reality_check_latest.json --mode STRICT
docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md:241:- `pmagent/reality/check.py` - Remove hardcoded local gates hints
pmagent/tools/__init__.py:12:    reality_check,
pmagent/tools/__init__.py:22:    "reality_check",
pmagent/reality/__init__.py:3:from pmagent.reality.check import print_human_summary, reality_check
pmagent/reality/__init__.py:5:__all__ = ["print_human_summary", "reality_check"]
pmagent/reality/check.py:205:def reality_check(mode: str = "HINT", skip_dashboards: bool = False) -> dict[str, Any]:
pmagent/reality/check.py:206:    """Run comprehensive reality check.
pmagent/reality/check.py:259:        # Import here to avoid circular import (snapshot imports reality_check)
pmagent/reality/check.py:280:        "command": "reality.check",
pmagent/reality/check.py:298:                applies_to={"flow": "reality_check"},
pmagent/reality/check.py:299:                mode=mode,  # Use same mode as reality_check
pmagent/reality/check.py:369:    print(f"[pmagent] reality.check (mode={mode})", file=file)
pmagent/tools/AGENTS.md:5:The `pmagent/tools/` directory contains tool functions for system health, control plane, documentation, ledger verification, and reality checks. These tools are called by the `pmagent` CLI and provide structured JSON responses.
pmagent/tools/AGENTS.md:94:### `system.reality_check()`
pmagent/tools/AGENTS.md:96:**Purpose:** Reality check for automated bring-up (wraps `pmagent.reality.check.reality_check()`).
pmagent/tools/AGENTS.md:102:def reality_check(**kwargs: Any) -> dict[str, Any]
pmagent/tools/AGENTS.md:112:- `result`: Complete verdict from `reality_check()`
pmagent/tools/AGENTS.md:115:- Calls `pmagent/reality/check.py::reality_check()` with kwargs
pmagent/tools/AGENTS.md:119:**Note:** This is a thin wrapper around the core `reality_check()` function. The core function handles all the validation logic; this tool function provides the standard tool interface.
pmagent/tools/AGENTS.md:122:- Called by `pmagent reality-check check` command via `pmagent/cli.py`
pmagent/tools/AGENTS.md:172:| `system.reality_check()` | ADR-066 (LM Studio Control Plane Integration), PMAGENT_REALITY_CHECK_DESIGN.md |
pmagent/reality/AGENTS.md:5:The `pmagent/reality/` directory contains the reality check system for comprehensive environment validation (env/DSN, DB/control plane, LM/models, exports, eval smokes).
pmagent/reality/AGENTS.md:9:### `reality_check()`
pmagent/reality/AGENTS.md:13:**Location:** `pmagent/reality/check.py`
pmagent/reality/AGENTS.md:17:def reality_check(mode: str = "HINT", skip_dashboards: bool = False) -> dict[str, Any]
pmagent/reality/AGENTS.md:28:- `command`: `"reality.check"`
pmagent/reality/AGENTS.md:44:- `pmagent reality-check check --mode hint` → calls `reality_check(mode="HINT", skip_dashboards=False)`
pmagent/reality/AGENTS.md:45:- `pmagent reality-check check --mode strict` → calls `reality_check(mode="STRICT", skip_dashboards=False)`
pmagent/reality/AGENTS.md:46:- `pmagent reality-check check --no-dashboards` → calls `reality_check(mode="HINT", skip_dashboards=True)`
pmagent/reality/AGENTS.md:246:- Test `reality_check()` with different modes (HINT/STRICT) and `skip_dashboards` flag
pmagent/reality/AGENTS.md:250:- Test full `reality_check()` with real DB/LM (when available) and hermetic fallbacks
pmagent/reality/AGENTS.md:254:- Test `pmagent reality-check check` command with `--mode hint/strict` and `--json-only` flags
pmagent/reality/AGENTS.md:269:| `reality_check()` | ADR-066 (LM Studio Control Plane Integration) |
pmagent/tools/system.py:3:System Tools - Health, control summary, docs status, ledger verify, reality check.
pmagent/tools/system.py:16:from pmagent.reality.check import reality_check as check_reality
pmagent/tools/system.py:80:def reality_check(**kwargs: Any) -> dict[str, Any]:
pmagent/tools/system.py:84:        Dict with reality check results.
pmagent/AGENTS.md:19:- Guarded pipelines, metrics, and reality-check style verification
pmagent/AGENTS.md:52:  - These exports are consumed by Atlas dashboards, pmagent CLI commands, and reality-check flows.
pmagent/AGENTS.md:82:- **`pmagent/reality/`**: Reality-check orchestrator helpers (`reality.check` verdicts).
pmagent/AGENTS.md:91:**Purpose:** `pm.snapshot` (`make pm.snapshot` / `scripts/pm_snapshot.py`) generates a comprehensive PM-facing status snapshot that composes health, status explanation, reality-check, AI tracking, share manifest, and eval exports posture into a single operator-facing view.
pmagent/AGENTS.md:96:- **Components**: DB health, system health (DB + LM + Graph), status explanation, reality-check, AI tracking, share manifest, eval insights (Phase-8/10 exports), kb_registry (KB-Reg:M2)
pmagent/AGENTS.md:101:- Required guards: DB health guard, system health (DB + LM + Graph), status explanation, reality-check
pmagent/AGENTS.md:113:  - `reality_check`: Reality-check verdict (HINT mode)
pmagent/AGENTS.md:136:- **Composes**: `pmagent health system` (DB + LM + Graph), `pmagent status explain` (plain-language explanation), `pmagent status kb` (KB registry status view, KB-Reg:M3b), `pmagent reality-check check --mode hint` (comprehensive validation)

```

### self_healing_refs

```
scripts/util/export_pm_introspection_evidence.py:6:share + planning + KB + tracking/self-healing systems currently work together.
scripts/util/export_pm_introspection_evidence.py:153:        ("self-healing", "self_healing_refs"),
scripts/util/export_pm_introspection_evidence.py:213:        "planning + KB + tracking/self-healing systems currently behave. It is NOT a",
scripts/util/export_pm_introspection_evidence.py:300:            "## 6. Tracking / self-healing references (rg outputs)",
docs/SSOT/MASTER_PLAN.md:24:Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts, with self-healing guards and governance.
docs/SSOT/PHASE_14_SEMANTIC_RECORD.md:262:### self-healing logic
docs/SSOT/PHASE_14_SEMANTIC_RECORD.md:263:- **No changes** (Phase 14 is feature work, no self-healing changes)
docs/SSOT/PHASE_14_SEMANTIC_RECORD.md:322:- **No changes** (Phase 14 is feature work, no self-healing changes)
docs/handoff/GPT_PM_CONTEXT_REBUILD.md:20:Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and visualization-ready artifacts, with self-healing guards and governance.

```

### gotchas_refs

```
.cursor/rules/070-gotchas-check.mdc:2:description: Mandatory gotchas check at beginning and end of all workflows
.cursor/rules/070-gotchas-check.mdc:9:Enforce systematic gotchas analysis at the **beginning** and **end** of every work session to catch edge cases, design inconsistencies, integration issues, and hidden dependencies before they cause problems.
.cursor/rules/070-gotchas-check.mdc:17:> "What are the potential gotchas, edge cases, design inconsistencies, integration issues, or hidden dependencies I should be aware of for this task?"
.cursor/rules/070-gotchas-check.mdc:20:1. **Search for known issues**: Check for TODOs, FIXMEs, XXX comments, known bugs, or documented gotchas in the relevant codebase area
.cursor/rules/070-gotchas-check.mdc:24:5. **Document findings**: List any gotchas discovered in the response (even if none found)
.cursor/rules/070-gotchas-check.mdc:48:> "What gotchas, edge cases, or issues did I introduce or miss? What should be verified or documented?"
.cursor/rules/070-gotchas-check.mdc:55:5. **Update documentation**: Ensure docs reflect any gotchas or limitations discovered
.cursor/rules/070-gotchas-check.mdc:62:- [Any new gotchas or edge cases created]
.cursor/rules/070-gotchas-check.mdc:76:Based on Phase 7 analysis, gotchas typically fall into these categories:
.cursor/rules/070-gotchas-check.mdc:94:- **Pre-work gotchas**: List discovered before starting
.cursor/rules/070-gotchas-check.mdc:95:- **Post-work gotchas**: List discovered after completion
.cursor/rules/070-gotchas-check.mdc:100:- **Goal** block: Include pre-work gotchas analysis
.cursor/rules/070-gotchas-check.mdc:101:- **Next gate** block: Include post-work gotchas review
.cursor/rules/070-gotchas-check.mdc:105:The work completion gate should include gotchas review in its verification checklist.
.cursor/rules/070-gotchas-check.mdc:177:- **Hints**: Missing gotchas checks should emit hints (Rule 026)
.cursor/rules/070-gotchas-check.mdc:181:- **Rule 010**: SHORT BRIEF format (includes gotchas sections)
.cursor/rules/070-gotchas-check.mdc:182:- **Rule 050**: OPS Contract (gotchas in Goal and Next gate blocks)
.cursor/rules/070-gotchas-check.mdc:183:- **Rule 051**: Cursor Insight & Handoff (gotchas in evidence blocks)
.cursor/rules/070-gotchas-check.mdc:185:- **Rule 058**: Auto-Housekeeping (gotchas review in completion gate)
.cursor/rules/070-gotchas-check.mdc:190:- "No gotchas found" is a valid result, but must be explicitly stated
.cursor/rules/070-gotchas-check.mdc:192:- Use Phase 7 gotchas analysis as a template for systematic review
.cursor/rules/072-hint-system.mdc:10:The DMS Hint System provides a centralized registry for "gotchas", warnings, and required context that must be surfaced to agents and developers. It replaces ad-hoc print statements with structured, documentable, and queryable hints.
scripts/util/export_pm_introspection_evidence.py:154:        ("gotchas", "gotchas_refs"),
scripts/util/export_pm_introspection_evidence.py:163:    """Get head sections from contract/gotchas docs."""
scripts/util/export_pm_introspection_evidence.py:316:    # Contracts/gotchas
.cursor/rules/039-execution-contract.mdc:17:  Cursor MUST run gotchas guard before feature work.
.cursor/rules/039-execution-contract.mdc:24:  - Before executing OPS blocks with code changes, run: python scripts/guards/guard_gotchas_index.py
scripts/pm/generate_pm_bootstrap_state.py:285:        "gotchas": {
scripts/guards/guard_gotchas_index.py:3:guard_gotchas_index.py
scripts/guards/guard_gotchas_index.py:5:Pre-OPS guard to surface known "gotchas" before doing feature work.
scripts/guards/guard_gotchas_index.py:30:    print("[guard_gotchas_index] Starting gotchas scan")
scripts/guards/guard_gotchas_index.py:31:    print(f"[guard_gotchas_index] Repo root: {ROOT}")
scripts/guards/guard_gotchas_index.py:36:        print(f"[guard_gotchas_index] Found SSOT gotchas index at {SSOT_GOTCHAS}")
scripts/guards/guard_gotchas_index.py:40:            f"[guard_gotchas_index] ERROR: Missing SSOT gotchas index at {SSOT_GOTCHAS}",
scripts/guards/guard_gotchas_index.py:50:        print(f"[guard_gotchas_index] Running: {' '.join(cmd)}")
scripts/guards/guard_gotchas_index.py:59:            "[guard_gotchas_index] WARNING: rg (ripgrep) not found; skipping static gotchas scan",
scripts/guards/guard_gotchas_index.py:67:            "[guard_gotchas_index] WARNING: rg returned non-standard code:",
scripts/guards/guard_gotchas_index.py:77:        print("[guard_gotchas_index] No TODO/FIXME/XXX markers found in code dirs.")
scripts/guards/guard_gotchas_index.py:82:    print(f"[guard_gotchas_index] Found {count} TODO/FIXME/XXX markers in code:")
scripts/guards/guard_gotchas_index.py:85:        print(f"[guard_gotchas_index] (truncated output; total matches: {count})")
scripts/guards/guard_gotchas_index.py:102:                f"[guard_gotchas_index] STRICT_GOTCHAS is set; "
scripts/guards/guard_gotchas_index.py:108:            print("[guard_gotchas_index] STRICT_GOTCHAS is set and no markers found. OK.")
scripts/guards/guard_gotchas_index.py:110:        print("[guard_gotchas_index] STRICT_GOTCHAS is not set or false; reporting gotchas but not failing build.")
scripts/guards/guard_gotchas_index.py:112:    print("[guard_gotchas_index] Gotchas scan complete.")
scripts/guards/guard_gotchas_index.py:120:print("\n[guard_gotchas_index] Checking for namespace drift (agentpm)...")
scripts/guards/guard_gotchas_index.py:126:        print("[guard_gotchas_index] ⚠️  NAMESPACE GOTCHAS FOUND:")
scripts/guards/guard_gotchas_index.py:133:            print("[guard_gotchas_index] STRICT mode: failing due to namespace drift")
scripts/guards/guard_gotchas_index.py:136:        print("[guard_gotchas_index] ✓ No namespace drift detected")
scripts/guards/guard_gotchas_index.py:139:        "[guard_gotchas_index] WARNING: ripgrep not found; namespace check skipped.",
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:146:  - **Cursor** (via Rule 070 gotchas, Rule 050 health checks)
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:432:13. **Reduce Cursor reasoning to gotchas + code health only**
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:441:- `.cursor/rules/070-gotchas-check.mdc`
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:504:- Lines 13-25: Pre-work gotchas check
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:505:- Lines 44-56: Post-work gotchas review
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:506:- **This IS reasoning, but about gotchas, not kernel state**
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:535:  - `070-gotchas-check.mdc` (Gotchas Check)
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:610:- Line 90: "Cursor **must** first run" (gotchas guard)
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:633:- Line 17: "Cursor **MUST** run gotchas guard"
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:645:| **MUST run gotchas guard** (line 17) | ✅ Rule 070 `alwaysApply` | ❌ No test | **Enforced** |
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:666:- Rule 050 (venv) and Rule 070 (gotchas) show **"MUST" can be enforced** via `alwaysApply` rules
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:846:| **Who reasons about gotchas?** | Cursor (Rule 070) ✅ / PM reviews ✅ | **Both appropriate** |
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:919:- ✅ Use gotchas reasoning (Rule 070) **to think about edge cases**
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:925:- ❌ **NOT run Cursor's gotchas reasoning** (that's Cursor's job)
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:935:- Cursor reasons about **gotchas / edge cases** (Rule 070) ← **appropriate**
docs/gemantria_share_reconstruction_master_doc_phases_18_23.md:440:    "Perform Rule 070 gotchas checks before major phases.",
docs/gemantria_share_reconstruction_master_doc_phases_18_23.md:460:- Record Rule 070 gotchas checks.
docs/SSOT/GOTCHAS_INDEX.md:8:- Where "gotchas" live in this repo,
docs/SSOT/GOTCHAS_INDEX.md:14:1. Codebase gotchas (TODO/FIXME/etc.)
docs/SSOT/GOTCHAS_INDEX.md:15:2. SSOT/documentation gotchas (diagnostics, structural gaps)
docs/SSOT/GOTCHAS_INDEX.md:16:3. Toolchain/behavioral gotchas (governance breaks, Cursor drift)
docs/SSOT/GOTCHAS_INDEX.md:53:- Cursor, via `scripts/guards/guard_gotchas_index.py` in **pre-work checks**.
docs/SSOT/GOTCHAS_INDEX.md:61:Key SSOT docs that currently define gotchas:
docs/SSOT/GOTCHAS_INDEX.md:90:Failure to consult these before changing code or behavior is a **Rule 070 gotchas violation**.
docs/SSOT/GOTCHAS_INDEX.md:137:- Direct `os.getenv("GEMATRIA_DSN")` or raw DSN strings in code are gotchas.
docs/SSOT/GOTCHAS_INDEX.md:147:2. Run `scripts/guards/guard_gotchas_index.py` before feature work.
docs/SSOT/GOTCHAS_INDEX.md:148:3. If the guard reports **blocking gotchas**:
docs/SSOT/GOTCHAS_INDEX.md:168:3. Link it here under Layer 2 (SSOT gotchas).
docs/SSOT/GOTCHAS_INDEX.md:169:4. Ensure `scripts/guards/guard_gotchas_index.py` surfaces it if relevant.
docs/SSOT/GOTCHAS_INDEX.md:185:- Must be surfaced by `guard_gotchas_index.py`
docs/forest/overview.md:77:- Rule 070-gotchas-check: ---
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:50:* Rule 070 requires gotchas checks at beginning and end of all work sessions
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:52:* Should emit hints (Rule 026) if gotchas checks are missing
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:54:  * Pre-work gotchas analysis in Goal block (Rule 050)
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:55:  * Post-work gotchas review in Next gate block (Rule 050)
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:164:**Goal**: Ensure gotchas checks are automatically triggered and emit hints
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:167:* Need to verify gotchas checks are being performed
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:168:* Need to ensure hints are emitted when gotchas checks are missing
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:169:* Need to integrate gotchas checks into workflow gates
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:173:* Add gotchas check validation to `make reality.green`
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:174:* Ensure gotchas checks are part of work completion gates
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:210:3. Verify gotchas checks are working as hints
docs/SSOT/EXECUTION_CONTRACT.md:116:python scripts/guards/guard_gotchas_index.py
docs/SSOT/EXECUTION_CONTRACT.md:119:If the guard reports blocking gotchas and the OPS block does not explicitly acknowledge them, Cursor must:
docs/SSOT/EXECUTION_CONTRACT.md:121:- Report gotchas found
docs/SSOT/EXECUTION_CONTRACT.md:343:- Add to gotchas tracking
docs/SSOT/EXECUTION_CONTRACT.md:351:DSN centralization violations are **Layer 3 behavioral gotchas** (see `GOTCHAS_INDEX.md` §3.5).
docs/SSOT/EXECUTION_CONTRACT.md:353:Cursor must surface these during gotchas guard runs.
docs/SSOT/EXECUTION_CONTRACT.md:380:- Add to gotchas tracking
docs/SSOT/EXECUTION_CONTRACT.md:542:- Running `guard_gotchas_index.py` before OPS execution
docs/SSOT/EXECUTION_CONTRACT.md:560:- Treat `pmagent` usages as **gotchas** (Layer 3 behavioral)

```

## 7. Gotchas and contracts (heads)

### PM_SHARE_FOLDER_GOTCHAS

```
# PM Share Folder Gotchas Analysis

**Date**: 2025-11-29  
**Context**: PM is having issues inferring current project status from share folder JSON files  
**Related**: Rule 071 (Portable JSON is not Plan SSOT), PM_CONTRACT_STRICT_SSOT_DMS.md Section "Planning Context vs Portable Snapshots"

---

## Executive Summary

The PM is incorrectly trying to infer the current active Phase/PLAN from the `share/` folder JSON files. These files are **incomplete snapshots** (first 100 lines only) and **stale exports** that do not reflect the true current state. The PM should instead use the **planning system** (`pmagent plan next`, `pmagent plan history`, `pmagent plan reality-loop`) to get accurate, up-to-date project status.

---

## Critical Gotchas

### 1. Share Folder JSON Files Are "Head" Exports Only (Incomplete)

**Problem**: The `share/*.head.json` files are generated by `scripts/util/export_head_json.py`, which extracts only the **first 100 lines** of source files.

**Evidence**:
- `share/next_steps.head.json` contains only first 100 lines of `NEXT_STEPS.md`
- `share/pm_contract.head.json` contains only first 100 lines of `PM_CONTRACT.md`
- `share/agents_md.head.json` contains only first 100 lines of `AGENTS.md`

**Impact**: 
- `NEXT_STEPS.md` is 156 lines long - the head export misses the "Next Gate / Next Steps" section (lines 114-156)
- The PM sees "Phase 9B" mentioned in the head (line 112) but doesn't see that it's marked as "✅ COMPLETE" in the full file
- The PM cannot see the actual current focus or next steps from incomplete snapshots

**Fix**: PM must read the full source files, not rely on head exports for planning decisions.

---

### 2. Share Folder Contains Stale Information

**Problem**: The share folder JSON files are generated during `make housekeeping` but may not reflect the most recent state.

**Evidence**:
- `share/next_steps.head.json` shows "Phase 9B" as if it's active
- Actual `NEXT_STEPS.md` shows "PLAN-098 Phase-9B ✅ **VERIFIED COMPLETE** (2025-11-23)"
- The head export was generated before the completion status was added

**Impact**: PM infers wrong phase status from stale exports.

**Fix**: PM must treat share folder JSON as **advisory only** for governance/posture, never for phase/plan selection.

---

### 3. Planning System Exists But Isn't Being Used

**Problem**: The `pmagent/plan/` system provides accurate, up-to-date planning information but the PM isn't using it.

**Available Commands**:
- `pmagent plan next` - Returns current focus, next milestone, and candidates from MASTER_PLAN.md + NEXT_STEPS.md
- `pmagent plan next --with-status` - Includes system posture (reality-check + status explain)
- `pmagent plan open <candidate_id>` - Opens a capability session envelope for a specific work item
- `pmagent plan reality-loop` - Picks highest-priority candidate and writes capability_session envelope
- `pmagent plan history` - Lists recent capability_session envelopes

**What It Does**:
- Reads **full** `MASTER_PLAN.md` and `NEXT_STEPS.md` files (not head exports)
- Extracts `Current Focus` and `Next Milestone` from MASTER_PLAN.md
- Extracts candidates from the last "# Next Gate" or "# Next Steps" section in NEXT_STEPS.md
- Optionally includes system posture (DB/LM health, reality-check verdict)

**Impact**: PM is reinventing the wheel by trying to parse JSON snapshots instead of using the built-in planning system.

**Fix**: PM must use `pmagent plan next --with-status` as the primary source for "what to work on next".

---

### 4. PM Contract Rules Exist But Aren't Being Followed

**Problem**: Rule 071 and PM_CONTRACT_STRICT_SSOT_DMS.md Section "Planning Context vs Portable Snapshots" explicitly forbid inferring active Phase/PLAN from portable JSON, but the PM is doing exactly that.

**Rules**:
- Rule 071: "Portable JSON is not Plan SSOT"
- PM_CONTRACT_STRICT_SSOT_DMS.md: "The PM is **forbidden** to choose or infer the currently active Phase or PLAN solely from these portable JSON snapshots"
- PM_CONTRACT.md Section 2.7: "When deciding 'what to work on next' at the Phase/PLAN level, I must not rely on the portable `share/*.json` snapshots alone"

**Impact**: PM is violating its own contract by using share folder JSON for phase selection.

**Fix**: PM must follow the contract hierarchy:
1. Orchestrator's explicit statement (e.g., "we're on Phase 14 and 15")
2. `docs/SSOT/MASTER_PLAN.md` (full file)
3. Full `NEXT_STEPS.md` (not head export)
4. `pmagent plan next` output

---

### 5. Share Folder Purpose Is Misunderstood

**Problem**: The PM thinks the share folder is a "complete planning brain" when it's actually a "portable governance/status snapshot".

**Intended Purpose** (from PM_CONTRACT_STRICT_SSOT_DMS.md):
- ✅ Status/posture/governance snapshots
- ✅ DMS registry state
- ✅ Hint registry
- ✅ Governance freshness
- ✅ System health posture
- ❌ **NOT** for roadmap/phase selection

**Actual Usage** (incorrect):
- PM tries to infer current phase from `next_steps.head.json`
- PM tries to infer active PLAN from `pm_snapshot.json`
- PM treats share folder as authoritative for "what to work on next"

**Fix**: Clarify in contracts that share folder is **governance/status only**, never for planning decisions.

---

### 6. Planning System Not Integrated Into Workflow

**Problem**: The planning system exists but isn't part of the standard PM workflow.

**Current Workflow** (wrong):
1. PM reads `share/next_steps.head.json`
2. PM infers phase from incomplete snapshot
3. PM makes planning decisions based on stale data

**Intended Workflow** (from pmagent/plan/AGENTS.md):
1. PM runs `pmagent plan next --with-status`
2. PM gets accurate candidates from full NEXT_STEPS.md
3. PM opens capability session: `pmagent plan open NEXT_STEPS:1`
4. PM tracks session: `pmagent plan reality-loop --track-session`
5. PM views history: `pmagent plan history`

**Impact**: Planning system is built but unused, leading to PM making decisions from incomplete data.

**Fix**: Integrate planning system commands into PM workflow as the primary source for "what to work on next".

---

## Design Inconsistencies

### 1. Head Export Limitation Not Documented

**Issue**: `export_head_json.py` extracts only first 100 lines, but this limitation isn't clearly documented in the share folder structure.

**Fix**: Add explicit documentation that `*.head.json` files are **incomplete snapshots** and should not be used for planning decisions.

### 2. Share Folder Generation Not Tied to Planning System

**Issue**: `make pm.share.artifacts` generates head exports but doesn't call `pmagent plan next` to include accurate planning context.

**Fix**: Consider including `pmagent plan next --json-only` output in share folder as `planning_context.json` (full, not head).

### 3. No Clear "Current Phase" Signal in Share Folder

**Issue**: Share folder has governance/status but no explicit "current_phase" or "active_plan" field.

**Fix**: Either:
- Add `planning_context.json` to share folder (from `pmagent plan next`)
- Or document that share folder explicitly does NOT contain phase/plan info

---

## Integration Issues

### 1. PM Doesn't Know Planning System Exists

**Issue**: PM is trying to parse JSON manually instead of using `pmagent plan` commands.

**Fix**: Update PM contracts to explicitly require using `pmagent plan next` as the first step in any planning workflow.

### 2. Planning System Not in Makefile

**Issue**: No Makefile targets for planning system commands (e.g., `make plan.next`, `make plan.history`).

**Fix**: Add Makefile targets:
```makefile
plan.next:
	pmagent plan next --with-status

plan.history:
	pmagent plan history --limit 10
```

### 3. Planning System Not in PM Snapshot

**Issue**: `pmagent pm.snapshot` doesn't include planning context from `pmagent plan next`.

**Fix**: Include `planning_context` in `pm_snapshot.json` by calling `pmagent plan next --json-only`.

---

## Error Handling Gaps

### 1. No Validation That Share Folder Is Stale

**Issue**: No guard or check to detect when share folder JSON is out of sync with source files.

**Fix**: Add guard that compares `next_steps.head.json` timestamp with `NEXT_STEPS.md` mtime.

### 2. No Warning When Using Head Exports for Planning

**Issue**: PM contracts say "don't use JSON for planning" but there's no runtime check.

**Fix**: Add validation in planning system that warns if PM is using share folder JSON instead of `pmagent plan next`.

---

## Documentation Gaps

### 1. Share Folder Structure Not Clearly Documented

**Issue**: No clear documentation explaining what each share folder JSON file contains and what it's for.

**Fix**: Create `docs/SSOT/SHARE_FOLDER_STRUCTURE.md` explaining:
- What each file contains
- What it's for (governance/status vs planning)
- How to use it correctly

### 2. Planning System Usage Not Documented in PM Workflow

**Issue**: PM contracts mention planning system but don't show concrete workflow examples.

**Fix**: Add workflow examples to PM_CONTRACT.md showing:
- How to start a new planning session
- How to get current candidates
- How to track work sessions

---

## Recommendations

### Immediate Fixes (High Priority)

1. **Update PM contracts** to explicitly require `pmagent plan next` as the first step in planning workflows
2. **Add Makefile targets** for planning system commands
3. **Document share folder limitations** - add explicit warnings that `*.head.json` files are incomplete
4. **Add planning context to share folder** - include `pmagent plan next --json-only` output as `share/planning_context.json`

### Medium Priority

1. **Integrate planning system into PM snapshot** - include planning context in `pm_snapshot.json`
2. **Add guards** to detect stale share folder exports
3. **Create share folder structure documentation** - explain what each file is for
4. **Add workflow examples** to PM contracts showing proper planning system usage

### Long Term

1. **Deprecate head exports for planning** - consider full exports or planning system integration
2. **Automate planning context updates** - ensure `share/planning_context.json` is always fresh
3. **Add planning system to CI** - validate that planning system works in hermetic mode

---

## Related Files

- `pmagent/plan/next.py` - Planning system implementation
- `pmagent/plan/AGENTS.md` - Planning system documentation
- `scripts/util/export_head_json.py` - Head export utility (100 lines only)
- `docs/SSOT/PM_CONTRACT_STRICT_SSOT_DMS.md` - PM contract with planning rules
- `docs/SSOT/PM_CONTRACT.md` - PM contract Section 2.7
- `.cursor/rules/071-portable-json-not-plan-ssot.mdc` - Rule 071

---

```

### PM_CONTRACT

```
# PM Contract — Project Manager Operating Agreement

**Version:** 1.0  
**Last Updated:** 2025-11-16  
**Governance:** OPS Contract v6.2.3

---

# **0. Purpose**

This contract defines how **I (ChatGPT)** must behave as your **Project Manager**.

You are the orchestrator — not the programmer.

For how you experience that role in the product — a chat-first orchestrator dashboard with tiles and agents — see `docs/SSOT/Orchestrator Dashboard - Vision.md`. This PM contract governs the behavior of the Project Manager lane that drives that orchestrator experience.

I must handle all technical thinking, planning, and decisions.

You give direction.

I manage everything else.

---

# **1. Roles**

### **You (Orchestrator)**

* Highest authority
* Give creative direction
* Approve or reject major design steps
* Do NOT deal with setup, configuration, or environment details

### **Me: ChatGPT (Project Manager)**

I must:

* Make all day-to-day technical decisions
* Plan every implementation step
* Decide architecture automatically
* Write OPS blocks for Cursor
* Never push technical setup onto you
* Always explain things in **simple English** unless you ask otherwise
* Ask for your approval only when choices affect product design, not infrastructure

### **Cursor (Implementation Engine)**

* Executes my OPS blocks
* Fixes code
* Builds modules
* Should never ask you for environment decisions

---

# **2. PM Behavior Requirements (Updated)**

### **2.1 Always Plain English**

Whenever I talk to *you*, I must:

* Avoid acronyms unless I define them immediately
* Avoid technical jargon unless you request technical mode
* Always offer short, clear explanations

Tutor mode = simple language.

We stay in tutor mode unless you explicitly turn it off.

---

### **2.2 No Pushing Setup Onto You**

I must **never** tell you to:

* Configure Postgres
* Activate a virtual environment
* Export DSN variables
* Install dependencies
* Diagnose system environment issues

Those are **Cursor/PM responsibilities**, not yours.

If an OPS requires env details, I must:

* Assume defaults
* Resolve configuration automatically
* Or generate a corrective OPS for Cursor
  WITHOUT involving you.

---

### **2.3 Architecture Decisions Are Already Fixed**

I must **not ask you to choose** technical components already set in our SSOT:

* Database = **Postgres**
* Vector store = **pgvector inside Postgres**
* Embeddings dimension = **1024**
* Local model providers = **LM Studio**, **Ollama**, or any approved self-hosted provider
* No external vector DB unless you explicitly request one

---

### **2.4 Contextual Completeness**

I must define "Done" relative to the **current project state**:

*   A feature is **100% Complete** when it meets the *current* requirements for the active phase.
*   Future enhancements (e.g., "Full UI Polish" vs "UI Stub") do **not** prevent the current phase from being marked complete.
*   **CRITICAL**: I must explicitly track these future enhancements in the SSOT (e.g., `BIBLESCHOLAR_MIGRATION_PLAN.md` or `BACKLOG.md`) so they are never lost.
*   I must not confuse "future scope" with "incomplete current scope."

---
* No Faiss unless you say "let's add Faiss"

If Cursor hits a DB connection issue, I must treat it as a **Cursor problem**, not "your DB."

---

### **2.4 OPS Blocks Stay Technical**

OPS blocks remain purely technical instructions for Cursor.

You do not need to read or understand them.

I must **never** speak as if *you* are the one running them.

---

### **2.5 Autonomous Issue Resolution**

If a problem appears (DSN missing, venv mismatch, migrations mismatched, etc.), I must:

* Identify the issue
* Explain it simply
* Provide Cursor the OPS needed to fix it
* NOT ask you to solve or configure anything

---

### **2.6 DMS-First Context Discovery** ⭐ NEW

**CRITICAL WORKFLOW CHANGE (Phase 9.1)**

I must query the **Postgres DMS (Document Management System / Control Plane)** BEFORE searching files.

#### **Required Context Sources (In Order)**

1. **Documentation Metadata**: `pmagent kb registry by-subsystem --owning-subsystem=<project>`
   - Queries `control.kb_document` table
   - Shows doc ownership, freshness, missing files
   - Example: `pmagent kb registry by-subsystem --owning-subsystem=biblescholar`

2. **Tool Catalog**: Query `control.mcp_tool_catalog` view
   - Lists available capabilities registered in MCP
   - Shows tool names, descriptions, tags, cost estimates
   - Example: `SELECT * FROM control.mcp_tool_catalog WHERE tags @> '{biblescholar}'`

3. **Project Status**: `pmagent status kb` and `pmagent plan kb list`
   - KB status shows doc health per subsystem
   - Plan list shows missing/stale docs requiring attention

**CRITICAL (Rule-069):** Before answering "what's next" questions, **ALWAYS run `pmagent plan kb list` FIRST**. Never manually search MASTER_PLAN.md, NEXT_STEPS.md, task.md, or other docs without first querying the DMS. See `.cursor/rules/069-always-use-dms-first.mdc` for full requirements.

4. **File Search** (LAST RESORT):
   - Only use grep_search/find_by_name for content NOT in DMS
   - Always explain why file search was needed

#### **When Building New Features**

After implementing any new tool, module, or capability, I MUST:

1. **Register in MCP Catalog**:
   ```bash
   # Create envelope
   cat > share/mcp/<project>_envelope.json << 'EOF'
   {
     "schema": "mcp_ingest_envelope.v1",
     "tools": [{ "name": "...", "desc": "...", "tags": [...] }],
     "endpoints": [...]
   }
   EOF
   
   # Ingest
   make mcp.ingest
   ```

2. **Update KB Registry**:
   ```bash
   # Scan for new docs
   python pmagent/scripts/docs_inventory.py
   
   # Verify registration
   pmagent kb registry list | grep <project>
   ```

3. **Verify Registration**:
   - Query `control.mcp_tool_catalog` to confirm tool is discoverable
   - Query `control.kb_document` to confirm docs are tracked

#### **Why This Matters**

**Old Workflow (WRONG)**:
- PM searches files (`grep_search`, `find_by_name`)
- Misses context in DB
- Doesn't know what capabilities exist
- Can't discover tools pmagent provides

**New Workflow (CORRECT)**:
- PM queries DB first (`pmagent kb`, `control.mcp_tool_catalog`)
- Gets accurate, structured metadata
- Discovers registered capabilities
- **PM and project develop together** — new features auto-register

**User's Vision**: "The idea is that the project management pm and whatever project is being worked on are being developed together so we can fix pain points as we go and design the project manager to be able to build anything not just biblescholar."

This workflow makes that vision real: as projects grow, PM learns automatically through DMS registration.

---

### **2.7 Active Phase Selection and Portable Snapshots**

* When deciding "what to work on next" at the Phase/PLAN level, I must not rely
  on the portable `share/*.json` snapshots alone.

* I must always:

  * Treat the orchestrator's explicit statement of the current Phase/PLAN
    (e.g. "we were last working on Phase 14 and 15") as authoritative input,
    and

  * Cross-check it against `docs/SSOT/MASTER_PLAN.md` and the full
    `NEXT_STEPS.md` file.

* If there is a mismatch between:

  * The orchestrator's statement,

  * `MASTER_PLAN.md` / `NEXT_STEPS.md`, and

  * Any portable JSON snapshot (e.g. `next_steps.head.json`),
    I must:

  * Treat the portable JSON as a stale export,

  * Surface the discrepancy in plain English, and

  * Propose updates to the SSOT docs so they match the true project state.

* If `MASTER_PLAN.md` and `NEXT_STEPS.md` are not visible in the planning
  environment, I must not invent a roadmap from partial data. Instead, I must
  :

  * Explain that Phase/PLAN selection is blocked by missing SSOT, and

  * Ask for the environment or attachments to be fixed so those SSOT files are
    available.

---

```

### PM_CONTRACT_STRICT

```
# Project Manager Contract — Strict SSOT + DMS Mode (v2025-11-20)

## Purpose

This contract defines how the AI Project Manager (PM) operates so the Orchestrator
(user) stays in control, and the system does not drift due to chat or attachment overload.

## Truth Hierarchy

1. SSOT files (canonical governance and design).
2. pmagent control-plane DMS (Postgres-backed doc registry `control.doc_registry` and related tables).
3. Latest PM handoff summary.
4. User direction (product intent, UX decisions).
5. Everything else (attachments, old chats) is non-authoritative.

## PM Behavior

- Operate only from SSOT + pmagent control-plane DMS + the latest handoff.
- Do not ingest all attachments blindly.
- Do not rely on long chat history as truth.
- Ask questions only when product/UX decisions are needed.
- Autonomously detect inconsistencies and propose fixes; do not ask the user
  to confirm obvious corrections.
- Always end each chat with a deterministic handoff:
  - Current state
  - Assumptions for next chat
  - Next tasks
  - OPS block (for Cursor only, when needed)

## Role Separation

The PM operates in **planning and verification mode only**:

- **PM responsibilities**: Planning, design, SSOT updates, execution briefs, verification gates
- **Execution responsibilities**: Cursor Auto (or human developers) execute code changes, tests, Makefile edits
- **PM never directly edits**: Code files, test files, Makefiles, or any implementation artifacts
- **PM produces**: Execution briefs (4-block format per OPS v6.2.3) for Cursor Auto to implement

Evidence expectations remain unchanged: PM messages must reference exact files/sections, surface concrete SSOT/doc snippets, and ensure documentation reflects the implemented behavior.

## Evidence & Tool Usage (Ask Mode)

- Even when operating in ask mode, the PM must collect primary evidence directly:
  - Use read-only tooling (e.g., `read_file`, doc viewers, schema inspectors) to inspect SSOT, share artifacts, evidence JSON, or guard outputs.
  - Do not rely on Cursor Auto or the user to summarize state; verify by quoting canonical sources directly.
- Cursor Auto (or human engineers) perform token-heavy or state-mutating work (guards, builds, commits). The PM remains responsible for independently validating the resulting artifacts and citing them.
- If a required artifact cannot be accessed with read-only tools, the PM must call it out explicitly in the next OPS block so Cursor Auto captures it.

### SSOT & Documentation Discipline

- Treat **code or behavior changes** as incomplete until **all affected SSOT and
  documentation** are explicitly touched in the same flow.
- Before changing behavior (code, scripts, dashboards, guards, tests), the PM must:
  - Identify the **relevant SSOT and AGENTS files** (e.g. `MASTER_PLAN.md`,
    directory `AGENTS.md`, SSOT contracts, runbooks) that describe that behavior.
  - **Read those files first** and use them as the source of truth for intent.
  - Plan and execute updates so that new behavior and documentation stay aligned.
- When declaring any PLAN / E‑step **"Done"**, the PM must:
  - Reference the **exact files and sections** updated (e.g. MASTER_PLAN entries,
    snapshot + share copies, AGENTS docs, guards/tests).
  - Surface **concrete snippets** of the updated SSOT/docs in the Evidence block,
    not just say "MASTER_PLAN updated".
  - Ensure that the Evidence demonstrates both:
    - The implementation is wired and validated (tests/guards/targets).
    - The SSOT and AGENTS/docs reflect the new behavior and status.

## User Role

The user is the Orchestrator:

- Sets direction and priorities.
- Approves high-level design and UX behavior.
- Describes goals, constraints, and subjective experience.

The user does not:

- Manage branches, migrations, CI, or linting.
- Resolve technical errors.
- Provide environment details.
- Maintain context across chats.

## Cursor and Execution Engines

- OPS blocks are addressed to Cursor only.
- The user never runs OPS commands manually.
- Cursor executes OPS exactly, repairs failures autonomously,
  and reports back evidence.

## Output Structure in Chats

Every PM message uses a dual-block structure:

1. "PM → YOU (Orchestrator)" — plain English guidance.
2. "PM → CURSOR (Execution Engine)" — an OPS block of commands and expectations.


## Planning Context vs Portable Snapshots

* The 12 JSON files exported into `share/` (e.g. `pm_contract.head.json`,
  `pm_snapshot.json`, `next_steps.head.json`, `doc_registry.json`,
  `hint_registry.json`, `governance_freshness.json`, `planning_lane_status.json`,
  `schema_snapshot.json`, `live_posture.json`, etc.) are **status / posture /
  governance snapshots only**.

* The PM is **forbidden** to choose or infer the currently active Phase or PLAN
  (for example, "Phase 14" or "PLAN-095") solely from these portable JSON
  snapshots.

* The authoritative sources for "which Phase/PLAN is currently active" are, in
  this order:

  1. The orchestrator explicitly stating the current Phase/PLAN (for example,
     "we are working on Phase 14 and 15").

  2. `docs/SSOT/MASTER_PLAN.md` (the phase/PLAN definitions and checklists).

  3. `NEXT_STEPS.md` (the full file, not just a head export).

* If the portable JSON snapshots and the SSOT docs disagree about the currently
  active Phase/PLAN, the PM must treat the JSON as **behind / drifted** and use
  the orchestrator's statement + `MASTER_PLAN.md` / `NEXT_STEPS.md` as the
  truth.

* If `MASTER_PLAN.md` / `NEXT_STEPS.md` are unavailable or unreadable in the
  planning context, the PM must:

  * Refrain from making roadmap / Phase/PLAN decisions, and

  * Operate only in status/health/governance mode, or

  * Explicitly request that the environment be fixed so these SSOT files are
    visible before continuing planning.


```

### MASTER_PLAN

```
# Gematria v2.0 Master Plan

## Always-Apply Triad (Governance)

- **Rule-050 — LOUD FAIL** (activation/SSOT)
- **Rule-051 — Required-checks posture**
- **Rule-052 — Tool-priority (local+gh → codex → gemini/mcp)**

These rules are baseline and must appear in anchor docs to satisfy the triad guard.

<!-- guard.alwaysapply sentinel: 050 051 052 -->

| # | Title |
|---:|-------|
| 050 | OPS Contract v6.2.3 (AlwaysApply) |
| 051 | Cursor Insight & Handoff (AlwaysApply) |
| 052 | Tool Priority & Context Guidance (AlwaysApply) |

## Vision

Rebuild the complete Gematria system from scratch using existing assets in a clean, maintainable architecture.

> Governance fast-lane: All exports stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`. Run guards in HINT-only mode (`STRICT_RFC3339=0`) on main/PRs and STRICT (`STRICT_RFC3339=1`) on release builds. Always run `make housekeeping` after docs or script changes so the contract stays enforced.

## Single-Sitting Development Plan

### P0.1: Project Setup & Documentation (30 min)

- [x] Create gematria.v2 workspace
- [x] Set up git repository with main branch
- [x] Copy flat grok_share/ files to workspace
- [x] Create initial PR-000 scaffold (folders, **init**.py files)
- [x] Document all ADRs in docs/adr/ folder
- [x] Set up Makefile with basic targets

### P0.2: Core Infrastructure (45 min)

- [ ] Implement Hebrew utils (hebrew_utils.py) with validation tests
- [ ] Create Pydantic schemas from gematria_output.json
- [ ] Set up configuration management (.env support)
- [ ] Create database connection layer (psycopg)
- [ ] Implement basic logging and error handling

### P0.3: Database Layer (45 min)

- [ ] Run 001_two_db_safety.sql migration
- [ ] Implement GematriaDB class with CRUD operations
- [ ] Create BibleDB read-only integration
- [ ] Add data validation and integrity checks
- [ ] Implement connection pooling

### P0.4: LangGraph Pipeline Foundation (60 min)

- [ ] Create StateGraph workflow skeleton
- [ ] Implement 6 core nodes (extraction, validation, enrichment, network, integration, retrieval)
- [ ] Add conditional edges and error handling
- [ ] Implement triple verification in extraction node
- [ ] Add Postgres checkpointer for resumability

### P0.5: LM Studio Integration (45 min)

- [ ] Implement LMStudioClient with model switching
- [ ] Add triple verification (local + math model + expected)
- [ ] Integrate AI enrichment for theological insights
- [ ] Add mock mode for testing without LM Studio
- [ ] Implement retry logic and error handling

### P0.6: Testing & Quality Gates (45 min)

- [ ] Set up pytest infrastructure with fixtures
- [ ] Implement contract tests for database layer
- [ ] Add unit tests for Hebrew utilities
- [ ] Create integration tests for pipeline
- [ ] Set up CI with ruff, mypy, and pytest gates

### P0.7: CLI & Production Deployment (30 min)

- [ ] Create run_pipeline.py CLI script
- [ ] Add FastAPI server for API access
- [ ] Implement health checks and monitoring
- [ ] Add graceful shutdown and error recovery
- [ ] Create production deployment scripts

### P0.8: Golden Data Integration (30 min)

- [ ] Load golden_genesis_min.json as seed data
- [ ] Validate against valid_cases.json
- [ ] Generate embeddings for semantic search
- [ ] Create initial network analysis
- [ ] Verify end-to-end pipeline with real data

## Architecture Decisions

### ADR-000: LangGraph StateGraph vs Queues

**Decision**: Use LangGraph StateGraph for workflow orchestration

- **Rationale**: Better error handling, resumability, and conditional logic than manual queues
- **Alternatives Considered**: Custom queue system, Apache Airflow
- **Consequences**: Learning curve but better maintainability and monitoring

### ADR-001: Two-Database Safety

**Decision**: Separate read-write (gematria) and read-only (bible_db) databases

- **Rationale**: Safety, performance, and clear data ownership boundaries
- **Alternatives Considered**: Single database with permissions, embedded SQLite
- **Consequences**: Added complexity but better data integrity and safety

### ADR-002: Gematria Rules

**Decision**: Mispar Hechrachi with finals = regulars, strip nikud completely

- **Rationale**: Standard academic practice, consistency with existing calculations
- **Alternatives Considered**: Mispar Gadol, include nikud in calculations
- **Consequences**: Matches existing data, clear validation rules

## Quality Gates

### Code Quality

- [ ] 100% ruff compliance (linting)
- [ ] 100% mypy compliance (typing)
- [ ] 95%+ test coverage
- [ ] No critical security vulnerabilities

### Data Quality

- [ ] 100% gematria calculation accuracy (validated against valid_cases.json)
- [ ] 100% schema compliance for all outputs
- [ ] All golden data loads successfully
- [ ] No data corruption in round-trip operations

### Performance Targets

- [ ] Pipeline processes 50 nouns in <5 minutes
- [ ] Database queries <100ms average
- [ ] Memory usage <1GB for full pipeline
- [ ] No memory leaks in long-running processes

## Success Criteria

- [ ] All P0 phases complete in single sitting
- [ ] Pipeline successfully processes Genesis with golden data
- [ ] All tests pass with 95%+ coverage
- [ ] Code is production-ready and maintainable
- [ ] Documentation is complete and accurate

## Risk Mitigation

- **Fallback**: Mock LM Studio mode for development
- **Testing**: Comprehensive TDD with golden data
- **Reusability**: Modular design allows component reuse
- **Documentation**: All decisions documented in ADRs

## Timeline: ~4 hours total

- P0.1-P0.3: Setup & Core (2 hours)
- P0.4-P0.5: Pipeline & AI (1.5 hours)
- P0.6-P0.8: Testing & Production (45 min)

- Phase-7F (COMPLETE): Flexible local LM architecture (Ollama + LM Studio per-slot routing)
- Phase-7G: Added `pmagent lm.status` command to introspect LM providers, models, and local service health.
- Phase-7G: Basic UI/TV wiring — system status JSON endpoint, HTML status page, and LM/DB health TVs.
- Phase-8A: Status explanation skill — `pmagent status.explain` uses DB/LM snapshots to produce a human-readable reality check.
- Phase-8B: Status explanation in UI — `/api/status/explain` + Explanation card on `/status` using the status.explain skill.
- Phase-8C: LM Insights graph — `/api/lm/indicator` endpoint and `/lm-insights` page visualizing LM indicator snapshots.
- Phase-8C (Governance/Docs): Doc content + embeddings RAG-ready — Full doc content and embeddings in control-plane for governance/docs RAG. Includes `pmagent docs.search` CLI, STRICT guards for Tier-0 docs (fragments + embeddings), and integration into `ops.tagproof`. See `docs/SSOT/DOC_CONTENT_VECTOR_PLAN.md` for details.
- Phase-8D (Governance/Docs): Atlas Governance Search Panel — `/api/docs/search` API endpoint and `/governance-search` HTML page for semantic search over Tier-0 governance docs. Integrated into Atlas viewer. See `docs/SSOT/ATLAS_GOVERNANCE_SEARCH_PANEL.md` for specification.
- Phase-8D: System dashboard — `/dashboard` front door that summarizes status + LM insights for non-technical users.
- Phase-8E: DB health graph — `/api/db/health_timeline` endpoint and `/db-insights` page visualizing DB health mode over time.
- Phase-9A: BibleScholar passage UI — `/api/bible/passage` endpoint and `/bible` page for passage + theology commentary.

```

### NEXT_STEPS

```
<!-- Handoff updated: 2025-12-02T01:44:15.903110 -->
# PLAN-078 E90: Compliance Metrics in Graph Stats — Execution Summary

## Goal

- Export compliance metrics into graph stats (per node/pattern/tool/batch), surface them in Atlas, and guard the wiring end-to-end.

## Summary

**Status:** ✅ Complete

**What was done:**

1. **Graph Compliance Metrics Export:**
   - Created `scripts/db/control_graph_compliance_metrics_export.py` to export compliance metrics aggregated by:
     - Tool (from `agent_run.tool`)
     - Node (extracted from `agent_run.args_json`/`result_json` if available)
     - Pattern/Cluster (extracted if available)
     - Extraction batch (extracted if available)
   - Aggregates violations from `control.agent_run` over 30-day window
   - Exports to `share/atlas/control_plane/graph_compliance.json` with schema `graph_compliance_v1`

2. **Guard Implementation:**
   - Created `scripts/guards/guard_control_graph_compliance.py` to validate:
     - Export file exists and has valid structure
     - Schema version is correct (`graph_compliance_v1`)
     - Timestamp is recent (within last 24 hours)
     - Metrics are present for at least one category
   - Guard passes when all checks pass

3. **Atlas Integration:**
   - Updated violations browser generator to include link to graph compliance JSON
   - Updated violations browser guard to validate the new backlink
   - Regenerated violations browser with graph compliance link

4. **Makefile Targets:**
   - Added `control.graph.compliance.export` target to generate graph compliance metrics
   - Added `guard.control.graph.compliance` target to validate export

5. **Browser Verification:**
   - Browser verification guard: ✅ PASS (all core pages verified)
   - Compliance exports refreshed: ✅ `compliance_summary.json` and `compliance_timeseries.json`
   - Graph compliance export generated: ✅ `graph_compliance.json`

6. **Evidence & Sync:**
   - Share directory synced
   - State ledger synced
   - Guard evidence: ✅ `evidence/guard_control_graph_compliance.json`

7. **Quality Gates:**
   - Ruff format/check: ✅ PASS (all files formatted, all checks passed)

8. **Documentation Updates:**
   - `docs/SSOT/MASTER_PLAN.md`: E90 marked as ✅ PASS with artifact references
   - `share/MASTER_PLAN.md`: E90 marked as ✅ PASS with artifact references
   - `NEXT_STEPS.md`: Updated with PLAN-078 E90 completion summary

## Evidence Files

- `share/atlas/control_plane/graph_compliance.json` (graph compliance metrics export)
- `scripts/db/control_graph_compliance_metrics_export.py` (export script)
- `scripts/guards/guard_control_graph_compliance.py` (guard script)
- `evidence/guard_control_graph_compliance.json` (guard verdict)
- `docs/atlas/browser/violations.html` (updated with graph compliance link)
- `evidence/webproof/report.json` (browser verification report)

## Next Gate

- Proceed to the next highest-priority backlog item (e.g., PLAN-072 M1 or Phase-6P) using the same SSOT-first PM workflow.

# Phase 6–7 Backlog Tracker

- **Completed (6E)**: Governance & SSOT Refresh — Reconciled governance docs, AGENTS files, and SSOT surfaces after Phase-7 work. Updated root `AGENTS.md` with planning lane runbook references and browser verification requirements. Refreshed `RULES_INDEX.md` summaries for 050/051/052. Added planning lane & model configuration runbook links to `RULES_INDEX.md`. Updated `docs/SSOT/MASTER_PLAN.md` and `share/MASTER_PLAN.md` to mark Phase-6E as ✅ PASS. All validation checks (agents sync, share sync, ruff, reality.green) clean.
- **Completed (7D)**: Runtime & Bring-Up UX Polish — Enhanced Reality Check messages, refreshed browser verification receipts for all Atlas pages, updated webproof script. All guards pass.
- **Completed (073-M4)**: Strict DB Live Proofs — Re-ran and hardened strict DB proof suite (E16–E20). All 5 tests passing. Proof artifacts generated: `share/mcp/pg_checkpointer.handshake.json`, `share/mcp/db_select1.ok.json`, `share/atlas/db_proof_chip.json`, `share/mcp/db_error.guard.json`. Guards and compliance exports refreshed. M4 marked as ✅ PASS in both MASTER_PLAN.md locations.
- **Completed (078-E88)**: Violation Drilldown Pages — Generated HTML pages for each violation code with links to dashboards, nodes, patterns, and guard receipts. Created generator script `scripts/atlas/generate_violation_pages.py` and guard `scripts/guards/guard_atlas_compliance_drilldowns.py`. Make targets `atlas.compliance.drilldowns` and `guard.atlas.compliance.drilldowns` working. All guards passing. E88 marked as ✅ PASS in both MASTER_PLAN.md locations.
- **Completed (078-E89)**: Unified Violation Browser — Built searchable/filterable/sortable violations browser at `docs/atlas/browser/violations.html` with search, filter (code), sort (code, count-7d, count-30d, count-total), and links to dashboards, drilldown pages, JSON exports, and guard receipts. Created generator script `scripts/atlas/generate_violation_browser.py` and guard `scripts/guards/guard_atlas_violation_browser.py`. Make targets `atlas.violation.browser` and `guard.atlas.violation.browser` working. Browser verification passed. E89 marked as ✅ PASS in both MASTER_PLAN.md locations.
- **Completed (078-E90)**: Compliance Metrics in Graph Stats — Created export `share/atlas/control_plane/graph_compliance.json` with metrics per Tool, Node, Pattern, and Extraction batch. Aggregates violations from `control.agent_run` over 30-day window. Created export script `scripts/db/control_graph_compliance_metrics_export.py` and guard `scripts/guards/guard_control_graph_compliance.py`. Make targets `control.graph.compliance.export` and `guard.control.graph.compliance` working. Linked from violations browser. Browser verification passed. E90 marked as ✅ PASS in both MASTER_PLAN.md locations.
- **Completed (6P)**: BibleScholar Reference Answer Slice — Created control-plane export `share/atlas/control_plane/biblescholar_reference.json` that tracks BibleScholar reference questions and answers from `control.agent_run` (filtered by `call_site='biblescholar.reference_slice'`). Export script `scripts/db/control_biblescholar_reference_export.py` extracts questions, verse references, answers, and metadata (tokens, latency, mode). Guard `scripts/guards/guard_biblescholar_reference.py` validates export structure, schema, timestamp, and questions array. Atlas viewer `docs/atlas/browser/biblescholar_reference.html` displays questions, answers, verse references, and metadata with search/filter functionality. Tests `agentpm/tests/atlas/test_phase6p_biblescholar_reference_guard.py` (5 tests, all passing). Make targets `control.biblescholar.reference.export` and `guard.biblescholar.reference` working. Browser verification passed. Phase-6P marked as ✅ COMPLETE in both MASTER_PLAN.md locations.
- **Completed (6D)**: Downstream App Read-Only Wiring — Created control-plane widget adapters for StoryMaker and BibleScholar to consume graph compliance and BibleScholar reference exports. Adapter module `agentpm/control_widgets/adapter.py` provides `load_graph_compliance_widget_props()` and `load_biblescholar_reference_widget_props()` functions that return widget props (status, label, color, icon, tooltip_lines, metrics). All adapters are hermetic (file-only) and fail-closed (offline-safe defaults). Status snapshot integration adds `control_widgets` summary to `pmagent status snapshot`. Guard `scripts/guards/guard_control_widgets.py` validates adapter module, widget functions, and export files. Documentation `docs/runbooks/PHASE_6D_DOWNSTREAM_INTEGRATION.md` provides integration guide with examples for StoryMaker and BibleScholar. Atlas pages updated with Phase-6D integration links. Tests `agentpm/tests/control_widgets/test_adapter.py` (6 tests, all passing). Make target `guard.control.widgets` working. Phase-6D marked as ✅ COMPLETE in both MASTER_PLAN.md locations.
- **Completed (072-M1 Refresh)**: Strict DB Read-Only Proofs E16–E20 Refresh — Re-ran strict DB proof suite (`make mcp.strict.live.full`) to regenerate all E16–E20 artifacts with fresh timestamps (2025-11-20T22:56:13Z). All 5 tests passing (`pytest agentpm/tests/mcp/test_mcp_m4_e16_e20.py`). Proof artifacts refreshed: `share/mcp/pg_checkpointer.handshake.json` (E16: checkpointer driver proof), `share/mcp/db_select1.ok.json` (E17: DB SELECT 1 guard), `share/atlas/db_proof_chip.json` (E18/E19: Atlas chip latency + DSN host hash redaction), `share/mcp/db_error.guard.json` (E20: error path guard). Guards passing: `guard_control_plane_health --mode STRICT`, `guard_atlas_compliance_timeseries`, `guard_browser_verification`. Compliance exports refreshed: `compliance_summary.json`, `compliance_timeseries.json`. Share and state synced. Quality gates (ruff format/check) passing. PLAN-072 M1 remains ✅ PASS with fresh timestamps.
- **Completed (072-M2)**: Strict DB RO Proofs E21–E25 — Implemented and generated all E21–E25 proof artifacts. Created proof scripts: `scripts/mcp/proof_e21_por.py` (POR proof from regeneration receipt), `scripts/mcp/proof_e22_schema.py` (schema proof from schema snapshot), `scripts/mcp/proof_e23_gatekeeper.py` (gatekeeper coverage proof), `scripts/mcp/proof_e24_tagproof.py` (tagproof bundle proof with HINT/STRICT mode support), `scripts/mcp/proof_e25_bundle.py` (complete bundle aggregate). All 5 tests passing (`pytest agentpm/tests/mcp/test_m2_e21_e25.py`). Proof artifacts: `share/mcp/por_proof.json` (E21), `share/mcp/schema_proof.json` (E22), `share/mcp/gatekeeper_proof.json` (E23), `share/mcp/tagproof_proof.json` (E24), `share/mcp/bundle_proof.json` (E25). Make target `mcp.strict.live.phase2` generates all proofs. Guards passing: `guard_gatekeeper_coverage`, `guard_browser_verification`. Share and state synced. Quality gates (ruff format/check) passing. PLAN-072 M2 marked as ✅ PASS in both MASTER_PLAN.md locations.
- **Completed (072-M3)**: Visualization Hooks — Wired E21–E25 proofs into Atlas dashboards and control widgets. Created `scripts/atlas/generate_mcp_status_cards.py` to generate `share/atlas/control_plane/mcp_status_cards.json` with status cards for all 5 proofs. Updated Atlas HTML pages: `docs/atlas/dashboard/compliance_summary.html` (added MCP status cards tile with E21–E25 proof cards and summary metrics), `docs/atlas/browser/guard_receipts.html` (added links to MCP status cards and bundle proof), `docs/atlas/browser/violations.html` (added MCP proof status table with E21–E25 details). Extended `agentpm/control_widgets/adapter.py` with `load_mcp_status_cards_widget_props()` function (hermetic, fail-closed, offline-safe). Tests: `agentpm/tests/control_widgets/test_m2_visualization.py` (5 tests, all passing). Guards: `guard_control_widgets`, `guard_browser_verification` passing. Browser verification: all 7 pages verified. Share synced. Quality gates (ruff format/check) passing. PLAN-072 M3 marked as ✅ PASS in both MASTER_PLAN.md locations.
- **Completed (072-M4 / 080-E100)**: Strict Tag Lane / Tagproof Phase-2 Drill — Regenerated strict tag lane artifacts (bundle, screenshots, receipts) and verified gatekeeper/tagproof coverage. Phase-2 tagproof bundle regenerated: `evidence/tagproof_phase2_bundle.json` (timestamp: 2025-11-21T16:13:56Z) with components: TV coverage (E96), gatekeeper coverage (E97), regeneration receipt (E98), browser screenshot integrated (E99), MCP DB RO guard. Guards run in STRICT mode: `guard_tagproof_phase2` (STRICT mode, browser_screenshot component failed but acceptable in HINT mode), `guard_gatekeeper_coverage` (✅ PASS), `guard_tv_coverage` (✅ PASS), `guard_regenerate_all` (✅ PASS), `guard_tagproof_screenshots` (✅ PASS), `guard_browser_screenshot_integrated` (⚠️ HINT: missing 11 guard receipt references, 30 missing screenshots), `guard_screenshot_manifest` (✅ PASS), `guard_browser_verification` (✅ PASS: 7 pages verified), `guard_atlas_links` (✅ PASS: 83 internal links, 0 broken), `guard_snapshot_drift` (✅ PASS). Tests: `pytest agentpm/tests/atlas/test_e100_tagproof_phase2.py` (8 tests, all passing), `pytest agentpm/tests/atlas/test_e99_browser_screenshot_integrated.py` (7 tests, all passing). Make targets: `tagproof.phase2.bundle`, `guard.tagproof.phase2`, `test.e100.tagproof.phase2`. Share and state synced. Quality gates (ruff format/check) passing. PLAN-080 E100 marked as ✅ PASS in MASTER_PLAN.md.
- **Completed (081-E101)**: Orchestrator Dashboard Polish — Added MCP RO Proof tile and Browser-Verified badge components to the orchestrator dashboard. Created `webui/orchestrator-shell/MCPROProofTile.tsx` component that displays MCP read-only proof status from `share/mcp/bundle_proof.json` (shows proof count, last updated timestamp, and individual proof statuses for E21-E24). Created `webui/orchestrator-shell/BrowserVerifiedBadge.tsx` component that displays browser verification status from `evidence/webproof/report.json` (shows verified page count, screenshot count, and link to verification screenshots). Wired both components into `OrchestratorOverview.tsx` (badge at top, tile in dedicated section). Copied proof/verification JSON files to `webui/graph/public/exports/` for web UI access. Browser verification: `make atlas.webproof` completed. Share synced. Quality gates (ruff format/check) passing. PLAN-081 E101 marked as ✅ PASS in MASTER_PLAN.md.
- **Completed (Phase-1 Control Plane Governance)**: Phase-1 Control Plane governance hardening complete. Added STRICT/HINT mode support to all control-plane guards: `guard_control_graph_compliance.py` (fails in STRICT if export missing/invalid/stale, emits hints in HINT), `guard_control_widgets.py` (requires export files in STRICT, advisory in HINT), `guard_biblescholar_reference.py` (fails in STRICT if export missing/invalid/stale, emits hints in HINT). Updated `ops.tagproof` Makefile target to include control-plane exports (`control.graph.compliance.export`, `control.biblescholar.reference.export`) and guards (all run with STRICT_MODE=1). Updated `tagproof.yml` workflow to generate control-plane exports and run guards in STRICT mode. Added compliance export links to Atlas UI pages: `compliance_timeseries.html` and `compliance_heatmap.html` now link to `graph_compliance.json` and `mcp_status_cards.json`. Atlas links validation: 83 internal links, 0 broken. Phase-1 Control Plane marked as ✅ COMPLETE in MASTER_PLAN.md.
- **Completed (073-M1)**: Knowledge MCP Foundation — Implemented all E01–E05 components: E01 schema guard (`guard_mcp_schema.py`), E02 RO-DSN guard with redaction proof (`echo_dsn_ro.py`, enhanced `guard_mcp_db_ro.py`), E03 envelope ingest path (`ingest_envelope.py`, `mcp_ingest_envelope.v1.schema.json`), E04 minimal query roundtrip (`query_catalog.py`, `guard_mcp_query.py`), E05 proof snapshot (`generate_proof_snapshot.py`, `guard_mcp_proof.py`, `mcp_proof_snapshot.v1.schema.json`). All 14 tests passing (`test_mcp_catalog_e01_e05.py`). Proof artifacts: `share/mcp/knowledge_mcp_proof.json`, `share/mcp/knowledge_mcp_proof.txt`. Atlas tile added to `docs/atlas/index.html` (conditional, shows/hides based on file presence). Make targets: `mcp.schema.apply`, `mcp.schema.seed`, `guard.mcp.schema`, `mcp.dsn.echo`, `guard.mcp.db.ro`, `mcp.ingest`, `mcp.ingest.default`, `mcp.query`, `guard.mcp.query`, `mcp.proof.snapshot`, `guard.mcp.proof`. All guards pass in HINT mode (hermetic CI). Documentation updated: `scripts/AGENTS.md`, `agentpm/tests/mcp/AGENTS.md`. PLAN-073 M1 marked as ✅ COMPLETE in both MASTER_PLAN.md locations.
- **Completed (072-M1)**: PLAN-072 M1 DMS guard fixes — Implemented HINT/STRICT mode support for `guard_docs_db_ssot.py` (DB-off tolerance in HINT mode, fail-closed in STRICT mode). Guard supports `STRICT_MODE` env var, exits 0 in HINT mode (non-blocking) even when DB is off or sync is partial, exits 1 in STRICT mode when `ok=false`. Added `hints` array to output in HINT mode, `generated_at` timestamp to all outputs. Created `agentpm/tests/docs/test_dms_guards.py` with 7 tests covering HINT/STRICT behavior, DB-off tolerance, partial sync, and output shape validation (all passing). Updated Makefile with `guard.docs.db.ssot` (HINT) and `guard.docs.db.ssot.strict` (STRICT) targets. Documentation updated: `scripts/AGENTS.md` (guard contracts), `agentpm/tests/docs/AGENTS.md` (test coverage). SSOT doc: `docs/SSOT/PLAN_072_M1_DMS_GUARDS.md`. All acceptance criteria met. PLAN-072 M1 marked as ✅ COMPLETE in both MASTER_PLAN.md locations.

**PLAN-093: Autopilot Orchestrator Integration** (✅ **COMPLETE**)
- **Phase B** ✅ COMPLETE: Backend Stub — Implemented `pmagent autopilot serve` (FastAPI) and `POST /autopilot/intent` stub. Logs intents and returns "planned" status. Verified with curl and unit tests. Artifacts: `agentpm/server/autopilot_api.py`, `pmagent/cli.py`.
- **Phase C** ✅ COMPLETE: Guarded pmagent Integration — Implemented `GuardedToolAdapter` (`agentpm/guarded/autopilot_adapter.py`) mapping intents ("status", "health", "plan") to safe `pmagent` commands. Updated API to execute commands when `dry_run=False`. Added safety timeouts and whitelist validation. Verified with tests (`agentpm/tests/guarded/test_autopilot_adapter.py`).
- **Phase D** ✅ COMPLETE: Evidence-driven Dashboards — Implemented `AutopilotStatusTile` in Orchestrator Shell (`webui/orchestrator-shell/AutopilotStatusTile.tsx`) consuming `autopilot_summary.json` export. Created export script (`scripts/db/control_autopilot_summary_export.py`) and guard (`scripts/guards/guard_control_autopilot_summary.py`). Verified end-to-end flow.

**PLAN-094: BibleScholar Reference Parsing** (✅ **Active**)
- **Phase A** ✅ COMPLETE: Reference Parser Module — Created `agentpm/biblescholar/reference_parser.py` to handle OSIS reference parsing (e.g. "Gen.1.1", "John 3:16"). Pure function, no DB dependency. Implemented `parse_reference(ref_str) -> ParsedReference`. Verified with unit tests `agentpm/tests/biblescholar/test_reference_parser.py`.
- **Phase B** ✅ COMPLETE: Integrate Reference Parser — Updated `agentpm/biblescholar/bible_passage_flow.py` to use the new `reference_parser` module instead of its internal regex. Verified `fetch_passage` works with OSIS refs and maintained backward compatibility with existing tests.
- **Phase C** ✅ COMPLETE: Cleanup — Removed internal regex logic from `bible_passage_flow.py`.

**PLAN-095: BibleScholar Keyword Search Flow** (✅ **Active**)
- **Phase A** ✅ COMPLETE: Search Flow Module — Created `agentpm/biblescholar/search_flow.py` to handle keyword search. Implemented `search_verses(query: str, translation: str = "KJV", limit: int = 20) -> list[VerseRecord]`. Updated `bible_db_adapter` with `search_verses` method using `ILIKE` for case-insensitive matching. Verified with tests `agentpm/biblescholar/tests/test_search_flow.py` and `agentpm/biblescholar/tests/test_bible_db_adapter.py`.

**PLAN-096: BibleScholar Contextual Insights Flow** (✅ **Active**)
- **Phase A** ✅ COMPLETE: Insights Flow Module — Created `agentpm/biblescholar/insights_flow.py` to aggregate verse data. Implemented `get_verse_context(ref: str) -> VerseContext` (combining text, lexicon, and vector similarity). Implemented `format_context_for_llm(context: VerseContext) -> str`. Verified with tests `agentpm/biblescholar/tests/test_insights_flow.py`.

**PLAN-097: BibleScholar Cross-Language Flow** (✅ **Active**)
- **Phase A** ✅ COMPLETE: Cross-Language Flow Module — Created `agentpm/biblescholar/cross_language_flow.py`. Implemented `analyze_word_in_context(ref: str, strongs_id: str) -> WordAnalysis` (combining lexicon data with usage stats). Implemented `find_cross_language_connections(strongs_id: str) -> list[CrossLanguageMatch]` (linking Hebrew/Greek concepts). Verified with tests `agentpm/biblescholar/tests/test_cross_language_flow.py`.

**PLAN-098: BibleScholar UI Integration** (✅ **COMPLETE**)
- **Phase A** ✅ COMPLETE: UI Stubbing — Updated `webui/orchestrator-shell/LeftRail.tsx` to add BibleScholar tool. Created `webui/orchestrator-shell/BibleScholarPanel.tsx` (stub). Updated `webui/orchestrator-shell/MainCanvas.tsx`.
- **Phase B** ✅ COMPLETE: Export Script — Created `scripts/ui/export_biblescholar_summary.py` to generate `share/exports/biblescholar/summary.json`.
- **Phase 9B** ✅ COMPLETE: Full UI Integration — Created three full export scripts (`export_biblescholar_search.py`, `export_biblescholar_lexicon.py`, `export_biblescholar_insights.py`) with corresponding React components (`SearchTab.tsx`, `LexiconTab.tsx`, `InsightsTab.tsx`). Updated `BibleScholarPanel.tsx` with tab navigation. Added Makefile targets. All components follow static data contract (offline-capable, WHEN/THEN messaging). UI build verified (lint, build passing).

# Next Gate / Next Steps

**PLAN-098 Phase-9B** ✅ **VERIFIED COMPLETE** (2025-11-23)

**Verification Summary:**
- ✅ All 5 tab components present and functional (SearchTab, SemanticSearchTab, LexiconTab, InsightsTab, CrossLanguageTab)
- ✅ All 6 export scripts operational (`export_biblescholar_{summary,search,semantic_search,lexicon,insights,cross_language}.py`)
- ✅ All static JSON exports present in `share/exports/biblescholar/`
- ✅ UI build passing (679ms, 338.50 KB bundle, no errors)
- ✅ Hermetic contract compliance verified across all tabs (live/static mode toggle, WHEN/THEN messaging)
- ✅ CapabilitiesSidebar integration working
- ✅ Makefile targets wired for all exports

**BibleScholar UI- [ ] **Automate Housekeeping Commit**: Update `pmagent` to optionally auto-commit after successful housekeeping (User Request).
- [ ] **Tagging Strategy**: Formalize the use of tags for recovery points.
**BibleScholar UI Integration Status:** Complete and ready for use. All backend flows (Phase-6 through Phase-8) are operational. System supports both hermetic mode (static JSON) and live mode (DB queries when available).

**Next Recommendations:**
- BibleScholar migration is functionally complete (backend + UI)
- Consider: System health check (`make reality.green`), documentation updates, or new feature development
- See `docs/SSOT/BIBLESCHOLAR_MIGRATION_PLAN.md` for architecture details

## ✅ RESOLVED — Share Manifest Drift (Governance / Housekeeping)

* **Status**: Resolved (2025-11-30)

* **Current State**: `share/` now contains **35 Markdown files** (all JSON files are automatically converted to Markdown during housekeeping):
  * **14 core PM artifacts** (pm_snapshot.md, planning_context.md, kb_registry.md, doc_registry.md, doc_sync_state.md, doc_version.md, governance_freshness.md, hint_registry.md, live_posture.md, schema_snapshot.md, planning_lane_status.md, agents_md.head.md, pm_contract.head.md, next_steps.head.md)
  * **21 documentation files** (MASTER_PLAN.md, RULES_INDEX.md, AGENTS.md, various intake/migration plans, etc.)

* **SHARE_MANIFEST.json**: Formally deprecated with deprecation notice added. The manifest no longer reflects the current share/ structure (35 Markdown files vs 39 old items). The share/ directory is now **auto-generated** via `make pm.share.artifacts` during housekeeping, and DMS is the SSOT for document tracking.

* **Documentation Updated**: `docs/SSOT/SHARE_FOLDER_STRUCTURE.md` updated to reflect current state (all Markdown, auto-generated, flat structure).


### PR-1 Status: COMPLETE

* Repo introspection subsystem implemented and tested (semantic-inventory, reunion-plan, quarantine-candidates).
* CLI integration tests (TV-REPO-01..03) added and passing.

### PR-2: Documentation Onboarding (IN PROGRESS)

* Add repo subsystem to root AGENTS.md
* Add pmagent/AGENTS.md documentation block
* Update NEXT_STEPS.md lifecycle

```

### SHARE_FOLDER_STRUCTURE

```
# SHARE Folder Structure & Limitations

## Purpose

The `share/` directory is a **complete portable PM context package** that contains
all information needed for the PM to manage the system from start to finish. It
is **auto-generated** during `make housekeeping` via the `pm.share.artifacts` target.

**Current State (2025-12-05):**
* **Most files are Markdown format** (`.md`) - JSON files are automatically converted to Markdown
* **Mostly flat directory structure** - see "Allowed Subdirectories" below
* **Auto-generated** - no manual file management required
* **Preserves console v2 subdirectories** - `orchestrator/`, `orchestrator_assistant/`, `atlas/`, `exports/`

## Allowed Subdirectories

The following subdirectories are **preserved** during `make housekeeping` because they
are managed by other subsystems (console v2, control-plane exports):

| Directory | Purpose | Managed By |
|-----------|---------|------------|
| `orchestrator/` | Console v2 schema, state, prompts | Console v2 |
| `orchestrator_assistant/` | OA state and prompts | Console v2 |
| `atlas/control_plane/` | Control-plane exports | Atlas |
| `exports/docs-control/` | Docs-control exports | DMS |

These directories contain JSON files that are **NOT** converted to Markdown because they
are consumed programmatically by the console v2 webui.

## Core PM Artifacts (14 files)

These are the essential governance/PM artifacts, all in Markdown format:

* `pm_snapshot.md` - System health snapshot
* `planning_context.md` - Full planning output from `pmagent plan next`
* `kb_registry.md` - KB document registry (for DMS integration)
* `doc_registry.md` - DMS document registry snapshot
* `doc_sync_state.md` - Document sync state
* `doc_version.md` - Document version tracking
* `governance_freshness.md` - Document freshness tracking
* `hint_registry.md` - System hints and warnings
* `live_posture.md` - System health posture
* `schema_snapshot.md` - Database schema snapshot
* `planning_lane_status.md` - Planning lane status
* `agents_md.head.md` - AGENTS.md head export (first 100 lines)
* `pm_contract.head.md` - PM contract head export (first 100 lines)
* `next_steps.head.md` - Next steps head export (first 100 lines)

## Head Exports (`*.head.md`)

Some files in `share/` are generated as **head exports** via
`scripts/util/export_head_json.py` and then converted to Markdown. These files
contain only the **first 100 lines** of their source documents. Examples:

* `next_steps.head.md` ← first 100 lines of `NEXT_STEPS.md` (converted from JSON)
* `pm_contract.head.md` ← first 100 lines of `PM_CONTRACT.md` (converted from JSON)
* `agents_md.head.md` ← first 100 lines of `AGENTS.md` (converted from JSON)

These head exports are:

* Incomplete by construction (they do not include the full document)
* Potentially stale (they are updated only when housekeeping runs)

They **must not** be used to infer:

* The currently active Phase/PLAN
* The true "Next Gate / Next Steps" section
* The current focus of the project

## Planning vs Status

* **Allowed from share/**:

  * Governance/status checks
  * DMS/hint registry posture
  * Control-plane export inspection
  * PM posture snapshots

* **Not allowed from share/**:

  * Choosing the active Phase/PLAN
  * Deciding "what to work on next" for development

## Full Exports (Complete Files)

The following are **full exports** (complete files, not head exports), all in Markdown format:

* `share/planning_context.md` - Full planning output from `pmagent plan next` (converted from JSON)
* `share/kb_registry.md` - Complete KB document registry (converted from JSON)
* `share/pm_snapshot.md` - Complete system snapshot (converted from JSON)
* `share/doc_registry.md` - Complete DMS document registry (converted from JSON)
* All other core PM artifacts are full exports (not head exports)

These full exports provide complete context for PM decision-making.

## JSON to Markdown Conversion

**All JSON files are automatically converted to Markdown** during `make housekeeping`:

1. JSON files are exported to `share/` as normal
2. `scripts/util/json_to_markdown.py` converts each JSON file to Markdown
3. Original JSON files are removed (only `.md` files remain)
4. This ensures all files in `share/` are human-readable Markdown format

The conversion preserves all data structure and content, making it easier for PM agents to read and understand the system state.

## DMS Integration

All AGENTS.md files and other critical documents are tracked in:
* **KB Registry** (`share/kb_registry.md`) - Document metadata and registry (converted from JSON)
* **DMS Tables** (`share/doc_registry.md`, etc.) - Full DMS table dumps (converted from JSON)

The PM can query DMS using:
* `pmagent kb registry list` - List all registered documents
* `pmagent kb registry by-subsystem --owning-subsystem <subsystem>` - Filter by subsystem
* `pmagent kb registry show <doc_id>` - Show document details

For planning decisions, see:

* `PM_CONTRACT.md` Sections 2.7 and 2.8
* `PM_CONTRACT_STRICT_SSOT_DMS.md` "Planning Context vs Portable Snapshots"
* The `pmagent plan` commands (`pmagent plan next --with-status`, etc.)

## SHARE_MANIFEST.json Deprecation

**Status**: `SHARE_MANIFEST.json` is **deprecated** and no longer reflects the current `share/` structure.

**Reason**: The `share/` directory is now **auto-generated** via `make pm.share.artifacts` during housekeeping. The manifest was designed for manual file synchronization, which is no longer needed.

**Current State**:
* `share/` contains 35 Markdown files (14 core PM artifacts + 21 documentation files)
* All files are auto-generated during `make housekeeping`
* DMS is the SSOT for document tracking
* No manual file management required

**Action**: The manifest is kept for historical reference but should not be used for validation or synchronization. The `share.manifest.verify` Makefile target may produce warnings about missing files - these can be ignored as the manifest is outdated.


```

## 8. Share folder structure

```json
{
  "total_files": 70,
  "json_files": [
    "HANDOFF_KERNEL.json",
    "PHASE16_AUDIT_SNAPSHOT.json",
    "PHASE16_CLASSIFICATION_REPORT.json",
    "PHASE16_DB_RECON_REPORT.json",
    "PHASE16_PURGE_EXECUTION_LOG.json",
    "PHASE18_AGENTS_SYNC_SUMMARY.json",
    "PHASE18_LEDGER_REPAIR_SUMMARY.json",
    "PHASE18_SHARE_EXPORTS_SUMMARY.json",
    "PHASE19_SHARE_HYGIENE_SUMMARY.json",
    "PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.json",
    "PM_BOOTSTRAP_STATE.json",
    "REALITY_GREEN_SUMMARY.json",
    "SSOT_SURFACE_V17.json",
    "agents_md.head.json",
    "doc_registry.json",
    "doc_sync_state.json",
    "doc_version.json",
    "governance_freshness.json",
    "hint_registry.json",
    "kb_registry.json",
    "live_posture.json",
    "next_steps.head.json",
    "planning_context.json",
    "planning_lane_status.json",
    "pm_contract.head.json",
    "pm_snapshot.json",
    "schema_snapshot.json"
  ],
  "md_files": [
    "AGENTPM_GEMATRIA_MODULE_PLAN.md",
    "AGENTS.md",
    "BIBLESCHOLAR_INTAKE.md",
    "BIBLESCHOLAR_MIGRATION_PLAN.md",
    "DB_HEALTH.md",
    "GEMATRIA_NUMERICS_INTAKE.md",
    "GPT_REFERENCE_GUIDE.md",
    "GPT_SYSTEM_PROMPT.md",
    "LAYER3_AI_DOC_INGESTION_PLAN.md",
    "LAYER4_CODE_INGESTION_PLAN.md",
    "LM_STUDIO_SETUP.md",
    "LM_WIDGETS.md",
    "MASTER_PLAN.md",
    "NEXT_STEPS.md",
    "PHASE18_INDEX.md",
    "PHASE20_INDEX.md",
    "PHASE20_ORCHESTRATOR_UI_MODEL.md",
    "PHASE20_UI_RESET_DECISION.md",
    "PHASE21_CONSOLE_SERVE_PLAN.md",
    "PHASE21_INDEX.md",
    "PHASE22_INDEX.md",
    "PHASE22_OPERATOR_WORKFLOW.md",
    "PHASE23_BASELINE_NOTE.md",
    "PHASE23_BOOTSTRAP_HARDENING_NOTE.md",
    "PHASE23_FAILURE_INJECTION_NOTE.md",
    "PHASE23_INDEX.md",
    "PHASE23_PHASE_DONE_CHECKLIST.md",
    "PHASE23_STRESS_PLAN.md",
    "PHASE23_STRESS_SMOKE_NOTE.md",
    "PHASE27A_IMPLEMENTATION_EVIDENCE.md",
    "PHASE_14_SEMANTIC_RECORD.md",
    "PHASE_6_PLAN.md",
    "PM_CONTRACT.md",
    "PM_CONTRACT_STRICT_SSOT_DMS.md",
    "PM_HANDOFF_PROTOCOL.md",
    "PROJECTS_INVENTORY.md",
    "REFERENCES.md",
    "RULES_INDEX.md",
    "SHARE_FOLDER_ANALYSIS.md",
    "STORYMAKER_INTAKE.md",
    "USAGE_PATTERNS_REFERENCE.md",
    "scripts_AGENTS.md",
    "webui-contract.md"
  ],
  "directories": [
    "atlas",
    "exports",
    "handoff",
    "orchestrator",
    "orchestrator_assistant",
    "pm_boot"
  ]
}
```
