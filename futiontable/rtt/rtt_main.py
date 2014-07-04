import sqlite3
import sys
import numpy

locaname={'rnm13':'Ukwa, Paraswada, Balaghat, Madhya Pradesh',
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

locorder=['rnm11',
'rnm0',
'rnm18',
'rnm3',
'rnm2',
'rnm14',
'rnm7',
'rnm13'
]


loc_isp={
	'rnm':['airtel','idea','mtnl'],
	'rnm0':['airtel','mtnl','idea'],
	'rnm2':['mtnl','airtel','reliance'],
	'rnm3':['idea','airtel','mtnl','reliance',],
	'rnm7':['mtnl','reliance','idea'],
	'rnm11':['idea','airtel','mtnl'],
	'rnm13':['airtel','idea','mtnl'],
	'rnm14':['airtel','idea','mtnl'],
	# # 'rnm15':['airtel','mtnl','reliance','idea'],
	'rnm18':['reliance','airtel','mtnl'],
	'rnm31':['airtel','mtnl','idea'],
	'rnm101':['airtel','mtnl','idea']
}
		  

def main(loc,isp,tpy):
	num=[]
	con = sqlite3.connect(":memory:")
	cur = con.cursor()
	cur.execute("CREATE TABLE t (location TEXT ,TS TEXT,isp TEXT,ipaddress TEXT,latency REAL);")
	fin=open(typ,'r')
	lines=fin.readlines()
	data=[]
	for line in lines:
		data.append(tuple(line.strip().split(',')))
	cur.executemany("INSERT INTO t (location,TS,isp,ipaddress,latency) VALUES (?,?,?,?,?);", data)
	con.commit()
	rows=cur.execute("select latency from t where location=\'"+loc+"\' and isp=\'"+isp+"\'")
	for row in rows:
		num.append(row[0])
	try:
		print locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(num))+'\t'+str(numpy.min(num))+'\t'+str(numpy.max(num))+'\t'+str(numpy.std(num))+'\t'+str(numpy.median(num))
	except ValueError:
		# print loc,isp
		pass		


if __name__ == '__main__':
	typ=sys.argv[1]
	for loc in locorder:
		for isp in loc_isp[loc]:			
			main(loc,isp,typ)

