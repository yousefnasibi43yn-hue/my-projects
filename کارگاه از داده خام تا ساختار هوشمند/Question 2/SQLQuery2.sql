;WITH iran_groups AS (SELECT tournament_id, stage_name, group_name FROM  group_standings
WHERE team_id = 'T-38'),
group_with_iran AS ( SELECT gs.tournament_id,gs.team_id,gs.points,gs.goal_difference FROM group_standings gs
JOIN iran_groups ig ON gs.tournament_id = ig.tournament_id
AND gs.stage_name = ig.stage_name
AND gs.group_name = ig.group_name
WHERE gs.team_id <> 'T-38')
SELECT tn.tournament_name,AVG(gi.points)  avg_points_iran_group,
AVG(gi.goal_difference)  avg_goal_diff_iran_group,
(SELECT AVG(gs2.points) FROM group_standings gs2
WHERE gs2.tournament_id = gi.tournament_id
AND gs2.team_id <> 'T-38'
AND NOT EXISTS (SELECT 1 FROM iran_groups ig2
WHERE ig2.tournament_id = gs2.tournament_id
AND ig2.stage_name = gs2.stage_name
AND ig2.group_name = gs2.group_name)) avg_points_other_group
FROM group_with_iran gi
JOIN tournaments tn ON gi.tournament_id = tn.tournament_id
GROUP BY tn.tournament_name, gi.tournament_id
ORDER BY gi.tournament_id;