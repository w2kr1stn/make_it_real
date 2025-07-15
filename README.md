# make_it_real

A multi-agent CLI to flesh out project ideas.

AI agents derive use-cases, a tech stack as well as tasks from a given idea, letting the user confirm each (human-in-the-loop) after it was successfully reviewed by another AI agent.

It is written in Python using the LangChain and LangGraph frameworks.

## Environment setup

To run the containerized CLI, you need to have `make` and [docker](https://docs.docker.com/engine/install/) installed.

### Configuration

Copy `.env_example` to `.env` and specify your OpenAI API key as value of `OPENAI_API_KEY`.

## Run

To build and run the containerized CLI:
```sh
make run IDEA='task management app for developers'
```

## Graph of the AI workflow

To dump the LangGraph mermaid diagram, run:
```sh
make dump-graph
```

Main graph of the AI workflow (top-level; the nodes `requirements_analysis`, `techstack_discovery`, `task_creation` are actually sub graphs):
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
