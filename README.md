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

To dump the LangGraph mermaid, run:
```sh
make dump-graph
```

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	idea_curator(idea_curator)
	spec_writer(spec_writer)
	evaluator(evaluator)
	human_review(human_review<hr/><small><em>__interrupt = before</em></small>)
	__end__([<p>__end__</p>]):::last
	__start__ --> idea_curator;
	evaluator -. &nbsp;end&nbsp; .-> __end__;
	evaluator -. &nbsp;continue&nbsp; .-> human_review;
	human_review -. &nbsp;continue&nbsp; .-> __end__;
	human_review -. &nbsp;revise&nbsp; .-> spec_writer;
	idea_curator -. &nbsp;end&nbsp; .-> __end__;
	idea_curator -. &nbsp;continue&nbsp; .-> spec_writer;
	spec_writer -. &nbsp;end&nbsp; .-> __end__;
	spec_writer -. &nbsp;continue&nbsp; .-> evaluator;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```