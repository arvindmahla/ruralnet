DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_upafterthroughput_3g//
CREATE PROCEDURE ninety_percentile_upafterthroughput_3g()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minthr  FLOAT DEFAULT 0.0;
DECLARE maxthr FLOAT DEFAULT 0.0;
DECLARE medianthr FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE medianlimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0 AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp and bitrate > 3999 group by u.nodeisp  having count(*) > 4 order by n.district;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minthr=0.0;
	SET maxthr=0.0;
	SET medianthr=0.0;
	SET lowlimit=0;
	SET uplimit=0;
	SET medianlimit=0;
	SELECT COUNT(*) INTO cnt FROM up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0 AND bitrate > 3999  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SET medianlimit = 0.5 * cnt;
	SELECT afterthroughput  INTO minthr from up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0 AND bitrate > 3999  AND nodeisp= node_isp order by afterthroughput limit lowlimit,1 ;
	SELECT afterthroughput INTO maxthr from up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0 AND bitrate > 3999  AND nodeisp= node_isp order by afterthroughput limit uplimit,1 ;
	SELECT afterthroughput INTO medianthr from up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0 AND bitrate > 3999  AND nodeisp= node_isp order by afterthroughput limit medianlimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(afterthroughput),3) as avgsize,Round(min(afterthroughput),3) as mnsize,Round(max(afterthroughput),3) as mxsize , Round(medianthr,3) ,Round(std(afterthroughput),3) as stdsize from up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and afterthroughput between minthr and maxthr AND bitrate > 3999  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;


DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_upafterthroughput_2g//
CREATE PROCEDURE ninety_percentile_upafterthroughput_2g()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minthr  FLOAT DEFAULT 0.0;
DECLARE maxthr FLOAT DEFAULT 0.0;
DECLARE medianthr FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE medianlimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0 AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp   AND bitrate between 2000 and 3900 group by u.nodeisp  having count(*) > 4 order by n.district;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_finished=1;
OPEN nodeisps;
getdata : LOOP
	FETCH nodeisps INTO node_isp;
	IF v_finished=1 THEN LEAVE getdata;
	END IF;
	SET cnt=0;
	SET minthr=0.0;
	SET maxthr=0.0;
	SET medianthr=0.0;
	SET lowlimit=0;
	SET uplimit=0;
	SET medianlimit=0;
	SELECT COUNT(*) INTO cnt FROM up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0   AND bitrate between 2000 and 3900  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SET medianlimit = 0.5 * cnt;
	SELECT afterthroughput  INTO minthr from up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0   AND bitrate between 2000 and 3900  AND nodeisp= node_isp order by afterthroughput limit lowlimit,1 ;
	SELECT afterthroughput INTO maxthr from up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0   AND bitrate between 2000 and 3900  AND nodeisp= node_isp order by afterthroughput limit uplimit,1 ;
	SELECT afterthroughput INTO medianthr from up_throughput WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and beforepackets > 0   AND bitrate between 2000 and 3900 AND nodeisp= node_isp order by afterthroughput limit medianlimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(afterthroughput),3) as avgsize,Round(min(afterthroughput),3) as mnsize,Round(max(afterthroughput),3) as mxsize, Round(medianthr,3) ,Round(std(afterthroughput),3) as stdsize from up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE afterthroughput > 0 and afterpackets > 1 and beforepackets >1  and beforethroughput > 0 and afterthroughput between minthr and maxthr   AND bitrate between 2000 and 3900  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;


call ninety_percentile_upafterthroughput_2g();
call ninety_percentile_upafterthroughput_3g();
