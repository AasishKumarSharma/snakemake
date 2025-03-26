import pulp
import json
import os
import logging

from snakemake.scheduler import JobScheduler

class MILPScheduler(JobScheduler):
    def __init__(self, workflow, dag):
        super().__init__(workflow, dag)
        self.system_resources = self.load_json(workflow.config["system_resources"])
        self.alpha = workflow.config.get("alpha", 1)
        self.beta = workflow.config.get("beta", 1)
        #self.max_concurrent_jobs = workflow.config.get("max_concurrent_jobs", 10)
        self.tasks = self.extract_task_info(dag.jobs)

    def load_json(self, filepath):
        with open(filepath) as f:
            return json.load(f)["nodes"]

    def extract_task_info(self, jobs):
        tasks = {}
        for job in jobs:
            tasks[job.name] = {
                "cores": job.resources.get("cores", 1),
                "memory_required": job.resources.get("mem_mb", 1024)/1024,
                "features": ["CPU"],  # adjust dynamically as needed
                "duration": job.resources.get("duration", 1),
                "data": job.resources.get("data", 1),
                "dependencies": [dep.name for dep in job.dag.dependencies[job]],
                #"priority": job.priority if hasattr(job, 'priority') else 1
            }
        return tasks

    def schedule(self):
        ready_jobs = list(self.dag.ready_jobs)
        assignments = self.milp_schedule(self.system_resources, self.tasks, self.alpha, self.beta)
        scheduled_jobs = {job for job in ready_jobs if job.name in assignments}
        logging.info(f"MILP Scheduled: {scheduled_jobs}")
        print(f"Selected jobs: {len(scheduled_jobs)}")
        return scheduled_jobs

    def milp_schedule(self, nodes, tasks, alpha, beta):
        prob = pulp.LpProblem("HPCScheduling", pulp.LpMinimize)

        x = pulp.LpVariable.dicts("assign", [(t, n) for t in tasks for n in nodes], cat='Binary')
        start_time = pulp.LpVariable.dicts("start_time", tasks, lowBound=0, cat='Continuous')
        end_time = pulp.LpVariable.dicts("end_time", tasks, lowBound=0, cat='Continuous')
        makespan = pulp.LpVariable("makespan", lowBound=0, cat='Continuous')

        ## Objectives
        #resource_usage = pulp.lpSum(tasks[t]["cores"]*x[(t, n)] for t in tasks for n in nodes)
        #priority_term = pulp.lpSum(tasks[t]["priority"] * start_time[t] for t in tasks)

        #prob += alpha * makespan - beta * priority_term
        total_usage = pulp.lpSum(tasks[t]["cores"] * x[(t, n)] for t in tasks for n in nodes)
        prob += alpha * total_usage  # simplified, extend for other objectives

        # Constraints
        for t in tasks:
            prob += pulp.lpSum(x[(t, n)] for n in nodes) == 1
            prob += end_time[t] >= start_time[t] + pulp.lpSum(
                tasks[t]['duration'] / nodes[n]['processing_speed'].get('CPU', 1) * x[(t, n)] for n in nodes)

        # Makespan constraint
        for t in tasks:
            prob += makespan >= end_time[t]

        # Resource constraints
        for n in nodes:
            prob += pulp.lpSum(tasks[t]["cores"] * x[(t, n)] for t in tasks) <= nodes[n]["cores"]
            prob += pulp.lpSum(tasks[t]["memory_required"] * x[(t, n)] for t in tasks) <= nodes[n]["memory"]

        # Dependency constraints
        # for t in tasks:
        #     for dep in tasks[t]['dependencies']:
        #         prob += start_time[t] >= end_time[dep]
        for t in tasks:
            for dep in tasks[t]['dependencies']:
                for n in nodes:
                    for m in nodes:
                        if n != m:
                            prob += start_time[t] >= end_time[dep] + round(
                                (tasks[dep]['data'] / nodes[n]['data_transfer_rate']), 2) * (
                                                x[(t, n)] + x[(dep, m)] - 1)

        ## Concurrency limit constraint
        #prob += pulp.lpSum([x[(t, n)] for t in tasks for n in nodes]) <= self.max_concurrent_jobs

        prob.solve()

        assignments = {}
        if pulp.LpStatus[prob.status] == 'Optimal':
            for t in tasks:
                for n in nodes:
                    if pulp.value(x[(t, n)]) == 1:
                        assignments[t] = n

        return assignments