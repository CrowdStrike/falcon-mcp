# Calculate Total Network Bandwidth Per Host | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-network-bandwidth.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Total Network Bandwidth Per Host

Analyze network traffic patterns using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function with [`sum()`](https://library.humio.com/data-analysis/functions-sum.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    event_simpleName="NetworkConnectStats"
    groupBy([ComputerName], function=[
            sum(field="BytesReceived", as=InboundTraffic),
            sum(field="BytesSent", as=OutboundTraffic)
            ])
    TotalTraffic := InboundTraffic + OutboundTraffic
    sort(field="TotalTraffic", order="desc")

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to perform aggregate calculations on grouped data, allowing analysis of metrics like network traffic across different hosts or systems. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) is used with nested [`sum()`](https://library.humio.com/data-analysis/functions-sum.html) functions to calculate total inbound and outbound network traffic per host, followed by calculating the total bandwidth consumption. 

Example incoming data might look like this: 

@timestamp| event_simpleName| ComputerName| BytesReceived| BytesSent  
---|---|---|---|---  
1686837825000| NetworkConnectStats| DESKTOP-A1| 15000000| 8500000  
1686837825000| NetworkConnectStats| DESKTOP-A1| 8900000| 4200000  
1686837825000| NetworkConnectStats| LAPTOP-B2| 25000000| 12000000  
1686837826000| NetworkConnectStats| SERVER-C3| 95000000| 45000000  
1686837826000| NetworkConnectStats| DESKTOP-A1| 12000000| 6800000  
1686837826000| NetworkConnectStats| LAPTOP-B2| 18000000| 9500000  
1686837827000| NetworkConnectStats| SERVER-C3| 85000000| 42000000  
1686837827000| NetworkConnectStats| DESKTOP-D4| 5000000| 2800000  
1686837827000| NetworkConnectStats| LAPTOP-B2| 22000000| 11000000  
1686837828000| NetworkConnectStats| SERVER-C3| 105000000| 52000000  
1686837828000| NetworkConnectStats| DESKTOP-D4| 6500000| 3200000  
1686837828000| NetworkConnectStats| DESKTOP-A1| 9800000| 5100000  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         event_simpleName="NetworkConnectStats"

Filters events to include only those where event_simpleName equals `NetworkConnectStats`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy([ComputerName], function=[
                 sum(field="BytesReceived", as=InboundTraffic),
                 sum(field="BytesSent", as=OutboundTraffic)
                 ])

Groups the data by the ComputerName field and calculates two aggregate values: the sum of BytesReceived stored in a field named InboundTraffic, and the sum of BytesSent stored in a field named OutboundTraffic. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         TotalTraffic := InboundTraffic + OutboundTraffic

Creates a new field named TotalTraffic containing the values from the InboundTraffic and OutboundTraffic fields. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} 3["Expression"] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         sort(field="TotalTraffic", order="desc")

Sorts the results based on the TotalTraffic field in descending order ([_`order`_](https://library.humio.com/data-analysis/functions-sort.html#query-functions-sort-order)=`desc`), showing hosts with highest bandwidth consumption first. 

  6. Event Result set.




### Summary and Results

The query is used to analyze network bandwidth consumption patterns across different hosts in the network. 

This query is useful, for example, to identify hosts consuming excessive bandwidth, monitor network usage patterns, or detect potential network-intensive applications or anomalies. 

Sample output from the incoming example data: 

ComputerName| InboundTraffic| OutboundTraffic| TotalTraffic  
---|---|---|---  
SERVER-C3| 285000000| 139000000| 424000000  
LAPTOP-B2| 65000000| 32500000| 97500000  
DESKTOP-A1| 45700000| 24600000| 70300000  
DESKTOP-D4| 11500000| 6000000| 17500000  
  
Note that the traffic values are in bytes and that each row represents the aggregated traffic for a unique host
