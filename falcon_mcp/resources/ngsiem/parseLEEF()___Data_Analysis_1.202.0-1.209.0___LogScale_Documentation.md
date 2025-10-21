# parseLEEF() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parseleef.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseLEEF()`](functions-parseleef.html "parseLEEF\(\)")

Parse Log Event Extended Format (LEEF) encoded message. Only LEEF versions 1.0 and 2.0 are supported. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`delimiter`_](functions-parseleef.html#query-functions-parseleef-delimiter)|  string| optional[a] |  |  Delimiter to use when parsing the extension fields of a LEEF:1.0 message. When processing LEEF:2.0 messages this argument is ignored as the value is specified in a message header. The value must be a single character with unicode value in the range `0x0000-0xffff`.   
[_`field`_](functions-parseleef.html#query-functions-parseleef-field)[b]| string| optional[[a]](functions-parseleef.html#ftn.table-functions-parseleef-optparamfn) | `@rawstring`|  Field that holds the input in LEEF form.   
[_`headerprefix`_](functions-parseleef.html#query-functions-parseleef-headerprefix)|  string| optional[[a]](functions-parseleef.html#ftn.table-functions-parseleef-optparamfn) | `leef.`|  Prefix to the field names for the header fields.   
[_`keeplabels`_](functions-parseleef.html#query-functions-parseleef-keeplabels)|  boolean| optional[[a]](functions-parseleef.html#ftn.table-functions-parseleef-optparamfn) | `false`|  Keep short form label fields (LEEF:1.0 only), which is interpreted as CEF.   
[_`labelprefix`_](functions-parseleef.html#query-functions-parseleef-labelprefix)|  string| optional[[a]](functions-parseleef.html#ftn.table-functions-parseleef-optparamfn) | `leef.label`|  Prefix to extension fields with labels (LEEF:1.0 only), which is interpreted as CEF.   
[_`parsetime`_](functions-parseleef.html#query-functions-parseleef-parsetime)|  boolean| optional[[a]](functions-parseleef.html#ftn.table-functions-parseleef-optparamfn) | [`true`](functions-parseleef.html#query-functions-parseleef-parsetime-option-true)|  Control if the devTime extension field should be parsed. Setting this to false can be used to disable the time parsing step.   
|  |  | **Values**  
|  |  | [`false`](functions-parseleef.html#query-functions-parseleef-parsetime-option-false)| Disables parsing of the devTime field  
|  |  | [`true`](functions-parseleef.html#query-functions-parseleef-parsetime-option-true)| Enables parsing of the devTime field  
[ _`prefix`_](functions-parseleef.html#query-functions-parseleef-prefix)|  string| optional[[a]](functions-parseleef.html#ftn.table-functions-parseleef-optparamfn) | `leef.ext.`|  Prefix to extension fields. Fields in the LEEF extension part are prefixed with this.   
[_`timezone`_](functions-parseleef.html#query-functions-parseleef-timezone)|  string| optional[[a]](functions-parseleef.html#ftn.table-functions-parseleef-optparamfn) | `Z`|  Time zone to use if none specified in `devTimeFormat` string. See the full list of timezones supported by LogScale at [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones").   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-parseleef.html#query-functions-parseleef-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parseleef.html#query-functions-parseleef-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseLEEF("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseLEEF(field="value")
> 
> These examples show basic structure only.

### [`parseLEEF()`](functions-parseleef.html "parseLEEF\(\)") Function Operation

This function will skip any prefix up to the marker `LEEF:1.0|` or `LEEF:2.0|`. So even though LEEF messages are typically delivered via Syslog, the Syslog part of the message has to be parsed separately. 

If the LEEF message contains a devTime (and optionally `devTimeFormat`) this function will extract the time stamp from there and assign it to [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp). 

Use the (unnamed) field parameter to specify which field should be parsed. Specify [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) to parse the rawstring. You can use the parameter prefix to specify an alternative to leef.ext. as prefix for the extension fields. 

You may want to review the [Specifications for LEEF](https://www.ibm.com/support/knowledgecenter/SS42VS_DSM/com.ibm.dsm.doc/b_Leef_format_guide.pdf). For legacy support, a LEEF:0| is parsed as LEEF:1.0 headers, with CEF:0-style body. In general the implementation is more permissive than the spec to allow for common mistakes in log writers. 

### [`parseLEEF()`](functions-parseleef.html "parseLEEF\(\)") Syntax Examples

  * From a log line like this: 

Raw Events

&lt;13&gt;1 2019-01-18T11:07:53.520Z 192.168.1.1 LEEF:2.0  
---  
| Lancope  
| StealthWatch  
| 1.0  
| 41  
| ^  
| src=10.0.0.1^act=blocked an X^dst=1.1.1.1  
  
Parse the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field to show how the LEEF format is parsed with the default field names: 

logscale
        
        parseLEEF(field=@rawstring)

Field |  Value   
---|---  
leef.version |  `2.0`  
leef.device.vendor |  `Lanscope`  
leef.device.product |  `StealthWatch`  
leef.device.version |  `1.0`  
leef.event_id |  ` 41`  
leef.ext.src |  `10.0.0.1`  
leef.ext.act |  `"blocked an X"`  
leef.ext.dst |  `1.1.1.1`  
  
  * From a log line like this: 
        
        LEEF:2.0|Palo Alto Networks|LF|2.0|THREAT| |TimeReceived=2016-01-01T00:00:58.000000Z DeviceSN=123456789123 EventID=THREAT cat= ConfigVersion=9.1

    * Show how the LEEF format is parsed with changed header prefix: 

logscale
          
          parseLEEF(headerprefix="leef.header.")

This will add the following fields to the event: 

Field |  Value   
---|---  
leef.header.version |  `2.0`  
leef.header.device.vendor |  `Palo Alto Networks`  
leef.header.device.product |  `LF`  
leef.header.device.version |  `2.0`  
leef.ext.DeviceSN |  `123456789123`  
leef.ext.EventID |  `THREAT`  
leef.ext.TimeReceived |  `2016-01-01T00:00:58.000000Z`  
leef.ext.cat |  `""`  
leef.ext.ConfigVersion |  `9.1`  
  
    * Show how the LEEF format is parsed with changed extension prefix: 

logscale
          
          parseLEEF(prefix="my.prefix.")

The output will produce the following: 

Field |  Value   
---|---  
leef.version |  `2.0`  
leef.event_id |  `THREAT`  
leef.device.vendor |  `Palo Alto Networks`  
leef.device.product |  `2LF`  
leef.device.version |  `2.0`  
my.prefix.DeviceSN |  `2123456789123`  
my.prefix.EventID |  `THREAT`  
my.prefix.TimeReceived |  `2016-01-01T00:00:58.000000Z`  
my.prefix.cat |  `""`  
my.prefix.ConfigVersion |  `9.1`
