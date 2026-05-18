# Is there a schema for the replicated database?

**Source:** [](docs/raw/wiki.free.law/c/courtlistener/help/api/rest/faqs/is-there-a-schema-for-the-replicated-database.html)

---

Is there a schema for the replicated database? Yes. You can find the schema in the API documentation. The images on that page are updated on a somewhat regular basis. To learn more about the field definitions you have two choices: Use the API — The API is self-documenting, and you can make an HTTP OPTIONS request to any endpoint to get a list of field definitions. For example:curl -X OPTIONS 'https://www.courtlistener.com/api/rest/v4/opinions/' That will return a JSON object with the field definitions. Read the Source — If you want to go further, or to see fields that are not defined or available via the API, you can simply read the source code itself. CourtListener is a Django project, which use models.py files to define database schemas. Look for those files witin the Courtlistener source code, and you will find the full information about each table, column, index, etc.