DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_tcp//
CREATE PROCEDURE ninety_percentile_tcp(IN testtype VARCHAR(20))
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE nodeisp INT DEFAULT 0;
DECLARE medianthr  FLOAT DEFAULT 0.0;
DECLARE maxthr FLOAT DEFAULT 0.0;
DECLARE minthr FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE medianlimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE Node_ISP_ids CURSOR FOR SELECT Node_ISP_id FROM charts_tcpanalysis as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE Availability='yes' AND test=testtype AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.Node_ISP_id group by u.Node_ISP_id  having count(*) > 4 order by n.district;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN Node_ISP_ids;
getdata : LOOP
	FETCH Node_ISP_ids INTO nodeisp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET medianthr=0.0;
	SET maxthr=0.0;
	SET minthr=0.0;
	SET lowlimit=0;
	SET uplimit=0;
	SET medianlimit=0;
	SELECT COUNT(*) INTO cnt FROM charts_tcpanalysis WHERE Availability='yes'  AND Node_ISP_id= nodeisp AND test=testtype;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SET medianlimit = 0.5 * cnt;
	SELECT Round((8* Throughput /1024),3) INTO medianthr  from charts_tcpanalysis as u, test.node_isp as ni, test.nodes as n , test.isp as i WHERE Availability='yes' AND test=testtype  AND Node_ISP_id= nodeisp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.Node_ISP_id order by Throughput limit medianlimit,1 ;
	SELECT (8* Throughput /1024) INTO maxthr  from charts_tcpanalysis as u, test.node_isp as ni, test.nodes as n , test.isp as i WHERE Availability='yes' AND test=testtype  AND Node_ISP_id= nodeisp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.Node_ISP_id order by Throughput limit uplimit,1 ;
	SELECT (8* Throughput /1024) INTO minthr  from charts_tcpanalysis as u, test.node_isp as ni, test.nodes as n , test.isp as i WHERE Availability='yes' AND test=testtype  AND Node_ISP_id= nodeisp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.Node_ISP_id order by Throughput limit lowlimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(8* Throughput /1024),3) as avgsize,Round(min(8* Throughput /1024),3) as mnsize,Round(max(8* Throughput /1024),3) as mxsize ,Round(std(8* Throughput /1024),3) as stdsize,medianthr from charts_tcpanalysis as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE Availability='yes' AND test=testtype  AND Node_ISP_id= nodeisp and (8* Throughput /1024) between minthr and maxthr AND  ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.Node_ISP_id;	

END LOOP getdata;
CLOSE Node_ISP_ids;
END //
DELIMITER ;
call ninety_percentile_tcp('curl');
call ninety_percentile_tcp('iperfup');
