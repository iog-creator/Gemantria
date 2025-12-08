# PM System Introspection — Raw Evidence Bundle

This file aggregates raw evidence about how the pmagent + AGENTS + share +
planning + KB + tracking/self-healing systems currently behave. It is NOT a
designed doc; it is an evidence pack for the PM to read and interpret.

**Generated**: 2025-12-08T16:47:24.441577+00:00

## 1. Repo / branch / status

```
## feat/phase27l-agents-dms-contract
 M share/HANDOFF_KERNEL.json
 M share/kb_registry.json
 M share/pm_boot/DIRECTORY_DUPLICATION_MAP.md
 M share/pm_boot/HANDOFF_KERNEL.json
 M share/pm_boot/PM_BOOTSTRAP_STATE.json
 M share/pm_boot/REALITY_GREEN_SUMMARY.json
 M share/pm_boot/SHARE_FOLDER_ANALYSIS.md
?? share/agents_md.head.json
?? share/doc_registry.json
?? share/doc_sync_state.json
?? share/doc_version.json
?? share/governance_freshness.json
?? share/hint_registry.json
?? share/live_posture.json
?? share/next_steps.head.json
?? share/planning_context.json
?? share/planning_lane_status.json
?? share/pm_contract.head.json
?? share/pm_snapshot.json
?? share/schema_snapshot.json

```

## 2. pmagent commands (help text)

### pmagent

```
                                                  
 Usage: pmagent [OPTIONS] COMMAND [ARGS]...       
                                                  
╭─ Options ──────────────────────────────────────╮
│ --help          Show this message and exit.    │
╰────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────╮
│ health          Health check commands          │
│ graph           Graph operations               │
│ control         Control-plane operations       │
│ ask             Ask questions using SSOT       │
│                 documentation                  │
│ reality-check   Reality checks for automated   │
│                 bring-up                       │
│ reality         Reality validation commands    │
│ bringup         System bring-up commands       │
│ mcp             MCP server commands            │
│ lm              LM (Language Model) operations │
│ status          System status helpers          │
│ docs            Documentation search           │
│                 operations                     │
│ models          Model introspection commands   │
│ state           System state ledger operations │
│ kb              Knowledge-base document        │
│                 registry operations            │
│ plan            Planning workflows powered by  │
│                 KB registry                    │
│ report          Reporting commands             │
│ tools           External planning/tool helpers │
│                 (Gemini, Codex)                │
│ autopilot       Autopilot backend operations   │
│ repo            Repository introspection and   │
│                 git workflow commands.         │
│ handoff         Handoff service commands       │
│ hints           Hint generation and management │
│ dms             DMS governance operations      │
│ oa              Orchestrator Assistant kernel  │
│                 consumer operations            │
│ bible           Bible operations               │
│ rerank          Rerank operations              │
│ extract         Extract operations             │
│ embed           Embed operations               │
╰────────────────────────────────────────────────╯


```

### pmagent plan

```
                                                  
 Usage: pmagent plan [OPTIONS] COMMAND [ARGS]...  
                                                  
 Planning workflows powered by KB registry        
                                                  
╭─ Options ──────────────────────────────────────╮
│ --help          Show this message and exit.    │
╰────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────╮
│ next           Suggest next work items from    │
│                MASTER_PLAN + NEXT_STEPS        │
│ open           Open a NEXT_STEPS item as a     │
│                capability_session envelope     │
│ reality-loop   Run a single plan+posture loop  │
│                and persist a                   │
│                capability_session envelope     │
│ history        List recent capability_session  │
│                envelopes (read-only)           │
│ kb             KB-powered planning commands    │
╰────────────────────────────────────────────────╯


```

### pmagent kb

```
                                                  
 Usage: pmagent kb [OPTIONS] COMMAND [ARGS]...    
                                                  
 Knowledge-base document registry operations      
                                                  
╭─ Options ──────────────────────────────────────╮
│ --help          Show this message and exit.    │
╰────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────╮
│ registry   KB document registry commands       │
╰────────────────────────────────────────────────╯


```

### pmagent status

```
                                                  
 Usage: pmagent status [OPTIONS] COMMAND          
 [ARGS]...                                        
                                                  
 System status helpers                            
                                                  
╭─ Options ──────────────────────────────────────╮
│ --help          Show this message and exit.    │
╰────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────╮
│ explain   Explain current DB + LM health in    │
│           plain language                       │
│ kb        KB registry status view for          │
│           PM/AgentPM planning                  │
╰────────────────────────────────────────────────╯


```

### pmagent status snapshot

```

```

### pmagent status kb

```
                                                  
 Usage: pmagent status kb [OPTIONS]               
                                                  
 KB registry status view for PM/AgentPM planning  
                                                  
╭─ Options ──────────────────────────────────────╮
│ --json-only                  Print only JSON   │
│ --registry-path        TEXT  Path to registry  │
│                              JSON file         │
│ --help                       Show this message │
│                              and exit.         │
╰────────────────────────────────────────────────╯


```

### pmagent status explain

```
                                                  
 Usage: pmagent status explain [OPTIONS]          
                                                  
 Explain current DB + LM health in plain language 
                                                  
╭─ Options ──────────────────────────────────────╮
│ --json-only          Return JSON instead of    │
│                      text                      │
│ --no-lm              Skip LM enhancement, use  │
│                      rule-based only           │
│ --help               Show this message and     │
│                      exit.                     │
╰────────────────────────────────────────────────╯


```

### pmagent hints

```
                                                  
 Usage: pmagent hints [OPTIONS] COMMAND [ARGS]... 
                                                  
 Hint generation and management                   
                                                  
╭─ Options ──────────────────────────────────────╮
│ --help          Show this message and exit.    │
╰────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────╮
│ generate   Generate a hint from an error       │
│            message and context.                │
│ batch      Batch-generate hints from a session │
│            error log.                          │
│ list       List hints from the registry.       │
│ export     Export all hints to markdown        │
│            documentation.                      │
╰────────────────────────────────────────────────╯


```

### pmagent health

```
                                                  
 Usage: pmagent health [OPTIONS] COMMAND          
 [ARGS]...                                        
                                                  
 Health check commands                            
                                                  
╭─ Options ──────────────────────────────────────╮
│ --help          Show this message and exit.    │
╰────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────╮
│ system   Aggregate system health (DB + LM +    │
│          Graph)                                │
│ db       Check database health                 │
│ lm       Check LM Studio health                │
│ graph    Check graph overview                  │
╰────────────────────────────────────────────────╯


```

### pmagent health system

```
                                                  
 Usage: pmagent health system [OPTIONS]           
                                                  
 Aggregate system health (DB + LM + Graph)        
                                                  
╭─ Options ──────────────────────────────────────╮
│ --json-only          Print only JSON           │
│ --help               Show this message and     │
│                      exit.                     │
╰────────────────────────────────────────────────╯


```

### pmagent reality-check

```
                                                  
 Usage: pmagent reality-check [OPTIONS] COMMAND   
 [ARGS]...                                        
                                                  
 Reality checks for automated bring-up            
                                                  
╭─ Options ──────────────────────────────────────╮
│ --help          Show this message and exit.    │
╰────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────╮
│ 1       Run Reality Check #1 automated         │
│         bring-up                               │
│ live    Run Reality Check #1 LIVE (DB + LM +   │
│         pipeline)                              │
│ check   Run comprehensive reality check (env + │
│         DB + LM + exports + eval)              │
╰────────────────────────────────────────────────╯


```

### pmagent reality-check check

