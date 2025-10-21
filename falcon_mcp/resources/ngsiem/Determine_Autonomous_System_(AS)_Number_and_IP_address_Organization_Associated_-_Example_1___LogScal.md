# Determine Autonomous System (AS) Number and IP address/Organization Associated - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-asn-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Determine Autonomous System (AS) Number and IP address/Organization Associated - Example 1

Determine the autonomous system (AS) number and organization associated with a given IP address 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    asn(field=address)

### Introduction

The [`asn()`](https://library.humio.com/data-analysis/functions-asn.html) function provides the Autonomous System Number (ASN) of a given IP address, providing information on the owner. By default, [`asn()`](https://library.humio.com/data-analysis/functions-asn.html) uses the ip field as the input parameter. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         asn(field=address)

Adds the ASN to a given event (based on the field address) in the fields address.asn and address.org are added to the event. 

  3. Event Result set.




### Summary and Results

The query is used to automatically add an AS number to its associated IP address (and organization with that IP address associated). Knowing the Autonomos System Number of the associated IP addresses is useful to identify registered owners/organizations of an IP range. When using the ASN search to query a list of IP addresses, it is possible to mix IPv4 and IPv6 addresses within the one query.
