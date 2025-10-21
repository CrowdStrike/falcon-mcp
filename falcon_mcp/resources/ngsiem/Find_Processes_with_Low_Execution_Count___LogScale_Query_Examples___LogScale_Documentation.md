# Find Processes with Low Execution Count | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-count-processes-low.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Processes with Low Execution Count

Group processes by hash and name to identify rarely executed ones using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result

logscale
    
    
    #event_simpleName=ProcessRollup2 OR #event_simpleName=SyntheticProcessRollup2
    aid=?aid
    groupBy([SHA256HashData, ImageFileName], limit=max)
    _count < 5
    sort(_count, limit=1000)

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to group events by specified fields and perform aggregate calculations on the grouped data. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to identify processes that have been executed only a few times on a specific host, which could be useful for detecting unusual or potentially suspicious activity. 

Example incoming data might look like this: 

@timestamp| event_simpleName| aid| SHA256HashData| ImageFileName| CommandLine  
---|---|---|---|---|---  
2025-10-06T10:00:00Z| ProcessRollup2| 12345abc| a1b2c3d4e5f6...| chrome.exe| C:\Program Files\Google\Chrome\Application\chrome.exe  
2025-10-06T10:05:00Z| ProcessRollup2| 12345abc| a1b2c3d4e5f6...| chrome.exe| C:\Program Files\Google\Chrome\Application\chrome.exe  
2025-10-065T10:10:00Z| SyntheticProcessRollup2| 12345abc| f6e5d4c3b2a1...| suspicious.exe| C:\Users\Admin\Downloads\suspicious.exe  
2025-10-06T10:15:00Z| ProcessRollup2| 12345abc| 98765432dcba...| notepad.exe| C:\Windows\System32\notepad.exe  
2025-10-06T10:20:00Z| ProcessRollup2| 12345abc| 98765432dcba...| notepad.exe| C:\Windows\System32\notepad.exe  
2025-10-06T10:25:00Z| ProcessRollup2| 12345abc| 11223344aabb...| calc.exe| C:\Windows\System32\calc.exe  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #event_simpleName=ProcessRollup2 OR #event_simpleName=SyntheticProcessRollup2

Filters events to include only process execution events with event_simpleName equal to `ProcessRollup2` or `SyntheticProcessRollup2`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         aid=?aid

Filters events for a specific host using the aid (agent ID) parameter. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy([SHA256HashData, ImageFileName], limit=max)

Groups events by both the SHA256HashData and ImageFileName fields. The [_`limit`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-limit) parameter is set to `max` to ensure all groups are included. 

By default the [`count()`](https://library.humio.com/data-analysis/functions-count.html) function is used and the grouped count returned in a field named _count. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         _count < 5

Filters the groups to show only those with fewer than 5 executions, using the built-in _count field that is automatically created by [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html). 

  6. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3{{Aggregate}} 4[/Filter/] 5{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> 5 5 --> result style 5 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sort(_count, limit=1000)

Sorts the results by execution count in ascending order, limiting the output to 1000 results. 

  7. Event Result set.




### Summary and Results

The query is used to identify processes that have been executed infrequently on a specific host by grouping them based on their hash value and image name. 

This query is useful, for example, to detect potentially suspicious or unusual processes that do not run often, which could indicate malicious activity or unauthorized software installations. 

Sample output from the incoming example data: 

SHA256HashData| ImageFileName| _count  
---|---|---  
f6e5d4c3b2a1...| suspicious.exe| 1  
11223344aabb...| calc.exe| 1  
98765432dcba...| notepad.exe| 2  
  
The results are sorted by execution count, showing the least frequently executed processes first. Each row represents a unique combination of process hash and name, along with how many times it was executed. 

Processes with the same name but different hashes are treated as separate entries, helping identify potentially malicious files masquerading as legitimate processes.
