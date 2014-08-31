DELIMITER //
DROP PROCEDURE IF EXISTS percentile_availability//
CREATE PROCEDURE percentile_availability(IN nodeisp INT,IN sttime INT,IN etime INT,IN percent INT)
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE minsize  INT DEFAULT 0;
DECLARE maxsize INT DEFAULT 0;
DECLARE perlimit  INT DEFAULT 0;
SELECT COUNT(*) INTO cnt FROM (select c.duration as con,IFNULL(d.duration,0) as don ,IFNULL(n.duration,0) as nos from ((select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id=nodeisp and reason in ("connected") and starttime between sttime AND etime   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as c LEFT JOIN ( select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id=nodeisp and reason in ("nosignal") and starttime between sttime AND etime   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as n ON c.day=n.day) LEFT JOIN (select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id=nodeisp and reason in ("nocarrier","manual","freeze","removed") and starttime between sttime AND etime   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as d ON c.day=d.day where (c.duration <=86400) and (n.duration is NULL or d.duration is NULL or c.duration + n.duration <= 86400 )) as a where ((a.con/(86400-greatest(a.don,a.nos))) * 100) <=100 ;
SET perlimit = percent * cnt;
SET perlimit = perlimit / 100;
SELECT nodeisp,((a.con/(86400-greatest(a.don,a.nos))) * 100) as avail FROM (select c.duration as con,IFNULL(d.duration,0) as don ,IFNULL(n.duration,0) as nos from ((select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id=nodeisp and reason in ("connected") and starttime between sttime AND etime   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as c LEFT JOIN ( select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id=nodeisp and reason in ("nosignal") and starttime between sttime AND etime   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as n ON c.day=n.day) LEFT JOIN (select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id=nodeisp and reason in ("nocarrier","manual","freeze","removed") and starttime between sttime AND etime   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as d ON c.day=d.day where (c.duration <=86400) and (n.duration is NULL or d.duration is NULL or c.duration + n.duration <= 86400 )) as a where ((a.con/(86400-greatest(a.don,a.nos))) * 100) <=100 order by ((a.con/(86400-greatest(a.don,a.nos))) * 100) limit perlimit,1;
END //
DELIMITER ;
