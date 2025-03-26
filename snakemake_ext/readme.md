.
├── Snakefile
├── plugins
│   ├── schedulers
│   │   ├── __init__.py
│   │   └── milp_scheduler.py      <-- Your custom MILP Scheduler Plugin
│   └── resources
│       ├── __init__.py
│       └── system_resources.py    <-- System Resources Plugin
├── profiles
│   └── my_hpc_profile
│       ├── config.yaml
│       └── system_characteristics.json
├── src
│   └── executor.py               <-- Uses Snakemake built-in executors
└── run.sh
