# Pytasy

Pytasy is an expeirmental project meant to aggregate player stats and predict fantasy cricket league performances (rather unsuccessfully, don't sue me if you loose money because of this).

## Data Source
Download raw data from : https://cricsheet.org/matches/

## How to train the model
1. create and activate a new conda/virtual env
2. install all deps in the env from requirements.txt
3. set use JAVA8 in JAVA_HOME
4. run : `python model_workflow.py`

## How to predict fantasy points for a given dt, venue and set of players
1. Activate the env used while model training
2. In InferenceFeaturePrep.ipynb notebook , replace player last names
3. Run the InferenceFeaturePrep.ipynb notebook in jupyter

## High Level flow:
1. Download data zip, each match is represented as a single json file in unzipped folder.
2. Read all match json files and flatten relevant data into parquet files where each row represents a single delivery.
    
    a. Capture delivery info like batter, bowler, runs, wickets and relevant fielder
    
    b. Capture match info, like teams, venue, dt, match_id

3. Aggregate batter, bowler and fielder stats into 3 different parquent locations.
    
    a. dimensions are agggregate on dt intervals 30days, 90days, 300days, 1000days
    
    b. there is an additional dimension for 1000days_venue to capture stats for last 1000 days at the venue

4. Aggregates are combined into training rows such that each row represents stats by match,player,dt dimensions and also historical stats.
    
    a. stats like runs_scored, runs_conceeded, wickets_taken etc in the match are used to calculate the actual_fantasy_points attributed to a player (based on dream11 fantasy system).

    b. stats like runs_scored_1000D, wickets_taken_30D are used as input features in a model in next step.

5. Model Training
    a. used pyspark GBTRegressor to predict the overall fantasy points based on historical stats for a player upto a match_id.

    b. feature list: check features list in `model_trainer`

6. Although regression model predicted_fantasy_points help us in deciding a team but the in terms of fantasy cricket, we need to answer 2 major questions:
    
    a. What 11 players should be included in the team?
    
    b. What would be the two players, this would be used to set captain and vice-captain.

    c. So it is possible for regression model to error prone but be directly correct when you compare scores of all players playing a rank, thus it was import to evluate the model both in regression metric and also on ranking metrics.


## Extensions
1. Connect this model to an explianability tool to get feature importances.
    
    i. this is one of the reasons I am not sure if using gender as a feature has an impact

2. Figure out a ways to compute batter_vs_bowler stats efficiently for both time and venue dimensions.

