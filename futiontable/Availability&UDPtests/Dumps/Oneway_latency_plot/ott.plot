set terminal png font arial 16  size 1024,800
set output "ott.png"
set xlabel "Number of Packets Arrived"
set ylabel "Oneway Delay in sec"
plot  "./uplinkbuffer/Up_Latency_44_ul_recv_2187_1400_1400133189.txt" using 0:6. t "Reliance Samnapur" with linespoint,\
  "./uplinkbuffer/Up_Latency_9_ul_recv_2187_1400_1402947833.txt" using 0:6. t "Airtel Amarpur" with linespoint,\
  "./uplinkbuffer/Up_Latency_21_ul_recv_2187_1400_1403093571.txt" using 0:6. t "IDEA Amarpur" with linespoint,\
  "./uplinkbuffer/Up_Latency_23_ul_recv_2734_1400_1402751853.txt" using 0:6. t "IDEA Paraswada" with linespoint,\
  "./uplinkbuffer/Up_Latency_32_ul_recv_2187_1400_1402664748.txt" using 0:6. t "MTNL Amarpur" with linespoint,\
  "./uplinkbuffer/Up_Latency_33_ul_recv_2187_1400_1403277098.txt" using 0:6. t "MTNL Samnapur" with linespoint,\
"./uplinkbuffer/Up_Latency_36_ul_recv_2734_1400_1399893098.txt" using 0:6. t "MTNL Lamta"  with linespoint

set output "inter.png"
set xlabel "Number of Packets Arrived"
set ylabel "Inter-packet Arrival Time"
plot  "./uplinkbuffer/Up_Latency_36_ul_recv_2734_1400_1399893098.txt" using 0:2. t "inter tx time" with linespoint,\
  "./uplinkbuffer/Up_Latency_36_ul_recv_2734_1400_1399893098.txt" using 0:3. t "inter rx time" with linespoint
