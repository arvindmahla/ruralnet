import sqlite3
import sys
import numpy
import csv
import thread


locaname={
		  'rnm13':'Ukwa, Paraswada, Balaghat, Madhya Pradesh',
		  'rnm3':'New Delhi3, South Delhi, Delhi, NCT',
		  'rnm0':'Dindori, Dindori, Dindori, Madhya Pradesh',\
		  'rnm7':'Samnapur, Dindori, Dindori, Madhya Pradesh',
		  'rnm11':'Amarpur, Dindori, Dindori, Madhya Pradesh',
		  'rnm2':'New Delhi2, South Delhi, Delhi, NCT',
		  'rnm18':'Lamta, Balaghat, Balaghat, Madhya Pradesh',
		  'rnm14':'Paraswada, Paraswada, Balaghat, Madhya Pradesh',
		  'rnm':'Hanumanpura, Kuchaman, Nagaur , Rajasthan',
		  'rnm101':'Jaipur, Jaipur, Jaipur, Rajasthan',
		  'rnm31':'Sikar, Sikar, Sikar, Rajasthan'}

loc_isp1={
	'rnm':['airtel','idea','mtnl'],
	'rnm31':['airtel','mtnl','idea'],
	'rnm101':['airtel','mtnl','idea']
}


loc_isp={
	'rnm31':['airtel','mtnl','idea'],
	'rnm101':['airtel','mtnl','idea']
}

log_path='tr/'


def fun(loc,isp,tid):
	print "In Thread "+tid
	ffile=open('rttavg/'+loc+'_'+isp,'w')
	con = sqlite3.connect(":memory:")
	con.text_factory = str
	cur = con.cursor()
	cur.execute("CREATE TABLE t (location TEXT ,TS TEXT,isp TEXT,hopid INTEGER,landmark TEXT,ipaddress TEXT,ASN TEXT,latency REAL);")
	fin=open(log_path+loc+'_'+isp+'.csv','r')
	lines=fin.readlines()
	data=[]
	for line in lines:
		data.append(tuple(line.strip().split(',')))
	cur.executemany("INSERT INTO t (location,TS,isp,hopid,landmark,ipaddress,ASN,latency) VALUES (?,?,?,?,?,?,?,?);", data)
	con.commit()
	rows=cur.execute("select max(hopid),TS,landmark from t where ASN =  \'"+isp+"\' group by TS,landmark order by TS,landmark")
	for row in rows:
		for lat in cur.execute("select latency from t where TS=\'"+row[1]+"\' and landmark=\'"+row[2]+"\' and hopid="+str(row[0])):
			ffile.write(str(lat[0])+'\n')
	ffile.close()
	print tid+': rttavg/'+loc+'_'+isp+' done'

def fun1(loc,isp,tid):
	print "In Thread "+tid
	ffile=open('raj/'+loc+'_'+isp,'w')
	con = sqlite3.connect(":memory:")
	con.text_factory = str
	cur = con.cursor()
	cur.execute("CREATE TABLE t (location TEXT ,TS TEXT,isp TEXT,hopid INTEGER,landmark TEXT,ipaddress TEXT,ASN TEXT,latency REAL);")
	fin=open(log_path+loc+'_'+isp+'.csv','r')
	lines=fin.readlines()
	data=[]
	for line in lines:
		data.append(tuple(line.strip().split(',')))
	cur.executemany("INSERT INTO t (location,TS,isp,hopid,landmark,ipaddress,ASN,latency) VALUES (?,?,?,?,?,?,?,?);", data)
	con.commit()
	rows=cur.execute("select max(hopid) ,TS from t group by TS,landmark having landmark=\'106.187.35.87\'")
	for row in rows:
		for lat in cur.execute("select latency from t where TS="+row[1]+" and hopid="+str(row[0])+" and landmark=\'106.187.35.87\'"):
			ffile.write(str(lat[0])+'\n')
	ffile.close()
	print tid+': raj/'+loc+'_'+isp+' done'

def main():
	i=0
	for loc in loc_isp:
		for isp in loc_isp[loc]:
			try:
				i+=1
				thread.start_new_thread(fun1,(loc,isp,str(i)))																							
			except Exception as e:
				# print e
				print "Error: unable to start thread"
	while 1:
		pass

def proc():	
	for loc in loc_isp1:
		for isp in loc_isp1[loc]:
			num=[]
			fin=open('raj/'+loc+'_'+isp,'r')
			lines=fin.readlines()
			for line in lines:
				num.append(float(line.strip()))
			try:
				print locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(num))+'\t'+str(numpy.min(num))+'\t'+str(numpy.max(num))+'\t'+str(numpy.std(num))+'\t'+str(numpy.median(num))
			except ValueError:
				# print 'travg/'+loc+'_'+isp
				pass

if __name__ == '__main__':
	# main()		  
	proc()