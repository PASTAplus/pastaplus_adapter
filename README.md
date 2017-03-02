# PASTAplus Adapter

The PASTAplus Adapter (adapter, here after) is a DataONE slender node bridge between the DataONE Generic Member Node (GMN) and the PASTAplus data repository. The adapter itself operates in two phases: the first phase polls PASTA for recent additions, updates, or deletions of data packages in the reopsitory -- this information is written to a common data queue in the form of data package identifier and an event timestamp; the second phase of the adapter reads the queue for new event information and performs a create, update, or deletion (archive) of all objects associated with each data package.

![image of sequence diagram](https://www.planttext.com/plantuml/img/RP4zRiCm38Ltda9ZCiG7q60aKwOM0T9TO6J65IfBYam3pUr3vyUruau2oCVlFOhRdZ7pq7a02kpugWwxuzSEabITTGa3gnIzDnq6R2b3WumdxEbHlGmqK2b6-oF2IV-axZy-0UQWJNqtqgebDfciw8pznj1Ilrh3lRUfvmDQbIhpEuRsCIRnp3sjbktrc-DVP3tbTE4S9MG3K5NLa-UOCl8xKMZbRYKm4pQce2xaiurVFHkx58EuZ5il-ML1gzFW_EJotuJyirRZZLwYnswmbKUkV0C0)
