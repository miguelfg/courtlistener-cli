# CourtListener Data Models and Schemas

**Source:** [](docs/raw/wiki.free.law/c/courtlistener/help/api/rest/v4/courtlistener-data-models-and-schemas.html)

---

CourtListener Data Models and Schemas The two images below show how the APIs and replicated database are organized. The first image shows the models we use for people, and the second shows the models we use for case law, PACER data, and related columns. You can see that these models currently link together on the Docket, Person, and Court tables. A complete version of the schema is also available. These models are exported from the CourtListener code base and may not always be the most up to date. To go beyond these images, you can read model.py files in the CourtListener code.