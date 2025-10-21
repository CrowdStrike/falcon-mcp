# Compute Community ID | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-communityid-netflow-logs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compute Community ID

Computes the Community ID, a standard for hashing network flows 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    communityId(proto=flow.protocolIdentifier,
    sourceip=flow.sourceIPv4Address,
    sourceport=flow.sourceTransportPort,
    destinationip=flow.destinationIPv4Address,
    destinationport=flow.destinationTransportPort)

### Introduction

The Community ID is a standard for hashing network flows. The [`communityId()`](https://library.humio.com/data-analysis/functions-communityid.html) function is used to compute the Community ID (the 6 digit code at the end of your profile URL). 

In this example, the [`communityId()`](https://library.humio.com/data-analysis/functions-communityid.html) function is used to calculate the Community IDs for netflow logs. To generate the Community ID, a hash is performed with the source and destination IP addresses and ports, along with the protocol and a seed. By default the Community ID is outputted in a _community_id field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         communityId(proto=flow.protocolIdentifier,
         sourceip=flow.sourceIPv4Address,
         sourceport=flow.sourceTransportPort,
         destinationip=flow.destinationIPv4Address,
         destinationport=flow.destinationTransportPort)

Calculates the Community IDs for netflow logs, and returns the results in a _community_id field. The value in the destinationip and sourceip field must be an IPv4 or IPv6 address. The Community ID values can be used for filtering. 

  3. Event Result set.




### Summary and Results

The query is used to compute the Community ID, a network flow hash standard. The query generates a consistent hash for each unique network flow, allowing for easy tracking and correlation. This can be used to easily correlate and join network flows across systems. The flow hash is useful for correlating all network events related to a single flow.
