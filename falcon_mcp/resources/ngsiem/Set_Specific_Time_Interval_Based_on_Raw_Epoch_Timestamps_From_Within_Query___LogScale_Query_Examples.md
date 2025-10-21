# Set Specific Time Interval Based on Raw Epoch Timestamps From Within Query | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-settimeinterval-specify-time-range.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set Specific Time Interval Based on Raw Epoch Timestamps From Within Query

Set a specific time interval based on raw epoch timestamps from within the query instead of through the QueryJobs API or UI 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    setTimeInterval(start=1746054000000, end=1746780124517)
    | "#event_simpleName" = ProcessRollup2

### Introduction

The [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function can be used to set the time interval and related metadata from within the query instead of through the QueryJobs API or UI. The time settings of the [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function will overwrite whatever was specified in the QueryJobs API or UI. [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) must appear in the preamble of the query, before any other functions, filters, free-text searches, etc. 

In this example, the [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) function is used to define a new time interval based on the epoch times `1746054000000` and `1746780124517` and return events of the type ProcessRollup2. 

For more information about time specification options, see [Search API Time Specification](https://library.humio.com/logscale-api/api-search-timespec.html). 

Example incoming data might look like this: 

timestamp| event_simpleName| ProcessId| CommandLine| ImageFileName| UserName| aid  
---|---|---|---|---|---|---  
1746054100000| ProcessRollup2| 4567| /usr/bin/python3 script.py| /usr/bin/python3| john.doe| a1b2c3d4e5f6  
1746054200000| ProcessRollup2| 4568| notepad.exe file.txt| C:\Windows\notepad.exe| jane.smith| b2c3d4e5f6g7  
1746054300000| ProcessRollup2| 4569| cmd.exe /c dir| C:\Windows\System32\cmd.exe| admin.user| c3d4e5f6g7h8  
1746054400000| ImageLoadv2| 4570| explorer.exe| C:\Windows\explorer.exe| john.doe| d4e5f6g7h8i9  
1746054500000| ProcessRollup2| 4571| powershell.exe -nologo| C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| system| e5f6g7h8i9j0  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         setTimeInterval(start=1746054000000, end=1746780124517)

Sets a time interval in raw epoch time to start at `1746054000000` and end at `1746780124517`. The timestamps are in Unix epoch milliseconds. 

Searches within the specified time period. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Preamble] 2[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | "#event_simpleName" = ProcessRollup2

Filters for events where the values in the field event_simpleName is of the type ProcessRollup2. The ProcessRollup2 events represent process execution/creation events in CrowdStrike. 

  4. Event Result set.




### Summary and Results

The query is used to return only ProcessRollup2 events that occurred during a specific timeframe defined in Epochs per millisecond. 

This query demonstrates how to use [`setTimeInterval()`](https://library.humio.com/data-analysis/functions-settimeinterval.html) to define the timespan in Epoch times from within the query instead of through the QueryJobs API or UI. 

For an example of using relative time, see [Set Relative Time Interval From Within Query](examples-settimeinterval-basic.html "Set Relative Time Interval From Within Query"). 

Sample output from the incoming example data: 

timestamp| event_simpleName| ProcessId| CommandLine| ImageFileName| UserName| aid  
---|---|---|---|---|---|---  
1746054100000| ProcessRollup2| 4567| /usr/bin/python3 script.py| /usr/bin/python3| john.doe| a1b2c3d4e5f6  
1746054200000| ProcessRollup2| 4568| notepad.exe file.txt| C:\Windows\notepad.exe| jane.smith| b2c3d4e5f6g7  
1746054300000| ProcessRollup2| 4569| cmd.exe /c dir| C:\Windows\System32\cmd.exe| admin.user| c3d4e5f6g7h8  
1746054500000| ProcessRollup2| 4571| powershell.exe -nologo| C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe| system| e5f6g7h8i9j0  
  
The query only returns rows 1, 2, 3, and 5 since row 4 has a different event_simpleName (ImageLoadv2).
