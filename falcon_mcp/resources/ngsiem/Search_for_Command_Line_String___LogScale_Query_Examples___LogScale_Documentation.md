# Search for Command Line String | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-regex-filter-commandline.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search for Command Line String

Search for command line string after `/` and before `@` using a regular expression 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #event_simpleName=ProcessRollup2
    | CommandLine=/@/
    | CommandLine=/\/.*@/

### Introduction

A regular expression can be used to run a query that looks for command line strings containing any characters after `/` and before `@`. It is important to perform as much filtering as possible to not exceed resource limits. 

In this example, a regular expression is used to filter and search for specific process events in the CrowdStrike Falcon platform. Note that the query filters on the `@` alone first to perform as much filtering as possible. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #event_simpleName=ProcessRollup2

Filters for events of the type `ProcessRollup2` in the #event_simpleName field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | CommandLine=/@/

Filters for any command line containing the `@` symbol. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | CommandLine=/\/.*@/

Uses a regular expression to search the returned results for command lines that contain a forward slash (`/`) followed by any number of characters, and then a `@` symbol. 

  5. Event Result set.




### Summary and Results

The query is used to search for command line strings that contain any characters after `/` and before `@`. The query could, for example, be used to help security analysts identify potentially suspicious processes that might be interacting with email addresses or using email-like syntax in their command lines.
