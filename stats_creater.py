from etl.spark.spark_session_helper import spark
from pyspark.sql import functions as f
from etl.commons.stats_helper import get_fantasy_points_udf

output_path = '/home/abhay/work/dream11/processed_output/training_rows'

t20_bowler_match_stats_df = spark.read.parquet("processed_output/t20_bowler_match_stats")\
    .withColumnRenamed("match_id", "bowler_match_id")\
    .withColumnRenamed("dt", "bowler_dt")\
    .withColumnRenamed("venue_name", "bowler_venue_name")
t20_batter_match_stats_df = spark.read.parquet("processed_output/t20_batter_match_stats")\
    .withColumnRenamed("match_id", "batter_match_id")\
    .withColumnRenamed("dt", "batter_dt")\
    .withColumnRenamed("venue_name", "batter_venue_name")

t20_fielder_match_stats_df = spark.read.parquet("processed_output/t20_fielder_match_stats")\
    .withColumnRenamed("match_id", "fielder_match_id")\
    .withColumnRenamed("dt", "fielder_dt")\

bat_bowl_df = t20_batter_match_stats_df \
    .join(t20_bowler_match_stats_df, 
          [
              t20_batter_match_stats_df.batter_id == t20_bowler_match_stats_df.bowler_id,
              t20_batter_match_stats_df.batter_match_id == t20_bowler_match_stats_df.bowler_match_id,
          ],
          how="full_outer"
    )\
    .withColumn("bat_bowl_player_id", f.coalesce(t20_batter_match_stats_df.batter_id,t20_bowler_match_stats_df.bowler_id))\
    .withColumn("bat_bowl_dt", f.coalesce(t20_batter_match_stats_df.batter_dt,t20_bowler_match_stats_df.bowler_dt))\
    .withColumn("bat_bowl_match_id", f.coalesce(t20_batter_match_stats_df.batter_match_id,t20_bowler_match_stats_df.bowler_match_id))\
    .withColumn("venue_name", f.coalesce(t20_batter_match_stats_df.batter_venue_name,t20_bowler_match_stats_df.bowler_venue_name))\
    .drop("bowler_match_id","bowler_dt","bowler_venue_name","batter_match_id","batter_dt","batter_venue_name", "batter_id", "bowler_id")

bat_bowl_field_df = bat_bowl_df \
    .join(t20_fielder_match_stats_df, 
          [
              bat_bowl_df.bat_bowl_player_id == t20_fielder_match_stats_df.wicket_fielder_id,
              bat_bowl_df.bat_bowl_match_id == t20_fielder_match_stats_df.fielder_match_id,
          ],
          how="full_outer"
    )\
    .withColumn("player_id", f.coalesce(bat_bowl_df.bat_bowl_player_id,t20_fielder_match_stats_df.wicket_fielder_id))\
    .withColumn("dt", f.coalesce(bat_bowl_df.bat_bowl_dt,t20_fielder_match_stats_df.fielder_dt))\
    .withColumn("match_id", f.coalesce(bat_bowl_df.bat_bowl_match_id,t20_fielder_match_stats_df.fielder_match_id))\
    .drop("fielder_match_id","fielder_dt","wicket_fielder_id","bat_bowl_player_id","bat_bowl_dt", "bat_bowl_match_id")

bat_bowl_field_df_with_points = bat_bowl_field_df\
    .withColumn(
        "fantasy_points",get_fantasy_points_udf(
            bat_bowl_field_df.batter_run_sum, bat_bowl_field_df.dismissals, bat_bowl_field_df.balls_faced,
            bat_bowl_field_df.boundary_count, bat_bowl_field_df.six_count,
            bat_bowl_field_df.total_run_sum, bat_bowl_field_df.wicket_sum, bat_bowl_field_df.deliveries, bat_bowl_field_df.maiden_count,
            bat_bowl_field_df.fielding_wicket_sum
        )
    ).na.fill(0)

bat_bowl_field_df_with_points.write.format("parquet").partitionBy(["dt", "match_id"]).mode("overwrite").save(output_path)

# fantasy points coming as Nan