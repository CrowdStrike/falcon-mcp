# parseCEF() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsecef.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Sep 26, 2023

## [`parseCEF()`](functions-parsecef.html "parseCEF\(\)")

Parse Common Event Format (CEF) encoded messages. Only CEF version 0 is supported. This function will skip any prefix up to the marker `CEF:0`. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-parsecef.html#query-functions-parsecef-field)[a]| string| optional[b] | `@rawstring`|  Field that holds the input in CEF form. This parameter specifies which field should be parsed. The default value parses the rawstring.   
[_`headerprefix`_](functions-parsecef.html#query-functions-parsecef-headerprefix)|  string| optional[[b]](functions-parsecef.html#ftn.table-functions-parsecef-optparamfn) | `cef.`|  Prefix to the field names for the header fields.   
[_`keeplabels`_](functions-parsecef.html#query-functions-parsecef-keeplabels)|  boolean| optional[[b]](functions-parsecef.html#ftn.table-functions-parsecef-optparamfn) | `false`|  Removes fields ending with label along with any field that has the same name, for example, cef.ext.csLabel and cef.ext.cs.   
[_`labelprefix`_](functions-parsecef.html#query-functions-parsecef-labelprefix)|  string| optional[[b]](functions-parsecef.html#ftn.table-functions-parsecef-optparamfn) | `cef.label.`|  Prefix to the field names for the label fields.   
[_`prefix`_](functions-parsecef.html#query-functions-parsecef-prefix)|  string| optional[[b]](functions-parsecef.html#ftn.table-functions-parsecef-optparamfn) | `cef.ext.`|  Prefix to extension fields. Fields in the CEF extension part are prefixed with this.   
[a] The parameter name [_`field`_](functions-parsecef.html#query-functions-parsecef-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parsecef.html#query-functions-parsecef-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseCEF("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseCEF(field="value")
> 
> These examples show basic structure only.

You may want to review the specification for CEF: [ArcSight CEF Spec](https://www.microfocus.com/documentation/arcsight/arcsight-smartconnectors-8.3/cef-implementation-standard/#CEF/AS_smartconn_Intro.htm). For compatibility with legacy systems, this implementation allows the tab character (ascii `0x09`) in addition to space (ascii `0x20`) as separator for key value pairs in the extensions section. Literal backslash followed by **t** (as in `\t`) is not a separator, but re-interpreted line `\n` and `\r` in the specification. 

### [`parseCEF()`](functions-parsecef.html "parseCEF\(\)") Syntax Examples

  * From a log line like this: 

syslog
        
        Sep 19 08:26:10 host CEF:0 | security| threatmanager| 1.0| 100| detected a \\ in packet| 10| src=10.0.0.1 act=blocked a \\ dst=1.1.1.1

CEF parse the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field to show how the CEF format is parsed with the default field names: 

logscale
        
        parseCEF(field=@rawstring)

The following fields will be added to the event: 

Field |  Value   
---|---  
cef.version |  `0`  
cef.device.vendor |  `security`  
cef.device.product |  `threatmanager`  
cef.device.version |  `1.0`  
cef.event_class_id |  `100`  
cef.name |  `"detected a \\ in packet"`  
cef.severity |  `10`  
cef.ext.src |  `10.0.0.1`  
cef.ext.act |  `"blocked a \\"`  
cef.ext.dst |  `1.1.1.1`  
  
  * From a log line like this: 
        
        CEF:0|Incapsula|SIEMintegration|1|1|Illegal Resource Access|3| fileid=3412341160002518171 sourceServiceName=site123.abcd.info siteid=1509732 suid=50005477 requestClientApplication=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0 deviceFacility=mia cs2=true cs2Label=Javascript Support start=14532901213

    * Show the output of [`parseCEF()`](functions-parsecef.html "parseCEF\(\)") with changed header prefix: 

logscale
          
          parseCEF(headerprefix="new.header.")

This will add the following fields to the event: 

Field |  Value   
---|---  
new.header.device.version |  `1`  
new.header.device.vendor |  `Incapsula`  
new.header.event_class_id |  `1`  
new.header.device.product |  `SIEMintegration`  
new.header.name |  `Illegal Resource Access`  
new.header.version |  `0`  
new.header.severity |  `3`  
cef.label.Javascript Support |  `"true"`  
cef.ext.requestClientApplication |  `"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"`  
cef.ext.siteid |  `1509732`  
cef.ext.sourceServiceName |  `"site123.abcd.info"`  
cef.ext.fileid |  `3412341160002518171`  
cef.ext.suid |  `50005477`  
cef.ext.start |  `14532901213`  
cef.ext.deviceFacility |  `mia`  
  
    * Show the output of [`parseCEF()`](functions-parsecef.html "parseCEF\(\)") with changed label prefix: 

logscale
          
          parseCEF(labelprefix="new.label.")

This will add the following fields to the event: 

Field |  Value   
---|---  
cef.device.version |  `1`  
cef.device.vendor |  `Incapsula`  
cef.event_class_id |  `1`  
cef.device.product |  `SIEMintegration`  
cef.name |  `Illegal Resource Access`  
cef.version |  `0`  
cef.severity |  `3`  
new.label.Javascript Support |  `"true"`  
cef.ext.requestClientApplication |  `"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"`  
cef.ext.siteid |  `1509732`  
cef.ext.sourceServiceName |  `"site123.abcd.info"`  
cef.ext.fileid |  `3412341160002518171`  
cef.ext.suid |  `50005477`  
cef.ext.start |  `14532901213`  
cef.ext.deviceFacility |  `mia`  
  
    * Show the output of [`parseCEF()`](functions-parsecef.html "parseCEF\(\)") with changed extension prefix: 

logscale
          
          parseCEF(prefix="content.")

This will add the following fields to the event: 

Field |  Value   
---|---  
cef.device.version |  `1`  
cef.device.vendor |  `Incapsula`  
cef.event_class_id |  `1`  
cef.device.product |  `SIEMintegration`  
cef.name |  `Illegal Resource Access`  
cef.version |  `0`  
cef.severity |  `3`  
cef.label.Javascript Support |  `"true"`  
content.requestClientApplication |  `"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"`  
content.siteid |  `1509732`  
content.sourceServiceName |  `"site123.abcd.info"`  
content.fileid |  `3412341160002518171`  
content.suid |  `50005477`  
content.start |  `14532901213`  
content.deviceFacility |  `mia`
