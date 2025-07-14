# make_it_real

Multi-agent end user application with modern chatbot UI to structure ideas for apps, prepare them technically and work out a structured plan to systematically implement a first, functional prototype.

## Configuration

Copy `.env_example` to `.env` and specify your OpenAI API key as value of `OPENAI_API_KEY`.

Similarly, copy `.mcp.env_example` to `.mcp.env` and replace `PAT` with your personal GitHub access token.

## Run

To build and run containerized CLI:
```sh
make run IDEA='task management app for developers'
```

## Graph

To dump the LangGraph mermaid diagram, run:
```sh
make dump-graph
```

Main Graph (top-level; each node is actually a sub graph):
```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	requirement_analysis(requirement_analysis)
	techstack_discovery(techstack_discovery)
	task_creation(task_creation)
	log_tasks(log_tasks)
	__end__([<p>__end__</p>]):::last
	__start__ --> requirement_analysis;
	requirement_analysis --> techstack_discovery;
	task_creation --> log_tasks;
	techstack_discovery --> task_creation;
	log_tasks --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```
Sub graph (used within each `requirements_analysis`, `techstack_discovery`, `task_creation` in the graph above)
```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	requirements_agent(requirements_agent)
	review_agent(review_agent)
	human_review(human_review)
	__end__([<p>__end__</p>]):::last
	__start__ --> requirements_agent;
	human_review -. &nbsp;approved&nbsp; .-> __end__;
	human_review -. &nbsp;rejected&nbsp; .-> requirements_agent;
	requirements_agent --> review_agent;
	review_agent -. &nbsp;approved&nbsp; .-> human_review;
	review_agent -. &nbsp;rejected&nbsp; .-> requirements_agent;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc

```
