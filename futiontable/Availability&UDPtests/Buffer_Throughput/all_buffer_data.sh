echo "nodeisp,district, ISP,count,average,stddev,min,max " > downbuffersize
echo "nodeisp,district, ISP,count,average,stddev,min,max" > upbuffersize
echo "nodeisp,district, ISP,count,average,min,max ,std dev" > downdrainsize
echo "nodeisp,district, ISP,count,average,min,max,std dev"  > updrainsize
echo "nodeisp,district, ISP,count,avgThroughput,min Throughput,max Throughput ,median throughput,std dev" > downthroughput
echo "nodeisp,district, ISP,count,avgThroughput,min Throughput,max Throughput ,median throughput,std dev" > upthroughput
echo "nodeisp,district, ISP,count,avgThroughput,min Throughput,max Throughput ,median throughput,std dev" > downafterthroughput
echo "nodeisp,district, ISP,count,avgThroughput,min Throughput,max Throughput ,median throughput,std dev" > upafterthroughput
echo "nodeisp,district, ISP,count,avgThroughput,min Throughput,max Throughput ,std dev,median throughput" > downtcpthroughput
echo "nodeisp,district, ISP,count,avgThroughput,min Throughput,max Throughput ,std dev,median throughput" > uptcpthroughput
> downBDP
>upBDP
#find buffersizes
mysql -uroot -pnetspeed test -e "CALL ninety_percentile_3gdownbuffersize();" | grep -v "|" | grep -v "("  >> downbuffersize
mysql -uroot -pnetspeed test -e "CALL ninety_percentile_2gdownbuffersize();" | grep -v "|" | grep -v "("  >> downbuffersize
mysql -uroot -pnetspeed test -e "CALL ninety_percentile_3gupbuffersize();" | grep -v "|" | grep -v "(" >> upbuffersize
mysql -uroot -pnetspeed test -e "CALL ninety_percentile_2gupbuffersize();" | grep -v "|" | grep -v "(" >> upbuffersize
#find drainsizes

mysql -uroot -pnetspeed test -e "CALL ninety_percentile_down3drainsize();" | grep -v "|" | grep -v "(" >> downdrainsize
mysql -uroot -pnetspeed test -e "CALL ninety_percentile_down2drainsize();" | grep -v "|" | grep -v "(" >> downdrainsize
mysql -uroot -pnetspeed test -e "CALL ninety_percentile_up3drainsize();" | grep -v "|" | grep -v "(" >> updrainsize
mysql -uroot -pnetspeed test -e "CALL ninety_percentile_up2drainsize();" | grep -v "|" | grep -v "(" >> updrainsize
#find udp throughput before buffer filling
mysql -uroot -pnetspeed test -e "call ninety_percentile_downthroughput_3g();" | grep -v "|" | grep -v "(" >> downthroughput
mysql -uroot -pnetspeed test -e "call ninety_percentile_downthroughput_2g();" | grep -v "|" | grep -v "(" >>downthroughput
mysql -uroot -pnetspeed test -e "call ninety_percentile_upthroughput_3g();" | grep -v "|" | grep -v "(" >> upthroughput
mysql -uroot -pnetspeed test -e "call ninety_percentile_upthroughput_2g();" | grep -v "|" | grep -v "(" >> upthroughput
#find udp throughput after buffer filling
mysql -uroot -pnetspeed test -e "call ninety_percentile_downafterthroughput_3g();" | grep -v "|" | grep -v "(" >> downafterthroughput
mysql -uroot -pnetspeed test -e "call ninety_percentile_downafterthroughput_2g();" | grep -v "|" | grep -v "(" >> downafterthroughput
mysql -uroot -pnetspeed test -e "call ninety_percentile_upafterthroughput_3g();" | grep -v "|" | grep -v "(" >> upafterthroughput
mysql -uroot -pnetspeed test -e "call ninety_percentile_upafterthroughput_2g();" | grep -v "|" | grep -v "(" >> upafterthroughput

#find tcp throughputs
mysql -uroot -pnetspeed measurements1 -e "call ninety_percentile_tcp('curl');" | grep -v "|" | grep -v "(" >> downtcpthroughput
mysql -uroot -pnetspeed measurements1 -e "call ninety_percentile_tcp('iperfup');" | grep -v "|" | grep -v "(" >> uptcpthroughput

#for BDP
mysql -uroot -pnetspeed test -e "CALL ninety_bdp_percentile('curl');" | grep -v "|" | grep -v "(" >> downBDP
mysql -uroot -pnetspeed test -e "CALL ninety_bdp_percentile('iperfup');" | grep -v "|" | grep -v "(" >> upBDP
