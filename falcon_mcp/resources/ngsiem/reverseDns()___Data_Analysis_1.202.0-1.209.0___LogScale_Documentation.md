# reverseDns() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-reversedns.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jun 10, 2025

## [`reverseDns()`](functions-reversedns.html "reverseDns\(\)")

The [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function performs reverse DNS lookups to find hostnames associated with IP addresses. It adds hostname information to events by querying DNS servers. 

The [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function works in the following way: 

  * Functions only in the result phase (after the first aggregator). 

  * Cannot run in subqueries. 

  * Processes a limited number of results. 

  * Cannot run in filter alerts and aggregate alerts. For alerts, use schedule searches with appropriate actions instead. 




The function attempts to resolve as many IP addresses within specified limits such as; the maximum number of addresses or a limited period of time (timeout period). 

If resolution fails for any addresses (for example, if no response was received before the timeout or because there were too many addresses), the function does the following: 

  * Emits a warning. 

  * Returns events without hostname information. 




Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-reversedns.html#query-functions-reversedns-as)|  string| optional[a] | `_hostname`|  Name of the field containing the resolved hostname, if any.   
[_`field`_](functions-reversedns.html#query-functions-reversedns-field)[b]| string| required |  |  Name of the field that contains the IP address to look up.   
[_`limit`_](functions-reversedns.html#query-functions-reversedns-limit)|  number| optional[[a]](functions-reversedns.html#ftn.table-functions-reversedns-optparamfn) | `ReverseDnsDefaultLimit`|  Maximum number of unique IPs to process. If the input events contain more unique IP addresses than the limit allows, a warning is issued and the rest of the events are not annotated with host name information. The default is the value of the dynamic configuration [`ReverseDnsDefaultLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-reversedns_default_limit.html) (or 5000 if not set).   
|  | **Maximum**| [`ReverseDnsMaxLimit`](functions-reversedns.html#query-functions-reversedns-limit-max-reversednsmaxlimit)|   
|  | **Controlling Variables**  
|  | [`ReverseDnsDefaultLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-reversedns_default_limit.html)|  **Variable default:**`5,000 unique IPs`  
[ _`server`_](functions-reversedns.html#query-functions-reversedns-server)|  string| optional[[a]](functions-reversedns.html#ftn.table-functions-reversedns-optparamfn) |  |  Name or address of the DNS server to use. The default is the value of the configuration value [`RDNS_DEFAULT_SERVER`](https://library.humio.com/falcon-logscale-self-hosted/envar-rdns_default_server.html) or as otherwise configured in the system.   
|  | **Controlling Variables**  
|  | [`RDNS_DEFAULT_SERVER`](https://library.humio.com/falcon-logscale-self-hosted/envar-rdns_default_server.html)|  **Variable default:**  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-reversedns.html#query-functions-reversedns-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-reversedns.html#query-functions-reversedns-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     reverseDns("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     reverseDns(field="value")
> 
> These examples show basic structure only.

### [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") Function Operation

  * The [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function can only be used in the result phase (after an aggregator) and only at top-level. 

  * The [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function uses an external network service to resolve hostnames and therefore has restrictions on how many addresses can be resolved and can fail to resolve addresses at runtime if the DNS server or the network is unreliable, or if the DNS server is throttling or blocking the IP range of the cluster. Therefore, LogScale does not recommend using the annotated hostname for filtering. 

  * There is a cluster wide rate limit on the number of requests. 

This limit is by default set to 1000 requests per second divided between the nodes in the cluster. However, the exact request rate can vary between clusters depending on the cluster setup and load. This is controlled by administrators using the dynamic configuration [`ReverseDnsRequestsPerSecond`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-reversedns_requests_per_second.html). 

  * The number of concurrent requests a node can make is also limited to 10 by default. This is controlled by administrators using the dynamic configuration ​​[`ReverseDnsConcurrentRequests`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-reversedns_concurrent_requests.html). 

  * If a lookup fails, the event will be kept as a result without modification. To exclude such events, a field test after the function can be used, for example, `_hostname=*`. 

  * To prevent the [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function from blocking query execution for an indeterminate amount of time, a timeout is applied to the function call. If a result from the DNS server is not received before the timeout, the result is not annotated with a host name. 

The default timeout is 5 second. However, it can be controlled by administrators using the dynamic configuration [`ReverseDnsDefaultTimeoutInMs`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-reversedns_default_timeout_in_ms.html). 

  * The number of unique IP addresses that can be resolved per query is limited by the [_`limit`_](functions-reversedns.html#query-functions-reversedns-limit) parameter, the timeout, and the node-wide rate limit. 

  * Generally, Reverse DNS cannot be considered authoritative and should only be considered informational. The owner of an IP address can change it to point to an arbitrary hostname. 

For an authoritative alternative without the above limitations, consider using [`asn()`](functions-asn.html "asn\(\)") instead. 

  * If no DNS server is specified, the value of the environment variable [`RDNS_DEFAULT_SERVER`](https://library.humio.com/falcon-logscale-self-hosted/envar-rdns_default_server.html) is used. If this environment variable is not set, the system default DNS server is used. 

  * The [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function caches (remembers) resolved hostnames for a limited time to reduce the number of external calls and provide faster results. 




### [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") Function Usage

The default list of IP address ranges that are disallowed by [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") are listed below: 

ini
    
    
    # IPv4
    # See https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml
    0.0.0.0/8          # RFC791 (https://www.iana.org/go/rfc791)
    0.0.0.0/32         # RFC1122 (https://www.iana.org/go/rfc1122)
    10.0.0.0/8         # RFC1918 (https://www.iana.org/go/rfc1918)
    100.64.0.0/10      # RFC6598 (https://www.iana.org/go/rfc6598)
    127.0.0.0/8        # RFC1122 (https://www.iana.org/go/rfc1122)
    169.254.0.0/16     # RFC3927 (https://www.iana.org/go/rfc3927)
    172.16.0.0/12      # RFC1918 (https://www.iana.org/go/rfc1918)
    192.0.0.0/24       # RFC6890 (https://www.iana.org/go/rfc6890)
    192.0.0.0/29       # RFC7335 (https://www.iana.org/go/rfc7335)
    192.0.0.8/32       # RFC7600 (https://www.iana.org/go/rfc7600)
    192.0.0.9/32       # RFC7723 (https://www.iana.org/go/rfc7723)
    192.0.0.10/32      # RFC8155 (https://www.iana.org/go/rfc8155)
    192.0.0.170/32     # RFC8880 (https://www.iana.org/go/rfc8880)
    192.0.0.171/32     # RFC7050 (https://www.iana.org/go/rfc7050)
    192.0.2.0/24       # RFC5737 (https://www.iana.org/go/rfc5737)
    192.31.196.0/24    # RFC7535 (https://www.iana.org/go/rfc7535)
    192.52.193.0/24    # RFC7450 (https://www.iana.org/go/rfc7450)
    192.88.99.0/24     # RFC7526 (https://www.iana.org/go/rfc7526)
    192.168.0.0/16     # RFC1918 (https://www.iana.org/go/rfc1918)
    192.175.48.0/24    # RFC7534 (https://www.iana.org/go/rfc7534)
    198.18.0.0/15      # RFC2544 (https://www.iana.org/go/rfc2544)
    198.51.100.0/24    # RFC5737 (https://www.iana.org/go/rfc5737)
    203.0.113.0/24     # RFC5737 (https://www.iana.org/go/rfc5737)
    240.0.0.0/4        # RFC1112 (https://www.iana.org/go/rfc1112)
    255.255.255.255/32 # RFC8190 (https://www.iana.org/go/rfc8190)
    
    # IPv6
    # See https://www.iana.org/assignments/iana-ipv6-special-registry/iana-ipv6-special-registry.xhtml
    ::/128             # RFC4291 (https://www.iana.org/go/rfc4291)
    ::1/128            # RFC4291 (https://www.iana.org/go/rfc4291)
    ::ffff:0:0/96      # RFC4291 (https://www.iana.org/go/rfc4291)
    64:ff9b::/96       # RFC6052 (https://www.iana.org/go/rfc6052)
    64:ff9b:1::/48     # RFC8215 (https://www.iana.org/go/rfc8215)
    100::/64           # RFC6666 (https://www.iana.org/go/rfc6666)
    2001::/23          # RFC2928 (https://www.iana.org/go/rfc2928)
    2001::/32          # RFC8190 (https://www.iana.org/go/rfc8190)
    2001:1::1/128      # RFC7723 (https://www.iana.org/go/rfc7723)
    2001:1::2/128      # RFC8155 (https://www.iana.org/go/rfc8155)
    2001:2::/48        # RFC5180 (https://www.iana.org/go/rfc5180)
    2001:3::/32        # RFC7450 (https://www.iana.org/go/rfc7450)
    2001:4:112::/48    # RFC7535 (https://www.iana.org/go/rfc7535)
    2001:10::/28       # RFC4843 (https://www.iana.org/go/rfc4843)
    2001:20::/28       # RFC7343 (https://www.iana.org/go/rfc7543)
    2001:30::/28       # RFC9374 (https://www.iana.org/go/rfc9374)
    2001:db8::/32      # RFC3056 (https://www.iana.org/go/rfc3056)
    2002::/16          # RFC3056 (https://www.iana.org/go/rfc3056)
    2620:4f:8000::/48  # RFC7534 (https://www.iana.org/go/rfc7534)
    fc00::/7           # RFC8190 (https://www.iana.org/go/rfc8190)
    fe80::/10          # RFC4291 (https://www.iana.org/go/rfc4291)

Last updated in v1.129. 

### [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") Syntax Examples

Resolve the hostname for the IP address in the field ip, using the default DNS server. The aggregator function `tail() ` is used to restrict the number of events: 

logscale Syntax
    
    
    tail(100) 
    | reverseDns(ip)

Instead of` tail()`, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function can be used to restrict the number of events, but it produces a lot of events by default (`20,000`). You can use the [`groupBy()`](functions-groupby.html "groupBy\(\)") function's [_`limit`_](functions-groupby.html#query-functions-groupby-limit) parameter to reduce that number: 

logscale Syntax
    
    
    groupby(ip, function=[], limit=100) 
    | reverseDns(ip)

If no default DNS server is configured, or a specific server should be used, the server can be specified using the [_`server`_](functions-reversedns.html#query-functions-reversedns-server) parameter: 

logscale Syntax
    
    
    groupby(ip, function=[], limit=100) 
    | reverseDns(ip, server=8.8.8.8)

To get more (or fewer) results, the maximum number of unique IPs to process can be changed using the [_`limit`_](functions-reversedns.html#query-functions-reversedns-limit) parameter (higher values may lead to missing results, if the DNS server throttles lookups from the cluster): 

logscale Syntax
    
    
    tail(100) 
    | reverseDns(ip, limit=10)
