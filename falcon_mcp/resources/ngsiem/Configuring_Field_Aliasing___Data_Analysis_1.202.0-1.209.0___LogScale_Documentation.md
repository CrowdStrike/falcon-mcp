# Configuring Field Aliasing | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-field-aliasing-configure.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

/ [Field Aliasing](searching-data-field-aliasing.html)

### Configuring Field Aliasing

Configuration of field aliasing is a three-step configuration process comprising creation of a schema (step 1-3 in the procedure that follows), creation of field alias mapping (step 4-7), and activation of the schema (step 8-10). See [Field Aliasing](searching-data-field-aliasing.html "Field Aliasing") for an overview of this configuration process. 

  1. From your avatar icon  go to Organization Settings → under Field aliasing on the left navigation panel click Schemas and field aliasing. 

![screenshot showing how to access field aliasing feature](images/search-data/field-alias-select.png)  
---  
  
**Figure 116. Select field aliasing option**

  

  2. On the `Schemas and field aliasing` page, click Configure schemas and field aliasing and click \+ New schema. 

Option to import the schema from a YAML template: 

![Import schema from template](images/search-data/import-schema-template.png)  
---  
  
**Figure 117. Import schema from template**

  

  3. Provide a name for the new schema and click Next. Schema names have to be unique. 

  4. In the Define schema fields dialog box, enter aliases for your schema and add a description for each alias. Aliases are the names used as standard fields in your schema. 

You can add more fields to the schema by clicking \+ Add field. The maximum allowed number of fields in a schema is 1,000.

  5. After you are done entering the desired aliases and descriptions, click Confirm: the new schema has now been created, but it's empty and it's not applied to any views or repositories at this stage. 

![screenshot showing how to create field aliasing scherma](images/search-data/schema-fields.png)  
---  
  
**Figure 118. Define fields**

  

  6. Still in Configure schemas and field aliasing, select the newly created schema and click +Add alias. 

![screenshot showing how to add aliases](images/search-data/add-alias.png)  
---  
  
**Figure 119. Add aliases**

  

  7. Now you need to create the mapping. In the New field alias mapping dialog box, enter a name for the field mapping, then click Next. 

![screenshot showing how to create the field aliasing mapping](images/search-data/create-field-mapping.png)  
---  
  
**Figure 120. Create mapping**

  

  8. In the Alias into schema fields dialog popping up, do the matching: 

     * Specify the original, vendor field names that correspond to your schema fields. 

     * Enable the [Keep original field?](searching-data-field-aliasing-configure.html "Configuring Field Aliasing") checkbox if you want to keep the original field in the mapping (tickSelect all to keep all original fields in the mapping). If checked, the original field will still be searchable. If not checked, only the alias can be searched (original field is removed from results). See [Searching with Field Aliasing](searching-data-field-aliasing-search.html "Searching with Field Aliasing") for more information on this behavior. 

You can filter rows by vendor field, schema field or description when doing the mapping. Each mapping can have a maximum of 50 aliases configured.

Click Next. 

![screenshot showing how to match fields in mapping](images/search-data/field-matching-new.png)  
---  
  
**Figure 121. Match fields and aliases**

  


Refer to [Understanding Schema Requirements](searching-data-field-aliasing-schema-requirements.html "Understanding Schema Requirements") on how to create consistent schemas with valid mappings. 

### Note

You cannot install a field alias mapping that has no schema, field aliasing must always refer to a schema that you define. 

  9. The Set conditions for field aliasing to take effect dialog pops up: enter tag field names and tag field values in order to set at least one condition for your mapping; for example, you want field aliasing to apply when field #kind is equal to value `logs` or if field [#repo](searching-data-event-fields.html#searching-data-event-fields-tag-repo) is equal to value `github`. 

You can add more conditions by clicking \+ Add condition. 

Click Confirm: the alias mapping is created. 

![screenshot showing how to apply field aliasing conditions](images/search-data/set-conditions.png)  
---  
  
**Figure 122. Set conditions**

  


### Note

When setting the conditions for a mapping, tag field values **do not** accept glob patterns for the filtering (**`humio*`** for repository names, for instance). Only literal values are allowed. 

  10. Now you must activate the new schema. Click the Active schemas page and click Activate schema, then select your schema from the Select schema dialog, and click Next. 

![screenshot showing how to activate field aliasing schema](images/search-data/activate-schema.png)  
---  
  
**Figure 123. Activate schema**

  

  11. Select the scope for the schema — whether you want to: 

     * Apply to whole organization — this sets a general rule that would apply the schema to all repositories and views. 

     * Apply to a selection of repositories and views — the schema is associated with specific repositories or views that you select from those available; this choice will overwrite the organization level schema for the selected views, if one is applied. 

Click Next. 

![screenshot showing how to select field aliasing schema scope](images/search-data/select-scope.png)  
---  
  
**Figure 124. Select schema scope**

  

  12. If you choose to apply to a selection of repositories and views, select the relevant view/repo in the next dialog popping up, then click Confirm: 

![screenshot showing how to select view or repo scope](images/search-data/select-repo.png)  
---  
  
**Figure 125.**

  




Your schema is now ready and appears in the list of active schemas. This means that the fields aliased through the mapping you've done in [step 6](searching-data-field-aliasing-configure.html#searching-data-field-aliasing-configure-step6)) are now renamed in the [Fields panel](searching-data-displaying-fields.html "Display Fields") and ready to use as such in the [`Search`](searching-data.html "Search Data") page. See [Searching with Field Aliasing](searching-data-field-aliasing-search.html "Searching with Field Aliasing") for information on how field aliasing works during search.
