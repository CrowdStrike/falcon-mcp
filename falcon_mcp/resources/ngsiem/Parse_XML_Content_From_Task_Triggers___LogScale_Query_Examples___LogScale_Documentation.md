# Parse XML Content From Task Triggers | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsexml-task-triggers.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse XML Content From Task Triggers

Extract and analyze XML data from scheduled tasks using the [`parseXml()`](https://library.humio.com/data-analysis/functions-parsexml.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3["Expression"] 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result

logscale
    
    
    #event_simpleName=ScheduledTaskRegistered
    | parseXml(TaskXml)
    | Trigger:=rename(Task.Triggers.LogonTrigger.Enabled)
    | Trigger=*
    | table([aid, Trigger, TaskXml], limit=1000)

### Introduction

The [`parseXml()`](https://library.humio.com/data-analysis/functions-parsexml.html) function can be used to parse XML content from fields, making the structured data available for analysis. 

In this example, the [`parseXml()`](https://library.humio.com/data-analysis/functions-parsexml.html) function is used to extract trigger information from scheduled task XML data. 

Example incoming data might look like this: 

@timestamp| aid| event_simpleName| TaskXml  
---|---|---|---  
2025-10-15T10:00:00Z| aid123| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
2025-10-15T10:01:00Z| aid124| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>  
2025-10-15T10:02:00Z| aid125| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
2025-10-15T10:03:00Z| aid126| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3["Expression"] 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #event_simpleName=ScheduledTaskRegistered

Filters events where event_simpleName equals `ScheduledTaskRegistered`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3["Expression"] 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseXml(TaskXml)

Parses the XML content from the TaskXml field. The function creates a structured object with the parsed XML data, making nested elements accessible using dot notation. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3["Expression"] 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | Trigger:=rename(Task.Triggers.LogonTrigger.Enabled)

Creates a new field named Trigger containing the value from the parsed XML path Task.Triggers.LogonTrigger.Enabled. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3["Expression"] 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | Trigger=*

Filters to keep only events where Trigger has a value. This line can be removed if empty trigger values should be included in the results. 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[\Add Field/] 3["Expression"] 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | table([aid, Trigger, TaskXml], limit=1000)

Creates a table showing the aid, Trigger, and original TaskXml fields, limited to 1000 rows. 

  7. Event Result set.




### Summary and Results

The query is used to extract and analyze trigger settings from scheduled task XML data. 

This query is useful, for example, to monitor and audit scheduled task configurations and identify tasks with specific trigger settings. 

Sample output from the incoming example data: 

aid| Trigger| TaskXml  
---|---|---  
aid123| true| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
aid124| false| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>  
aid125| true| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
aid126| false| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>
