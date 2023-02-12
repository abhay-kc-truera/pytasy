from pyspark.sql.functions import sum, col, trunc
from common_requirements import t20_df_with_boundaries

output_path = '/home/abhay/work/dream11/processed_output/t20_fielder_month_stats'

fielder_relevant_dimensions = ["dt","wicket_fielder_id", "wicket_fielder_name", "bowler_name", "bowler_id"] 
fielder_relevant_metrics = ["is_dismissed"]

t20_batter_fielder_df = t20_df_with_boundaries\
    .select(fielder_relevant_dimensions+fielder_relevant_metrics) \
    .filter(col("wicket_fielder_id").isNotNull()) \
    .withColumn("dt", trunc("dt", "month"))

t20_batter_fielder_df_per_month = t20_batter_fielder_df.groupBy(fielder_relevant_dimensions) \
    .agg(
        sum("is_dismissed").alias("wicket_sum")
    )

t20_batter_fielder_df_per_month.write.format("parquet").partitionBy(["dt"]).mode("overwrite").save(output_path)

