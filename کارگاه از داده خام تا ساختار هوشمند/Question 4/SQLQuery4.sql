;WITH group_performance AS (SELECT gs.team_id, gs.tournament_id,gs.points,gs.goal_difference,gs.goals_for,gs.goals_against,gs.advanced
FROM group_standings gs
JOIN tournaments t ON gs.tournament_id = t.tournament_id
WHERE gs.team_id IN ('T-38', 'T-44', 'T-71')
AND t.tournament_name NOT LIKE '%Women%')
SELECT tm.team_name,
COUNT(gp.tournament_id) AS tournaments_played,
SUM(CASE WHEN gp.advanced = 1 THEN 1 ELSE 0 END) times_advanced,
AVG(gp.points) AS avg_points,
AVG(gp.goal_difference)  avg_goal_diff,
SUM(gp.goals_for) total_goals_for,
SUM(gp.goals_against) total_goals_against
FROM group_performance gp
JOIN teams tm ON gp.team_id = tm.team_id
GROUP BY tm.team_name
ORDER BY times_advanced DESC, avg_points DESC;