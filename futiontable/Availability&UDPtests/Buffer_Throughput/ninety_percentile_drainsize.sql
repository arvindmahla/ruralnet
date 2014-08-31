DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_up3drainsize//
CREATE PROCEDURE ninety_percentile_up3drainsize()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minsize  FLOAT DEFAULT 0.0;
DECLARE maxsize FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp and bitrate > 3999 group by u.nodeisp  having count(*) > 4 order by n.district;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minsize=0;
	SET maxsize=0;
	SET lowlimit=0;
	SET uplimit=0;
	SELECT COUNT(*) INTO cnt FROM bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND bitrate > 3999  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT drainsize  INTO minsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND  bitrate > 3999  AND nodeisp= node_isp order by drainsize limit lowlimit,1 ;
	SELECT drainsize INTO maxsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND bitrate > 3999  AND nodeisp= node_isp order by drainsize limit uplimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(drainsize),3) as avgsize ,Round(min(drainsize),3) as mnsize,Round(max(drainsize),3) as mxsize ,Round(std(drainsize),3) as stdsize from bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND drainsize between minsize and maxsize AND bitrate > 3999  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_down3drainsize//
CREATE PROCEDURE ninety_percentile_down3drainsize()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minsize  FLOAT DEFAULT 0.0;
DECLARE maxsize FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp and bitrate > 3999 group by u.nodeisp  having count(*) > 4 order by n.district;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minsize=0;
	SET maxsize=0;
	SET lowlimit=0;
	SET uplimit=0;
	SELECT COUNT(*) INTO cnt FROM bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND bitrate > 3999  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT drainsize  INTO minsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND  bitrate > 3999  AND nodeisp= node_isp order by drainsize limit lowlimit,1 ;
	SELECT drainsize INTO maxsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND bitrate > 3999  AND nodeisp= node_isp order by drainsize limit uplimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(drainsize),3) as avgsize,Round(min(drainsize),3) as mnsize,Round(max(drainsize),3) as mxsize,Round(std(drainsize),3) as stdsize from bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND drainsize between minsize and maxsize AND bitrate > 3999  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;
DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_up2drainsize//
CREATE PROCEDURE ninety_percentile_up2drainsize()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minsize  FLOAT DEFAULT 0.0;
DECLARE maxsize FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp and bitrate between 2000 and 3900 group by u.nodeisp  having count(*) > 4 order by n.district;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minsize=0;
	SET maxsize=0;
	SET lowlimit=0;
	SET uplimit=0;
	SELECT COUNT(*) INTO cnt FROM bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND bitrate between 2000 and 3900  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT drainsize  INTO minsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND  bitrate between 2000 and 3900  AND nodeisp= node_isp order by drainsize limit lowlimit,1 ;
	SELECT drainsize INTO maxsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND bitrate between 2000 and 3900  AND nodeisp= node_isp order by drainsize limit uplimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(drainsize),3) as avgsize,Round(min(drainsize),3) as mnsize,Round(max(drainsize),3) as mxsize,Round(std(drainsize),3) as stdsize from bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE buffersize > 0 and drainsize > 0 AND updown='up' AND drainsize between minsize and maxsize AND bitrate between 2000 and 3900  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;
DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_down2drainsize//
CREATE PROCEDURE ninety_percentile_down2drainsize()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minsize  FLOAT DEFAULT 0.0;
DECLARE maxsize FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp and bitrate between 2000 and 3900 group by u.nodeisp  having count(*) > 4 order by n.district;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minsize=0.0;
	SET maxsize=0.0;
	SET lowlimit=0;
	SET uplimit=0;
	SELECT COUNT(*) INTO cnt FROM bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND bitrate between 2000 and 3900  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT drainsize  INTO minsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND  bitrate between 2000 and 3900  AND nodeisp= node_isp order by drainsize limit lowlimit,1 ;
	SELECT drainsize INTO maxsize from bufferdepth WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND bitrate between 2000 and 3900  AND nodeisp= node_isp order by drainsize limit uplimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(drainsize),3) as avgsize,Round(min(drainsize),3) as mnsize,Round(max(drainsize),3) as mxsize,Round(std(drainsize),3) as stdsize from bufferdepth as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE buffersize > 0 and drainsize > 0 AND updown='down' AND drainsize between minsize and maxsize AND bitrate between 2000 and 3900  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;
CALL ninety_percentile_up3drainsize();
CALL ninety_percentile_up2drainsize();
CALL ninety_percentile_down3drainsize();
CALL ninety_percentile_down2drainsize();