```
                                                  
 Usage: pmagent reality-check check [OPTIONS]     
                                                  
 Run comprehensive reality check (env + DB + LM + 
 exports + eval)                                  
                                                  
╭─ Options ──────────────────────────────────────╮
│ --mode                 TEXT  Mode: hint        │
│                              (default) or      │
│                              strict            │
│                              [default: hint]   │
│ --json-only                  Print only JSON   │
│ --no-dashboards              Skip exports/eval │
│                              checks            │
│ --help                       Show this message │
│                              and exit.         │
╰────────────────────────────────────────────────╯


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
      "timestamp": "2025-12-08T16:47:28.593128+00:00",
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
        "generated_at": "2025-12-08T16:47:28.593171+00:00",
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
                "row_count": 144,
                "latest_created_at": "2025-12-08T08:47:28.579664-08:00"
              },
              "control.kb_document": {
                "present": true,
                "row_count": 4238,
                "latest_created_at": "2025-11-27T10:39:03.026669-08:00"
              },
              "control.doc_registry": {
                "present": true,
                "row_count": 1245,
                "latest_created_at": "2025-12-08T08:25:28.507635-08:00"
              },
              "control.doc_version": {
                "present": true,
                "row_count": 12469,
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
              "control.agent_run_cli": 144,
              "control.capability_rule": 5,
              "control.capability_session": 5,
              "control.doc_embedding": 46570,
              "control.doc_fragment": 46570,
              "control.doc_registry": 1245,
              "control.doc_sync_state": 0,
              "control.doc_version": 12469,
              "control.guard_definition": 0,
              "control.hint_registry": 43,
              "control.kb_document": 4238,
              "control.rule_definition": 69,
              "control.rule_source": 138,
              "control.system_state_ledger": 471,
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
              "public.governance_compliance_log": 245,
              "public.hint_emissions": 824,
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
        "KB: KB registry references 112 missing file(s)",
        "KB: Subsystem 'pmagent' has low document coverage (2 doc(s))",
        "KB: KB registry validation issue: Registry validation failed: 114 errors",
        "KB: KB registry validation issue: Registry has 3 warnings",
        "KB: 9 document(s) are stale (exceed refresh interval)",
        "KB: Doc freshness: 9 stale, 0 out-of-sync"
      ],
      "kb_hints": [
        {
          "level": "WARN",
          "code": "KB_MISSING_DOCS",
          "message": "KB registry references 112 missing file(s)",
          "missing_count": 112,
          "missing_files": [
            "agentpm/AGENTS.md (ID",
            "backup/20251207T045808Z/share/AGENTS.md (ID",
            "backup/20251207T045808Z/share/scripts_AGENTS.md (ID",
            "backup/20251207T062821Z/share/AGENTS.md (ID",
            "backup/20251207T062821Z/share/pm_boot/AGENTS.md (ID",
            "backup/20251207T062821Z/share/scripts_AGENTS.md (ID",
            "backup/20251207T153233Z/share/AGENTS.md (ID",
            "backup/20251207T153233Z/share/pm_boot/AGENTS.md (ID",
            "backup/20251207T153233Z/share/scripts_AGENTS.md (ID",
            "backup/20251207T164600Z/share/AGENTS.md (ID"
          ]
        },
        {
          "level": "INFO",
          "code": "KB_LOW_COVERAGE_SUBSYSTEM",
          "message": "Subsystem 'pmagent' has low document coverage (2 doc(s))",
          "subsystem": "pmagent",
          "have": 2
        },
        {
          "level": "WARN",
          "code": "KB_VALIDATION_ISSUES",
          "message": "KB registry validation issue: Registry validation failed: 114 errors"
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
        "total": 1227,
        "by_subsystem": {
          "root": 112,
          "pm": 429,
          "webui": 53,
          "biblescholar": 68,
          "gematria": 12,
          "docs": 4,
          "ops": 309,
          "pmagent": 2,
          "general": 238
        },
        "by_type": {
          "other": 1054,
          "ssot": 140,
          "runbook": 33
        },
        "hints": [
          {
            "level": "WARN",
            "code": "KB_MISSING_DOCS",
            "message": "KB registry references 112 missing file(s)",
            "missing_count": 112,
            "missing_files": [
              "agentpm/AGENTS.md (ID",
              "backup/20251207T045808Z/share/AGENTS.md (ID",
              "backup/20251207T045808Z/share/scripts_AGENTS.md (ID",
              "backup/20251207T062821Z/share/AGENTS.md (ID",
              "backup/20251207T062821Z/share/pm_boot/AGENTS.md (ID",
              "backup/20251207T062821Z/share/scripts_AGENTS.md (ID",
              "backup/20251207T153233Z/share/AGENTS.md (ID",
              "backup/20251207T153233Z/share/pm_boot/AGENTS.md (ID",
              "backup/20251207T153233Z/share/scripts_AGENTS.md (ID",
              "backup/20251207T164600Z/share/AGENTS.md (ID"
            ]
          },
          {
            "level": "INFO",
            "code": "KB_LOW_COVERAGE_SUBSYSTEM",
            "message": "Subsystem 'pmagent' has low document coverage (2 doc(s))",
            "subsystem": "pmagent",
            "have": 2
          },
          {
            "level": "WARN",
            "code": "KB_VALIDATION_ISSUES",
            "message": "KB registry validation issue: Registry validation failed: 114 errors"
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
          "total": 1227,
          "stale_count": 9,
          "missing_count": 112,
          "out_of_sync_count": 0,
          "fresh_count": 1106
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
  "total": 1227,
  "by_subsystem": {
    "root": 112,
    "pm": 429,
    "webui": 53,
    "biblescholar": 68,
    "gematria": 12,
    "docs": 4,
    "ops": 309,
    "pmagent": 2,
    "general": 238
  },
  "by_type": {
    "other": 1054,
    "ssot": 140,
    "runbook": 33
  },
  "missing_files": [
    "agentpm/AGENTS.md (ID",
    "backup/20251207T045808Z/share/AGENTS.md (ID",
    "backup/20251207T045808Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T062821Z/share/AGENTS.md (ID",
    "backup/20251207T062821Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T062821Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T153233Z/share/AGENTS.md (ID",
    "backup/20251207T153233Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T153233Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T164600Z/share/AGENTS.md (ID",
    "backup/20251207T164600Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T164600Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T173128Z/share/AGENTS.md (ID",
    "backup/20251207T173128Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T173128Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T173726Z/share/AGENTS.md (ID",
    "backup/20251207T173726Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T173726Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T174051Z/share/AGENTS.md (ID",
    "backup/20251207T174051Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T174051Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T174800Z/share/AGENTS.md (ID",
    "backup/20251207T174800Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T175416Z/share/AGENTS.md (ID",
    "backup/20251207T175416Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T175416Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T180048Z/share/AGENTS.md (ID",
    "backup/20251207T180048Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T180048Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T180115Z/share/AGENTS.md (ID",
    "backup/20251207T180115Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T180115Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T181455Z/share/AGENTS.md (ID",
    "backup/20251207T181455Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T181455Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T181847Z/share/AGENTS.md (ID",
    "backup/20251207T181847Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T181847Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T183044Z/share/AGENTS.md (ID",
    "backup/20251207T183044Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T183044Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T183105Z/share/AGENTS.md (ID",
    "backup/20251207T183105Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T183105Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T183129Z/share/AGENTS.md (ID",
    "backup/20251207T183129Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T183129Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T183807Z/share/AGENTS.md (ID",
    "backup/20251207T183807Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T183807Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T185140Z/share/AGENTS.md (ID",
    "backup/20251207T185140Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T185140Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T185702Z/share/AGENTS.md (ID",
    "backup/20251207T185702Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T185702Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T191953Z/share/AGENTS.md (ID",
    "backup/20251207T191953Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T191953Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T192924Z/share/AGENTS.md (ID",
    "backup/20251207T192924Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T192924Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T192924Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T192924Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T204251Z/share/AGENTS.md (ID",
    "backup/20251207T204251Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T204251Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T204251Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T204251Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T205308Z/share/AGENTS.md (ID",
    "backup/20251207T205308Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T205308Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T205308Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T205308Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T205652Z/share/AGENTS.md (ID",
    "backup/20251207T205652Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T205652Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T205652Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T205652Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T210509Z/share/AGENTS.md (ID",
    "backup/20251207T210509Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T210509Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T210509Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T210509Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T215714Z/share/AGENTS.md (ID",
    "backup/20251207T215714Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T215714Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T215714Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T215714Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T221253Z/share/AGENTS.md (ID",
    "backup/20251207T221253Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T221253Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T221253Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T221253Z/share/scripts_AGENTS.md (ID",
    "backup/20251207T222044Z/share/AGENTS.md (ID",
    "backup/20251207T222044Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md (ID",
    "backup/20251207T222044Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md (ID",
    "backup/20251207T222044Z/share/pm_boot/AGENTS.md (ID",
    "backup/20251207T222044Z/share/scripts_AGENTS.md (ID",
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
    "Registry validation failed: 114 errors",
    "Registry has 3 warnings"
  ],
  "freshness": {
    "total": 1227,
    "stale_count": 9,
    "missing_count": 112,
    "out_of_sync_count": 0,
    "fresh_count": 1106
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
        "id": "agents::agentpm/agents.md",
        "path": "agentpm/AGENTS.md",
        "title": "AGENTS::agentpm/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t045808z/share/agents.md",
        "path": "backup/20251207T045808Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T045808Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t045808z/share/scripts-agents.md",
        "path": "backup/20251207T045808Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T045808Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t062821z/share/agents.md",
        "path": "backup/20251207T062821Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T062821Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t062821z/share/pm-boot/agents.md",
        "path": "backup/20251207T062821Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T062821Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t062821z/share/scripts-agents.md",
        "path": "backup/20251207T062821Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T062821Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t153233z/share/agents.md",
        "path": "backup/20251207T153233Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T153233Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t153233z/share/pm-boot/agents.md",
        "path": "backup/20251207T153233Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T153233Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t153233z/share/scripts-agents.md",
        "path": "backup/20251207T153233Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T153233Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t164600z/share/agents.md",
        "path": "backup/20251207T164600Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T164600Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t164600z/share/pm-boot/agents.md",
        "path": "backup/20251207T164600Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T164600Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t164600z/share/scripts-agents.md",
        "path": "backup/20251207T164600Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T164600Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t173128z/share/agents.md",
        "path": "backup/20251207T173128Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T173128Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t173128z/share/pm-boot/agents.md",
        "path": "backup/20251207T173128Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T173128Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t173128z/share/scripts-agents.md",
        "path": "backup/20251207T173128Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T173128Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t173726z/share/agents.md",
        "path": "backup/20251207T173726Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T173726Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t173726z/share/pm-boot/agents.md",
        "path": "backup/20251207T173726Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T173726Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t173726z/share/scripts-agents.md",
        "path": "backup/20251207T173726Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T173726Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t174051z/share/agents.md",
        "path": "backup/20251207T174051Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T174051Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t174051z/share/pm-boot/agents.md",
        "path": "backup/20251207T174051Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T174051Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t174051z/share/scripts-agents.md",
        "path": "backup/20251207T174051Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T174051Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t174800z/share/agents.md",
        "path": "backup/20251207T174800Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T174800Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t174800z/share/pm-boot/agents.md",
        "path": "backup/20251207T174800Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T174800Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t175416z/share/agents.md",
        "path": "backup/20251207T175416Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T175416Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t175416z/share/pm-boot/agents.md",
        "path": "backup/20251207T175416Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T175416Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t175416z/share/scripts-agents.md",
        "path": "backup/20251207T175416Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T175416Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t180048z/share/agents.md",
        "path": "backup/20251207T180048Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T180048Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t180048z/share/pm-boot/agents.md",
        "path": "backup/20251207T180048Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T180048Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t180048z/share/scripts-agents.md",
        "path": "backup/20251207T180048Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T180048Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t180115z/share/agents.md",
        "path": "backup/20251207T180115Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T180115Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t180115z/share/pm-boot/agents.md",
        "path": "backup/20251207T180115Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T180115Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t180115z/share/scripts-agents.md",
        "path": "backup/20251207T180115Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T180115Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t181455z/share/agents.md",
        "path": "backup/20251207T181455Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T181455Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t181455z/share/pm-boot/agents.md",
        "path": "backup/20251207T181455Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T181455Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t181455z/share/scripts-agents.md",
        "path": "backup/20251207T181455Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T181455Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t181847z/share/agents.md",
        "path": "backup/20251207T181847Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T181847Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t181847z/share/pm-boot/agents.md",
        "path": "backup/20251207T181847Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T181847Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t181847z/share/scripts-agents.md",
        "path": "backup/20251207T181847Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T181847Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183044z/share/agents.md",
        "path": "backup/20251207T183044Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T183044Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183044z/share/pm-boot/agents.md",
        "path": "backup/20251207T183044Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T183044Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183044z/share/scripts-agents.md",
        "path": "backup/20251207T183044Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T183044Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183105z/share/agents.md",
        "path": "backup/20251207T183105Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T183105Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183105z/share/pm-boot/agents.md",
        "path": "backup/20251207T183105Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T183105Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183105z/share/scripts-agents.md",
        "path": "backup/20251207T183105Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T183105Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183129z/share/agents.md",
        "path": "backup/20251207T183129Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T183129Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183129z/share/pm-boot/agents.md",
        "path": "backup/20251207T183129Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T183129Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183129z/share/scripts-agents.md",
        "path": "backup/20251207T183129Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T183129Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183807z/share/agents.md",
        "path": "backup/20251207T183807Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T183807Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183807z/share/pm-boot/agents.md",
        "path": "backup/20251207T183807Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T183807Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t183807z/share/scripts-agents.md",
        "path": "backup/20251207T183807Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T183807Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t185140z/share/agents.md",
        "path": "backup/20251207T185140Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T185140Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t185140z/share/pm-boot/agents.md",
        "path": "backup/20251207T185140Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T185140Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t185140z/share/scripts-agents.md",
        "path": "backup/20251207T185140Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T185140Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t185702z/share/agents.md",
        "path": "backup/20251207T185702Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T185702Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t185702z/share/pm-boot/agents.md",
        "path": "backup/20251207T185702Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T185702Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t185702z/share/scripts-agents.md",
        "path": "backup/20251207T185702Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T185702Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t191953z/share/agents.md",
        "path": "backup/20251207T191953Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T191953Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t191953z/share/pm-boot/agents.md",
        "path": "backup/20251207T191953Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T191953Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t191953z/share/scripts-agents.md",
        "path": "backup/20251207T191953Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T191953Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t192924z/share/agents.md",
        "path": "backup/20251207T192924Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T192924Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t192924z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T192924Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T192924Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t192924z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T192924Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T192924Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t192924z/share/pm-boot/agents.md",
        "path": "backup/20251207T192924Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T192924Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t192924z/share/scripts-agents.md",
        "path": "backup/20251207T192924Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T192924Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t204251z/share/agents.md",
        "path": "backup/20251207T204251Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T204251Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t204251z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T204251Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T204251Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t204251z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T204251Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T204251Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t204251z/share/pm-boot/agents.md",
        "path": "backup/20251207T204251Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T204251Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t204251z/share/scripts-agents.md",
        "path": "backup/20251207T204251Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T204251Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205308z/share/agents.md",
        "path": "backup/20251207T205308Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T205308Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205308z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T205308Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T205308Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205308z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T205308Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T205308Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205308z/share/pm-boot/agents.md",
        "path": "backup/20251207T205308Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T205308Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205308z/share/scripts-agents.md",
        "path": "backup/20251207T205308Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T205308Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205652z/share/agents.md",
        "path": "backup/20251207T205652Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T205652Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205652z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T205652Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T205652Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205652z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T205652Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T205652Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205652z/share/pm-boot/agents.md",
        "path": "backup/20251207T205652Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T205652Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t205652z/share/scripts-agents.md",
        "path": "backup/20251207T205652Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T205652Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t210509z/share/agents.md",
        "path": "backup/20251207T210509Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T210509Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t210509z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T210509Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T210509Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t210509z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T210509Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T210509Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t210509z/share/pm-boot/agents.md",
        "path": "backup/20251207T210509Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T210509Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t210509z/share/scripts-agents.md",
        "path": "backup/20251207T210509Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T210509Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t215714z/share/agents.md",
        "path": "backup/20251207T215714Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T215714Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t215714z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T215714Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T215714Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t215714z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T215714Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T215714Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t215714z/share/pm-boot/agents.md",
        "path": "backup/20251207T215714Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T215714Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t215714z/share/scripts-agents.md",
        "path": "backup/20251207T215714Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T215714Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t221253z/share/agents.md",
        "path": "backup/20251207T221253Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T221253Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t221253z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T221253Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T221253Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t221253z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T221253Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T221253Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t221253z/share/pm-boot/agents.md",
        "path": "backup/20251207T221253Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T221253Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t221253z/share/scripts-agents.md",
        "path": "backup/20251207T221253Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T221253Z/share/scripts_AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t222044z/share/agents.md",
        "path": "backup/20251207T222044Z/share/AGENTS.md",
        "title": "AGENTS::backup/20251207T222044Z/share/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t222044z/share/phase18-agents-sync-summary.md",
        "path": "backup/20251207T222044Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "title": "AGENTS::backup/20251207T222044Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t222044z/share/phase23-agents-sync-repair-summary.md",
        "path": "backup/20251207T222044Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "title": "AGENTS::backup/20251207T222044Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t222044z/share/pm-boot/agents.md",
        "path": "backup/20251207T222044Z/share/pm_boot/AGENTS.md",
        "title": "AGENTS::backup/20251207T222044Z/share/pm_boot/AGENTS.md",
        "type": "other"
      },
      {
        "id": "agents::backup/20251207t222044z/share/scripts-agents.md",
        "path": "backup/20251207T222044Z/share/scripts_AGENTS.md",
        "title": "AGENTS::backup/20251207T222044Z/share/scripts_AGENTS.md",
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
    "total": 1227,
    "by_subsystem": {
      "root": 112,
      "pm": 429,
      "webui": 53,
      "biblescholar": 68,
      "gematria": 12,
      "docs": 4,
      "ops": 309,
      "pmagent": 2,
      "general": 238
    },
    "by_type": {
      "other": 1054,
      "ssot": 140,
      "runbook": 33
    },
    "hints": [
      {
        "level": "WARN",
        "code": "KB_MISSING_DOCS",
        "message": "KB registry references 112 missing file(s)",
        "missing_count": 112,
        "missing_files": [
          "agentpm/AGENTS.md (ID",
          "backup/20251207T045808Z/share/AGENTS.md (ID",
          "backup/20251207T045808Z/share/scripts_AGENTS.md (ID",
          "backup/20251207T062821Z/share/AGENTS.md (ID",
          "backup/20251207T062821Z/share/pm_boot/AGENTS.md (ID",
          "backup/20251207T062821Z/share/scripts_AGENTS.md (ID",
          "backup/20251207T153233Z/share/AGENTS.md (ID",
          "backup/20251207T153233Z/share/pm_boot/AGENTS.md (ID",
          "backup/20251207T153233Z/share/scripts_AGENTS.md (ID",
          "backup/20251207T164600Z/share/AGENTS.md (ID"
        ]
      },
      {
        "level": "INFO",
        "code": "KB_LOW_COVERAGE_SUBSYSTEM",
        "message": "Subsystem 'pmagent' has low document coverage (2 doc(s))",
        "subsystem": "pmagent",
        "have": 2
      },
      {
        "level": "WARN",
        "code": "KB_VALIDATION_ISSUES",
        "message": "KB registry validation issue: Registry validation failed: 114 errors"
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
      "total": 1227,
      "stale_count": 9,
      "missing_count": 112,
      "out_of_sync_count": 0,
      "fresh_count": 1106
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
  "timestamp": "2025-12-08T16:47:34.756599+00:00",
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
    "generated_at": "2025-12-08T16:47:34.756621+00:00",
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
            "row_count": 146,
            "latest_created_at": "2025-12-08T08:47:34.743436-08:00"
          },
          "control.kb_document": {
            "present": true,
            "row_count": 4238,
            "latest_created_at": "2025-11-27T10:39:03.026669-08:00"
          },
          "control.doc_registry": {
            "present": true,
            "row_count": 1245,
            "latest_created_at": "2025-12-08T08:25:28.507635-08:00"
          },
          "control.doc_version": {
            "present": true,
            "row_count": 12469,
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
          "control.agent_run_cli": 146,
          "control.capability_rule": 5,
          "control.capability_session": 5,
          "control.doc_embedding": 46570,
          "control.doc_fragment": 46570,
          "control.doc_registry": 1245,
          "control.doc_sync_state": 0,
          "control.doc_version": 12469,
          "control.guard_definition": 0,
          "control.hint_registry": 43,
          "control.kb_document": 4238,
          "control.rule_definition": 69,
          "control.rule_source": 138,
          "control.system_state_ledger": 471,
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
          "public.governance_compliance_log": 245,
          "public.hint_emissions": 824,
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
    "KB: KB registry references 112 missing file(s)",
    "KB: Subsystem 'pmagent' has low document coverage (2 doc(s))",
    "KB: KB registry validation issue: Registry validation failed: 114 errors",
    "KB: KB registry validation issue: Registry has 3 warnings",
    "KB: 9 document(s) are stale (exceed refresh interval)",
    "KB: Doc freshness: 9 stale, 0 out-of-sync"
  ],
  "kb_hints": [
    {
      "level": "WARN",
      "code": "KB_MISSING_DOCS",
      "message": "KB registry references 112 missing file(s)",
      "missing_count": 112,
      "missing_files": [
        "agentpm/AGENTS.md (ID",
        "backup/20251207T045808Z/share/AGENTS.md (ID",
        "backup/20251207T045808Z/share/scripts_AGENTS.md (ID",
        "backup/20251207T062821Z/share/AGENTS.md (ID",
        "backup/20251207T062821Z/share/pm_boot/AGENTS.md (ID",
        "backup/20251207T062821Z/share/scripts_AGENTS.md (ID",
        "backup/20251207T153233Z/share/AGENTS.md (ID",
        "backup/20251207T153233Z/share/pm_boot/AGENTS.md (ID",
        "backup/20251207T153233Z/share/scripts_AGENTS.md (ID",
        "backup/20251207T164600Z/share/AGENTS.md (ID"
      ]
    },
    {
      "level": "INFO",
      "code": "KB_LOW_COVERAGE_SUBSYSTEM",
      "message": "Subsystem 'pmagent' has low document coverage (2 doc(s))",
      "subsystem": "pmagent",
      "have": 2
    },
    {
      "level": "WARN",
      "code": "KB_VALIDATION_ISSUES",
      "message": "KB registry validation issue: Registry validation failed: 114 errors"
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
Gemantria and pmagent; the pmagent control-plane DMS records that worldview in structured form.

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
4. **File Search** (LAST RESORT): Only if content not in pmagent control-plane DMS

**Feature Registration**:
- After building new tool/module: Create MCP envelope → `make mcp.ingest` → Update KB registry
- PM learns capabilities automatically through pmagent control-plane DMS registration
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
pmagent/hints/registry.py:1:"""Hint Registry - DMS-backed hint loading and embedding for envelopes."""
pmagent/hints/registry.py:92:def embed_hints_in_envelope(
pmagent/hints/registry.py:93:    envelope: dict[str, Any],
pmagent/hints/registry.py:97:    Embed hints into an envelope structure.
pmagent/hints/registry.py:99:    Adds "required_hints" and "suggested_hints" sections to the envelope.
pmagent/hints/registry.py:103:        envelope: Existing envelope dict
pmagent/hints/registry.py:110:    result = envelope.copy()
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
docs/phase10/STRUCTURE.md:10:* `ui/src/lib/` helpers (envelope loader)
docs/phase10/STRUCTURE.md:15:1. Build envelope locally: `make ingest.local.envelope`
docs/phase10/STRUCTURE.md:17:3. Load `/tmp/p9-ingest-envelope.json` for views
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
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:92:- After generating diagrams, MUST run `make housekeeping` before committing
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:95:  1. Run housekeeping: `make housekeeping`
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:184:8. **Run housekeeping** (Rule 058)
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:185:   - Execute `make housekeeping` after all changes
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:216:8. Run `make housekeeping`
.cursor/plans/atlas-enhancement-flow-and-architecture-diagrams-1045166e.plan.md:272:- Housekeeping: `make housekeeping` runs after diagram generation
pmagent/ai_docs/reality_check_ai_notes.py:68:    prompt = f"""You are the Granite housekeeping AI for the Gemantria project.
.cursor/plans/plan-e3abd805.plan.md:34:- Every execution brief includes required SSOT references, guard/tests, and housekeeping/reality.green expectations per OPS v6.2.3.
.cursor/plans/plan-e3abd805.plan.md:50:- [ ] Specify final repo-wide gates (ruff, focused smokes, housekeeping, optionally reality.green) to run after the E-step.
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:144:### Step 5: Integrate doc registry ingestion into housekeeping
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:150:- Add `governance.ingest.docs` as a dependency to `housekeeping` target (before `share.sync`)
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:176:7. Run `make housekeeping` and verify it completes successfully
.cursor/plans/dms-only-docs-management-d24d0c78.plan.md:209:- [ ] Add governance.ingest.docs as dependency to housekeeping target in Makefile (before share.sync)
pmagent/control_plane/sessions.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/control_plane/doc_fragments.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/control_plane/exports.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/validate_ingest_envelope_schema.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/show_meta.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/__init__.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
docs/hints/HINT-DB-002-postgres-not-running.md:85:- ❌ Cannot run housekeeping or regenerate KB
scripts/ingest/validate_snapshot.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/validate_envelope_schema.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/build_envelope.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/check_env.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/mappers.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ingest/stub_ingest.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/book_policy_check.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
docs/BACKUP_STRATEGY_AUDIT.md:45:- Part of housekeeping (`make housekeeping`)
docs/BACKUP_STRATEGY_AUDIT.md:130:- Run during housekeeping
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
pmagent/AGENTS.md:182:  - Run `make housekeeping` (or at least `make share.sync governance.housekeeping`) after changes to ensure docs and share/ are updated.
scripts/docs/apply_ops_header.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/docs/apply_ops_header.py:7:HEADER = """# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/exports_smoke.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/temporal_analytics.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/verify_enrichment_prompts.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/echo_env.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/housekeeping_gpu/__init__.py:4:Purpose: Performance-optimized housekeeping operations using GPU acceleration when available.
scripts/goldens_status.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
pmagent/guarded/guard_shim.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
.cursor/rules/README.md:5:> Governance fast-lane: All exports stamp `generated_at` as RFC3339 and set `metadata.source="fallback_fast_lane"`. Run guards in HINT-only mode (`STRICT_RFC3339=0`) on main/PRs and STRICT (`STRICT_RFC3339=1`) on release builds. Always run `make housekeeping` after docs or script changes so the contract stays enforced.
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
scripts/housekeeping_gpu/gpu_classifier.py:7:Provide GPU-accelerated batch classification for housekeeping operations.
scripts/gematria_verify.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/governance_tracker.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/governance_tracker.py:293:        return True  # Return success to allow housekeeping to pass
scripts/governance_tracker.py:329:        return True  # Return success to allow housekeeping to pass
scripts/housekeeping_gpu/classify_fragments_gpu.py:18:    python scripts/housekeeping_gpu/classify_fragments_gpu.py [--dry-run] [--limit N]
scripts/housekeeping_gpu/classify_fragments_gpu.py:36:from scripts.housekeeping_gpu.gpu_classifier import classify_batch_gpu
scripts/ingest_bible_db_morphology.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ai_enrichment.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/document_management_hints.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/sandbox_smoke_check.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
.cursor/rules/006-agents-md-governance.mdc:13:- **MANDATORY**: Run `make housekeeping` after ANY changes to docs, scripts, rules, or database
.cursor/rules/006-agents-md-governance.mdc:50:- **Rule 058**: Auto-housekeeping (mandatory after any modifications)
scripts/math_verifier.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ai_session_monitor.py:3:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
.cursor/rules/010-task-brief.mdc:23:- **MANDATORY**: Include `make housekeeping` in Tests/checks for any doc/script/rule changes
.cursor/rules/010-task-brief.mdc:38:- **Rule 058**: Auto-housekeeping (mandatory after modifications)
pmagent/guarded/gatekeeper.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/backfill_bge_embeddings.py:2:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/ontology_compat.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/audit_genesis_db.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/repo_audit.py:1:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
scripts/exports/export_biblescholar_summary.py:14:# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`

