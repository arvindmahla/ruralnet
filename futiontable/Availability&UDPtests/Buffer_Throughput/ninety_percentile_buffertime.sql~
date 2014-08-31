DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_upbuffertime//
CREATE PROCEDURE ninety_percentile_upbuffertime()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minTime  INT DEFAULT 0;
DECLARE maxTime INT DEFAULT 0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0 group by nodeisp having count(*) > 4  order by buffertime ;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minTime=0;
	SET maxTime=0;
	SET lowlimit=0;
	SET uplimit=0;
	SELECT COUNT(*) INTO cnt FROM up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT buffertime  INTO minTime from up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp order by buffertime limit lowlimit,1 ;
	SELECT buffertime INTO maxTime from up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp order by buffertime  limit uplimit,1 ;
	SELECT nodeisp,count(*),Round(avg(buffertime),3) as avgtime,Round(std(buffertime),3) as stdtime from up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp order by buffertime ;

END LOOP getdata;
CLOSE nodeisps;

END //
DELIMITER ;


DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_downbuffertime//
CREATE PROCEDURE ninety_percentile_downbuffertime()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minTime  INT DEFAULT 0;
DECLARE maxTime INT DEFAULT 0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM down_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0 group by nodeisp having count(*) > 4  order by buffertime ;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minTime=0;
	SET maxTime=0;
	SET lowlimit=0;
	SET uplimit=0;
	SELECT COUNT(*) INTO cnt FROM down_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT buffertime  INTO minTime from down_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp order by buffertime  limit lowlimit,1 ;
	SELECT buffertime INTO maxTime from down_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp order by buffertime  limit uplimit,1 ;
	SELECT nodeisp,count(*),Round(avg(buffertime),3) as avgtime,Round(std(buffertime),3) as stdtime from down_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and buffertime > 0  AND nodeisp= node_isp order by buffertime ;

END LOOP getdata;
CLOSE nodeisps;

END //
DELIMITER ;
