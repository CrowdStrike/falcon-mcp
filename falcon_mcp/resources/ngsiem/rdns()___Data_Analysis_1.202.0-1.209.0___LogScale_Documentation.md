# rdns() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-rdns.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jun 17, 2025

## [`rdns()`](functions-rdns.html "rdns\(\)")

Resolves hostnames using reverse DNS lookups. 

The [`rdns()`](functions-rdns.html "rdns\(\)") function is deprecated and will be removed in version 1.249. Use [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function to replicate [`rdns()`](functions-rdns.html "rdns\(\)") functionality as the [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") function opposed to [`rdns()`](functions-rdns.html "rdns\(\)") provides: 

  * More reliable DNS resolution. 

  * Error warnings for failures. 

  * Returns all events and annotates all hosts that have been resolved within the timeout (whereas rdns() only returns a limited set of events). 

  * Allows for a longer timeout period. 




See [`reverseDns()`](functions-reversedns.html "reverseDns\(\)") for description of limitations. Mitigation example: `rdns(ip, as=hostname, limit=100)` Would be equivalent to: `tail(100) | reverseDns(ip, as=hostname, limit=100)` Note that the [`tail()`](functions-tail.html "tail\(\)") function handles the event collection that [`rdns()`](functions-rdns.html "rdns\(\)") previously performed internally. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-rdns.html#query-functions-rdns-as)|  string| optional[a] | `hostname`|  Specifies the field into which the resolved value is stored.   
[_`field`_](functions-rdns.html#query-functions-rdns-field)[b]| string| required |  |  Specifies the field to run the RDNS lookup against.   
[_`limit`_](functions-rdns.html#query-functions-rdns-limit)|  number| optional[[a]](functions-rdns.html#ftn.table-functions-rdns-optparamfn) | `RdnsDefaultLimit`|  Limits the number of resulting events in the RDNS request, controlled by the corresponding dynamic configurations.   
|  | **Maximum**| [`RdnsMaxLimit`](functions-rdns.html#query-functions-rdns-limit-max-rdnsmaxlimit)|   
[ _`server`_](functions-rdns.html#query-functions-rdns-server)|  string| optional[[a]](functions-rdns.html#ftn.table-functions-rdns-optparamfn) |  |  Specifies a DNS server address.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-rdns.html#query-functions-rdns-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-rdns.html#query-functions-rdns-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     rdns("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     rdns(field="value")
> 
> These examples show basic structure only.

### [`rdns()`](functions-rdns.html "rdns\(\)") Function Operation

  * If a lookup fails, it will keep the event but not add the given field. 

  * The number of resulting events from this function is limited by the dynamic configuration parameter [`RdnsMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-rdns_max_limit.html). If the number of events exceeds this limit, the result will be truncated with a warning. 

  * To prevent the [`rdns()`](functions-rdns.html "rdns\(\)") function from blocking query execution for an indeterminate amount of time, a timeout is applied to all RDNS requests. If an RDNS request doesn't return a result within the timeout, the lookup is considered to have failed for the associated event. However, if the request eventually returns, its result is added to an internal cache within LogScale for a period of time. 

Therefore, a static query using the [`rdns()`](functions-rdns.html "rdns\(\)") function may fail a lookup for an event on its first execution, but succeed in a subsequent execution. In live queries, this behaviour is less of a problem, as the [`rdns()`](functions-rdns.html "rdns\(\)") function will be evaluated continually. Thus, it is preferable to mainly use the [`rdns()`](functions-rdns.html "rdns\(\)") function in live queries. 

  * Reverse DNS can generally not be considered authoritative and should only be considered informational. The owner of an IP address can change it to point to an arbitrary hostname. 

  * For an authoritative alternative without the above limitations, consider using [`asn()`](functions-asn.html "asn\(\)") instead. 

  * If no RDNS server is specified then a system default is used. This can be overwritten via `server` to select a different default server. 




### [`rdns()`](functions-rdns.html "rdns\(\)") Function Usage

The default list of IP address ranges that are disallowed by `rns()` are listed below: 

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

  * The default list of IP address ranges that are disallowed by [`rdns()`](functions-rdns.html "rdns\(\)") are listed below: 

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

  * For self-hosted customers, the allowed IP addresses and servers that can be queried can be restricted by setting: 

    * [`IP_FILTER_RDNS`](https://library.humio.com/falcon-logscale-self-hosted/envar-ip_filter_rdns.html) – for filtering which IP addresses one may do reverse dns queries against. 

    * [`IP_FILTER_RDNS_SERVER`](https://library.humio.com/falcon-logscale-self-hosted/envar-ip_filter_rdns_server.html) – for filtering which DNS servers may be specified in the function. 




### [`rdns()`](functions-rdns.html "rdns\(\)") Syntax Examples

Resolve ipAddress (if present) using the server 8.8.8.8, and store the resulting DNS name in dnsName

logscale
    
    
    rdns(ipAddress, server="8.8.8.8", as=dnsName)

Resolve ipAddress (if present) and store the resulting DNS name in hostname

logscale
    
    
    rdns(ipAddress)
