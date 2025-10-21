# Retention Update per Repository | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-retention-update-repo.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Retention Update per Repository

Determine when the retention settings were updated for a single repository 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    type = "dataspace.retention" repoName=<REPO_NAME>

### Introduction

It is possible to create a retention policy that just retains content without deleting, retains and then deletes after a specified period of time, or just deletes content after a specified period of time. The audit log event dataspace.retention records operations for data retention. This audit log type is used to determine when retention was updated for a repository. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         type = "dataspace.retention" repoName=<REPO_NAME>

Filters for the audit log type dataspace.retention in a given repository. 

  3. Event Result set.




### Summary and Results

The query is used to determine when retention settings were last updated for a repository. Data retention is useful as it focuses on preserving data during a specific period of time in order to meet particular business or legal requirements.
