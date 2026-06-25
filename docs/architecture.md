# Architecture

This document describes the architecture of the organizational-memory toolkit
using text-only diagrams. The toolkit is a local, deterministic pipeline: raw
transcripts flow through rule-based extraction into a memory store, and recall,
analytics, and reporting are layered on top of that store. There are no network
calls and no external models.

The diagrams below are also available as plain-text files under
[`docs/assets/architecture/`](assets/architecture/).

## System overview

```
          +------------------+
          |  Transcript text |
          +--------+---------+
                   |
                   v
          +------------------+
          |   Ingestion      |  load + normalize text
          +--------+---------+
                   |
                   v
          +------------------+
          |   Extraction     |  rule-based extractors
          +--------+---------+
                   |
                   v
          +------------------+
          |   Memory store   |  JSON / SQLite
          +----+--------+----+
               |        |
       +-------+        +--------+
       v                         v
+--------------+         +----------------+
|   Recall     |         |   Analytics    |
| (search/query|         | & Reporting    |
+------+-------+         +--------+-------+
       |                          |
       +------------+-------------+
                    v
            +---------------+
            |      CLI      |
            +---------------+
```

See [`system_overview.txt`](assets/architecture/system_overview.txt).

## Extraction pipeline

```
raw text
   |
   v
[ normalize_text ] -- unicode, whitespace, bullets, timestamps
   |
   v
[ segment / speaker turns ]
   |
   v
[ extractors run in order ]
   |  participant   decision   commitment   task
   |  question      dependency risk         action_item   topic
   v
[ confidence filter + duplicate filter ]
   |
   v
ExtractionResult
```

See [`extraction_pipeline.txt`](assets/architecture/extraction_pipeline.txt).

## Storage layer

```
           +-------------------+
           |   MemoryStore     |  abstract interface
           +---------+---------+
                     |
        +------------+------------+
        v                         v
+----------------+        +-----------------+
|   JSONStore    |        |   SQLiteStore   |
+----------------+        +-----------------+
```

The `MemoryStore` interface (`save_record`, `get_record`, `list_records`,
`update_record`, `delete_record`, `query`, `clear`) has two interchangeable
implementations. See [`storage_layer.txt`](assets/architecture/storage_layer.txt).

## Recall layer

```
query --> parse_query --> load records --> keyword search
      --> filter by fields --> ranked results (+ pagination)
```

Recall is purely lexical: queries are parsed into free text plus `key:value`
filters, records are tokenized and scored by coverage with an exact-phrase bonus.
See [`recall_layer.txt`](assets/architecture/recall_layer.txt).

## Analytics and reporting layer

```
store records --> analytics --> report builders --> Report
                                                  --> Markdown / JSON / CSV
```

Analytics computes summary metrics, memory health, bottlenecks, and owner load.
Report builders assemble these into typed `Report` objects that exporters render
deterministically. See
[`analytics_reporting_layer.txt`](assets/architecture/analytics_reporting_layer.txt).

## CLI flow

```
argv --> build_parser --> parse_args --> command handler
     --> open store --> run operation --> write output --> exit code
```

The CLI registers every subcommand on a single parser and dispatches to the
selected handler. See [`cli_flow.txt`](assets/architecture/cli_flow.txt).
