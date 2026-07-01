# Incident-Response-Graph


## Context

Incident response data is often scattered across alerts, tickets, analyst notes, and endpoint logs. This leads to Cybersecurity analysts having to manually search through several logs to understand the relationships between users, hosts, ip's and several other entities. The knowledge graph connects these records so analysts can quickly determine whether a new alert is related to prior activity.


## What it is
The Incident Knowledge Platform is a cybersecurity analytics framework that retrieves heterogeneous security telemetry from multiple enterprise security tools, converts it into a canonical security event model, constructs a unified knowledge graph, and applies graph analytics and AI-assisted reasoning to accelerate incident investigation and organizational security intelligence.


## System Architecture 

``
incident-response-graph/
│
├── data/
│   ├── raw/
│   │   ├── assets.csv
│   │   ├── incidents.csv
│   │   ├── alerts.csv
│   │   ├── vulnerabilities.csv
│   │   └── threat_intel.csv
│   │
│   ├── processed/
│   │   ├── entities.csv
│   │   ├── relationships.csv
│   │   └── normalized_events.csv
│   │
│   └── database/
│       └── incident_graph.db
│
├── src/
│   ├── ingestion/
│   │   ├── csv_loader.py
│   │   ├── scanner_loader.py
│   │   ├── wazuh_loader.py          # future
│   │   └── security_onion_loader.py # future
│   │
│   ├── normalization/
│   │   ├── normalize_hosts.py
│   │   ├── normalize_users.py
│   │   ├── normalize_indicators.py
│   │   └── normalize_mitre.py
│   │
│   ├── extraction/
│   │   ├── extract_entities.py
│   │   ├── extract_iocs.py
│   │   └── create_relationships.py
│   │
│   ├── graph/
│   │   ├── build_graph.py
│   │   ├── graph_schema.py
│   │   └── graph_queries.py
│   │
│   ├── analytics/
│   │   ├── recurring_entities.py
│   │   ├── similar_incidents.py
│   │   ├── centrality.py
│   │   └── recommendations.py
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── search_view.py
│   │   ├── incident_view.py
│   │   └── graph_view.py
│   │
│   ├── config.py
│   └── database.py
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_normalization.py
│   ├── test_graph_build.py
│   └── test_similarity.py
│
├── output/
│   ├── incident_graph.html
│   └── analyst_summary.csv
│
├── requirements.txt
├── README.md
└── run_pipeline.py
``




