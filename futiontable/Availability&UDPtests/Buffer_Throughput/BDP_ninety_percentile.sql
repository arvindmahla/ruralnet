DELIMITER //
DROP PROCEDURE IF EXISTS ninety_bdp_percentile//
CREATE PROCEDURE ninety_bdp_percentile(IN test_name VARCHAR(30))
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE nodeisp INT DEFAULT 0;
DECLARE minBDP  INT DEFAULT 0;
DECLARE maxBDP  INT DEFAULT 0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT Node_ISP_id FROM charts_serveranalysis WHERE test= test_name  AND availability='yes' and Rtt > 0 and Throughput > 0 and timestamp < 138530274600 group by Node_ISP_id having COUNT(*) > 3;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO nodeisp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minBDP=0;
	SET maxBDP=0;
	SET lowlimit=0;
	SET uplimit=0;
	SELECT COUNT(*) INTO cnt FROM charts_serveranalysis WHERE test= test_name AND node_isp_id= nodeisp AND availability='yes' and timestamp < 138530274600;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT Rtt*Throughput  INTO minBDP from charts_serveranalysis where test = test_name and Availability = 'yes' and Node_ISP_id = nodeisp and timestamp < 138530274600 order by Rtt*Throughput limit lowlimit,1 ;
	SELECT Rtt*Throughput INTO maxBDP from charts_serveranalysis where test = test_name and Availability = 'yes' and Node_ISP_id = nodeisp and timestamp < 138530274600 order by Rtt*Throughput limit uplimit,1 ;
	SELECT node_isp_id,count(*),Round(avg(Rtt),3) as avgRtt,Round(std(Rtt),3) as stdRtt,Round(avg(Throughput),3) as avgTh,Round(std(Throughput),3) as stdTh,Round(avg(Throughput*Rtt),3) as avgBdp,Round(std(Throughput*Rtt),3) as stdBdp from charts_serveranalysis where test = test_name and Availability = 'yes' and Node_ISP_id = nodeisp and Rtt*Throughput > minBDP and Rtt*Throughput < maxBDP and timestamp < 138530274600;

END LOOP getdata;
CLOSE nodeisps;

END //
DELIMITER ;
