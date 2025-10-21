# User Parameters (Variables) | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-fields-user-input.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## User Parameters (Variables)

The documentation explains how to implement user-configurable parameters in LogScale queries, allowing dynamic value substitution through user input rather than fixed values. Parameters can be created using a question mark prefix, support default values for automated contexts like triggers and scheduled searches, and offer special syntax for handling multi-value inputs in dashboard implementations. 

User-configurable parameters can be added to a query to allow for the user to specify a value in place of a fixed value within the query. The user-configurable value can also be integrated with dashboards and saved searches. 

To create a user-supplied parameter, use the **`?`** character in front of the parameter name. For example: **`?parameter`**. The expression can be embedded in the query and will be interpreted by dashboards and saved searches automatically, providing a prompt for user-input: 

logscale
    
    
    matchstring := ?searchtext

In the above example, the named parameter will be searchtext. 

For information on using parameters when using Dashboards, see [???](). 

For information on using parameters with saved searches, see [User Functions (Saved Searches)](syntax-function.html#syntax-function-user "User Functions \(Saved Searches\)"). 

### Default Parameter Values

For queries that execute in a automated context, for example [Triggers](automated-alerts.html "Triggers") or [Scheduled searches](automated-alerts.html#trigger_types-scheduled-searches), a default value to a parameter can be defined to ensure that the parameter has a value and the query does not fail. 

To specify a default value, use the following syntax in your query: 

logscale
    
    
    ?{param=default_value}

### Multi-Value Parameters Syntax for Dashboards

When using [???]() in dashboards, multiple values can be added at the same time by using commas as a delimiter for user-inputs in the UI. To add multi-value parameters to your query for a dashboard, use the syntax as in the following examples: 

User Input |  Parameter Value Options   
---|---  
**`cat, hat`** |  `cat` and `hat`  
**`"cat, hat"`** |  `cat, hat`  
**`\"cat, hat\"`** |  `"cat` and `hat"`  
**`\"cat\", \"hat\"`** |  `"cat"` and `"hat"`
