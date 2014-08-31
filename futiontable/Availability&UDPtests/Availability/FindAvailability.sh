# Find the Total Availability, Average max and min daily availability
> AvailabilityData
> DailyAvailability
>medianAvailability
>ninetyAvailability
#AvailabilityRange.txt is o the format "Node_ISP_ID Location Provider Starttime Endtime
for lines in `cat AvailabilityRange.txt | tr '\t' ' ' | tr -s ' ' | awk '{$1=$1}1' | tr ' ' ','`
do
	nodeisp=`echo $lines | cut -d',' -f1`
	startTime=`echo $lines | cut -d',' -f4`
	endTime=`echo $lines | cut -d',' -f5`
	#query1 is to find the total connected time
	query1='select c.Node_ISP_id,sum(c.duration),count(c.duration) from (select Node_ISP_id,round(starttime/86400),sum(Endtime - Starttime) as duration from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("connected") and starttime between '$startTime' and '$endTime' group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as c;'
	#query2  is to find the period where there was no dongle activity
	query2='select sum(n.duration),count(*)  from ( select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("nosignal") and starttime between '$startTime' and '$endTime'   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as n,(select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("connected") and starttime between '$startTime' and '$endTime'   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as c where c.day=n.day;'
	#query3 finds the period of dongle error
	query3='select sum(n.duration),count(*)  from ( select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("nocarrier","manual","freeze","removed") and starttime between '$startTime' and '$endTime'   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as n,(select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("connected") and starttime between '$startTime' and '$endTime'   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as c where c.day=n.day;'
	#query4 gives the avg, max and min daily availability 
	query4='select count(a.con) as count,round(avg(a.con/(86400-greatest(a.don,a.nos)))*100,3) as mean,round(stddev(a.con/(86400-greatest(a.don,a.nos)))*100,3) as st,max(a.con/(86400-greatest(a.don,a.nos))) as max,min(a.con/(86400-greatest(a.don,a.nos))) as min from (select c.duration as con,IFNULL(d.duration,0) as don ,IFNULL(n.duration,0) as nos from ((select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("connected") and starttime between '$startTime' and '$endTime'   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as c LEFT JOIN ( select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("nosignal") and starttime between '$startTime' and '$endTime'   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as n ON c.day=n.day) LEFT JOIN (select Node_ISP_id,round(starttime/86400) as day,sum(Endtime - Starttime) as duration  from charts_nodata where Node_ISP_id='$nodeisp' and reason in ("nocarrier","manual","freeze","removed") and starttime between '$startTime' and '$endTime'   group by Node_ISP_id,(round(starttime/86400)) having sum(Endtime - Starttime) <=86400) as d ON c.day=d.day where (c.duration <=86400) and (n.duration is NULL or d.duration is NULL or c.duration + n.duration <= 86400 )) as a where (a.con/(86400-greatest(a.don,a.nos))) <= 1;'
	query5='call percentile_availability('$nodeisp','$startTime','$endTime',50);'
	query6='call percentile_availability('$nodeisp','$startTime','$endTime',90);'
	echo $nodeisp"===connected" >> AvailabilityData
	mysql measurements2 -uact4d -pruralnet -e "`echo $query1`" >> AvailabilityData
       echo $nodeisp"===nosignal" >> AvailabilityData
	mysql measurements2 -uact4d -pruralnet -e "`echo $query2`" >> AvailabilityData
        echo $nodeisp"===dongleerror" >> AvailabilityData
	mysql measurements2 -uact4d -pruralnet -e "`echo $query3`" >> AvailabilityData
# In AvailabilityData file we have the Connected time, dongle error time and no signal with us. To calculate availability use the following formula:
# Availability = Total Connected Time / (NoofDaysof Connected time * 86400 - MAX(Dongleerrotime,NoSignalTime))
        echo $nodeisp" " >> DailyAvailability
	mysql measurements2 -uact4d -pruralnet -e "`echo $query4`" >> DailyAvailability
	echo "Median"
	mysql measurements2 -uact4d -pruralnet -e "`echo $query5`" | grep -v "|" | grep -v "node" >> medianAvailability
	echo "90percentile"
	mysql measurements2 -uact4d -pruralnet -e "`echo $query6`" | grep -v "|" | grep -v "node" >> ninetyAvailability
done
