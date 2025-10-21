# Managing Field Aliasing | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-field-aliasing-manage.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

/ [Field Aliasing](searching-data-field-aliasing.html)

### Managing Field Aliasing

It is possible to manage existing schemas as well as existing field mappings. For example, you can delete and edit schemas and field mappings, create new field alias mappings, change scope of schema, rename vendor field names and make changes to conditions. 

  1. From your avatar icon  go to Organization Settings → under Field aliasing on the left navigation panel click Schemas and field aliasing (see [Figure 116, “Select field aliasing option”](searching-data-field-aliasing-configure.html#figure_searching-data-field-aliasing-configure1 "Figure 116. Select field aliasing option")). 

  2. On the `Schemas and field aliasing` page, select the Configure schemas and field aliasing tab and click an existing schema to perform these operations: 

     * Delete deletes the schema. 

     * Edit allows renaming the schema or the existing fields, as well as adding new fields to the schema. 

     * \+ Add alias creates new field alias mappings associated with the schema. 

     * Apply schema allows selecting the scope of your schema. 

     * Export allows exporting the schema as a YAML template. 

![Screenshot showing the options for managing an existing schema](images/search-data/manage-schema-new.png)  
---  
  
**Figure 126. Manage an Existing Schema**

  

  3. Select a specific mapping under a schema to perform these actions: 

     * Delete deletes the mapping from the schema it belongs to. 

     * Edit allows you to: 

       * Rename the mapping. 

       * Rename the vendor field names associated with the schema fields. 

       * Edit the existing conditions/set a different condition to take effect in the mapping. 

![Manage an Existing Field Mapping](images/search-data/manage-mappings.png)  
---  
  
**Figure 127. Manage an Existing Field Mapping**
