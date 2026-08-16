;WITH iran_matches AS (SELECT match_id FROM team_appearances
WHERE team_id = 'T-38'),
iran_goals_tagged AS (SELECT
CASE WHEN g.team_id = 'T-38' THEN 'scored' ELSE 'conceded' END  goal_type,
CASE WHEN g.minute_regulation BETWEEN 1 AND 15 THEN '01: 1-15'
WHEN g.minute_regulation BETWEEN 16 AND 30 THEN '02: 16-30'
WHEN g.minute_regulation BETWEEN 31 AND 45 THEN '03: 31-45'
WHEN g.minute_regulation BETWEEN 46 AND 60 THEN '04: 46-60'
WHEN g.minute_regulation BETWEEN 61 AND 75 THEN '05: 61-75'
WHEN g.minute_regulation BETWEEN 76 AND 90 THEN '06: 76-90' ELSE '07: Extra Time' END AS time_interval
FROM goals g
JOIN iran_matches im ON g.match_id = im.match_id)
SELECT time_interval,SUM(CASE WHEN goal_type = 'scored' THEN 1 ELSE 0 END)  goals_scored,
SUM(CASE WHEN goal_type = 'conceded' THEN 1 ELSE 0 END)  goals_conceded
FROM iran_goals_tagged
GROUP BY time_interval
ORDER BY time_interval;