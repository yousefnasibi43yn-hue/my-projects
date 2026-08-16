;WITH iran_matches AS ( SELECT t.year, m.match_name, m.stage_name,ta.goals_for,ta.goals_against,ta.goal_differential,
CASE WHEN ta.win = 1 THEN 3 WHEN ta.draw = 1 THEN 1 ELSE 0 END  points
FROM team_appearances ta
JOIN matches m ON ta.match_id = m.match_id
JOIN tournaments t ON ta.tournament_id = t.tournament_id
WHERE ta.team_id = 'T-38')
SELECT year, match_name, stage_name,goals_for,goals_against,goal_differential,points,
ABS(goal_differential) + points impact_score,
DENSE_RANK() OVER (ORDER BY ABS(goal_differential) + points DESC) importance_rank
FROM iran_matches
ORDER BY importance_rank;