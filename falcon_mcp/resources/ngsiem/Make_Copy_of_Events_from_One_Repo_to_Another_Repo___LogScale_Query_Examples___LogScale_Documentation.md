# Make Copy of Events from One Repo to Another Repo | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-copyevent-repo-repo.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Make Copy of Events from One Repo to Another Repo

Use one parser to ingest data into multiple repositories 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{Conditional} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    copyEvent("cloned_event")
    | case { #type="cloned_event"
    | repo := "target-repo-name"; * }

### Introduction

The [`copyEvent()`](https://library.humio.com/data-analysis/functions-copyevent.html) function is used to make an extra copy of an event, when parsed, both copies will be visible. A common use of case statements is to return a specific value depending on a column's value in the result set. 

In this example, an event is copied from one repo to another and the copied event can only be used in a parser. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{Conditional} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         copyEvent("cloned_event")

Creates a copy of the current event, and assigns the type cloned_event to the copied event. Now two events are flowing through the parser, one event containing the field cloned_event, and one event without that field. In other words, it creates a copy with the type cloned_event and assigns it to a different repository. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{Conditional} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | case { #type="cloned_event"

Returns a specific value that meets the defined condition. In this case, it checks if the event type is cloned_event. The case construct is used to direct the two events to a different target repo. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{Conditional} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | repo := "target-repo-name"; * }

Creates a new repo named target-repo-name with all events of the type cloned_event being directed. The use of `*` ensures, that all other fields are kept unchanged. 

  5. Event Result set.




### Summary and Results

The query is used to ingest data into multiple repositories using the same parser. Shipping all data to one parser and having that parser ship data to many different repositories can be useful: for example, if logs are being sent from a single source, it is possible to setup one parser that can parse all events from this source and decide which repositories to send events to. 

### Note

For On-Prem deployments only: If you are using this function to copy an event to another repository, the [`ALLOW_CHANGE_REPO_ON_EVENTS`](https://library.humio.com/falcon-logscale-self-hosted/envar-allow_change_repo_on_events.html) environment variable must be set to `true`.
