DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_3gupbuffersize//
CREATE PROCEDURE ninety_percentile_3gupbuffersize()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minsize  FLOAT DEFAULT 0.0;
DECLARE maxsize FLOAT DEFAULT 0.0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp and bitrate > 3999 group by u.nodeisp  having count(*) > 4 order by n.district;
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
	SELECT COUNT(*) INTO cnt FROM up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND bitrate > 3999  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT beforepackets  INTO minsize from up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND bitrate > 3999  AND nodeisp= node_isp order by beforepackets limit lowlimit,1 ;
	SELECT beforepackets INTO maxsize from up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND bitrate > 3999  AND nodeisp= node_isp order by beforepackets limit uplimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(beforepackets*(packetsize/1024)),3) as avgsize,Round(std(beforepackets*(packetsize/1024)),3) as stdsize,Round(min(beforepackets*(packetsize/1024)),3) as mnsize,Round(max(beforepackets*(packetsize/1024)),3) as mxsize from up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets between minsize and maxsize AND bitrate > 3999  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS ninety_percentile_2gupbuffersize//
CREATE PROCEDURE ninety_percentile_2gupbuffersize()
BEGIN
DECLARE cnt  INT DEFAULT 0;
DECLARE node_isp INT DEFAULT 0;
DECLARE minsize  FLOAT DEFAULT 0;
DECLARE maxsize FLOAT DEFAULT 0;
DECLARE lowlimit  INT DEFAULT 0;
DECLARE uplimit  INT DEFAULT 0;
DECLARE v_finished INT DEFAULT 0;
DECLARE nodeisps CURSOR FOR SELECT nodeisp FROM up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i  WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp and bitrate  between 2000 and 3900 group by u.nodeisp  having count(*) > 4 order by n.district;
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
	SELECT COUNT(*) INTO cnt FROM up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND bitrate  between 2000 and 3900  AND nodeisp= node_isp;
	SET lowlimit = 0.1 * cnt;
	SET uplimit = 0.9 * cnt;
	SELECT beforepackets  INTO minsize from up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND bitrate  between 2000 and 3900  AND nodeisp= node_isp order by beforepackets limit lowlimit,1 ;
	SELECT beforepackets INTO maxsize from up_throughput WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets > 0 AND bitrate  between 2000 and 3900  AND nodeisp= node_isp order by beforepackets limit uplimit,1 ;
	SELECT nodeisp,n.district, i.name,count(*),Round(avg(beforepackets*(packetsize/1024)),3) as avgsize,Round(std(beforepackets*(packetsize/1024)),3) as stdsize,Round(min(beforepackets*(packetsize/1024)),3) as mnsize,Round(max(beforepackets*(packetsize/1024)),3) as mxsize from up_throughput as u,test.node_isp as ni, test.nodes as n , test.isp as i WHERE afterthroughput > 0 and beforethroughput > 0 and beforepackets between minsize and maxsize AND bitrate  between 2000 and 3900  AND nodeisp= node_isp AND ni.MeasurementNode_id = n.id and ni.ISP_id = i.id and ni.id=u.nodeisp;
END LOOP getdata;
CLOSE nodeisps;
END //
DELIMITER ;
