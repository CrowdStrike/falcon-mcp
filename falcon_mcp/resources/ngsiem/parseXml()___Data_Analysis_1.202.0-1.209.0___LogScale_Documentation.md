# parseXml() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsexml.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseXml()`](functions-parsexml.html "parseXml\(\)")

Parse data as XML. Specify `field=@rawstring` to parse the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) into XML. If the specified field does not exist, the event is skipped. If the specified field exists but contains non-XML data, the behaviors depends on the strict parameter. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-parsexml.html#query-functions-parsexml-field)[a]| string| required | `@rawstring`|  Field that should be parsed as XML.   
[_`prefix`_](functions-parsexml.html#query-functions-parsexml-prefix)|  string| optional[b] |  |  Prefix the name of the fields extracted from XML with the value of this parameter.   
[_`strict`_](functions-parsexml.html#query-functions-parsexml-strict)|  boolean| optional[[b]](functions-parsexml.html#ftn.table-functions-parsexml-optparamfn) | [`false`](functions-parsexml.html#query-functions-parsexml-strict-option-false)|  Specifies if events where the field does not contain valid XML should be filtered out of the result set.   
|  |  | **Values**  
|  |  | [`false`](functions-parsexml.html#query-functions-parsexml-strict-option-false)| All events are passed, including an error flag describing why the event parsing failed  
|  |  | [`true`](functions-parsexml.html#query-functions-parsexml-strict-option-true)| Events that do not contain valid XML will be filtered in the result set  
[a] The parameter name [_`field`_](functions-parsexml.html#query-functions-parsexml-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parsexml.html#query-functions-parsexml-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseXml("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseXml(field="value")
> 
> These examples show basic structure only.

### [`parseXml()`](functions-parsexml.html "parseXml\(\)") Syntax Examples

If the whole event sent to LogScale is XML like this: 

xml
    
    
    <log><service>userService</service><timestamp>2017-12-18T20:39:35Z</timestamp><msg>user with id=47 logged in</msg></log>

logscale
    
    
    parseXml()
    | parseTimestamp(field=timestamp)

If a field in the incoming event contains XML like this: 

xml
    
    
    2017-12-18T20:39:35Z user id=47 logged in details="<log><service>userService</service><timestamp>2017-12-18T20:39:35Z</timestamp><msg>user with id=47 logged in</msg></log>"\n\n

In the example below, the details field is extracted using the [`kvParse()`](functions-kvparse.html "kvParse\(\)") function and then [`parseXml()`](functions-parsexml.html "parseXml\(\)") is used to parse the XML inside the details field. 

logscale
    
    
    /(?<timestamp>\S+)/
    | parseTimestamp(field=timestamp)
    | kvParse()
    | parseXml(field=details)

### [`parseXml()`](functions-parsexml.html "parseXml\(\)") Examples

Click + next to an example below to get the full details.

#### Parse XML Content From Task Triggers

**Extract and analyze XML data from scheduled tasks using the[`parseXml()`](functions-parsexml.html "parseXml\(\)") function **

##### Query

logscale
    
    
    #event_simpleName=ScheduledTaskRegistered
    | parseXml(TaskXml)
    | Trigger:=rename(Task.Triggers.LogonTrigger.Enabled)
    | Trigger=*
    | table([aid, Trigger, TaskXml], limit=1000)

##### Introduction

In this example, the [`parseXml()`](functions-parsexml.html "parseXml\(\)") function is used to extract trigger information from scheduled task XML data. 

Example incoming data might look like this: 

@timestamp| aid| event_simpleName| TaskXml  
---|---|---|---  
2025-10-15T10:00:00Z| aid123| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
2025-10-15T10:01:00Z| aid124| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>  
2025-10-15T10:02:00Z| aid125| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
2025-10-15T10:03:00Z| aid126| ScheduledTaskRegistered| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #event_simpleName=ScheduledTaskRegistered

Filters events where event_simpleName equals `ScheduledTaskRegistered`. 

  3. logscale
         
         | parseXml(TaskXml)

Parses the XML content from the TaskXml field. The function creates a structured object with the parsed XML data, making nested elements accessible using dot notation. 

  4. logscale
         
         | Trigger:=rename(Task.Triggers.LogonTrigger.Enabled)

Creates a new field named Trigger containing the value from the parsed XML path Task.Triggers.LogonTrigger.Enabled. 

  5. logscale
         
         | Trigger=*

Filters to keep only events where Trigger has a value. This line can be removed if empty trigger values should be included in the results. 

  6. logscale
         
         | table([aid, Trigger, TaskXml], limit=1000)

Creates a table showing the aid, Trigger, and original TaskXml fields, limited to 1000 rows. 

  7. Event Result set.




##### Summary and Results

The query is used to extract and analyze trigger settings from scheduled task XML data. 

This query is useful, for example, to monitor and audit scheduled task configurations and identify tasks with specific trigger settings. 

Sample output from the incoming example data: 

aid| Trigger| TaskXml  
---|---|---  
aid123| true| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
aid124| false| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>  
aid125| true| <Task><Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers></Task>  
aid126| false| <Task><Triggers><LogonTrigger><Enabled>false</Enabled></LogonTrigger></Triggers></Task>
