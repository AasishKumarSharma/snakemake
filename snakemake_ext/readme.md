# Snakemake MILP Scheduler Extension

This extension enhances Snakemake's scheduling capabilities by integrating a custom Mixed Integer Linear Programming (MILP) scheduler designed specifically for High-Performance Computing (HPC) environments. It dynamically maps and schedules workflows across heterogeneous resources, optimizing for multiple objectives such as minimizing execution time, maximizing resource utilization, and respecting complex constraints.

---

## Features

- **Dynamic Resource Profiling:** Incorporates detailed system and workflow resource profiles.
- **Advanced Scheduling:** Uses MILP to optimize scheduling based on customizable objectives and constraints.
- **Extensible Architecture:** Easily extendable with additional objectives or system configurations.
- **Integration with Snakemake:** Seamlessly integrates with existing Snakemake workflows.

---

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

2. Install dependencies:

```bash
conda create -n snakemake_milp python=3.12 snakemake pulp
conda activate snakemake_milp
```

---

## Project Structure

```
project_root/
├── Snakefile
├── config.yaml
├── plugins/
│   └── schedulers/
│       ├── __init__.py
│       ├── milp_scheduler.py
│       └── system_characteristics.json
├── results/
└── run_custom_scheduler.py
```

---

## Usage

### Configure Resources

Edit `config.yaml` to set resource profiles and optimization parameters:

```yaml
system_resources: "plugins/schedulers/system_characteristics.json"
alpha: 1  # Weight for resource utilization
beta: 1   # Weight for makespan
```

### Run Workflow with MILP Scheduler

Execute the Snakemake workflow using the custom scheduler:

```bash
PYTHONPATH=$(pwd) python run_custom_scheduler.py
```

---

## Example Workflow

`Snakefile` example:

```snakemake
configfile: "config.yaml"

rule all:
    input:
        "results/task1.done",
        "results/task2.done"

rule task1:
    output: "results/task1.done"
    resources: cores=4, mem_mb=8000, duration=2, data=1
    shell: "sleep 2 && touch {output}"

rule task2:
    output: "results/task2.done"
    resources: cores=8, mem_mb=16000, duration=3, data=2
    shell: "sleep 3 && touch {output}"
```

---

## Extending the Scheduler

To add new constraints or objectives:
- Edit `plugins/schedulers/milp_scheduler.py`.
- Update the `milp_schedule` function to define additional MILP constraints or objectives.

---

## Troubleshooting

- Ensure all dependencies are correctly installed and activated.
- Check logs at `logs/` directory for detailed error messages.
- Verify JSON resource profile formats.

---

## License

This project is released under the MIT License.