```

### pm_snapshot_refs

```
.cursor/rules/070-gotchas-check.mdc:136:- All command execution wrappers (e.g., `scripts/pm_snapshot.py::run()`, `scripts/prepare_handoff.py::run_cmd()`)
docs/BACKUP_STRATEGY_AUDIT.md:32:- `Makefile` lines 187-189 (`pm.snapshot` target)
docs/BACKUP_STRATEGY_AUDIT.md:33:- `scripts/pm_snapshot.py`
docs/BACKUP_STRATEGY_AUDIT.md:34:- Output: `evidence/pm_snapshot/run.txt`
docs/BACKUP_STRATEGY_AUDIT.md:38:make pm.snapshot  # Generate PM health snapshot
docs/BACKUP_STRATEGY_AUDIT.md:128:**PM Snapshots** (`pm.snapshot`):
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
.cursor/rules/058-auto-housekeeping.mdc:48:13. **PM snapshot** (`pm.snapshot`) — generates PM-facing status snapshot
.cursor/rules/071-portable-json-not-plan-ssot.mdc:3:* The `share/*.json` portable bundle (e.g. `pm_snapshot.json`,
pmagent/status/snapshot.py:5:AgentPM-First:M3: Unified system snapshot helper for pm.snapshot and WebUI APIs.
pmagent/status/snapshot.py:458:    """Get unified system snapshot (pm.snapshot + API contract).
pmagent/status/eval_exports.py:24:DB_HEALTH_PATH = REPO_ROOT / "evidence" / "pm_snapshot" / "db_health.json"
pmagent/status/eval_exports.py:121:    """Load DB health snapshot (from pm.snapshot evidence).
pmagent/status/eval_exports.py:136:                "note": "DB health snapshot not available (file missing; run `make pm.snapshot`)",
pmagent/status/AGENTS.md:9:- `snapshot.py`: Unified system snapshot helpers used by `pm.snapshot` and `/api/status/system`. Now includes advisory `kb_doc_health` metrics (AgentPM-Next:M3).
pmagent/status/AGENTS.md:10:- `kb_metrics.py`: KB documentation health metrics helper (AgentPM-Next:M3) that aggregates KB registry freshness + M2 fix manifests into doc-health metrics for reporting surfaces (`pmagent report kb`, `pm.snapshot`, and future status integration).
scripts/util/export_pm_snapshot_json.py:5:Exports pm.snapshot as JSON format by calling get_system_snapshot() directly.
scripts/util/export_pm_snapshot_json.py:6:This is the JSON version of the markdown snapshot generated by make pm.snapshot.
scripts/util/export_pm_snapshot_json.py:9:    python scripts/util/export_pm_snapshot_json.py [--output <path>]
scripts/util/export_pm_snapshot_json.py:24:OUT_FILE = OUT_DIR / "pm_snapshot.json"
scripts/util/export_pm_snapshot_json.py:30:    parser.add_argument("--output", type=Path, help="Output JSON file path (default: share/pm_snapshot.json)")
scripts/util/export_pm_snapshot_json.py:67:            "schema": "pm_snapshot.v1",
scripts/kb/seed_registry.py:108:            id="runbook-pm-snapshot",
scripts/AGENTS.md:1390:- `share/pm.snapshot.md`
scripts/util/export_pm_introspection_evidence.py:148:        ("pm.snapshot", "pm_snapshot_refs"),
scripts/guard_pm_snapshot.sh:3:SNAPSHOT_PATH="${1:-share/pm.snapshot.md}"
.cursor/rules/AGENTS.md:2076:13. **PM snapshot** (`pm.snapshot`) — generates PM-facing status snapshot
scripts/pm_snapshot.py:12:doc_path = share_dir / "pm.snapshot.md"
scripts/pm_snapshot.py:14:evid_dir = root / "evidence" / "pm_snapshot"
scripts/pm_snapshot.py:237:entry = {"src": "share/pm.snapshot.md", "dst": "share/pm.snapshot.md"}
scripts/pm_snapshot.py:279:    "**Now**\n- Keep GemantriaV.2 as the active project.\n- Use `STRICT` posture when DSNs present; otherwise HINT mode is allowed for hermetic tests.\n- Regenerate this PM Snapshot on each bring-up or DSN change (`make pm.snapshot`).\n"
pmagent/kb/AGENTS.md:77:- **pm.snapshot**: Registry is included in system snapshots (KB-Reg:M2) — advisory-only, non-gating
pmagent/kb/AGENTS.md:85:The KB registry is integrated into `pm.snapshot` via `pmagent.status.snapshot.get_system_snapshot()`:
pmagent/kb/AGENTS.md:185:KB registry health is surfaced as structured hints in `pm.snapshot` and `pmagent reality-check`:
pmagent/kb/AGENTS.md:197:- **pm.snapshot**: KB hints included in `evidence/pm_snapshot/snapshot.json` and rendered in `share/pm.snapshot.md` under "KB Hints (Advisory)" section
scripts/guards/guard_share_sync_policy.py:90:    "share/pm_snapshot.md",
scripts/guards/guard_dms_share_alignment.py:71:    "pm_snapshot.md",
scripts/guards/guard_snapshot_drift.py:78:        "pm_snapshot": ROOT / "share" / "pm.snapshot.md",
docs/handoff/PLAN-092-AgentPM-Next-M1-M4-handoff.md:32:- **Snapshot Integration:** `pm.snapshot` generates complete doc-health data
docs/handoff/PLAN-092-AgentPM-Next-M1-M4-handoff.md:44:  - ✅ **Integration**: `pm.snapshot` includes `kb_doc_health` data (`pmagent/status/snapshot.py`)
docs/handoff/PLAN-092-AgentPM-Next-M1-M4-handoff.md:77:**M4 - UI Integration (pm.snapshot kb_doc_health):**
docs/handoff/PLAN-092-AgentPM-Next-M1-M4-handoff.md:111:- `evidence/pm_snapshot/snapshot.json` — Complete system snapshot with kb_doc_health data
docs/handoff/PLAN-092-AgentPM-Next-M1-M4-handoff.md:112:- `share/pm.snapshot.md` — Human-readable PM snapshot with doc health section
docs/SSOT/PHASE15_WAVE3_STEP2_OPS_BLOCK.md:27:| **Gate 1 (DMS Ingestion)** | ✅ COMPLETE | 65,243 fragments, 65,238 embeddings (1024-D) | `share/pm_snapshot.md`, `docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md` |
docs/plans/PLAN-080-Verification-Sweep-and-Tagproof.md:96:**M4 - UI Integration (pm.snapshot kb_doc_health):**
docs/SSOT/PM_CONTRACT_STRICT_SSOT_DMS.md:100:  `pm_snapshot.json`, `next_steps.head.json`, `doc_registry.json`,
docs/forest/overview.md:99:- pm-snapshot.yml
docs/SSOT/GEMATRIA_NUMERICS_INTAKE.md:222:- `scripts/pm_snapshot.py`
docs/SSOT/GEMATRIA_NUMERICS_INTAKE.md:305:- `.github/workflows/pm-snapshot.yml`
docs/SSOT/SHARE_MANIFEST.json:162:      "src": "share/pm.snapshot.md",
docs/SSOT/SHARE_MANIFEST.json:163:      "dst": "share/pm.snapshot.md"
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:14:   - Data exists: `pm_snapshot.md` shows `control.doc_fragment`: 65,243 rows, `control.doc_embedding`: 65,238 rows
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:36:**`share/pm_snapshot.md`** (generated 2025-12-02T09:44:27):
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:51:**Schema evidence** (from `pm_snapshot.md`):
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:69:2. It didn't check the actual data in `share/pm_snapshot.md`
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:73:1. Read `share/pm_snapshot.md`
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:92:**Source**: `pm_snapshot.md`, `kb_registry.json`, schema inspection
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:156:    # Read from pm_snapshot data
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:165:1. Reads `share/pm_snapshot.md` (or JSON source)
docs/SSOT/SHARE_FOLDER_GATE_STATUS_GAP.md:195:- `share/pm_snapshot.md` - System snapshot (data source)
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:65:- **Goal 1**: Expose doc-health metrics in `pmagent pm.snapshot` (the "110% signal")
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:94:- **`pmagent pm.snapshot`**: Include doc-health metrics in system snapshot
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:114:7. Regenerate snapshot: `make pm.snapshot` (now includes doc-health metrics)
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:195:- **`pmagent pm.snapshot`**: Include doc-health metrics in JSON and Markdown output
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:241:- **Integration points**: Specifies exactly 3 surfaces where metrics will appear (`pm.snapshot`, `/status`, `pmagent report kb`)
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:264:- **M3a**: Implement metrics in `pmagent pm.snapshot` (read-only aggregation)
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:271:- **Existing surfaces**: `pm.snapshot` already includes KB registry summary (advisory)
docs/SSOT/AGENTPM_NEXT_M3_DESIGN.md:290:| pm.snapshot integration | AgentPM-First:M3 + M4 |
docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md:129:* **pm.snapshot integration is implemented (AgentPM-First:M3 + M4 + KB-Reg:M2 + AgentPM-Next:M3)**:
docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md:130:  - `make pm.snapshot` / `scripts/pm_snapshot.py` composes health, status explanation, reality-check, AI tracking, share manifest, eval insights (Phase-8/10), KB registry, and KB doc-health into a single operator-facing snapshot
docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md:131:  - **Unified helper**: `pmagent.status.snapshot.get_system_snapshot()` — Single source of truth for system snapshot composition, shared by `pm.snapshot` and WebUI APIs (`/api/status/system`)
docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md:132:  - Generates both Markdown (`share/pm.snapshot.md`) and JSON (`evidence/pm_snapshot/snapshot.json`) outputs
docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md:139:  - **KB hints (KB-Reg:M4)**: KB registry health surfaced as structured hints in `pm.snapshot` and `pmagent reality-check`; hints include missing docs, low coverage subsystems, and validation issues; all hints are advisory-only and never affect `overall_ok`
docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md:140:  - **KB doc health (AgentPM-Next:M3)**: `pm.snapshot` includes "Documentation Health" section with aggregated metrics (freshness, missing/stale counts, fixes applied) derived from `pmagent report kb` logic; fully advisory-only.
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:106:- PM tries to infer active PLAN from `pm_snapshot.json`
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:182:**Issue**: `pmagent pm.snapshot` doesn't include planning context from `pmagent plan next`.
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:184:**Fix**: Include `planning_context` in `pm_snapshot.json` by calling `pmagent plan next --json-only`.
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:237:1. **Integrate planning system into PM snapshot** - include planning context in `pm_snapshot.json`
docs/analysis/AGENTS_KB_FORensics.md:23:- **orphan**: [{'doc_id': 'e7bbf9c9-0682-4994-a245-bf91f9c3a051', 'logical_name': 'AGENTS::agentpm/adapters/AGENTS.md', 'repo_path': 'agentpm/adapters/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '229e27be-55be-44ee-b236-e8d08c693480', 'logical_name': 'AGENTS::agentpm/ai_docs/AGENTS.md', 'repo_path': 'agentpm/ai_docs/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'cbf3b3d4-0c35-467c-9317-6352dd559c44', 'logical_name': 'AGENTS::agentpm/atlas/AGENTS.md', 'repo_path': 'agentpm/atlas/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '51dfbe11-9c7a-4056-b602-20b1335dbabe', 'logical_name': 'AGENTS::agentpm/biblescholar/AGENTS.md', 'repo_path': 'agentpm/biblescholar/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'e24ce94b-0991-46cc-8fa2-ebddeb5d4f1f', 'logical_name': 'AGENTS::agentpm/biblescholar/tests/AGENTS.md', 'repo_path': 'agentpm/biblescholar/tests/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'e5e129c9-0f15-4fe6-b98c-0d3d194fbc61', 'logical_name': 'AGENTS::agentpm/bus/AGENTS.md', 'repo_path': 'agentpm/bus/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '8767eb1d-17a1-4299-9cc9-a3de5a7df842', 'logical_name': 'AGENTS::agentpm/control_plane/AGENTS.md', 'repo_path': 'agentpm/control_plane/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '227d3d7c-7fbe-469b-bd13-07f20f051159', 'logical_name': 'AGENTS::agentpm/control_widgets/AGENTS.md', 'repo_path': 'agentpm/control_widgets/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '6ec9a9a7-47ba-468e-9804-a361546591c4', 'logical_name': 'AGENTS::agentpm/db/AGENTS.md', 'repo_path': 'agentpm/db/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '5ef33019-52a8-44ae-b563-1e686b9cfc4b', 'logical_name': 'AGENTS::agentpm/dms/AGENTS.md', 'repo_path': 'agentpm/dms/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '6922bf2a-698c-4b37-8ea4-0d77f22dd1d3', 'logical_name': 'AGENTS::agentpm/docs/AGENTS.md', 'repo_path': 'agentpm/docs/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '868f6c67-2f84-4118-8dd0-d90a2a74fe5a', 'logical_name': 'AGENTS::agentpm/exports/AGENTS.md', 'repo_path': 'agentpm/exports/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '92be0307-3aeb-496d-bd44-ee85626d23ef', 'logical_name': 'AGENTS::agentpm/extractors/AGENTS.md', 'repo_path': 'agentpm/extractors/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '9c0846d2-cff0-419c-952b-c2e5c38eef82', 'logical_name': 'AGENTS::agentpm/gatekeeper/AGENTS.md', 'repo_path': 'agentpm/gatekeeper/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '16a67728-a2ff-40bc-87f0-f78d39232267', 'logical_name': 'AGENTS::agentpm/governance/AGENTS.md', 'repo_path': 'agentpm/governance/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '06e49b5c-553b-4f57-a069-baa48a7852b8', 'logical_name': 'AGENTS::agentpm/graph/AGENTS.md', 'repo_path': 'agentpm/graph/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '0702f0f6-3ced-4778-8e2a-92435186c7ff', 'logical_name': 'AGENTS::agentpm/guard/AGENTS.md', 'repo_path': 'agentpm/guard/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'efc52f9f-1c79-44ec-b3c9-43f442ca3a47', 'logical_name': 'AGENTS::agentpm/guarded/AGENTS.md', 'repo_path': 'agentpm/guarded/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '56fdbaaf-d93a-4300-848a-d4a3bd48c571', 'logical_name': 'AGENTS::agentpm/handoff/AGENTS.md', 'repo_path': 'agentpm/handoff/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '4455a075-b647-4085-947d-74088f1a9f3e', 'logical_name': 'AGENTS::agentpm/hints/AGENTS.md', 'repo_path': 'agentpm/hints/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'cc65b81d-62e2-4aab-9303-ca219a3ae0ad', 'logical_name': 'AGENTS::agentpm/kb/AGENTS.md', 'repo_path': 'agentpm/kb/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '34f3bec0-5314-4472-b58d-94814086f78f', 'logical_name': 'AGENTS::agentpm/knowledge/AGENTS.md', 'repo_path': 'agentpm/knowledge/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '0b65aa56-22cd-4037-bb57-02b91d28fcdf', 'logical_name': 'AGENTS::agentpm/lm/AGENTS.md', 'repo_path': 'agentpm/lm/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '94a7027c-5b3f-4145-992f-3cb41de3f386', 'logical_name': 'AGENTS::agentpm/lm_widgets/AGENTS.md', 'repo_path': 'agentpm/lm_widgets/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'fb4f221c-2fb1-41d3-b805-c24856ab4e02', 'logical_name': 'AGENTS::agentpm/mcp/AGENTS.md', 'repo_path': 'agentpm/mcp/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '763f1f22-4a1b-41a7-b883-cef43da35c68', 'logical_name': 'AGENTS::agentpm/metrics/AGENTS.md', 'repo_path': 'agentpm/metrics/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'ee14c571-1373-4f9e-98a3-5d2a9a7bdf70', 'logical_name': 'AGENTS::agentpm/modules/AGENTS.md', 'repo_path': 'agentpm/modules/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'a160e364-b654-4e4e-99cb-7a43d9c605c7', 'logical_name': 'AGENTS::agentpm/modules/gematria/AGENTS.md', 'repo_path': 'agentpm/modules/gematria/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '29c1d30a-5c45-430f-b550-179ae1ae37a3', 'logical_name': 'AGENTS::agentpm/obs/AGENTS.md', 'repo_path': 'agentpm/obs/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'd855b1db-a6a3-4a38-aa37-48516bee76fd', 'logical_name': 'AGENTS::agentpm/plan/AGENTS.md', 'repo_path': 'agentpm/plan/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'b8f776d7-da55-4aa7-9b11-86a016225297', 'logical_name': 'AGENTS::agentpm/reality/AGENTS.md', 'repo_path': 'agentpm/reality/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '94af1cfb-df69-456f-99c8-6ed2d076f6e2', 'logical_name': 'AGENTS::agentpm/rpc/AGENTS.md', 'repo_path': 'agentpm/rpc/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '48e9fa7a-2e3a-43a1-8bcc-d2d165f15ff6', 'logical_name': 'AGENTS::agentpm/runtime/AGENTS.md', 'repo_path': 'agentpm/runtime/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'd868dad2-d4ee-4dd1-abeb-f1c2d16316d3', 'logical_name': 'AGENTS::agentpm/scripts/AGENTS.md', 'repo_path': 'agentpm/scripts/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'aad36226-e5ce-460e-9321-0a32e99c1f27', 'logical_name': 'AGENTS::agentpm/scripts/state/AGENTS.md', 'repo_path': 'agentpm/scripts/state/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '219dac86-ca91-4409-9d8f-adced1b8c161', 'logical_name': 'AGENTS::agentpm/server/AGENTS.md', 'repo_path': 'agentpm/server/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '77ca901e-0ff4-4718-b45f-f1056cb9d5cd', 'logical_name': 'AGENTS::agentpm/status/AGENTS.md', 'repo_path': 'agentpm/status/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '55da0565-1e9b-470a-b08d-37ed6376c4a4', 'logical_name': 'AGENTS::agentpm/tests/adapters/AGENTS.md', 'repo_path': 'agentpm/tests/adapters/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'b35e9167-5a2c-49bd-8aac-0d85942dca2a', 'logical_name': 'AGENTS::agentpm/tests/AGENTS.md', 'repo_path': 'agentpm/tests/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'b74d6775-c835-4b7e-bfb6-e49c7172a4d2', 'logical_name': 'AGENTS::agentpm/tests/atlas/AGENTS.md', 'repo_path': 'agentpm/tests/atlas/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'eda8ebc0-bc04-4c1f-8c08-0b6b43f7b615', 'logical_name': 'AGENTS::agentpm/tests/cli/AGENTS.md', 'repo_path': 'agentpm/tests/cli/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'eea9e470-95db-487a-9acd-702455d55d2c', 'logical_name': 'AGENTS::agentpm/tests/db/AGENTS.md', 'repo_path': 'agentpm/tests/db/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'ca138d6b-ba1b-4d0b-befc-6ea8194173d3', 'logical_name': 'AGENTS::agentpm/tests/docs/AGENTS.md', 'repo_path': 'agentpm/tests/docs/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'fe348f4c-2bcf-45a3-84e3-bef52dbc5a81', 'logical_name': 'AGENTS::agentpm/tests/exports/AGENTS.md', 'repo_path': 'agentpm/tests/exports/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '4e3ee39e-077a-42e5-a079-004679989923', 'logical_name': 'AGENTS::agentpm/tests/extractors/AGENTS.md', 'repo_path': 'agentpm/tests/extractors/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '19ccafdd-1f37-4ff7-8d6b-5eca74a38dd7', 'logical_name': 'AGENTS::agentpm/tests/html/AGENTS.md', 'repo_path': 'agentpm/tests/html/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'd50460db-c878-40c2-9fe9-76fcd0528340', 'logical_name': 'AGENTS::agentpm/tests/kb/AGENTS.md', 'repo_path': 'agentpm/tests/kb/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '70efc721-53e7-41ad-a90b-403b15a671d1', 'logical_name': 'AGENTS::agentpm/tests/knowledge/AGENTS.md', 'repo_path': 'agentpm/tests/knowledge/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '1d2971e3-e7ab-45a6-9f11-98947a688916', 'logical_name': 'AGENTS::agentpm/tests/lm/AGENTS.md', 'repo_path': 'agentpm/tests/lm/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '7320e56f-371d-4682-a892-95604fd65555', 'logical_name': 'AGENTS::agentpm/tests/mcp/AGENTS.md', 'repo_path': 'agentpm/tests/mcp/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'dc9af428-af01-40a8-bd6d-fd7b8f4cddb9', 'logical_name': 'AGENTS::agentpm/tests/phase1/AGENTS.md', 'repo_path': 'agentpm/tests/phase1/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '43f0f1f6-32a2-4193-9ded-8e328f3f9f47', 'logical_name': 'AGENTS::agentpm/tests/reality/AGENTS.md', 'repo_path': 'agentpm/tests/reality/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'a02721eb-13a4-48bb-b453-386b41fb16d5', 'logical_name': 'AGENTS::agentpm/tests/status/AGENTS.md', 'repo_path': 'agentpm/tests/status/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'da0bbb49-f53f-444b-abb0-572fe558e81b', 'logical_name': 'AGENTS::agentpm/tests/system/AGENTS.md', 'repo_path': 'agentpm/tests/system/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '08b10090-fce9-46a6-bf58-0eccd3650fab', 'logical_name': 'AGENTS::agentpm/tools/AGENTS.md', 'repo_path': 'agentpm/tools/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '01be4c82-771a-419b-817a-82c09bdf5d00', 'logical_name': 'AGENTS::archive/docs/codebase-cleanup/docs-analysis/AGENTS.snapshot.md', 'repo_path': 'archive/docs/codebase-cleanup/docs-analysis/AGENTS.snapshot.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '27c26272-85b9-480b-8d30-cb7d6d8685f0', 'logical_name': 'AGENTS::archive/docs_legacy/share_scripts_AGENTS.md', 'repo_path': 'archive/docs_legacy/share_scripts_AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'c50f2cc6-f356-478c-be2e-708b93db8a3d', 'logical_name': 'AGENTS::backup/20251206T011629Z/share/AGENTS.md', 'repo_path': 'backup/20251206T011629Z/share/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '070a34b7-ba95-4fa1-ba59-56e9e423925b', 'logical_name': 'AGENTS::backup/20251206T011629Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251206T011629Z/share/scripts_AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '8435b916-da3a-458b-a76d-7c7bb9539046', 'logical_name': 'AGENTS::backup/20251206T044916Z/share/AGENTS.md', 'repo_path': 'backup/20251206T044916Z/share/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'cecdb817-8498-450a-999b-45350a0a2b6a', 'logical_name': 'AGENTS::backup/20251206T044916Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251206T044916Z/share/scripts_AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '8bab6ab5-f325-4417-a6b6-13f05dcbaa91', 'logical_name': 'AGENTS::backup/20251206T050237Z/share/AGENTS.md', 'repo_path': 'backup/20251206T050237Z/share/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '48d69a8f-e65a-42de-95f1-572a0b87d640', 'logical_name': 'AGENTS::backup/20251206T050237Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251206T050237Z/share/scripts_AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '2ea5ae3b-be6a-4b06-820a-51b35d90dfb9', 'logical_name': 'AGENTS::backup/20251206T051001Z/share/AGENTS.md', 'repo_path': 'backup/20251206T051001Z/share/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'e7e6cb1b-ed75-4521-8abc-96b7194b5011', 'logical_name': 'AGENTS::backup/20251206T051001Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251206T051001Z/share/scripts_AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': 'a0cf26be-bf2d-4639-9681-2809b12bdc1d', 'logical_name': 'AGENTS::backup/20251206T051704Z/share/AGENTS.md', 'repo_path': 'backup/20251206T051704Z/share/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '6db27447-3b8f-494d-8075-f99e96972f71', 'logical_name': 'AGENTS::backup/20251206T051704Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251206T051704Z/share/scripts_AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '03b3ca8c-cbd4-4e91-af7e-85c0438161f1', 'logical_name': 'AGENTS::backup/20251207T032033Z/share/AGENTS.md', 'repo_path': 'backup/20251207T032033Z/share/AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '8ca4bc5a-e883-4fc2-a58c-0d39add2a044', 'logical_name': 'AGENTS::backup/20251207T032033Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T032033Z/share/scripts_AGENTS.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '96b5f2e1-9bc4-43f1-a485-b2d8aa3f0732', 'logical_name': 'AGENTS::backup/20251207T045808Z/share/AGENTS.md', 'repo_path': 'backup/20251207T045808Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '5b953be6-732a-4a7e-a060-7e5a55d23fa8', 'logical_name': 'AGENTS::backup/20251207T045808Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T045808Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3b6d7cc7-5629-4623-adc3-4295b4edd55a', 'logical_name': 'AGENTS::backup/20251207T062821Z/share/AGENTS.md', 'repo_path': 'backup/20251207T062821Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '4ad5b70b-a850-4230-ac13-68ed9acae2d0', 'logical_name': 'AGENTS::backup/20251207T062821Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T062821Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '97d330d4-4291-4ad7-a89e-f04a9068d76a', 'logical_name': 'AGENTS::backup/20251207T062821Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T062821Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '1015d64c-c7e1-4096-8ef3-883e944cb7af', 'logical_name': 'AGENTS::backup/20251207T153233Z/share/AGENTS.md', 'repo_path': 'backup/20251207T153233Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '447c360c-a3d9-46ec-bcc9-bb24d2c5f9f8', 'logical_name': 'AGENTS::backup/20251207T153233Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T153233Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'a46a67a4-2e57-4cec-8e89-0a1d3b07f1a8', 'logical_name': 'AGENTS::backup/20251207T153233Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T153233Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '72c7f368-1c2e-4e90-b507-3c4a2853a929', 'logical_name': 'AGENTS::backup/20251207T164600Z/share/AGENTS.md', 'repo_path': 'backup/20251207T164600Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'fb6762fd-ff0d-483a-a6dd-4ede24453eab', 'logical_name': 'AGENTS::backup/20251207T164600Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T164600Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '8b1df3c9-cd22-4a5b-a521-bb86d3508911', 'logical_name': 'AGENTS::backup/20251207T164600Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T164600Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3b1e1101-b19b-41f7-aee0-c052cac7aefa', 'logical_name': 'AGENTS::backup/20251207T173128Z/share/AGENTS.md', 'repo_path': 'backup/20251207T173128Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9ecb488c-5083-4f8f-829f-90f05ec9e878', 'logical_name': 'AGENTS::backup/20251207T173128Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T173128Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f1d5b89b-dc08-470e-80f0-843ca870ec23', 'logical_name': 'AGENTS::backup/20251207T173128Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T173128Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '284e8b66-04b2-45d4-a2f9-79f62b40d860', 'logical_name': 'AGENTS::backup/20251207T173726Z/share/AGENTS.md', 'repo_path': 'backup/20251207T173726Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c72c38a2-e99b-416d-b620-86d3134f08ec', 'logical_name': 'AGENTS::backup/20251207T173726Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T173726Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '1e3cf244-44d4-4723-9355-4d4f4be5b9b1', 'logical_name': 'AGENTS::backup/20251207T173726Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T173726Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '92bfabd8-2a07-47d8-a363-29a74dc56e59', 'logical_name': 'AGENTS::backup/20251207T174051Z/share/AGENTS.md', 'repo_path': 'backup/20251207T174051Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '4d38f7b7-f8d8-4717-afb6-d82dffb8e0d9', 'logical_name': 'AGENTS::backup/20251207T174051Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T174051Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '019467cd-b467-4d77-9575-396b9d326d47', 'logical_name': 'AGENTS::backup/20251207T174051Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T174051Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '8ccfe530-fabd-4d3c-92f5-aab0e929c723', 'logical_name': 'AGENTS::backup/20251207T174800Z/share/AGENTS.md', 'repo_path': 'backup/20251207T174800Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'b25e9c30-0143-44e2-b2d1-ecae09f62be3', 'logical_name': 'AGENTS::backup/20251207T174800Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T174800Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '04ceb22b-2125-4df1-97ee-b520cd4ebf14', 'logical_name': 'AGENTS::backup/20251207T175416Z/share/AGENTS.md', 'repo_path': 'backup/20251207T175416Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3f3153bf-1811-4314-b2db-e01f5aeaaa25', 'logical_name': 'AGENTS::backup/20251207T175416Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T175416Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '8ec63421-80ca-486f-8455-deda85db39f5', 'logical_name': 'AGENTS::backup/20251207T175416Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T175416Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '75bfa88d-01ec-4bf4-a761-f0a96ff96ad5', 'logical_name': 'AGENTS::backup/20251207T180048Z/share/AGENTS.md', 'repo_path': 'backup/20251207T180048Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'ab5c6bf0-30ae-4e2f-ad86-3659bd4a61c5', 'logical_name': 'AGENTS::backup/20251207T180048Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T180048Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '32f0d0a4-9945-401f-98ff-1d3d9baa40c8', 'logical_name': 'AGENTS::backup/20251207T180048Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T180048Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd3da4994-51ad-407d-9424-658691943e79', 'logical_name': 'AGENTS::backup/20251207T180115Z/share/AGENTS.md', 'repo_path': 'backup/20251207T180115Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '1331fc91-9544-4f04-bbb0-30877e1c4253', 'logical_name': 'AGENTS::backup/20251207T180115Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T180115Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd987ac2a-3e4d-4369-b2fc-049deae1da0a', 'logical_name': 'AGENTS::backup/20251207T180115Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T180115Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3e62f87b-73ac-44a4-87f2-28a882912964', 'logical_name': 'AGENTS::backup/20251207T181455Z/share/AGENTS.md', 'repo_path': 'backup/20251207T181455Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '29e9c7c2-3279-4feb-84ce-17aa4befbb7f', 'logical_name': 'AGENTS::backup/20251207T181455Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T181455Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e1949b87-30b6-43b8-8159-ed1946a07277', 'logical_name': 'AGENTS::backup/20251207T181455Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T181455Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'dcfb6510-12c4-46d4-ae0c-b393d1c85154', 'logical_name': 'AGENTS::backup/20251207T181847Z/share/AGENTS.md', 'repo_path': 'backup/20251207T181847Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'b43ad30c-2b9f-405b-984a-85918322044e', 'logical_name': 'AGENTS::backup/20251207T181847Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T181847Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e2cc7bc2-3d25-4780-b7de-950e739f3279', 'logical_name': 'AGENTS::backup/20251207T181847Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T181847Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'ed244474-5f6a-465f-9a4b-69e07ea16059', 'logical_name': 'AGENTS::backup/20251207T183044Z/share/AGENTS.md', 'repo_path': 'backup/20251207T183044Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd220bbe6-2cae-4971-9fe6-8348af9e15db', 'logical_name': 'AGENTS::backup/20251207T183044Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T183044Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '39e0a974-5c72-4040-a2b9-b04558cb7af3', 'logical_name': 'AGENTS::backup/20251207T183044Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T183044Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '6e940d71-7c45-4066-9ea4-decae82cac00', 'logical_name': 'AGENTS::backup/20251207T183105Z/share/AGENTS.md', 'repo_path': 'backup/20251207T183105Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '152490c8-fba5-4419-9bf7-1ba3aa735bd3', 'logical_name': 'AGENTS::backup/20251207T183105Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T183105Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3fb6f9bf-6fca-402f-8aec-ccc7320c395e', 'logical_name': 'AGENTS::backup/20251207T183105Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T183105Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd9f12524-82d0-4a2e-8c8a-e13736dc7f06', 'logical_name': 'AGENTS::backup/20251207T183129Z/share/AGENTS.md', 'repo_path': 'backup/20251207T183129Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '7f26ff7a-1526-46d8-a4ed-99d7855971bc', 'logical_name': 'AGENTS::backup/20251207T183129Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T183129Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '42145209-ab51-4ca7-a570-462352e34b47', 'logical_name': 'AGENTS::backup/20251207T183129Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T183129Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '90281d0d-be09-4800-84c3-781637ff5ef3', 'logical_name': 'AGENTS::backup/20251207T183807Z/share/AGENTS.md', 'repo_path': 'backup/20251207T183807Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '7c30348a-3207-4878-abb6-d482cd135f54', 'logical_name': 'AGENTS::backup/20251207T183807Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T183807Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '056c5e9b-7445-448e-87c3-55f24608e9f8', 'logical_name': 'AGENTS::backup/20251207T183807Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T183807Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '81f5b494-9be1-4dae-a36b-45a85b7471c4', 'logical_name': 'AGENTS::backup/20251207T185140Z/share/AGENTS.md', 'repo_path': 'backup/20251207T185140Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'dae82ac3-54db-470f-a2f2-9f7cfbf44959', 'logical_name': 'AGENTS::backup/20251207T185140Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T185140Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '6876e943-f0cc-4f8a-a831-c6820b4cd05f', 'logical_name': 'AGENTS::backup/20251207T185140Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T185140Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2d87f7be-be19-4266-a353-d058d2f50281', 'logical_name': 'AGENTS::backup/20251207T185702Z/share/AGENTS.md', 'repo_path': 'backup/20251207T185702Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9fc173a0-a4e3-4ca3-907f-d96ba662ebda', 'logical_name': 'AGENTS::backup/20251207T185702Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T185702Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '768ea4de-02ee-440e-ad0b-c728b03174b2', 'logical_name': 'AGENTS::backup/20251207T185702Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T185702Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'aed51097-b145-448c-a830-7a734fdca44e', 'logical_name': 'AGENTS::backup/20251207T191953Z/share/AGENTS.md', 'repo_path': 'backup/20251207T191953Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'a38b5480-b881-4640-8675-f84c65d4953f', 'logical_name': 'AGENTS::backup/20251207T191953Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T191953Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '8fd1a63c-283f-42c8-a8bd-3cc1ec71d91b', 'logical_name': 'AGENTS::backup/20251207T191953Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T191953Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'a8827e8e-89ad-4c10-88b3-771891508aa8', 'logical_name': 'AGENTS::backup/20251207T192924Z/share/AGENTS.md', 'repo_path': 'backup/20251207T192924Z/share/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'def551c4-e6e9-4246-8302-549abf5306c5', 'logical_name': 'AGENTS::backup/20251207T192924Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md', 'repo_path': 'backup/20251207T192924Z/share/PHASE18_AGENTS_SYNC_SUMMARY.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '33e2a6db-f4d8-48ea-a08e-67d3a72773bc', 'logical_name': 'AGENTS::backup/20251207T192924Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md', 'repo_path': 'backup/20251207T192924Z/share/PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'aafc8edb-880f-4842-aa69-21b352206fc3', 'logical_name': 'AGENTS::backup/20251207T192924Z/share/pm_boot/AGENTS.md', 'repo_path': 'backup/20251207T192924Z/share/pm_boot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9a334c6d-6b96-4aa5-9c22-4df95e56c68a', 'logical_name': 'AGENTS::backup/20251207T192924Z/share/scripts_AGENTS.md', 'repo_path': 'backup/20251207T192924Z/share/scripts_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '186f8d94-608b-4230-90af-39945aa180b9', 'logical_name': 'AGENTS::.cursor/rules/AGENTS.md', 'repo_path': '.cursor/rules/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '69a956eb-5ba8-4138-ad43-0447e9a2fa14', 'logical_name': 'AGENTS::docs/adr/AGENTS.md', 'repo_path': 'docs/adr/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3ce3c26d-9545-430f-8301-5e5dcb51fd67', 'logical_name': 'AGENTS::docs/ADRs/AGENTS.md', 'repo_path': 'docs/ADRs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e5d7fa9e-08db-4c6f-9dbe-3a9fe9258fc9', 'logical_name': 'AGENTS::docs/AGENTS.md', 'repo_path': 'docs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e3ff8330-baea-47e3-bbbd-c9e97bd4cbe0', 'logical_name': 'AGENTS::docs/AI_LEARNING_SYSTEM_AGENTS.md', 'repo_path': 'docs/AI_LEARNING_SYSTEM_AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '7c71590c-7c48-4fad-87f7-0875fe1562d8', 'logical_name': 'AGENTS::docs/analysis/AGENTS_KB_FORensics.md', 'repo_path': 'docs/analysis/AGENTS_KB_FORensics.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '91fb4ee2-26fb-454c-b3a1-cece4de06c55', 'logical_name': 'AGENTS::docs/analysis/AGENTS.md', 'repo_path': 'docs/analysis/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '846a694f-938b-4003-9ccc-a1f3450e79fb', 'logical_name': 'AGENTS::docs/ANALYSIS/AGENTS.md', 'repo_path': 'docs/ANALYSIS/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd2e3ff9c-915e-4209-a114-124346ae8c75', 'logical_name': 'AGENTS::docs/analysis/phase7_governance/AGENTS.snapshot.md', 'repo_path': 'docs/analysis/phase7_governance/AGENTS.snapshot.md', 'exists_on_disk': False, 'enabled': False, 'importance': 'unknown'}, {'doc_id': '686c4ff6-5a7a-4823-b506-e6bb1cc71496', 'logical_name': 'AGENTS::docs/atlas/AGENTS.md', 'repo_path': 'docs/atlas/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'ee911e86-fe82-4b8c-aed7-bbdec80acd9a', 'logical_name': 'AGENTS::docs/audits/AGENTS.md', 'repo_path': 'docs/audits/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '0bb53c96-158f-4b2a-a8f9-5c4fe25eaaa9', 'logical_name': 'AGENTS::docs/audits/AGENTS_MD_AUDIT_20251112.md', 'repo_path': 'docs/audits/AGENTS_MD_AUDIT_20251112.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '69f46074-9511-42b8-b32b-bb2ad87db28f', 'logical_name': 'AGENTS::docs/consumers/AGENTS.md', 'repo_path': 'docs/consumers/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2d5e06f7-19f6-4c60-829a-acb28e77e6ae', 'logical_name': 'AGENTS::docs/evidence/AGENTS.md', 'repo_path': 'docs/evidence/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '56d68327-9178-4428-aff3-fdb95bfb9ee7', 'logical_name': 'AGENTS::docs/forest/AGENTS.md', 'repo_path': 'docs/forest/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2a913c75-2532-4c02-963f-452b184ef93d', 'logical_name': 'AGENTS::docs/handoff/AGENTS.md', 'repo_path': 'docs/handoff/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f1190a6d-8b99-4a0a-ba6e-94bd6f8620ee', 'logical_name': 'AGENTS::docs/hints/AGENTS.md', 'repo_path': 'docs/hints/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f1fef275-67fa-4bbb-875b-1f97062cd470', 'logical_name': 'AGENTS::docs/ingestion/AGENTS.md', 'repo_path': 'docs/ingestion/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '90445013-6349-49b2-ae0d-bdf97ad9e24e', 'logical_name': 'AGENTS::docs/ops/AGENTS.md', 'repo_path': 'docs/ops/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd55536f4-9024-4b89-823b-0f672fe08355', 'logical_name': 'AGENTS::docs/OPS/AGENTS.md', 'repo_path': 'docs/OPS/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f7895dce-67c4-43b1-9dd2-8f4cc275d6e2', 'logical_name': 'AGENTS::docs/phase10/AGENTS.md', 'repo_path': 'docs/phase10/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '50af9a75-af93-4a25-b4ed-b83cc48f4925', 'logical_name': 'AGENTS::docs/phase9/AGENTS.md', 'repo_path': 'docs/phase9/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '888fc5a1-48bc-4512-b5e6-e6df0edbce65', 'logical_name': 'AGENTS::docs/plan-074/AGENTS.md', 'repo_path': 'docs/plan-074/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '1f80883e-97e1-4793-b15e-dfac3a47f282', 'logical_name': 'AGENTS::docs/plans/AGENTS.md', 'repo_path': 'docs/plans/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f0ee7e3c-2923-4144-9ae6-53e15ec41ada', 'logical_name': 'AGENTS::docs/projects/AGENTS.md', 'repo_path': 'docs/projects/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9bc2879a-baaf-4df6-b667-4d2e13bad042', 'logical_name': 'AGENTS::docs/projects/storymaker/AGENTS.md', 'repo_path': 'docs/projects/storymaker/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9a6f35f5-59fa-4b90-a2b5-50a725279034', 'logical_name': 'AGENTS::docs/research/AGENTS.md', 'repo_path': 'docs/research/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9cf9c101-ae6e-4251-aa97-c7be0c9fb8ea', 'logical_name': 'AGENTS::docs/rfcs/AGENTS.md', 'repo_path': 'docs/rfcs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '305aced3-93fa-44fc-9e10-dcfdc6727d7a', 'logical_name': 'AGENTS::docs/runbooks/AGENTS.md', 'repo_path': 'docs/runbooks/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '223c6e23-2a08-4ecb-8dc8-02b4ca75dc2c', 'logical_name': 'RUNBOOK::docs/runbooks/AGENTS.md', 'repo_path': 'docs/runbooks/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '77990c6e-22b2-4935-83aa-faa252c79847', 'logical_name': 'AGENTS::docs/schema/AGENTS.md', 'repo_path': 'docs/schema/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '77de3242-0a68-4d04-81dc-7a561a9f81c9', 'logical_name': 'AGENTS::docs/schemas/AGENTS.md', 'repo_path': 'docs/schemas/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f7b36005-e226-4fe1-a0c7-c6551501ec4d', 'logical_name': 'AGENTS::docs/sql/AGENTS.md', 'repo_path': 'docs/sql/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c9895b60-6f8f-4558-8c9b-b5aa179339ca', 'logical_name': 'AGENTS::docs/SSOT/AGENTS.md', 'repo_path': 'docs/SSOT/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'critical'}, {'doc_id': 'e2f2c400-a356-4144-bfc8-5c8066014b40', 'logical_name': 'SSOT::docs/SSOT/AGENTS.md', 'repo_path': 'docs/SSOT/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'critical'}, {'doc_id': '51e37396-5b23-4afb-a577-4a63e3f4573e', 'logical_name': 'AGENTS::docs/tickets/AGENTS.md', 'repo_path': 'docs/tickets/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c64d0662-32e5-48ae-a54f-6b53fcfc192c', 'logical_name': 'AGENTS::docs/vendor/AGENTS.md', 'repo_path': 'docs/vendor/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '847c94dc-9235-4325-8d4a-0a53230a7dab', 'logical_name': 'AGENTS::migrations/AGENTS.md', 'repo_path': 'migrations/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e8ad4438-acc1-4e78-a78a-4c1d2f152b66', 'logical_name': 'AGENTS::pmagent/adapters/AGENTS.md', 'repo_path': 'pmagent/adapters/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '91b14944-ee48-4151-83c1-b0ca3476ea7c', 'logical_name': 'CODE::pmagent/adapters/codex_cli.py', 'repo_path': 'pmagent/adapters/codex_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '38ab7700-6235-4e74-934c-4f9c0a50c061', 'logical_name': 'CODE::pmagent/adapters/gemini_cli.py', 'repo_path': 'pmagent/adapters/gemini_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4681f03b-b87e-4224-a920-8f67b365c02a', 'logical_name': 'CODE::pmagent/adapters/lm_studio.py', 'repo_path': 'pmagent/adapters/lm_studio.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6cfcfe97-9cd5-4082-906b-09e36bd51dae', 'logical_name': 'CODE::pmagent/adapters/mcp_db.py', 'repo_path': 'pmagent/adapters/mcp_db.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '3b4e581b-2a1d-4714-b925-84aac0006ea8', 'logical_name': 'CODE::pmagent/adapters/ollama.py', 'repo_path': 'pmagent/adapters/ollama.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '53c99409-d776-4c5e-b0b0-8941c56825de', 'logical_name': 'CODE::pmagent/adapters/planning_common.py', 'repo_path': 'pmagent/adapters/planning_common.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '61b033e1-4087-4087-99b1-5d5f6b9fce39', 'logical_name': 'CODE::pmagent/adapters/planning.py', 'repo_path': 'pmagent/adapters/planning.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6d662561-8fc0-4f48-a545-c85315b46745', 'logical_name': 'CODE::pmagent/adapters/theology.py', 'repo_path': 'pmagent/adapters/theology.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '03bfe7e1-912d-4b43-ac39-4b7cc21588da', 'logical_name': 'AGENTS::pmagent/ai_docs/AGENTS.md', 'repo_path': 'pmagent/ai_docs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '08bac9d2-cc55-407f-a62d-cdf1e0622365', 'logical_name': 'CODE::pmagent/ai_docs/reality_check_ai_notes.py', 'repo_path': 'pmagent/ai_docs/reality_check_ai_notes.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '00b54952-fc92-4cc9-a026-4b54c62d6757', 'logical_name': 'AGENTS::pmagent/atlas/AGENTS.md', 'repo_path': 'pmagent/atlas/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '00f8e6aa-edd3-425c-9515-dab7e802e640', 'logical_name': 'CODE::pmagent/atlas/drilldowns.py', 'repo_path': 'pmagent/atlas/drilldowns.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '909f62dc-6923-4eef-880b-c237f60781cd', 'logical_name': 'CODE::pmagent/atlas/generate.py', 'repo_path': 'pmagent/atlas/generate.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'fbcbc2d9-a773-4485-8fb8-8d72ac79af79', 'logical_name': 'CODE::pmagent/atlas/reranker_badges.py', 'repo_path': 'pmagent/atlas/reranker_badges.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f2ec6f6a-7fdd-4569-a9c5-4b949f93aa2b', 'logical_name': 'CODE::pmagent/atlas/screenshots.py', 'repo_path': 'pmagent/atlas/screenshots.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '9d486daa-6216-4e2a-975f-1da22bca9b0d', 'logical_name': 'CODE::pmagent/atlas/webproof.py', 'repo_path': 'pmagent/atlas/webproof.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e00406d0-ecee-48d8-ac67-0b1b4b6c1101', 'logical_name': 'AGENTS::pmagent/biblescholar/AGENTS.md', 'repo_path': 'pmagent/biblescholar/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f636f66d-b9e8-4541-80ef-f97453ebb342', 'logical_name': 'CODE::pmagent/biblescholar/bible_db_adapter.py', 'repo_path': 'pmagent/biblescholar/bible_db_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f2c1d1d4-f215-4163-814e-41c1aab6700d', 'logical_name': 'CODE::pmagent/biblescholar/bible_passage_flow.py', 'repo_path': 'pmagent/biblescholar/bible_passage_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'a30954c1-e9a2-40b0-8579-af643216fe1e', 'logical_name': 'CODE::pmagent/biblescholar/cross_language_flow.py', 'repo_path': 'pmagent/biblescholar/cross_language_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1daaae78-010d-4e58-a426-003a45b668c0', 'logical_name': 'CODE::pmagent/biblescholar/cross_language_semantic_flow.py', 'repo_path': 'pmagent/biblescholar/cross_language_semantic_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6e7cf77f-f38b-4c71-9a68-541c5d401f23', 'logical_name': 'CODE::pmagent/biblescholar/gematria_adapter.py', 'repo_path': 'pmagent/biblescholar/gematria_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '3d956269-b8fb-45c4-8c8c-8e3da0764a30', 'logical_name': 'CODE::pmagent/biblescholar/gematria_flow.py', 'repo_path': 'pmagent/biblescholar/gematria_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '68b0ea6a-8f1c-423d-b14e-02709855df97', 'logical_name': 'CODE::pmagent/biblescholar/insights_flow.py', 'repo_path': 'pmagent/biblescholar/insights_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bef86ec0-2c45-45cb-bc09-68310ad54d49', 'logical_name': 'CODE::pmagent/biblescholar/lexicon_adapter.py', 'repo_path': 'pmagent/biblescholar/lexicon_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5a17f31a-3234-4edc-84da-30c7cdf045af', 'logical_name': 'CODE::pmagent/biblescholar/lexicon_flow.py', 'repo_path': 'pmagent/biblescholar/lexicon_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '7ae4f35d-f629-4f38-9803-9d773013d80c', 'logical_name': 'CODE::pmagent/biblescholar/passage.py', 'repo_path': 'pmagent/biblescholar/passage.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '95f47e90-df06-4781-8337-b5dae290e703', 'logical_name': 'CODE::pmagent/biblescholar/reference_parser.py', 'repo_path': 'pmagent/biblescholar/reference_parser.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'a0e95fa6-ed80-49bd-aec5-d3d078a8f19d', 'logical_name': 'CODE::pmagent/biblescholar/reference_slice.py', 'repo_path': 'pmagent/biblescholar/reference_slice.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'a7841acf-838b-41d5-bfb5-a109c93ead31', 'logical_name': 'CODE::pmagent/biblescholar/relationship_adapter.py', 'repo_path': 'pmagent/biblescholar/relationship_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '693f7efe-cf34-4488-917f-459daf096c1b', 'logical_name': 'CODE::pmagent/biblescholar/search_flow.py', 'repo_path': 'pmagent/biblescholar/search_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '7039232c-d513-4126-8291-e47cc47c3173', 'logical_name': 'CODE::pmagent/biblescholar/semantic_search_flow.py', 'repo_path': 'pmagent/biblescholar/semantic_search_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'cd359984-be79-4fb8-af97-8c58b0f91105', 'logical_name': 'AGENTS::pmagent/biblescholar/tests/AGENTS.md', 'repo_path': 'pmagent/biblescholar/tests/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9f02f598-4469-402a-9d7b-cab62aa58884', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_bible_db_adapter.py', 'repo_path': 'pmagent/biblescholar/tests/test_bible_db_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5420195e-2b0e-4ec3-a41c-36c7efe97c90', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_bible_passage_flow.py', 'repo_path': 'pmagent/biblescholar/tests/test_bible_passage_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ed33fa47-21fe-4726-b66a-bccc4ed8b005', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_cross_language_flow.py', 'repo_path': 'pmagent/biblescholar/tests/test_cross_language_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '51d05836-61e4-4f8a-96b5-29390858b3d1', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_cross_language.py', 'repo_path': 'pmagent/biblescholar/tests/test_cross_language.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '184f6a5d-7a63-4eb3-bc1d-f3d64554e95e', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_gematria_adapter.py', 'repo_path': 'pmagent/biblescholar/tests/test_gematria_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1aa83239-d4de-4c1a-9966-0f051c669c2a', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_gematria_flow.py', 'repo_path': 'pmagent/biblescholar/tests/test_gematria_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f15c62e5-34e9-4d13-8d46-46df4116cc18', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_insights_flow.py', 'repo_path': 'pmagent/biblescholar/tests/test_insights_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '19180db5-eb7a-4ec4-a5fc-0c12b5d08ff7', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_lexicon_adapter.py', 'repo_path': 'pmagent/biblescholar/tests/test_lexicon_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e2e61290-4fc3-4127-8804-acb799294aac', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_lexicon_flow.py', 'repo_path': 'pmagent/biblescholar/tests/test_lexicon_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4a0893c5-99da-4358-b1c5-efba234647b4', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_reference_parser.py', 'repo_path': 'pmagent/biblescholar/tests/test_reference_parser.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'c9ea4bd9-7a82-4c17-91c4-0b4913b11ae4', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_reference_slice.py', 'repo_path': 'pmagent/biblescholar/tests/test_reference_slice.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '26a5afe3-35b7-4f0f-aa38-90ee710272df', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_relationship_adapter.py', 'repo_path': 'pmagent/biblescholar/tests/test_relationship_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '2f59ab58-f4df-4cb3-81e2-aa18ca135caf', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_search_flow.py', 'repo_path': 'pmagent/biblescholar/tests/test_search_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bf75a564-1017-44b0-ab1f-ed1d650a9a86', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_vector_adapter.py', 'repo_path': 'pmagent/biblescholar/tests/test_vector_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f1b08866-9d8d-4fe5-b5da-9e8abd95b61a', 'logical_name': 'CODE::pmagent/biblescholar/tests/test_vector_flow.py', 'repo_path': 'pmagent/biblescholar/tests/test_vector_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '440df1fb-8378-4bc0-8763-b89eca453ab0', 'logical_name': 'CODE::pmagent/biblescholar/vector_adapter.py', 'repo_path': 'pmagent/biblescholar/vector_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f206a970-c38c-497f-a624-fc4dbdeca598', 'logical_name': 'CODE::pmagent/biblescholar/vector_flow.py', 'repo_path': 'pmagent/biblescholar/vector_flow.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1a77ed17-28d3-4e51-98c2-fae58d0dc238', 'logical_name': 'AGENTS::pmagent/bus/AGENTS.md', 'repo_path': 'pmagent/bus/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e30cbf29-9924-41e4-bcf7-f094b7fb20b6', 'logical_name': 'CODE::pmagent/cli.py', 'repo_path': 'pmagent/cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '347072e0-3895-4534-bd0d-2dd86a1cb450', 'logical_name': 'AGENTS::pmagent/control_plane/AGENTS.md', 'repo_path': 'pmagent/control_plane/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'a3f78a98-3dd0-4dc7-bb7a-624b5a16f0d3', 'logical_name': 'CODE::pmagent/control_plane/doc_fragments.py', 'repo_path': 'pmagent/control_plane/doc_fragments.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '3dc53777-d11a-4f31-a884-13e65338c37e', 'logical_name': 'CODE::pmagent/control_plane/exports.py', 'repo_path': 'pmagent/control_plane/exports.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '287c711f-af5d-4a9e-9520-ad0f3839996c', 'logical_name': 'CODE::pmagent/control_plane.py', 'repo_path': 'pmagent/control_plane.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd0b2f9eb-7e73-47a9-b553-6dd833501812', 'logical_name': 'CODE::pmagent/control_plane/sessions.py', 'repo_path': 'pmagent/control_plane/sessions.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '8b1d4f09-cfd2-433e-a1bd-f9947a365385', 'logical_name': 'CODE::pmagent/control_widgets/adapter.py', 'repo_path': 'pmagent/control_widgets/adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e4a828dc-15b2-414f-a049-9fb405cd5e6f', 'logical_name': 'AGENTS::pmagent/control_widgets/AGENTS.md', 'repo_path': 'pmagent/control_widgets/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '259d107b-b437-4a5a-acd5-21e74705c646', 'logical_name': 'AGENTS::pmagent/db/AGENTS.md', 'repo_path': 'pmagent/db/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f4e55bdf-63e6-4050-aceb-ef581479038c', 'logical_name': 'CODE::pmagent/db/loader.py', 'repo_path': 'pmagent/db/loader.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '2c957d31-1b40-49cb-8823-91ed69bb3e59', 'logical_name': 'CODE::pmagent/db/models_graph_stats.py', 'repo_path': 'pmagent/db/models_graph_stats.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'cc54ba30-cf0d-4a04-93c1-9e5595c3fef7', 'logical_name': 'AGENTS::pmagent/dms/AGENTS.md', 'repo_path': 'pmagent/dms/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3b4401d3-678e-4c6b-9acf-878bd66654a3', 'logical_name': 'AGENTS::pmagent/docs/AGENTS.md', 'repo_path': 'pmagent/docs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c7b4e998-a194-421e-a0c8-d18d6751d458', 'logical_name': 'CODE::pmagent/docs/search.py', 'repo_path': 'pmagent/docs/search.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'a0fcc619-3a8a-4244-8066-1fb9576b9ddb', 'logical_name': 'AGENTS::pmagent/exports/AGENTS.md', 'repo_path': 'pmagent/exports/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '66da76df-a2f4-46ed-9ceb-cb58c0310f91', 'logical_name': 'CODE::pmagent/exports/generate.py', 'repo_path': 'pmagent/exports/generate.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'b22e81c1-8503-4d8d-84fd-66e2439dd4d7', 'logical_name': 'AGENTS::pmagent/extractors/AGENTS.md', 'repo_path': 'pmagent/extractors/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '54057d07-fad7-4fdc-abdb-aeb9cc5aa15b', 'logical_name': 'CODE::pmagent/extractors/provenance.py', 'repo_path': 'pmagent/extractors/provenance.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '24c5828f-abf6-44b5-93ed-b1d663fc12c0', 'logical_name': 'AGENTS::pmagent/gatekeeper/AGENTS.md', 'repo_path': 'pmagent/gatekeeper/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3a01b1fc-260d-472d-af28-e8d78b057a59', 'logical_name': 'CODE::pmagent/gatekeeper/impl.py', 'repo_path': 'pmagent/gatekeeper/impl.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ce4e400f-dca3-485f-a8f8-7bc440156adc', 'logical_name': 'CODE::pmagent/gatekeeper/__init__.py', 'repo_path': 'pmagent/gatekeeper/__init__.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ae05576c-d4d3-4af5-9ebb-b4a417068b99', 'logical_name': 'CODE::pmagent/gatekeeper.py', 'repo_path': 'pmagent/gatekeeper.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'dbf5c323-a262-4914-a4e8-83f48634f664', 'logical_name': 'AGENTS::pmagent/governance/AGENTS.md', 'repo_path': 'pmagent/governance/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '66aaea86-a5bc-4709-8ce6-00f232d41717', 'logical_name': 'AGENTS::pmagent/graph/AGENTS.md', 'repo_path': 'pmagent/graph/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'fd79467b-b7bc-4e56-8daa-ad24dace1840', 'logical_name': 'CODE::pmagent/graph/assembler.py', 'repo_path': 'pmagent/graph/assembler.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '466a3c9a-88c1-42bc-8c20-5b7c132c9230', 'logical_name': 'AGENTS::pmagent/guard/AGENTS.md', 'repo_path': 'pmagent/guard/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '96125c94-1a1b-492a-a741-56ff72033716', 'logical_name': 'AGENTS::pmagent/guarded/AGENTS.md', 'repo_path': 'pmagent/guarded/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '00548742-fc93-432c-9132-f396d808236d', 'logical_name': 'CODE::pmagent/guarded/autopilot_adapter.py', 'repo_path': 'pmagent/guarded/autopilot_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6ebd2a7d-5206-43ab-b650-cb8636035fc4', 'logical_name': 'CODE::pmagent/guarded/gatekeeper.py', 'repo_path': 'pmagent/guarded/gatekeeper.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '9beee2ff-2c34-4999-9316-7f39777d3b2a', 'logical_name': 'CODE::pmagent/guarded/guard_shim.py', 'repo_path': 'pmagent/guarded/guard_shim.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e9259643-6015-4307-b958-b18ab88e5d09', 'logical_name': 'CODE::pmagent/guarded/violations.py', 'repo_path': 'pmagent/guarded/violations.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5fe2978b-cde4-472c-9882-df61469a90a7', 'logical_name': 'CODE::pmagent/guard/impl.py', 'repo_path': 'pmagent/guard/impl.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd3d9dc7f-6aca-4fef-afc8-f062942de70e', 'logical_name': 'CODE::pmagent/guard/__init__.py', 'repo_path': 'pmagent/guard/__init__.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '412de742-25e3-467d-80cb-50c7ac6f9ca1', 'logical_name': 'AGENTS::pmagent/handoff/AGENTS.md', 'repo_path': 'pmagent/handoff/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'a0852fce-4ac4-4934-b6af-142ab06401a3', 'logical_name': 'AGENTS::pmagent/hints/AGENTS.md', 'repo_path': 'pmagent/hints/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '6866d9f7-7c4c-4111-bfc9-2e1a7a1092e1', 'logical_name': 'CODE::pmagent/hints/registry.py', 'repo_path': 'pmagent/hints/registry.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'dd287ed2-581f-4a6f-ba66-25d27a18fa23', 'logical_name': 'AGENTS::pmagent/kb/AGENTS.md', 'repo_path': 'pmagent/kb/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2409211c-141a-4709-89dc-578f1b53be42', 'logical_name': 'CODE::pmagent/kb/classify.py', 'repo_path': 'pmagent/kb/classify.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e1f82632-8249-41a6-bb36-5ab863e66e13', 'logical_name': 'CODE::pmagent/kb/registry.py', 'repo_path': 'pmagent/kb/registry.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '3f6e87d2-e72e-4c51-94a1-a10cc89a059f', 'logical_name': 'CODE::pmagent/kb/search.py', 'repo_path': 'pmagent/kb/search.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '277debb0-c122-4105-a168-80569ffa2cff', 'logical_name': 'AGENTS::pmagent/kernel/AGENTS.md', 'repo_path': 'pmagent/kernel/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'aabddc1f-2fcb-47ee-9c84-f352712ec0ab', 'logical_name': 'AGENTS::pmagent/knowledge/AGENTS.md', 'repo_path': 'pmagent/knowledge/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '09f54afc-f2ae-4ce5-8d71-f8d9e28366c1', 'logical_name': 'CODE::pmagent/knowledge/qa_docs.py', 'repo_path': 'pmagent/knowledge/qa_docs.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '8b272076-f46b-49a2-94fe-b511a265d95c', 'logical_name': 'CODE::pmagent/knowledge/retrieval.py', 'repo_path': 'pmagent/knowledge/retrieval.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '40b72e67-8962-49ea-9d21-37303a587a66', 'logical_name': 'AGENTS::pmagent/lm/AGENTS.md', 'repo_path': 'pmagent/lm/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c8876696-b0c0-42a1-9c26-e70d7f8942d2', 'logical_name': 'CODE::pmagent/lm/lm_status.py', 'repo_path': 'pmagent/lm/lm_status.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '51cc64a7-2822-49ea-84cf-bb51d8d497c5', 'logical_name': 'CODE::pmagent/lm/router.py', 'repo_path': 'pmagent/lm/router.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'a575a579-a212-480d-8b95-329ff8e49ac4', 'logical_name': 'CODE::pmagent/lm_widgets/adapter.py', 'repo_path': 'pmagent/lm_widgets/adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6fdc7fd3-9376-4705-93e1-a9b820bc2631', 'logical_name': 'AGENTS::pmagent/lm_widgets/AGENTS.md', 'repo_path': 'pmagent/lm_widgets/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'fc1939a8-c7ed-44c8-ac66-53de4c0f73ad', 'logical_name': 'AGENTS::pmagent/mcp/AGENTS.md', 'repo_path': 'pmagent/mcp/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f0f3ac1c-759c-4f64-a380-aadbb5abfdb6', 'logical_name': 'CODE::pmagent/mcp/ingest.py', 'repo_path': 'pmagent/mcp/ingest.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '71520d22-67c0-40a2-9f36-dba0e53aa254', 'logical_name': 'AGENTS::pmagent/metrics/AGENTS.md', 'repo_path': 'pmagent/metrics/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '451a6327-0a50-48ec-aa45-5a4c9227c493', 'logical_name': 'CODE::pmagent/metrics/graph_rollup.py', 'repo_path': 'pmagent/metrics/graph_rollup.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5c08c276-fe0c-4d92-9e24-f03890b88d8f', 'logical_name': 'AGENTS::pmagent/modules/AGENTS.md', 'repo_path': 'pmagent/modules/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '38af1974-f2a6-4ffd-8ed2-da7496a335b9', 'logical_name': 'AGENTS::pmagent/modules/gematria/AGENTS.md', 'repo_path': 'pmagent/modules/gematria/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '17f5235d-4708-4542-9b42-ef73991a2df4', 'logical_name': 'CODE::pmagent/modules/gematria/core.py', 'repo_path': 'pmagent/modules/gematria/core.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6068ff25-7a31-4187-abad-83b514c6ae28', 'logical_name': 'CODE::pmagent/modules/gematria/hebrew.py', 'repo_path': 'pmagent/modules/gematria/hebrew.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5c1daa07-3818-44d8-8b89-7dc7463d5838', 'logical_name': 'CODE::pmagent/modules/gematria/nouns.py', 'repo_path': 'pmagent/modules/gematria/nouns.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f22586e0-cb2b-4bb9-bd26-0313dd3116ef', 'logical_name': 'CODE::pmagent/modules/gematria/osis.py', 'repo_path': 'pmagent/modules/gematria/osis.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1a30f034-21d5-46a1-a88b-4b45bbd58bad', 'logical_name': 'CODE::pmagent/modules/gematria/tests/test_core.py', 'repo_path': 'pmagent/modules/gematria/tests/test_core.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bf339f1d-f919-4333-a4ea-7cbdb7916232', 'logical_name': 'CODE::pmagent/modules/gematria/tests/test_hebrew.py', 'repo_path': 'pmagent/modules/gematria/tests/test_hebrew.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '01006b9b-bae9-4b78-96f3-7ce58badb245', 'logical_name': 'CODE::pmagent/modules/gematria/verification.py', 'repo_path': 'pmagent/modules/gematria/verification.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6f5fd773-1f44-4e2b-99b1-bde2c1f937ee', 'logical_name': 'AGENTS::pmagent/obs/AGENTS.md', 'repo_path': 'pmagent/obs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'ba69f4ad-3d11-418f-939a-fc216ca278f9', 'logical_name': 'CODE::pmagent/obs/logger.py', 'repo_path': 'pmagent/obs/logger.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '54f2f225-80b7-45ac-bccb-62c5d90b849d', 'logical_name': 'CODE::pmagent/obs/tv.py', 'repo_path': 'pmagent/obs/tv.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '740d2a3d-9880-488d-a58b-b4a9a0b78c74', 'logical_name': 'AGENTS::pmagent/plan/AGENTS.md', 'repo_path': 'pmagent/plan/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c8bb86ab-1093-4154-a84e-73ee9e51bf24', 'logical_name': 'CODE::pmagent/plan/fix.py', 'repo_path': 'pmagent/plan/fix.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'eb742763-12e3-4dd7-9c89-f0978d10e677', 'logical_name': 'CODE::pmagent/plan/kb.py', 'repo_path': 'pmagent/plan/kb.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '61a5fab0-c448-4292-bfc9-ffdda93f06f0', 'logical_name': 'CODE::pmagent/plan/next.py', 'repo_path': 'pmagent/plan/next.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4b0d8550-615c-44f7-808c-850bee778076', 'logical_name': 'AGENTS::pmagent/reality/AGENTS.md', 'repo_path': 'pmagent/reality/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '04c8ed2d-b7b9-47c7-bd02-372c8f5cf6d1', 'logical_name': 'CODE::pmagent/reality/capability_envelope_validator.py', 'repo_path': 'pmagent/reality/capability_envelope_validator.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'b8931136-fb14-4d13-bf1a-d007daa024ef', 'logical_name': 'CODE::pmagent/reality/capability_envelope_writer.py', 'repo_path': 'pmagent/reality/capability_envelope_writer.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '74f24f9e-9542-445f-b799-87279e872608', 'logical_name': 'CODE::pmagent/reality/check.py', 'repo_path': 'pmagent/reality/check.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '62ac0f09-e367-412f-a391-a0e95f8d7529', 'logical_name': 'CODE::pmagent/reality/sessions_summary.py', 'repo_path': 'pmagent/reality/sessions_summary.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6a787bac-b68b-48f0-95d6-76e8ac05fc85', 'logical_name': 'AGENTS::pmagent/repo/AGENTS.md', 'repo_path': 'pmagent/repo/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c0aeeae0-9c92-44ca-90a3-071b98e211c9', 'logical_name': 'CODE::pmagent/router.py', 'repo_path': 'pmagent/router.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4f6d33a8-13ff-4502-89ab-e9f37d45d0f2', 'logical_name': 'AGENTS::pmagent/rpc/AGENTS.md', 'repo_path': 'pmagent/rpc/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'dcb11866-884c-46d0-95ed-d5409b12ca64', 'logical_name': 'AGENTS::pmagent/runtime/AGENTS.md', 'repo_path': 'pmagent/runtime/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '8d100273-e216-4706-8d7e-bb7c78d87ab1', 'logical_name': 'CODE::pmagent/runtime/lm_budget.py', 'repo_path': 'pmagent/runtime/lm_budget.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '160ee426-b523-442a-9be5-13fa1cfe49b9', 'logical_name': 'CODE::pmagent/runtime/lm_helpers.py', 'repo_path': 'pmagent/runtime/lm_helpers.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '19a52c72-7370-4be6-9d83-0c6c5f0cad27', 'logical_name': 'CODE::pmagent/runtime/lm_logging.py', 'repo_path': 'pmagent/runtime/lm_logging.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '15583619-48a8-46e4-acbc-3dbd35008595', 'logical_name': 'CODE::pmagent/runtime/lm_routing.py', 'repo_path': 'pmagent/runtime/lm_routing.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f26440a1-1ba8-4519-8aa2-527bc7a0905d', 'logical_name': 'AGENTS::pmagent/scripts/AGENTS.md', 'repo_path': 'pmagent/scripts/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2ae9d736-c9ec-45ab-9db1-51301cd1487b', 'logical_name': 'CODE::pmagent/scripts/cleanup_codebase.py', 'repo_path': 'pmagent/scripts/cleanup_codebase.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'fb0be9da-def9-439a-92db-271e82eee285', 'logical_name': 'CODE::pmagent/scripts/cleanup_root.py', 'repo_path': 'pmagent/scripts/cleanup_root.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f42eef4d-f3fc-43cc-9ce2-f163d7b90a72', 'logical_name': 'CODE::pmagent/scripts/docs_archive_apply.py', 'repo_path': 'pmagent/scripts/docs_archive_apply.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '06e92242-28ef-48ea-911b-84a3a5ae1007', 'logical_name': 'CODE::pmagent/scripts/docs_archive_dryrun.py', 'repo_path': 'pmagent/scripts/docs_archive_dryrun.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'a4cf7584-30f1-4d07-af97-7077217f022c', 'logical_name': 'CODE::pmagent/scripts/docs_classify_direct.py', 'repo_path': 'pmagent/scripts/docs_classify_direct.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'eb794630-cda2-4f22-954a-a6e3cd783a27', 'logical_name': 'CODE::pmagent/scripts/docs_dashboard_refresh.py', 'repo_path': 'pmagent/scripts/docs_dashboard_refresh.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '11294a51-44e4-48ff-a1a8-ffe016bf9507', 'logical_name': 'CODE::pmagent/scripts/docs_dm002_preview.py', 'repo_path': 'pmagent/scripts/docs_dm002_preview.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'c963a883-9ce8-4ce3-8aae-57c291134593', 'logical_name': 'CODE::pmagent/scripts/docs_dm002_summary.py', 'repo_path': 'pmagent/scripts/docs_dm002_summary.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '98c46677-d805-4395-b564-db91f62e9074', 'logical_name': 'CODE::pmagent/scripts/docs_dm002_sync.py', 'repo_path': 'pmagent/scripts/docs_dm002_sync.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ced03fed-bfb7-46de-b780-f7c5ac23938d', 'logical_name': 'CODE::pmagent/scripts/docs_duplicates_report.py', 'repo_path': 'pmagent/scripts/docs_duplicates_report.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1956d0d8-528d-4994-b9cd-4a71cd6104db', 'logical_name': 'CODE::pmagent/scripts/docs_inventory.py', 'repo_path': 'pmagent/scripts/docs_inventory.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '9fab65b3-5cc8-4eed-b206-e17a45e23163', 'logical_name': 'CODE::pmagent/scripts/generate_tool_embeddings.py', 'repo_path': 'pmagent/scripts/generate_tool_embeddings.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '96061743-cd10-4d3a-bf7d-43c3a786f935', 'logical_name': 'CODE::pmagent/scripts/ingest_docs.py', 'repo_path': 'pmagent/scripts/ingest_docs.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '06d11bb6-bbb2-4fb3-a381-4470b8023f7e', 'logical_name': 'CODE::pmagent/scripts/reality_check_1_live.py', 'repo_path': 'pmagent/scripts/reality_check_1_live.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '71fade70-0332-4bdd-848c-777dc47a60b9', 'logical_name': 'CODE::pmagent/scripts/reality_check_1.py', 'repo_path': 'pmagent/scripts/reality_check_1.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6886d9ca-6791-4e99-b36a-8df6fb243eed', 'logical_name': 'AGENTS::pmagent/scripts/state/AGENTS.md', 'repo_path': 'pmagent/scripts/state/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'b3d088ab-a424-4191-a272-beadf7306661', 'logical_name': 'CODE::pmagent/scripts/state/ledger_sync.py', 'repo_path': 'pmagent/scripts/state/ledger_sync.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '7b8271ba-73b2-4d14-a680-9a7a44c06837', 'logical_name': 'CODE::pmagent/scripts/state/ledger_verify.py', 'repo_path': 'pmagent/scripts/state/ledger_verify.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd7fe4038-1cad-4235-98a8-a3b83d225f00', 'logical_name': 'CODE::pmagent/scripts/system_bringup.py', 'repo_path': 'pmagent/scripts/system_bringup.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd9adcf1d-3bf0-46aa-9250-fb8696d38368', 'logical_name': 'AGENTS::pmagent/server/AGENTS.md', 'repo_path': 'pmagent/server/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'ab3c2e04-5034-4f00-a0f1-b32506b5b421', 'logical_name': 'CODE::pmagent/server/autopilot_api.py', 'repo_path': 'pmagent/server/autopilot_api.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'effa051e-c9e5-4a88-9e1b-24371d9fc4a4', 'logical_name': 'AGENTS::pmagent/status/AGENTS.md', 'repo_path': 'pmagent/status/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'cb8f0b3c-3348-4753-b65f-d76d7493b0bf', 'logical_name': 'CODE::pmagent/status/eval_exports.py', 'repo_path': 'pmagent/status/eval_exports.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '092cfb4f-a0b0-435b-9c6f-e7332dabbc64', 'logical_name': 'CODE::pmagent/status/explain.py', 'repo_path': 'pmagent/status/explain.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '853bee6c-7096-4dcf-9b6f-2a1b48a20738', 'logical_name': 'CODE::pmagent/status/kb_metrics.py', 'repo_path': 'pmagent/status/kb_metrics.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6a23a4c7-542d-4c98-a3a3-6a36d643f415', 'logical_name': 'CODE::pmagent/status/snapshot.py', 'repo_path': 'pmagent/status/snapshot.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'dffc5727-4f3f-455f-9d24-20667386b255', 'logical_name': 'CODE::pmagent/status/system.py', 'repo_path': 'pmagent/status/system.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4f877d60-3f8a-4b4c-ad23-9ff93ab3b24f', 'logical_name': 'AGENTS::pmagent/tests/adapters/AGENTS.md', 'repo_path': 'pmagent/tests/adapters/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'df830aea-a4eb-4605-9efa-b9b6a527b843', 'logical_name': 'CODE::pmagent/tests/adapters/test_lm_studio_adapter.py', 'repo_path': 'pmagent/tests/adapters/test_lm_studio_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'fd7f5eb6-d348-430b-8a3a-2ead72ceeea0', 'logical_name': 'AGENTS::pmagent/tests/AGENTS.md', 'repo_path': 'pmagent/tests/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'addd4b5e-4a93-4676-851e-ba6389a2203a', 'logical_name': 'AGENTS::pmagent/tests/atlas/AGENTS.md', 'repo_path': 'pmagent/tests/atlas/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '0e1f563b-0555-4899-8620-a75f89ed3b57', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_accessibility_e38_e40.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_accessibility_e38_e40.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '2abe32ec-27a8-4f6c-9677-c39735a2e101', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_auditjump_e29_e31.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_auditjump_e29_e31.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5d1b25e3-7e85-44bb-a9b2-7d4176eeb6cd', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_download_backlinks_e32_e34.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_download_backlinks_e32_e34.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ffd3914a-4e2f-4db2-8718-57dd9f05689b', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_filters_breadcrumbs_sitemap_e44_e46.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_filters_breadcrumbs_sitemap_e44_e46.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '61bb0ae2-072c-424d-af12-204ba28cd29a', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_filters_contrast_sitemap_e47_e49.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_filters_contrast_sitemap_e47_e49.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5a739667-8837-48ac-a7ed-a068d03bf7c1', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_links_e26_e28.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_links_e26_e28.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e59ef3f4-caaa-4f2a-b395-c619978ad939', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_rawproof_e35_e37.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_rawproof_e35_e37.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f8aaa279-451f-46cb-8bb2-645724e8f7c1', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_search_microdata_guard_e50_e52.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_search_microdata_guard_e50_e52.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd20bf5a6-6a0d-4b47-a380-05d1cd979c55', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_search_title_aria_e41_e43.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_search_title_aria_e41_e43.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '74886d2a-953c-446c-9688-07cd1d1108c0', 'logical_name': 'CODE::pmagent/tests/atlas/test_atlas_smoke_e23_e25.py', 'repo_path': 'pmagent/tests/atlas/test_atlas_smoke_e23_e25.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '016e502d-86db-4cca-892c-8de6ad9a23d5', 'logical_name': 'CODE::pmagent/tests/atlas/test_e100_tagproof_phase2.py', 'repo_path': 'pmagent/tests/atlas/test_e100_tagproof_phase2.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ee304ee1-b31e-45b7-818f-3d5d2d65780e', 'logical_name': 'CODE::pmagent/tests/atlas/test_e86_compliance_summary.py', 'repo_path': 'pmagent/tests/atlas/test_e86_compliance_summary.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'dca94b5a-445f-4e02-a3de-c6a44ade686f', 'logical_name': 'CODE::pmagent/tests/atlas/test_e87_compliance_timeseries.py', 'repo_path': 'pmagent/tests/atlas/test_e87_compliance_timeseries.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '74afacb0-056f-45a3-b068-8756593db85a', 'logical_name': 'CODE::pmagent/tests/atlas/test_e91_guard_receipts_index.py', 'repo_path': 'pmagent/tests/atlas/test_e91_guard_receipts_index.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6551f72c-9d32-4b69-bd1b-55ef19bc92ce', 'logical_name': 'CODE::pmagent/tests/atlas/test_e92_screenshot_manifest_guard.py', 'repo_path': 'pmagent/tests/atlas/test_e92_screenshot_manifest_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e753b5b1-5174-4756-8eb3-bef78c64b223', 'logical_name': 'CODE::pmagent/tests/atlas/test_e93_browser_verification_guard.py', 'repo_path': 'pmagent/tests/atlas/test_e93_browser_verification_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '2742dc50-0ff8-4c75-ac56-01fdd38dce12', 'logical_name': 'CODE::pmagent/tests/atlas/test_e94_tagproof_screenshots_guard.py', 'repo_path': 'pmagent/tests/atlas/test_e94_tagproof_screenshots_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'c20317ec-84e4-4701-8521-762d65c4d018', 'logical_name': 'CODE::pmagent/tests/atlas/test_e95_atlas_links_guard.py', 'repo_path': 'pmagent/tests/atlas/test_e95_atlas_links_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '294b460a-412d-4250-837f-8861be6b8d74', 'logical_name': 'CODE::pmagent/tests/atlas/test_e96_tv_coverage_guard.py', 'repo_path': 'pmagent/tests/atlas/test_e96_tv_coverage_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ffb21c92-22cb-4827-b498-8bfd815a4307', 'logical_name': 'CODE::pmagent/tests/atlas/test_e97_gatekeeper_coverage_guard.py', 'repo_path': 'pmagent/tests/atlas/test_e97_gatekeeper_coverage_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5080393e-1c1e-4d64-bc64-f1910eff6a4a', 'logical_name': 'CODE::pmagent/tests/atlas/test_e98_regenerate_all_guard.py', 'repo_path': 'pmagent/tests/atlas/test_e98_regenerate_all_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '7f8d9323-3262-4aba-8a93-078246d2c145', 'logical_name': 'CODE::pmagent/tests/atlas/test_e99_browser_screenshot_integrated.py', 'repo_path': 'pmagent/tests/atlas/test_e99_browser_screenshot_integrated.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '8217cdcd-7afc-4b44-ae8d-649ff7be2d85', 'logical_name': 'CODE::pmagent/tests/atlas/test_lm_dashboards_config.py', 'repo_path': 'pmagent/tests/atlas/test_lm_dashboards_config.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1136f6e7-fa24-4ead-b99a-33a1e6199762', 'logical_name': 'CODE::pmagent/tests/atlas/test_lm_indicator_export.py', 'repo_path': 'pmagent/tests/atlas/test_lm_indicator_export.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'a58c9eca-7f46-4d1b-80c9-d02cfb4c9f0d', 'logical_name': 'CODE::pmagent/tests/atlas/test_lm_insights_exports.py', 'repo_path': 'pmagent/tests/atlas/test_lm_insights_exports.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'b93d965a-85e1-4c20-9b6e-9e043b06e9d8', 'logical_name': 'CODE::pmagent/tests/atlas/test_lm_metrics_exports.py', 'repo_path': 'pmagent/tests/atlas/test_lm_metrics_exports.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '75486e0c-989d-4673-9f0b-edea46d96510', 'logical_name': 'CODE::pmagent/tests/atlas/test_lm_status_page_insights.py', 'repo_path': 'pmagent/tests/atlas/test_lm_status_page_insights.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '7ed4ab14-9eab-40bb-b019-14ed62d01780', 'logical_name': 'CODE::pmagent/tests/atlas/test_phase6p_biblescholar_reference_guard.py', 'repo_path': 'pmagent/tests/atlas/test_phase6p_biblescholar_reference_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bcd5203a-e737-47ef-9d3d-2a9b54f62a07', 'logical_name': 'CODE::pmagent/tests/atlas/test_phase_d_autopilot_summary.py', 'repo_path': 'pmagent/tests/atlas/test_phase_d_autopilot_summary.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '570286c2-8c61-40db-8524-2fcb0be2d7e6', 'logical_name': 'AGENTS::pmagent/tests/cli/AGENTS.md', 'repo_path': 'pmagent/tests/cli/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e12edf2e-8741-41ed-a48a-858a02406aa3', 'logical_name': 'CODE::pmagent/tests/cli/test_phase3b_pmagent_control_pipeline_status_cli.py', 'repo_path': 'pmagent/tests/cli/test_phase3b_pmagent_control_pipeline_status_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'b3a9bf8f-cb69-4e51-9798-ae79a9b58135', 'logical_name': 'CODE::pmagent/tests/cli/test_phase3b_pmagent_control_schema_cli.py', 'repo_path': 'pmagent/tests/cli/test_phase3b_pmagent_control_schema_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1f251686-301a-49a8-9df6-e27d89f07d72', 'logical_name': 'CODE::pmagent/tests/cli/test_phase3b_pmagent_control_status_cli.py', 'repo_path': 'pmagent/tests/cli/test_phase3b_pmagent_control_status_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '39586345-bccb-422e-bd16-bd38997547b6', 'logical_name': 'CODE::pmagent/tests/cli/test_phase3b_pmagent_control_summary_cli.py', 'repo_path': 'pmagent/tests/cli/test_phase3b_pmagent_control_summary_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bdafef41-c6dc-45d7-98b1-08932c1f9941', 'logical_name': 'CODE::pmagent/tests/cli/test_phase3b_pmagent_control_tables_cli.py', 'repo_path': 'pmagent/tests/cli/test_phase3b_pmagent_control_tables_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '86ed33ba-1a13-40bb-8aa2-31042855813b', 'logical_name': 'CODE::pmagent/tests/cli/test_phase3b_pmagent_graph_cli.py', 'repo_path': 'pmagent/tests/cli/test_phase3b_pmagent_graph_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f73bf28d-ef9d-4aa6-be53-6cc8fc816f99', 'logical_name': 'CODE::pmagent/tests/cli/test_phase3b_pmagent_health_cli.py', 'repo_path': 'pmagent/tests/cli/test_phase3b_pmagent_health_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '9c1052ca-aa3a-46fc-88f2-bd19fdad3ad4', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_health_lm.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_health_lm.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '9b047f2d-0b7e-4802-90e5-2fe15fcab4af', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_lm_router_status.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_lm_router_status.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e65c471a-2683-4389-8122-89cfb1853b62', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_plan_kb_fix.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_plan_kb_fix.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '19e626fd-d361-4fe1-9bf2-3142496db464', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_plan_kb.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_plan_kb.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bc081dbb-519b-4306-943e-5ae37fc18451', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_plan_next.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_plan_next.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd3bbc862-4d62-4cf7-857c-72c10ca54eba', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_reality_check_cli.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_reality_check_cli.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'da7c4117-0ff9-4b1e-9bfe-010c2134e11b', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_report_kb.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_report_kb.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e5abd3ed-a3d0-438e-859b-1a2cb8452f98', 'logical_name': 'CODE::pmagent/tests/cli/test_pmagent_status_kb.py', 'repo_path': 'pmagent/tests/cli/test_pmagent_status_kb.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'cc8b0b2d-f670-44cf-a792-99cb7fafa1a6', 'logical_name': 'CODE::pmagent/tests/control_widgets/test_adapter.py', 'repo_path': 'pmagent/tests/control_widgets/test_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6c5f46a4-8c66-4f14-afdd-43e6c31f0f62', 'logical_name': 'CODE::pmagent/tests/control_widgets/test_m2_visualization.py', 'repo_path': 'pmagent/tests/control_widgets/test_m2_visualization.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '8df67f8f-bfc3-4864-969a-73be4ca9c7ff', 'logical_name': 'AGENTS::pmagent/tests/db/AGENTS.md', 'repo_path': 'pmagent/tests/db/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '199e2379-0f09-4b63-9308-d05b1e91c65e', 'logical_name': 'CODE::pmagent/tests/db/test_phase3a_db_health_guard.py', 'repo_path': 'pmagent/tests/db/test_phase3a_db_health_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '894ede54-1f3e-465a-9b91-f4024e679338', 'logical_name': 'CODE::pmagent/tests/db/test_phase3a_db_health_smoke.py', 'repo_path': 'pmagent/tests/db/test_phase3a_db_health_smoke.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'fd897295-80ec-476f-b024-04130a3b82a7', 'logical_name': 'CODE::pmagent/tests/db/test_phase3a_db_health_snapshot.py', 'repo_path': 'pmagent/tests/db/test_phase3a_db_health_snapshot.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd8081b97-b424-4661-be48-fb7e98ce992b', 'logical_name': 'CODE::pmagent/tests/db/test_phase3a_db_loader.py', 'repo_path': 'pmagent/tests/db/test_phase3a_db_loader.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'b8c9da8d-9b33-4fd6-989f-e8b3f62b0ee5', 'logical_name': 'CODE::pmagent/tests/db/test_phase3a_graph_stats_import.py', 'repo_path': 'pmagent/tests/db/test_phase3a_graph_stats_import.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f1239197-0d5f-4a90-9ee0-7089437b0af5', 'logical_name': 'CODE::pmagent/tests/db/test_phase3b_graph_overview.py', 'repo_path': 'pmagent/tests/db/test_phase3b_graph_overview.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bb00f9ed-5e23-4b61-9663-cb7f21d0bfae', 'logical_name': 'AGENTS::pmagent/tests/docs/AGENTS.md', 'repo_path': 'pmagent/tests/docs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'bf61fab4-71c5-4a5f-829c-fcefee7740d4', 'logical_name': 'CODE::pmagent/tests/docs/test_dms_guards.py', 'repo_path': 'pmagent/tests/docs/test_dms_guards.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '11464c42-b2ab-4068-9899-6caa612a8187', 'logical_name': 'AGENTS::pmagent/tests/exports/AGENTS.md', 'repo_path': 'pmagent/tests/exports/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'c5d66b08-e32a-4637-b1d4-c4a7521e21f7', 'logical_name': 'CODE::pmagent/tests/exports/test_graph_export_e20_e22.py', 'repo_path': 'pmagent/tests/exports/test_graph_export_e20_e22.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '60035fcf-546b-4c4c-a64f-51cf6fbc8c84', 'logical_name': 'AGENTS::pmagent/tests/extractors/AGENTS.md', 'repo_path': 'pmagent/tests/extractors/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '19cb6f26-978d-4661-92f9-6de705f271bc', 'logical_name': 'CODE::pmagent/tests/extractors/test_extraction_correctness.py', 'repo_path': 'pmagent/tests/extractors/test_extraction_correctness.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4599b21d-32d5-4f38-8ab3-a97ab1065874', 'logical_name': 'CODE::pmagent/tests/extractors/test_extraction_determinism_e11_e13.py', 'repo_path': 'pmagent/tests/extractors/test_extraction_determinism_e11_e13.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd35ee6da-fae3-4cb4-9c50-90da48d90d71', 'logical_name': 'CODE::pmagent/tests/extractors/test_extraction_graph_propagation_e14_e16.py', 'repo_path': 'pmagent/tests/extractors/test_extraction_graph_propagation_e14_e16.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4577c13e-fa55-4c49-9f1f-4741a72bbe0b', 'logical_name': 'CODE::pmagent/tests/extractors/test_extraction_provenance_e06_e10.py', 'repo_path': 'pmagent/tests/extractors/test_extraction_provenance_e06_e10.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'd8b01b35-71be-49c4-8341-0aa6131beb65', 'logical_name': 'CODE::pmagent/tests/extractors/test_graph_rollups_e17_e19.py', 'repo_path': 'pmagent/tests/extractors/test_graph_rollups_e17_e19.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '373be5e3-2c49-41b3-b441-23df45d386b1', 'logical_name': 'CODE::pmagent/tests/guarded/test_autopilot_adapter.py', 'repo_path': 'pmagent/tests/guarded/test_autopilot_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'be19ca81-85f9-4c69-acc4-369f2a9bab15', 'logical_name': 'AGENTS::pmagent/tests/html/AGENTS.md', 'repo_path': 'pmagent/tests/html/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd5bd878f-07e7-4f93-aef0-7f3540940bae', 'logical_name': 'CODE::pmagent/tests/html/test_lm_status_page.py', 'repo_path': 'pmagent/tests/html/test_lm_status_page.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '7fe51124-f3b9-48f5-843c-02b782479e74', 'logical_name': 'AGENTS::pmagent/tests/kb/AGENTS.md', 'repo_path': 'pmagent/tests/kb/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '17ea98f5-ed2a-4e38-b745-6b7c5c97bf22', 'logical_name': 'CODE::pmagent/tests/kb/test_freshness.py', 'repo_path': 'pmagent/tests/kb/test_freshness.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '0d3ef121-2801-4f38-9a04-019a1e22ed5b', 'logical_name': 'CODE::pmagent/tests/kb/test_registry.py', 'repo_path': 'pmagent/tests/kb/test_registry.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e82a7489-f524-417f-b715-fce51058e78d', 'logical_name': 'AGENTS::pmagent/tests/knowledge/AGENTS.md', 'repo_path': 'pmagent/tests/knowledge/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'df884972-298a-4485-9b7d-4105137e2686', 'logical_name': 'CODE::pmagent/tests/knowledge/test_kb_ingest_and_export.py', 'repo_path': 'pmagent/tests/knowledge/test_kb_ingest_and_export.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bf4f1e85-260b-4698-87ec-e781cc03e0a0', 'logical_name': 'CODE::pmagent/tests/knowledge/test_qa_docs.py', 'repo_path': 'pmagent/tests/knowledge/test_qa_docs.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '2d96a8ed-e6d7-4d2d-b3a4-975bdca9e517', 'logical_name': 'AGENTS::pmagent/tests/lm/AGENTS.md', 'repo_path': 'pmagent/tests/lm/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'b69186bc-2c05-48ea-8a6c-71882483120e', 'logical_name': 'CODE::pmagent/tests/lm/test_phase3b_lm_health_guard.py', 'repo_path': 'pmagent/tests/lm/test_phase3b_lm_health_guard.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '3f240ed8-c791-4633-baad-33ff30b6b4a4', 'logical_name': 'CODE::pmagent/tests/lm/test_phase6_lm_budgets.py', 'repo_path': 'pmagent/tests/lm/test_phase6_lm_budgets.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '994d23f7-895a-4e6b-a106-67831311b413', 'logical_name': 'CODE::pmagent/tests/lm/test_phase6_lm_enablement.py', 'repo_path': 'pmagent/tests/lm/test_phase6_lm_enablement.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '92fc5b13-fdec-49e5-8981-9dbae60741dc', 'logical_name': 'CODE::pmagent/tests/lm_widgets/test_adapter.py', 'repo_path': 'pmagent/tests/lm_widgets/test_adapter.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '0671028e-63da-4be0-8fa1-e555c9c0346f', 'logical_name': 'AGENTS::pmagent/tests/mcp/AGENTS.md', 'repo_path': 'pmagent/tests/mcp/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2c2e23d6-e9b2-4985-ae03-e104003a6a39', 'logical_name': 'CODE::pmagent/tests/mcp/test_m2_e21_e25.py', 'repo_path': 'pmagent/tests/mcp/test_m2_e21_e25.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'add1cd13-3d63-43e8-92ab-c9effcc14190', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_catalog_e01_e05.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_catalog_e01_e05.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e8bfc92a-86c8-44cf-b4a1-2574f346d45d', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m10_e46_e50.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m10_e46_e50.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '88aa7365-dbf2-48e9-a2d4-0aec33020d4a', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m11_e51_e55.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m11_e51_e55.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '92b04e9a-1eb8-429c-958c-42fa7d5fed98', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m12_e56_e60.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m12_e56_e60.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '192f0cd6-7347-440b-b028-76dfc5e67400', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m13_e61_e65.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m13_e61_e65.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f07c9c59-1a1e-4be8-8548-f049c5ca2ec3', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m14_e66_e70.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m14_e66_e70.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e753e73a-b558-4ac4-b8fa-fe5d0a23f5f8', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m2_e06_e10.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m2_e06_e10.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'adec3a71-7e03-497b-8cc2-451452aea36d', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m3_e11_e15.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m3_e11_e15.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '2246ee3e-5a64-4b2c-8efa-789a384d69ca', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m4_e16_e20.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m4_e16_e20.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '07f39314-d38e-4a14-ac3c-bcde5958d562', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m5_e21_e25.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m5_e21_e25.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6797dcea-ac9a-4282-8a70-92b2151722d6', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m6_e26_e30.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m6_e26_e30.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'fecde590-2190-491e-bf0a-c7d339e4d315', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m7_e31_e35.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m7_e31_e35.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '0e7766fc-41af-4cf9-83c7-bda9d639a2b8', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m8_e36_e40.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m8_e36_e40.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '8d823dc2-1b1b-494c-991a-f1f84759bf80', 'logical_name': 'CODE::pmagent/tests/mcp/test_mcp_m9_e41_e45.py', 'repo_path': 'pmagent/tests/mcp/test_mcp_m9_e41_e45.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '8722696e-45eb-4f5a-a412-30506f9779f6', 'logical_name': 'AGENTS::pmagent/tests/phase1/AGENTS.md', 'repo_path': 'pmagent/tests/phase1/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'd310e8de-ab8b-418d-8a54-1d2c7658c61c', 'logical_name': 'CODE::pmagent/tests/phase1/test_tv01_missing_por.py', 'repo_path': 'pmagent/tests/phase1/test_tv01_missing_por.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '59641702-f8ae-4e14-b0b2-118c669a5466', 'logical_name': 'CODE::pmagent/tests/phase1/test_tv02_arg_schema_invalid.py', 'repo_path': 'pmagent/tests/phase1/test_tv02_arg_schema_invalid.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6e4d3b4e-4ce8-4237-9d07-ea654608751e', 'logical_name': 'CODE::pmagent/tests/phase1/test_tv03_ring_violation.py', 'repo_path': 'pmagent/tests/phase1/test_tv03_ring_violation.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'cb375a4b-b662-4673-98d8-238558e9dad6', 'logical_name': 'CODE::pmagent/tests/phase1/test_tv04_provenance_mismatch.py', 'repo_path': 'pmagent/tests/phase1/test_tv04_provenance_mismatch.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '8dad25e4-83ea-49c7-aeba-e64cd0945eb6', 'logical_name': 'CODE::pmagent/tests/phase1/test_tv05_forbidden_tool.py', 'repo_path': 'pmagent/tests/phase1/test_tv05_forbidden_tool.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '2a48e10b-7518-4acf-83b9-85152895e068', 'logical_name': 'CODE::pmagent/tests/pipelines/test_enrich_nouns_lm_routing.py', 'repo_path': 'pmagent/tests/pipelines/test_enrich_nouns_lm_routing.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'b62ade26-d4f5-4dc6-80c4-4002fc2b7c37', 'logical_name': 'AGENTS::pmagent/tests/reality/AGENTS.md', 'repo_path': 'pmagent/tests/reality/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e3b74da4-7b86-40ba-aeec-753021d074c9', 'logical_name': 'CODE::pmagent/tests/reality/test_capability_envelope_validator.py', 'repo_path': 'pmagent/tests/reality/test_capability_envelope_validator.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '9b468a1d-e7dd-44b5-ba54-d1a00e3b7d0d', 'logical_name': 'CODE::pmagent/tests/reality/test_capability_envelope_writer.py', 'repo_path': 'pmagent/tests/reality/test_capability_envelope_writer.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '66dd087d-759b-40ac-95e2-eac02c2912ee', 'logical_name': 'CODE::pmagent/tests/reality/test_reality_check.py', 'repo_path': 'pmagent/tests/reality/test_reality_check.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1eed4df5-9526-480d-a942-5e9fc691e4e6', 'logical_name': 'CODE::pmagent/tests/reality/test_sessions_summary.py', 'repo_path': 'pmagent/tests/reality/test_sessions_summary.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'f3371f14-26ba-4fb3-85a0-7702ba9da6bb', 'logical_name': 'CODE::pmagent/tests/runtime/test_lm_logging.py', 'repo_path': 'pmagent/tests/runtime/test_lm_logging.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4dfa6df5-73d1-4a52-a4f1-862b049fab95', 'logical_name': 'CODE::pmagent/tests/runtime/test_lm_routing.py', 'repo_path': 'pmagent/tests/runtime/test_lm_routing.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4a3611d1-8690-4b0c-8180-0c9317cebe50', 'logical_name': 'CODE::pmagent/tests/runtime/test_pm_snapshot.py', 'repo_path': 'pmagent/tests/runtime/test_pm_snapshot.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e52751c1-0ed9-449a-84d6-f84c1935a03b', 'logical_name': 'CODE::pmagent/tests/server/test_autopilot_api.py', 'repo_path': 'pmagent/tests/server/test_autopilot_api.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '6d2f7670-5bb9-4d23-9daa-c27d52b39860', 'logical_name': 'AGENTS::pmagent/tests/status/AGENTS.md', 'repo_path': 'pmagent/tests/status/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'b8a46e06-fcdc-417c-a747-a52a99f3f8ea', 'logical_name': 'CODE::pmagent/tests/status/test_eval_exports.py', 'repo_path': 'pmagent/tests/status/test_eval_exports.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'fdb343fc-89ca-4366-b9ef-9de0092fd090', 'logical_name': 'CODE::pmagent/tests/status/test_explain_kb.py', 'repo_path': 'pmagent/tests/status/test_explain_kb.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'bf3262a2-f505-433a-9325-d20256d3454e', 'logical_name': 'CODE::pmagent/tests/status/test_kb_hints.py', 'repo_path': 'pmagent/tests/status/test_kb_hints.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '1958d2d8-dceb-422e-9e4c-a9b6b61279e4', 'logical_name': 'AGENTS::pmagent/tests/system/AGENTS.md', 'repo_path': 'pmagent/tests/system/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '9b943c9f-a750-40ca-9511-aaea0598d24c', 'logical_name': 'CODE::pmagent/tests/system/test_phase3b_system_health.py', 'repo_path': 'pmagent/tests/system/test_phase3b_system_health.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '158b4cfb-ff4e-4e24-8a09-47a3ebe967ad', 'logical_name': 'CODE::pmagent/tests/test_guarded_calls_tv.py', 'repo_path': 'pmagent/tests/test_guarded_calls_tv.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '3333912f-ede9-492d-abe0-5969a6c29054', 'logical_name': 'CODE::pmagent/tests/tools/test_system_reality_check.py', 'repo_path': 'pmagent/tests/tools/test_system_reality_check.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '5120950e-f48b-4548-9b12-329c7e24f4dd', 'logical_name': 'AGENTS::pmagent/tools/AGENTS.md', 'repo_path': 'pmagent/tools/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '1711c515-d33a-40eb-b4c1-e856546da127', 'logical_name': 'CODE::pmagent/tools/bible.py', 'repo_path': 'pmagent/tools/bible.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'e95e89b2-a248-4192-88c3-463f4db91345', 'logical_name': 'CODE::pmagent/tools/embed.py', 'repo_path': 'pmagent/tools/embed.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': 'ac5c061e-01e4-457b-b51f-33be1ba597ef', 'logical_name': 'CODE::pmagent/tools/extract.py', 'repo_path': 'pmagent/tools/extract.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '76a5edc0-853d-4b36-914b-831a99319ddb', 'logical_name': 'CODE::pmagent/tools/rerank.py', 'repo_path': 'pmagent/tools/rerank.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '3bcad3bb-098d-44fd-93c8-30977d2a73a4', 'logical_name': 'CODE::pmagent/tools/system.py', 'repo_path': 'pmagent/tools/system.py', 'exists_on_disk': True, 'enabled': True, 'importance': 'unknown'}, {'doc_id': '4ab32f63-1439-40d6-b861-75ebe8793e59', 'logical_name': 'AGENTS::src/AGENTS.md', 'repo_path': 'src/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e6e7219e-87e7-4a43-84ba-d4f87564ed4f', 'logical_name': 'AGENTS::src/core/AGENTS.md', 'repo_path': 'src/core/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'b0c63e61-7e4c-4d5d-88c6-095872c22800', 'logical_name': 'AGENTS::src/gemantria/AGENTS.md', 'repo_path': 'src/gemantria/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'edb801e4-1239-48ac-9d45-84ec6bd9533f', 'logical_name': 'AGENTS::src/gemantria.egg-info/AGENTS.md', 'repo_path': 'src/gemantria.egg-info/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '6e867837-06d3-4f13-a43f-3a1f188fafbf', 'logical_name': 'AGENTS::src/graph/AGENTS.md', 'repo_path': 'src/graph/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '7eba8da3-03eb-476b-8257-c1e77265db1b', 'logical_name': 'AGENTS::src/infra/AGENTS.md', 'repo_path': 'src/infra/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '1a02af4f-baca-49a4-a99a-1a73f409785e', 'logical_name': 'AGENTS::src/nodes/AGENTS.md', 'repo_path': 'src/nodes/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3f6f4164-317a-43e1-af00-2e7b317fb507', 'logical_name': 'AGENTS::src/obs/AGENTS.md', 'repo_path': 'src/obs/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '0308bc23-31c0-455f-883e-190b4a7d94b1', 'logical_name': 'AGENTS::src/persist/AGENTS.md', 'repo_path': 'src/persist/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '540f24cc-57ab-4ca9-a32a-40ff4017b27d', 'logical_name': 'AGENTS::src/rerank/AGENTS.md', 'repo_path': 'src/rerank/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '33de7421-1b5d-4ab2-b580-4caadd338f0a', 'logical_name': 'AGENTS::src/services/AGENTS.md', 'repo_path': 'src/services/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '22b621eb-3572-4032-a2a6-d0939ba0f42f', 'logical_name': 'AGENTS::src/ssot/AGENTS.md', 'repo_path': 'src/ssot/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2aca15ff-72d5-49f1-8a32-70ccc510911b', 'logical_name': 'AGENTS::src/utils/AGENTS.md', 'repo_path': 'src/utils/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'ae9d1ede-fac5-41af-af3f-895b7dfe6fc4', 'logical_name': 'AGENTS::tests/AGENTS.md', 'repo_path': 'tests/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2886602d-904b-490d-ab8c-dc180b7b8f83', 'logical_name': 'AGENTS::tools/AGENTS.md', 'repo_path': 'tools/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '3ddcbc40-2241-4b87-9f57-43cdd0d7dbf5', 'logical_name': 'AGENTS::webui/dashboard/AGENTS.md', 'repo_path': 'webui/dashboard/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'f31e3267-f8cb-4ffb-a350-f6f3e7187177', 'logical_name': 'AGENTS::webui/graph/AGENTS.md', 'repo_path': 'webui/graph/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e1f37b2c-d9a5-43da-ab45-101566d9eddc', 'logical_name': 'AGENTS::webui/orchestrator-console-v2/AGENTS.md', 'repo_path': 'webui/orchestrator-console-v2/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': '2128907a-b911-4477-940e-c68a47682ee3', 'logical_name': 'AGENTS::webui/orchestrator-shell/AGENTS.md', 'repo_path': 'webui/orchestrator-shell/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}, {'doc_id': 'e801cb1e-6f75-4e8a-a61a-a397e7e9a636', 'logical_name': 'AGENTS::webui/public/AGENTS.md', 'repo_path': 'webui/public/AGENTS.md', 'exists_on_disk': True, 'enabled': True, 'importance': 'high'}] entries
docs/runbooks/LM_HEALTH.md:156:make pm.snapshot
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:95:* `share/pm_snapshot.json` - PM system snapshot
docs/SSOT/MASTER_PLAN.md:80:- **M3** ✅ PASS: Doc-health control loop & reporting — `pmagent report kb` aggregates M1 worklists and M2 fix manifests into doc-health metrics and trends. `pm.snapshot` now includes an advisory "Documentation Health" section with fresh ratios, missing/stale counts, and fix activity. Artifacts: `pmagent/status/kb_metrics.py`, `pmagent/cli.py` (report_kb), `pmagent/tests/cli/test_pmagent_report_kb.py`. Targets: `pmagent report kb`. (PR #582)
docs/SSOT/MASTER_PLAN.md:170:- ✅ E103: Catalog integration into pm.snapshot + end-to-end TVs + tagproof evidence (read-only catalog access, TVs 06–07, bundle generation).
docs/SSOT/MASTER_PLAN.md:507:- **7C** ✅ PASS: Snapshot Integrity & Drift Review — Validated all snapshot/export artifacts (control-plane schema/MVs, ledger, pm snapshot, Atlas compliance artifacts, browser receipts) are consistent, drift-free, and covered by guards. Created `scripts/guards/guard_snapshot_drift.py` to validate snapshot file existence, structure, and ledger sync status. All snapshots refreshed: `share/atlas/control_plane/{schema_snapshot.json,mv_schema.json,mcp_catalog.json,compliance_summary.json,compliance_timeseries.json}`, `share/pm.snapshot.md`. Ledger verification shows all 9 tracked artifacts current. Guard outputs: `guard_control_plane_health` (STRICT), `guard_atlas_compliance_timeseries`, `guard_browser_verification`, `guard_snapshot_drift` all PASS. Evidence: `evidence/guard_snapshot_drift.json`.
docs/SSOT/SHARE_FOLDER_STRUCTURE.md:34:* `pm_snapshot.md` - System health snapshot
docs/SSOT/SHARE_FOLDER_STRUCTURE.md:90:* `share/pm_snapshot.md` - Complete system snapshot (converted from JSON)
pmagent/tests/runtime/test_pm_snapshot.py:2:Tests for pm.snapshot integration (AgentPM-First:M3).
pmagent/tests/runtime/test_pm_snapshot.py:4:Verifies that pm.snapshot composes health, status explain, reality-check,
pmagent/tests/runtime/test_pm_snapshot.py:8:executing the full pm_snapshot.py script (which runs at module import time).
pmagent/tests/runtime/test_pm_snapshot.py:21:    """Test pm.snapshot integration with pmagent commands."""

```

### planning_context_refs

```
scripts/util/export_pm_introspection_evidence.py:149:        ("planning_context", "planning_context_refs"),
scripts/pm/generate_pm_boot_surface.py:30:        (SHARE / "planning_context.json", PM_BOOT / "planning_context.json"),
scripts/guards/guard_pm_boot_surface.py:33:    "planning_context.json",
scripts/guards/guard_share_sync_policy.py:70:    "share/planning_context.json",  # planning pipeline output for agents (not a managed doc)
scripts/guards/guard_share_sync_policy.py:91:    "share/planning_context.md",
scripts/guards/guard_dms_share_alignment.py:53:    "planning_context.json",  # planning pipeline output for agents (not a managed doc)
scripts/guards/guard_dms_share_alignment.py:72:    "planning_context.md",
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:147:**Fix**: Consider including `pmagent plan next --json-only` output in share folder as `planning_context.json` (full, not head).
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:154:- Add `planning_context.json` to share folder (from `pmagent plan next`)
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:184:**Fix**: Include `planning_context` in `pm_snapshot.json` by calling `pmagent plan next --json-only`.
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:233:4. **Add planning context to share folder** - include `pmagent plan next --json-only` output as `share/planning_context.json`
docs/SSOT/PM_SHARE_FOLDER_GOTCHAS.md:245:2. **Automate planning context updates** - ensure `share/planning_context.json` is always fresh
docs/SSOT/PHASE27_INDEX.md:370:  - Treats planning_context.json as optional
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:69:2. **Planning Context** (`share/planning_context.json`)
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:128:* `make pm.share.planning_context` - Export planning context only
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:183:2. **Use planning context** from `share/planning_context.json` for current focus
docs/SSOT/PHASE15_RECON.md:48:- Multiple `share/` files (doc_registry, kb_registry, planning_context, etc.)
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
pmagent/AGENTS.md:66:  - **SSOT**: Registry entries live in `share/kb_registry.json` (read-only in CI per Rule-044)
pmagent/AGENTS.md:96:- **Components**: DB health, system health (DB + LM + Graph), status explanation, reality-check, AI tracking, share manifest, eval insights (Phase-8/10 exports), kb_registry (KB-Reg:M2)
pmagent/AGENTS.md:121:  - `kb_registry`: KB registry summary (KB-Reg:M2) — **advisory only, read-only in CI**:
pmagent/repo/logic.py:70:      - share/kb_registry.json (JSON export from pmagent control-plane DMS)
pmagent/repo/logic.py:73:      - If kb_registry.json is missing but doc_registry.md exists, fall back
pmagent/repo/logic.py:81:    kb_json_path = Path("share/kb_registry.json")
pmagent/repo/logic.py:85:    # Primary: Use kb_registry.json if available
pmagent/repo/logic.py:96:                f"Unrecognized kb_registry.json structure: expected dict with 'documents' key or list, got {type(data)}"
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
scripts/AGENTS.md:1089:### `kb/build_kb_registry.py` — KB Registry Builder from pmagent control-plane DMS
scripts/AGENTS.md:1096:- **Files Modified**: `scripts/kb/build_kb_registry.py` (3 query locations), `scripts/governance/classify_fragments.py` (1 query location)
scripts/AGENTS.md:1102:python scripts/kb/build_kb_registry.py
scripts/AGENTS.md:1105:python scripts/kb/build_kb_registry.py --dry-run
scripts/AGENTS.md:1109:- `share/kb_registry.json` (curated subset, <50KB target)
.cursor/rules/068-gpt-docs-sync.mdc:99:The KB document registry (`share/kb_registry.json`) serves as the SSOT for document coverage and freshness:
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
.cursor/rules/AGENTS.md:2998:The KB document registry (`share/kb_registry.json`) serves as the SSOT for document coverage and freshness:
pmagent/cli.py:2066:def kb_registry_list(
pmagent/cli.py:2092:def kb_registry_show(
pmagent/cli.py:2127:def kb_registry_by_subsystem(
pmagent/cli.py:2156:def kb_registry_by_tag(
pmagent/cli.py:2182:def kb_registry_summary(
pmagent/cli.py:2241:def kb_registry_validate(
scripts/kb/agents_kb_forensics.py:115:def load_kb_registry_entries() -> list[dict]:
scripts/kb/agents_kb_forensics.py:117:    Load KB registry entries from share/kb_registry.json (if exists).
scripts/kb/agents_kb_forensics.py:208:    kb_entries = load_kb_registry_entries()
scripts/kb/agents_kb_forensics.py:273:        "kb_registry_entries": kb_entries,
scripts/kb/build_kb_registry.py:8:SSOT: share/kb_registry.json (read-only in CI per Rule-044).
scripts/kb/build_kb_registry.py:48:def build_kb_registry_from_dms(dry_run: bool = False) -> KBDocumentRegistry:
scripts/kb/build_kb_registry.py:293:        registry = build_kb_registry_from_dms(dry_run=args.dry_run)
pmagent/oa/state.py:37:KB_REGISTRY = SHARE / "kb_registry.json"
pmagent/oa/state.py:121:        "kb_registry": str(KB_REGISTRY.relative_to(ROOT)),
pmagent/oa/state.py:133:        "kb_registry": _path_exists(KB_REGISTRY),
scripts/util/export_pm_snapshot_json.py:45:            include_kb_registry=True,
pmagent/kb/__init__.py:8:SSOT: Registry entries live in share/kb_registry.json (read-only in CI per Rule-044).
scripts/util/export_pm_introspection_evidence.py:150:        ("kb_registry", "kb_registry_refs"),
scripts/guards/guard_dms_share_alignment.py:50:    "kb_registry.json",
pmagent/kb/AGENTS.md:21:- **Registry file**: `share/kb_registry.json` (JSON format)
pmagent/kb/AGENTS.md:125:**Seeding Script**: `scripts/kb/seed_registry.py` — Populates `share/kb_registry.json` with initial document entries. Respects CI write guards (Rule-044) — only runs in local/dev environments.
pmagent/kb/AGENTS.md:223:The KB registry builder (`scripts/kb/build_kb_registry.py`) has been optimized for PostgreSQL performance:
pmagent/kb/AGENTS.md:236:- `scripts/kb/build_kb_registry.py` (3 query locations optimized)
pmagent/kb/registry.py:9:SSOT: Registry entries live in share/kb_registry.json (read-only in CI per Rule-044).
pmagent/kb/registry.py:25:REGISTRY_PATH = REPO_ROOT / "share" / "kb_registry.json"
pmagent/kb/registry.py:169:        registry_path: Path to registry JSON file (defaults to share/kb_registry.json)
pmagent/kb/registry.py:205:        registry_path: Path to registry JSON file (defaults to share/kb_registry.json)
scripts/guards/guard_share_sync_policy.py:67:    "share/kb_registry.json",
scripts/pm/generate_pm_bootstrap_state.py:41:REGISTRY_PATH = SHARE / "kb_registry.json"
scripts/pm/generate_pm_bootstrap_state.py:100:def load_kb_registry() -> dict[str, Any] | None:
scripts/pm/generate_pm_bootstrap_state.py:273:    registry = load_kb_registry()
scripts/pm/generate_pm_bootstrap_state.py:331:            "kb_registry": optional("share/kb_registry.json"),
scripts/pm/generate_pm_bootstrap_state.py:336:            "kb_registry_path": "share/kb_registry.json",
scripts/pm/generate_pm_bootstrap_state.py:375:                    optional("share/kb_registry.json"),
scripts/guards/guard_repo_layer4_alignment.py:58:        "scripts/kb/build_kb_registry.py",
docs/SSOT/PHASE15_WAVE3_STEP2_OPS_BLOCK.md:29:| **Gate 3 (KB Curation)** | ✅ COMPLETE | 40KB registry, 50 documents | `share/kb_registry.json`, `docs/SSOT/KB_REGISTRY_ARCHITECTURAL_COURSE_CORRECTION.md` |
docs/SSOT/PHASE22_HINTS_CONSOLE_V2.md:47:  - `share/atlas/control_plane/`, `share/exports/docs-control/`, `share/kb_registry.json`
docs/SSOT/LAYERS_AND_PHASES.md:29:  - **Artifact:** `share/kb_registry.json` (generated from DMS)
docs/SSOT/LAYERS_AND_PHASES.md:30:  - **Builder:** `scripts/kb/build_kb_registry.py`
docs/SSOT/LAYER4_CODE_INGESTION_PLAN.md:108:- `scripts/kb/build_kb_registry.py` - Extended to include code files (already supports CODE::*)
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:18:- **Already implemented**: Code updated in `build_kb_registry.py`
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:88:- Only used in one query (`build_kb_registry.py` line 130)
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:169:**Is `build_kb_registry.py` slow?**
docs/SSOT/POSTGRES_OPTIMIZATION_PRIORITY.md:198:2. ⚠️ **Test partial index** if `build_kb_registry.py` is slow
docs/SSOT/PMAGENT_CURRENT_VS_INTENDED.md:137:  - Reads `share/kb_registry.json` for KB registry summary (KB-Reg:M2 + M3a, advisory-only, read-only in CI, seeded with core SSOT/runbook/AGENTS docs)

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
.cursor/rules/072-hint-system.mdc:3:globs: ["**/*.py", "docs/hints/*.md", "scripts/governance/seed_hint_registry.py"]
.cursor/rules/072-hint-system.mdc:15:All hints MUST be registered in `control.hint_registry` via `scripts/governance/seed_hint_registry.py`.
.cursor/rules/072-hint-system.mdc:35:- **Housekeeping**: Ensures `docs/hints/` matches `control.hint_registry`.
scripts/util/export_pm_introspection_evidence.py:151:        ("hint_registry", "hint_registry_refs"),
scripts/guards/hints_required.py:5:Checks that envelopes contain all REQUIRED hints from the DMS hint_registry.
scripts/pm/generate_ssot_surface.py:71:            "hint_registry_status": "active",
scripts/guards/guard_dms_share_alignment.py:68:    "hint_registry.md",
scripts/guards/guard_share_sync_policy.py:87:    "share/hint_registry.md",
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:51:**Flows that load hints from `control.hint_registry`**:
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:458:- `migrations/054_control_hint_registry.sql`
docs/research/PHASE26_DEEP_RESEARCH_REPORT.md:703:   - Not querying `control.hint_registry` for guidance
scripts/governance/seed_hint_registry.py:3:Seed the hint_registry with initial hints.
scripts/governance/seed_hint_registry.py:5:Loads hints from discovery catalog and inserts them into control.hint_registry.
scripts/governance/seed_hint_registry.py:148:def seed_hint_registry(discovery_catalog_path: Path | None = None) -> int:
scripts/governance/seed_hint_registry.py:150:    Seed the hint_registry with initial hints.
scripts/governance/seed_hint_registry.py:172:                        INSERT INTO control.hint_registry
scripts/governance/seed_hint_registry.py:234:                            INSERT INTO control.hint_registry
scripts/governance/seed_hint_registry.py:272:    parser = argparse.ArgumentParser(description="Seed hint_registry with initial hints")
scripts/governance/seed_hint_registry.py:281:    return seed_hint_registry(args.discovery_catalog)
scripts/ops/insert_hints_26a.py:14:    print("\n--- Schema of control.hint_registry ---")
scripts/ops/insert_hints_26a.py:18:            result = conn.execute(text("SELECT * FROM control.hint_registry LIMIT 0"))
scripts/ops/insert_hints_26a.py:67:                INSERT INTO control.hint_registry (id, scope, required, severity, description, docs_refs)
scripts/db/export_dms_tables.py:9:- control.hint_registry
scripts/db/export_dms_tables.py:40:    "control.hint_registry",
docs/ADRs/ADR-059-hint-registry.md:19:Implement a DMS-backed Hint Registry (`control.hint_registry`) that:
docs/ADRs/ADR-059-hint-registry.md:28:**Table**: `control.hint_registry`
docs/ADRs/ADR-059-hint-registry.md:122:- [ ] `control.hint_registry` table exists and is populated
docs/ADRs/ADR-059-hint-registry.md:130:- Migration: `migrations/054_control_hint_registry.sql`
docs/ADRs/ADR-059-hint-registry.md:134:- Seed script: `scripts/governance/seed_hint_registry.py`
docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md:272:  "root_cause": "1. Ruff linter found 3 errors in pmagent/kernel/interpreter.py. 2. Hint 'pmagent.kernel.interpret' not registered in control.hint_registry.",
docs/SSOT/PHASE27_D_DSPY_REASONING_OUTLINE.md:276:    "Add hint 'pmagent.kernel.interpret' to control.hint_registry via pmagent cli",
docs/SSOT/GOTCHAS_INDEX.md:113:  - `doc_registry`, `hint_registry`, COMPASS exports, and SSOT docs.
docs/SSOT/PM_CONTRACT_STRICT_SSOT_DMS.md:101:  `hint_registry.json`, `governance_freshness.json`, `planning_lane_status.json`,
docs/SSOT/PM_SHARE_FOLDER_ENHANCEMENTS.md:93:* `share/hint_registry.json` - System hints registry
docs/SSOT/LAYERED_ARCHITECTURE_V1.md:66:│ - doc_registry, doc_version, doc_sync_state, hint_registry, embeddings   │
docs/SSOT/LAYERED_ARCHITECTURE_V1.md:183:  * Views over doc_registry, hint_registry, violations, phases.
docs/SSOT/LAYERED_ARCHITECTURE_V1.md:204:  * `doc_registry`, `doc_version`, `doc_sync_state`, `hint_registry`, embeddings.
docs/SSOT/SHARE_FOLDER_STRUCTURE.md:41:* `hint_registry.md` - System hints and warnings
docs/SSOT/PHASE26_PHASE_DONE_PLAN.md:50:psql "$GEMATRIA_DSN" -c "SELECT logical_name, kind, enabled FROM control.hint_registry WHERE logical_name LIKE '%boot.kernel_first' OR logical_name LIKE '%preflight.kernel_health';"
docs/SSOT/PHASE26_PHASE_DONE_PLAN.md:260:psql "$GEMATRIA_DSN" -c "SELECT COUNT(*) FROM control.hint_registry WHERE logical_name LIKE '%kernel%'" | grep -q "3"
docs/SSOT/ORCHESTRATOR_REALITY.md:61:4. `query_dms_hints(scope)` → queries `control.hint_registry`
docs/SSOT/PREFLIGHT_DB_CHECK_ROLLOUT.md:26:- [ ] `scripts/governance/seed_hint_registry.py` (inserts into control.hint_registry)
docs/gemantria_share_reconstruction_master_doc_phases_18_23.md:142:    "hint_registry_status": "unknown"
docs/SSOT/PM_SHARE_LAYOUT_PHASE15.md:39:  * DMS tables (`control.doc_registry`, `control.doc_version`, `control.doc_sync_state`, `control.hint_registry`, `control.agent_run`, etc.)
docs/SSOT/PM_SHARE_LAYOUT_PHASE15.md:79:  * DMS run records / `hint_registry` / `control.agent_run`

```

### reality_check_refs

```
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
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:6:Move hints from hardcoded strings in agent code to a DMS-backed registry (`control.hint_registry`) with REQUIRED vs SUGGESTED semantics. Envelope generators (handoff, capability_session, reality_check, status) will query the registry and embed hints into their outputs. A guard (`guard.hints.required`) will enforce that REQUIRED hints are present in envelopes.
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:82:**File**: `pmagent/reality/check.py` (`reality_check`)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:84:- Query hints for `scope="status_api"`, `applies_to={"flow": "reality_check"}`
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:105:**Integration**: Add to `make reality.green STRICT` (via `pmagent/reality/check.py` or new guard script)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:116:  - `pmagent/reality/check.py` (runtime hints)
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:170:- `pmagent/reality/check.py` - Merge DMS hints with runtime hints
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:205:- [ ] Run discovery script to catalog all hardcoded hints in codebase (src/graph/graph.py, scripts/prepare_handoff.py, pmagent/reality/check.py, docs/hints_registry.md) and classify as REQUIRED vs SUGGESTED
.cursor/plans/dms-hint-registry-implementation-a7527037.plan.md:208:- [ ] Wire envelope generators to query DMS and embed hints: scripts/prepare_handoff.py, pmagent/plan/next.py, pmagent/reality/check.py, pmagent/status/snapshot.py (parallel behavior, non-breaking)
pmagent/cli.py:52:from pmagent.ai_docs.reality_check_ai_notes import main as reality_check_ai_notes_main  # noqa: E402
pmagent/cli.py:102:app.add_typer(reality_app, name="reality-check")
pmagent/cli.py:533:    with_status: bool = typer.Option(False, "--with-status", help="Include system posture (reality-check + status)"),
pmagent/cli.py:538:    With --with-status: includes system posture (reality-check + status explain).
pmagent/cli.py:613:    Hermetic: file-only, optional posture via reality-check + status explain.
pmagent/cli.py:1434:def reality_check_one() -> None:
pmagent/cli.py:1439:        [sys.executable, "-m", "pmagent.scripts.reality_check_1"],
pmagent/cli.py:1450:def reality_check_live() -> None:
pmagent/cli.py:1456:        [sys.executable, "-m", "pmagent.scripts.reality_check_1_live"],
pmagent/cli.py:1463:@reality_app.command("check", help="Run comprehensive reality check (env + DB + LM + exports + eval)")
pmagent/cli.py:1464:def reality_check_check(
pmagent/cli.py:1469:    """Run comprehensive reality check."""
pmagent/cli.py:1470:    from pmagent.reality.check import reality_check, print_human_summary
pmagent/cli.py:1472:    run = create_agent_run("system.reality-check", {"mode": mode, "no_dashboards": no_dashboards})
pmagent/cli.py:1480:        verdict = reality_check(mode=mode_upper, skip_dashboards=no_dashboards)
pmagent/cli.py:1719:    "reality-check-ai-notes",
pmagent/cli.py:1720:    help="Generate AI notes for pmagent reality-check (uses Granite when available)",
pmagent/cli.py:1722:def docs_reality_check_ai_notes() -> None:
pmagent/cli.py:1723:    """Generate orchestrator-facing AI notes about the reality-check system."""
pmagent/cli.py:1724:    exit_code = reality_check_ai_notes_main()
pmagent/reality/__init__.py:3:from pmagent.reality.check import print_human_summary, reality_check
pmagent/reality/__init__.py:5:__all__ = ["print_human_summary", "reality_check"]
pmagent/reality/check.py:205:def reality_check(mode: str = "HINT", skip_dashboards: bool = False) -> dict[str, Any]:
pmagent/reality/check.py:206:    """Run comprehensive reality check.
pmagent/reality/check.py:259:        # Import here to avoid circular import (snapshot imports reality_check)
pmagent/reality/check.py:280:        "command": "reality.check",
pmagent/reality/check.py:298:                applies_to={"flow": "reality_check"},
pmagent/reality/check.py:299:                mode=mode,  # Use same mode as reality_check
pmagent/reality/check.py:369:    print(f"[pmagent] reality.check (mode={mode})", file=file)
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
pmagent/tools/AGENTS.md:5:The `pmagent/tools/` directory contains tool functions for system health, control plane, documentation, ledger verification, and reality checks. These tools are called by the `pmagent` CLI and provide structured JSON responses.

```

### self_healing_refs

```
scripts/util/export_pm_introspection_evidence.py:6:share + planning + KB + tracking/self-healing systems currently work together.
scripts/util/export_pm_introspection_evidence.py:153:        ("self-healing", "self_healing_refs"),
scripts/util/export_pm_introspection_evidence.py:213:        "planning + KB + tracking/self-healing systems currently behave. It is NOT a",
scripts/util/export_pm_introspection_evidence.py:300:            "## 6. Tracking / self-healing references (rg outputs)",
docs/handoff/GPT_PM_CONTEXT_REBUILD.md:20:Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and visualization-ready artifacts, with self-healing guards and governance.
docs/SSOT/PHASE_14_SEMANTIC_RECORD.md:262:### self-healing logic
docs/SSOT/PHASE_14_SEMANTIC_RECORD.md:263:- **No changes** (Phase 14 is feature work, no self-healing changes)
docs/SSOT/PHASE_14_SEMANTIC_RECORD.md:322:- **No changes** (Phase 14 is feature work, no self-healing changes)
docs/SSOT/MASTER_PLAN.md:24:Build a deterministic, resumable LangGraph pipeline that produces verified gematria data and viz-ready artifacts, with self-healing guards and governance.

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
.cursor/rules/039-execution-contract.mdc:17:  Cursor MUST run gotchas guard before feature work.
.cursor/rules/039-execution-contract.mdc:24:  - Before executing OPS blocks with code changes, run: python scripts/guards/guard_gotchas_index.py
scripts/util/export_pm_introspection_evidence.py:154:        ("gotchas", "gotchas_refs"),
scripts/util/export_pm_introspection_evidence.py:163:    """Get head sections from contract/gotchas docs."""
scripts/util/export_pm_introspection_evidence.py:316:    # Contracts/gotchas
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
scripts/pm/generate_pm_bootstrap_state.py:313:        "gotchas": {
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
docs/forest/overview.md:77:- Rule 070-gotchas-check: ---
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
docs/SSOT/PHASE10_WIRING_SELF_ASSESSMENT.md:33:- ❌ Did NOT perform pre-work gotchas analysis
docs/SSOT/PHASE10_WIRING_SELF_ASSESSMENT.md:119:# 4. Pre-work gotchas analysis (Rule 070)
docs/SSOT/PHASE10_WIRING_SELF_ASSESSMENT.md:151:# 4. Post-work gotchas review (Rule 070)
docs/SSOT/PHASE10_WIRING_SELF_ASSESSMENT.md:266:**Rule**: Pre-work and post-work gotchas checks are MANDATORY (Rule 070).
docs/SSOT/PHASE10_WIRING_SELF_ASSESSMENT.md:279:- `.cursor/rules/070-gotchas-check.mdc` - Gotchas check requirements
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

I must query the **pmagent control-plane DMS (Postgres `control.doc_registry` / Control Plane)** BEFORE searching files.

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

**CRITICAL (Rule-069):** Before answering "what's next" questions, **ALWAYS run `pmagent plan kb list` FIRST**. Never manually search MASTER_PLAN.md, NEXT_STEPS.md, task.md, or other docs without first querying the pmagent control-plane DMS. See `.cursor/rules/069-always-use-dms-first.mdc` for full requirements.

4. **File Search** (LAST RESORT):
   - Only use grep_search/find_by_name for content NOT in pmagent control-plane DMS
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

This workflow makes that vision real: as projects grow, PM learns automatically through pmagent control-plane DMS registration.

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
* `doc_registry.md` - pmagent control-plane DMS document registry snapshot
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
  * pmagent control-plane DMS/hint registry posture
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
* `share/doc_registry.md` - Complete pmagent control-plane DMS document registry (converted from JSON)
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
* **pmagent control-plane DMS Tables** (`share/doc_registry.md`, etc.) - Full pmagent control-plane DMS table dumps (converted from JSON)

The PM can query pmagent control-plane DMS using:
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
* pmagent control-plane DMS is the SSOT for document tracking
* No manual file management required

**Action**: The manifest is kept for historical reference but should not be used for validation or synchronization. The `share.manifest.verify` Makefile target may produce warnings about missing files - these can be ignored as the manifest is outdated.


```

## 8. Share folder structure

```json
{
  "total_files": 89,
  "json_files": [
    "HANDOFF_KERNEL.json",
    "PHASE16_AUDIT_SNAPSHOT.json",
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
    "HANDOFF_KERNEL.md",
    "LAYER3_AI_DOC_INGESTION_PLAN.md",
    "LAYER4_CODE_INGESTION_PLAN.md",
    "LM_STUDIO_SETUP.md",
    "LM_WIDGETS.md",
    "MASTER_PLAN.md",
    "NEXT_STEPS.md",
    "PHASE16_DB_RECON_REPORT.md",
    "PHASE16_PURGE_EXECUTION_LOG.md",
    "PHASE18_AGENTS_SYNC_SUMMARY.md",
    "PHASE18_INDEX.md",
    "PHASE18_LEDGER_REPAIR_SUMMARY.md",
    "PHASE18_SHARE_EXPORTS_SUMMARY.md",
    "PHASE19_SHARE_HYGIENE_SUMMARY.md",
    "PHASE20_INDEX.md",
    "PHASE20_ORCHESTRATOR_UI_MODEL.md",
    "PHASE20_UI_RESET_DECISION.md",
    "PHASE21_CONSOLE_SERVE_PLAN.md",
    "PHASE21_INDEX.md",
    "PHASE22_INDEX.md",
    "PHASE22_OPERATOR_WORKFLOW.md",
    "PHASE23_AGENTS_SYNC_REPAIR_SUMMARY.md",
    "PHASE23_BASELINE_NOTE.md",
    "PHASE23_BOOTSTRAP_HARDENING_NOTE.md",
    "PHASE23_FAILURE_INJECTION_NOTE.md",
    "PHASE23_INDEX.md",
    "PHASE23_PHASE_DONE_CHECKLIST.md",
    "PHASE23_STRESS_PLAN.md",
    "PHASE23_STRESS_SMOKE_NOTE.md",
    "PHASE27A_IMPLEMENTATION_EVIDENCE.md",
    "PHASE27BC_IMPLEMENTATION_EVIDENCE.md",
    "PHASE27D_IMPLEMENTATION_EVIDENCE.md",
    "PHASE27E_IMPLEMENTATION_EVIDENCE.md",
    "PHASE_14_SEMANTIC_RECORD.md",
    "PHASE_6_PLAN.md",
    "PM_BOOTSTRAP_STATE.md",
    "PM_CONTRACT.md",
    "PM_CONTRACT_STRICT_SSOT_DMS.md",
    "PM_HANDOFF_PROTOCOL.md",
    "PROJECTS_INVENTORY.md",
    "REALITY_GREEN_SUMMARY.md",
    "REFERENCES.md"
  ],
  "directories": [
    "atlas",
    "exports",
    "handoff",
    "oa",
    "orchestrator",
    "orchestrator_assistant",
    "pm_boot"
  ]
}
```
