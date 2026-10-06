Storefront's catalog-api and checkout-api store their data in MongoDB Atlas.
Their traces carry a child span for every database call (`db.system.name = mongodb`,
with the operation and collection). Atlas sends its own cluster metrics to Bronto,
which you can read with list_atlas_metrics and query_atlas_metrics. Atlas slow-query
log lines are in Bronto too, searchable like any other log.
