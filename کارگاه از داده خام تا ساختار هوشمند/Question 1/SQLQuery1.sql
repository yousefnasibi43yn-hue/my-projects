;with iran_wordcup AS (
select t.team_name,ts.year,sum(ta.goals_for) scored,SUM(ta.goals_against) ga_conceded,sum(ta.goals_for) - SUM(ta.goals_against) 'difference',
SUM(case WHEN ta.win = 1 then 3 when ta.draw = 1 then 1 ELSE 0 end) points
from team_appearances ta
join teams t on t.team_id=ta.team_id
join tournaments ts on ts.tournament_id=ta.tournament_id
where t.team_name = 'Iran'
group by ts.year,t.team_name)
select *,row_number() over(order by points desc, difference desc, scored desc)  rn
from iran_wordcup;