# Column Properties | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-column-properties.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Column Properties

Fields in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") can be configured in the Format event list panel (see [Figure 80, “Format Event List”](searching-data-add-remove-fields.html#figure_searching-data-add-remove-fields2 "Figure 80. Format Event List")). You can set the following column properties: 

  * Type options are: 

    * Field is the name of the field as it comes from the events. 

    * Field as link is used with fields that contain URLs to display clickable links. 

    * Custom link creates arbitrary links based on the contents of an event. Instead of just providing a field name, and using its content as the link, you write link templates, and use field interpolation to fill out the template. 

To use field interpolation, write two sets of curly braces (one nested in the other), and write fields **`["nameOfField"]`** inside, like this: **`https://internal-tool/customers/{{fields["customerId"]}}`**. This creates a unique link for every value of **`customerId`**. 

The same mechanism can also be used to generate the text for the link, if you would like a different text than the raw URL to show as the link. 

![Adding a New Custom Link Column](images/search-data/custom-link.png)  
---  
  
**Figure 91. Adding a New Custom Link Column**

  

    * Field list is used to format all fields in an event as a list of key-value pairs. Enable the Group fields by prefix checkbox to organize data that share a prefix into a tree-structure. A prefix is any string followed by a dot in the field name, as `actor` in actor.ip and actor.organizationId, for instance. 

![Group fields by prefix option](images/search-data/field-list.png)  
---  
  
**Figure 92. Group fields by prefix option**

  


In the following example, all fields prefixed with `actor.` and `user.` are grouped in a tree that can be expanded or collapsed. 

![Field List grouped by prefix](images/search-data/field-list-tree.png)  
---  
  
**Figure 93. Field List grouped by prefix**

  


  * Header is the custom field name you want to see displayed in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events"). 

  * Open link in new browser tab checkbox controls that the link is opened in new browser tab. 

  * Show as controls whether the link should be displayed as a link or a button.
