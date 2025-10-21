# communityId() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-communityid.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`communityId()`](functions-communityid.html "communityId\(\)")

Computes the Community ID, a standard for hashing network flows. This can be used to easily correlate and join network flows across systems. 

This implements the `community_id_v1` functions as described in the [Community ID Spec](https://github.com/corelight/community-id-spec). If the protocol is found to be ICMP, then icmptype and icmpcode will be mapped to port equivalents as described by the `community_id_icmp` function in the specification. 

If this function receives invalid inputs (for example, an invalid IP or a port out of range), it will assign the empty string to the output field as. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-communityid.html#query-functions-communityid-as)|  string| optional[a] | `_community_id`|  Name of the output field   
[_`destinationip`_](functions-communityid.html#query-functions-communityid-destinationip)|  string| required |  |  Name of destination IP address field. The value must be an IPv4 or IPv6 address.   
[_`destinationport`_](functions-communityid.html#query-functions-communityid-destinationport)|  integer| optional[[a]](functions-communityid.html#ftn.table-functions-communityid-optparamfn) |  |  Name of the destination port field. If set, the [_`destinationip`_](functions-communityid.html#query-functions-communityid-destinationip) parameter must also be set.   
|  | **Minimum**| `0`|   
|  | **Maximum**| [`65535`](functions-communityid.html#query-functions-communityid-destinationport-max-65535)|   
[ _`icmpcode`_](functions-communityid.html#query-functions-communityid-icmpcode)|  integer| optional[[a]](functions-communityid.html#ftn.table-functions-communityid-optparamfn) |  |  Name of the ICMP code field. If this parameter is set, then the [_`icmptype`_](functions-communityid.html#query-functions-communityid-icmptype) parameter must also be set.   
|  | **Minimum**| `0`|   
|  | **Maximum**| [`65535`](functions-communityid.html#query-functions-communityid-icmpcode-max-65535)|   
[ _`icmptype`_](functions-communityid.html#query-functions-communityid-icmptype)|  integer| optional[[a]](functions-communityid.html#ftn.table-functions-communityid-optparamfn) |  |  Name of the ICMP type field. If this parameter is set, then the [_`icmpcode`_](functions-communityid.html#query-functions-communityid-icmpcode) parameter must also be set.   
|  | **Minimum**| `0`|   
|  | **Maximum**| [`65535`](functions-communityid.html#query-functions-communityid-icmptype-max-65535)|   
[ _`proto`_](functions-communityid.html#query-functions-communityid-proto)|  string| required |  |  Name of protocol field. This field will be read directly and either interpreted directly as a IANA protocol number, or as the keyword of a protocol number from the Protocol Numbers. The value in the field must be either a protocol keyword or a number in the range 0 to 255.   
[_`seed`_](functions-communityid.html#query-functions-communityid-seed)|  integer| optional[[a]](functions-communityid.html#ftn.table-functions-communityid-optparamfn) | `0`|  The seed value used when computing the Community ID.   
|  | **Minimum**| `0`|   
|  | **Maximum**| [`65535`](functions-communityid.html#query-functions-communityid-seed-max-65535)|   
[ _`sourceip`_](functions-communityid.html#query-functions-communityid-sourceip)|  string| required |  |  Name of source IP address field. The value must be an IPv4 or IPv6 address.   
[_`sourceport`_](functions-communityid.html#query-functions-communityid-sourceport)|  string| optional[[a]](functions-communityid.html#ftn.table-functions-communityid-optparamfn) |  |  Name of the source port field. If set, the [_`destinationip`_](functions-communityid.html#query-functions-communityid-destinationip) parameter must also be set.   
|  | **Minimum**| `0`|   
|  | **Maximum**| [`65535`](functions-communityid.html#query-functions-communityid-sourceport-max-65535)|   
[a] Optional parameters use their default value unless explicitly set.  
  
### [`communityId()`](functions-communityid.html "communityId\(\)") Examples

Click + next to an example below to get the full details.

#### Compute Community ID

**Computes the Community ID, a standard for hashing network flows**

##### Query

logscale
    
    
    communityId(proto=flow.protocolIdentifier,
    sourceip=flow.sourceIPv4Address,
    sourceport=flow.sourceTransportPort,
    destinationip=flow.destinationIPv4Address,
    destinationport=flow.destinationTransportPort)

##### Introduction

In this example, the [`communityId()`](functions-communityid.html "communityId\(\)") function is used to calculate the Community IDs for netflow logs. To generate the Community ID, a hash is performed with the source and destination IP addresses and ports, along with the protocol and a seed. By default the Community ID is outputted in a _community_id field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         communityId(proto=flow.protocolIdentifier,
         sourceip=flow.sourceIPv4Address,
         sourceport=flow.sourceTransportPort,
         destinationip=flow.destinationIPv4Address,
         destinationport=flow.destinationTransportPort)

Calculates the Community IDs for netflow logs, and returns the results in a _community_id field. The value in the destinationip and sourceip field must be an IPv4 or IPv6 address. The Community ID values can be used for filtering. 

  3. Event Result set.




##### Summary and Results

The query is used to compute the Community ID, a network flow hash standard. The query generates a consistent hash for each unique network flow, allowing for easy tracking and correlation. This can be used to easily correlate and join network flows across systems. The flow hash is useful for correlating all network events related to a single flow.
