from itertools import izip, tee
import random
import commands
import pickle
import pprint
import sys
import socket
import subprocess as sub
import dns.resolver
import numpy
import json
import time
from collections import Counter,defaultdict
from fuzzywuzzy import fuzz
import iso8601
import datetime
from plotcdf import CDF,MyError

isp_loc={
	'bsnl':['rnm_mtnl','rnm0_mtnl','rnm7_mtnl','rnm11_mtnl','rnm18_mtnl','rnm31_mtnl','rnm101_mtnl'],
	'airtel2g':['rnm_airtel','rnm11_airtel','rnm18_airtel','rnm31_airtel','rnm101_airtel'],
	'airtel3g':['rnm0_airtel','rnm3_airtel'],
	'idea':['rnm3_idea','rnm7_idea','rnm11_idea','rnm14_idea','rnm31_idea','rnm_idea','rnm101_idea'],
	'reliance':['rnm2_reliance','rnm7_reliance','rnm18_reliance'],
	'mtnl':['rnm2_mtnl','rnm3_mtnl']

}

ISPlabel={
	'mtnl':'MTNL UMTS',
	'airtel2g':'AIRTEL EDGE',
	'airtel3g':'AIRTEL UMTS',
	'reliance':'RELIANCE 1xEVDO',
	'bsnl':'BSNL EDGE',
	'idea':'IDEA EDGE'
}
colorscdf={
	'reliance':'#DD1E2F',
	'idea':'#EBB035',
	'airtel':'#06A2CB',
	'mtnl':'#218559'
}

colors=[
'black',
'grey',
'yellow',
'dark_blue',
'med_blue',
'light_blue',
'cyan',
'light_green',
'dark_green',
'magenta',
'red',
]

markerscdf={
	'reliance':'o',
	'idea':'*',
	'airtel':'+',
	'mtnl':'^'
}

colors={
	'reliance':'light_green',
	'idea':'yellow',
	'airtel':'red',
	'mtnl':'med_blue'
}

landlist_wanted_label={
'106.187.35.87':'Linode(Asia)',
'www.baidu.com':'baidu-com(Asia)',
'www.argentina.gob.ar':'argentina-gob-ar(South-America)',
'www.bundesregierung.de':'bundesregierung-de(Europe)',
'www.cs.uwaterloo.ca':'cs-waterloo(North-America)',
'www.ebay.in':'Ebay(Asia)',
'www.espncricinfo.com':'espncricinfo(Asia)',
'www.google.com':'google(Asia)',
'www.gov.za':'gov-za(Africa)',
'www.iitd.ac.in':'IIT-Delhi(Asia)',
'www.nation.co.ke':'nation-co-ke(Africa)',
'www.ndtv.com':'NDTV(Asia)',
'www.nicta.com.au':'nicta-au(Australia)',
'www.timesofindia.com':'timesofindia(Asia)',
'www.wikipedia.org':'wikipedia(North-America)',
}

def getcolors(l):
	nl=[]
	for item in l:
		nl.append(colors[item])
	return nl

rank_hoplen={
'106.187.35.87':['reliance','idea','airtel','mtnl'],
'8.8.8.8':['reliance','airtel','idea','mtnl'],
'www.argentina.gob.ar':['airtel','reliance','idea','mtnl'],
'www.baidu.com':['reliance','airtel','idea','mtnl'],
'www.bbc.co.uk':['reliance','airtel','idea','mtnl'],
'www.bundesregierung.de':['reliance','idea','airtel','mtnl'],
'www.cs.uwaterloo.ca':['reliance','idea','airtel','mtnl'],
'www.derstandard.at':['reliance','airtel','idea','mtnl'],
'www.ebay.in':['reliance','idea','airtel','mtnl'],
'www.espncricinfo.com':['reliance','idea','airtel','mtnl'],
'www.facebook.com':['reliance','airtel','idea','mtnl'],
'www.google.com':['reliance','idea','airtel','mtnl'],
'www.gov.za':['reliance','airtel','idea','mtnl'],
'www.iitd.ac.in':['reliance','idea','airtel','mtnl'],
'www.iplt20.com':['reliance','idea','airtel','mtnl'],
'www.licindia.com':['reliance','idea','airtel','mtnl'],
'www.nation.co.ke':['reliance','airtel','idea','mtnl'],
'www.ndtv.com':['reliance','idea','airtel','mtnl'],
'www.nicta.com.au':['reliance','airtel','idea','mtnl'],
'www.spoj.pl':['reliance','airtel','idea','mtnl'],
'www.timesofindia.com':['reliance','idea','airtel','mtnl'],
'www.uol.com.br':['airtel','reliance','idea','mtnl'],
'www.wikipedia.org':['reliance','idea','airtel','mtnl'],
'www.youtube.com':['reliance','idea','airtel','mtnl']
}

rank_lat={
'106.187.35.87':['reliance','idea','airtel','mtnl'],
'8.8.8.8':['reliance','idea','airtel','mtnl'],
'www.argentina.gob.ar':['reliance',	'airtel','idea','mtnl'],
'www.baidu.com':['reliance','idea','airtel','mtnl'],
'www.bbc.co.uk':['reliance','idea','airtel','mtnl'],
'www.bundesregierung.de':['reliance','idea','airtel','mtnl'],
'www.cs.uwaterloo.ca':['reliance','idea','airtel','mtnl'],
'www.derstandard.at':['reliance','idea','airtel','mtnl'],
'www.ebay.in':['reliance','idea','airtel','mtnl'],
'www.espncricinfo.com':['reliance','idea','airtel','mtnl'],
'www.facebook.com':['reliance','idea','airtel','mtnl'],
'www.google.com':['reliance','idea','airtel','mtnl'],
'www.gov.za':['reliance','idea','airtel','mtnl'],
'www.iitd.ac.in':['reliance','idea','airtel','mtnl'],
'www.iplt20.com':['reliance','idea','airtel','mtnl'],
'www.licindia.com':['reliance','idea','airtel','mtnl'],
'www.nation.co.ke':['reliance','idea','airtel','mtnl'],
'www.ndtv.com':['reliance','idea','airtel','mtnl'],
'www.nicta.com.au':['reliance','idea','airtel','mtnl'],
'www.spoj.pl':['reliance','idea','airtel','mtnl'],
'www.timesofindia.com':['reliance','idea','airtel','mtnl'],
'www.uol.com.br':['reliance','idea','airtel','mtnl'],
'www.wikipedia.org':['reliance','idea','airtel','mtnl'],
'www.youtube.com':['reliance','idea','airtel','mtnl']
}

rank_lat_infra={
'106.187.35.87':['reliance','idea','airtel','mtnl'],
'8.8.8.8':['reliance','idea','airtel','mtnl'],
'www.argentina.gob.ar':['reliance',	'airtel','idea','mtnl'],
'www.baidu.com':['reliance','idea','airtel','mtnl'],
'www.bbc.co.uk':['reliance','idea','airtel','mtnl'],
'www.bundesregierung.de':['reliance','idea','airtel','mtnl'],
'www.cs.uwaterloo.ca':['reliance','idea','airtel','mtnl'],
'www.derstandard.at':['reliance','idea','airtel','mtnl'],
'www.ebay.in':['reliance','idea','airtel','mtnl'],
'www.espncricinfo.com':['reliance','idea','airtel','mtnl'],
'www.facebook.com':['reliance','idea','airtel','mtnl'],
'www.google.com':['reliance','idea','airtel','mtnl'],
'www.gov.za':['reliance','idea','airtel','mtnl'],
'www.iitd.ac.in':['reliance','idea','airtel','mtnl'],
'www.iplt20.com':['reliance','idea','airtel','mtnl'],
'www.licindia.com':['reliance','idea','airtel','mtnl'],
'www.nation.co.ke':['reliance','idea','airtel','mtnl'],
'www.ndtv.com':['reliance','idea','airtel','mtnl'],
'www.nicta.com.au':['reliance','idea','airtel','mtnl'],
'www.spoj.pl':['reliance','idea','airtel','mtnl'],
'www.timesofindia.com':['reliance','idea','airtel','mtnl'],
'www.uol.com.br':['reliance','idea','airtel','mtnl'],
'www.wikipedia.org':['reliance','idea','airtel','mtnl'],
'www.youtube.com':['reliance','idea','airtel','mtnl']
}


rank_hoplen_infra={
'106.187.35.87':['reliance','idea','airtel','mtnl'],
'8.8.8.8':['reliance','idea','airtel','mtnl'],
'www.argentina.gob.ar':['reliance','idea','airtel','mtnl'],
'www.baidu.com':['reliance','airtel','idea','mtnl'],
'www.bbc.co.uk':['reliance','idea','airtel','mtnl'],
'www.bundesregierung.de':['reliance','idea','airtel','mtnl'],
'www.cs.uwaterloo.ca':['reliance','airtel','idea','mtnl'],
'www.derstandard.at':['reliance','idea','airtel','mtnl'],
'www.ebay.in':['reliance','idea','airtel','mtnl'],
'www.espncricinfo.com':['reliance','idea','airtel','mtnl'],
'www.facebook.com':['reliance','idea','airtel','mtnl'],
'www.google.com':['reliance','idea','airtel','mtnl'],
'www.gov.za':['reliance','idea','airtel','mtnl'],
'www.iitd.ac.in':['reliance','idea','airtel','mtnl'],
'www.iplt20.com':['reliance','idea','airtel','mtnl'],
'www.licindia.com':['reliance','idea','airtel','mtnl'],
'www.nation.co.ke':['reliance','idea','airtel','mtnl'],
'www.ndtv.com':['reliance','idea','airtel','mtnl'],
'www.nicta.com.au':['reliance','idea','airtel','mtnl'],
'www.spoj.pl':['reliance','idea','airtel','mtnl'],
'www.timesofindia.com':['reliance','idea','airtel','mtnl'],
'www.uol.com.br':['airtel','reliance','idea','mtnl'],
'www.wikipedia.org':['reliance','idea','airtel','mtnl'],
'www.youtube.com':['reliance','idea','airtel','mtnl']
}

rank_ASlen={
'106.187.35.87':['reliance','airtel','idea','mtnl'],
'8.8.8.8':['reliance','airtel','idea','mtnl'],
'www.argentina.gob.ar':['reliance','airtel','idea','mtnl'],
'www.baidu.com':['reliance','airtel','idea','mtnl'],
'www.bbc.co.uk':['reliance','airtel','idea','mtnl'],
'www.bundesregierung.de':['reliance','airtel','idea','mtnl'],
'www.cs.uwaterloo.ca':['reliance','airtel','idea','mtnl'],
'www.derstandard.at':['reliance','airtel','idea','mtnl'],
'www.ebay.in':['reliance','airtel','idea','mtnl'],
'www.espncricinfo.com':['reliance','airtel','idea','mtnl'],
'www.facebook.com':['reliance','airtel','idea','mtnl'],
'www.google.com':['reliance','airtel','idea','mtnl'],
'www.gov.za':['reliance','airtel','idea','mtnl'],
'www.iitd.ac.in':['reliance','airtel','idea','mtnl'],
'www.iplt20.com':['reliance','airtel','idea','mtnl'],
'www.licindia.com':['reliance','airtel','idea','mtnl'],
'www.nation.co.ke':['reliance','airtel','idea','mtnl'],
'www.ndtv.com':['reliance','airtel','idea','mtnl'],
'www.nicta.com.au':['reliance','airtel','idea','mtnl'],
'www.spoj.pl':['reliance','airtel','idea','mtnl'],
'www.timesofindia.com':['reliance','airtel','idea','mtnl'],
'www.uol.com.br':['reliance','airtel','idea','mtnl'],
'www.wikipedia.org':['reliance','airtel','idea','mtnl'],
'www.youtube.com':['reliance','airtel','idea','mtnl'],
}

locorder=[
'Delhi3G',
'Jaipur',
'Dindori',
'Delhi',
'Paraswada',
'Samanapur',
'Lamta',
'Sikar',
'Hanumanpura',
'Amarpur',
]

urban=[
'Delhi3G',
'Jaipur',
'Dindori',
'Delhi',
]

rural=[
'Paraswada',
'Samanapur',
'Lamta',
'Sikar',
'Hanumanpura',
'Amarpur',
]

graphcontent4Hoplen="""
=cluster;<ISPLIST>
colors=<COLORS>
=table
title=Hop length for <LAND>
yformat=%g
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=Hop length
xlabel=Uraban/SemiUrban Location\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tRural Location\t\t\t\t
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""


graphcontent4HoplenbylandUrban="""
=cluster;<LOC>
=table
=sortdata_ascend
title=Hop length for <ISP>
yformat=%g
rotateby=-45
xlabelshift=0,-5
legendx=right
legendy=center
=nogridy
ylabel=Hop length
xlabel=<TYPE> Locations
# stretch it out in x direction
xscale=1
=table
#	<LOC_TAB>
"""


graphcontent4HoplenbylandRural="""
=cluster;<ISPLIST>
colors=<COLORS>
=table
title=Hop length for <LAND>
yformat=%g
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=Hop length
xlabel=<TYPE> Locations
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""

graphcontent4ASlen="""
=cluster;<ISPLIST>
colors=<COLORS>
=table
title=Number of ASs on path for <LAND>
yformat=%g
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=#AS 
xlabel=Locations
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""

graphcontent4prev="""
=cluster;<TYPE>
colors=<COLORS>
=table
title=Prevalence Parameter for <LOC>
yformat=%g
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=Prevalence parameter
xlabel=ISPs
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""
graphcontent4overall="""
=cluster;<ISP>
=table
title=Prevalence Parameter for Various Locations
yformat=%g
rotateby=-45
legendx=right
legendy=center
=nogridy
max=0.05
ylabel=Prevalence parameter
xlabel=Locations
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""

graphcontent4dur="""
=cluster;<ISPLIST>
colors=<COLORS>
=table
title=Median Duration between Traceroutes for <LAND>
yformat=%g
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=Duration in hrs
xlabel=Locations
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""

graphcontent4latency="""
=cluster;<ISPLIST>
colors=<COLORS>
=table
title=Last Hop Latency for <LAND>
yformat=%gms
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=latency in ms
xlabel=Uraban/SemiUrban Location\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tRural Location\t\t\t\t
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""

graphcontent4Hoplen_infra="""
=cluster;<ISPLIST>
colors=<COLORS>
=table
title=#hops inside ISP network for <LAND>
yformat=%g
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=Hop length
xlabel=Locations
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""

graphcontent4latency_infra="""
=cluster;<ISPLIST>
colors=<COLORS>
=table
title=Last Hop Latency inside ISP network for <LAND>
yformat=%gms
rotateby=-45
legendx=right
legendy=center
=nogridy
ylabel=latency in ms
xlabel=Locations
# stretch it out in x direction
xscale=1
=table
#	<ISPLIST_TAB>
"""


locaname={'rnm3':'Delhi3G','rnm0':'Dindori','rnm7':'Samanapur','rnm11':'Amarpur','rnm2':'Delhi','rnm18':'Lamta','rnm14':'Paraswada','rnm':'Hanumanpura','rnm101':'Jaipur','rnm31':'Sikar','rnm15':'Ahemadabad','rnm104':'Ormanjhi1','rnm105':'Getalsud','rnm13':'Ukwa'}
landlist=['106.187.35.87','8.8.8.8','www.argentina.gob.ar','www.baidu.com','www.bbc.co.uk','www.bundesregierung.de','www.cs.uwaterloo.ca'\
,'www.derstandard.at','www.ebay.in','www.espncricinfo.com','www.facebook.com','www.google.com','www.gov.za','www.iitd.ac.in','www.iplt20.com'\
,'www.licindia.com','www.nation.co.ke','www.ndtv.com','www.nicta.com.au','www.spoj.pl','www.timesofindia.com','www.uol.com.br','www.wikipedia.org','www.youtube.com']
def hoplen():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 hoplen/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('hoplen/'+landmark+'/'+fname,'r')
			lines=f.readlines()
			k=[int(x.strip()) for x in lines]
			ispdict={}
			val=str(numpy.mean(k))
			stddev=str(numpy.std(k))
			if val=='nan':
				val='0'
			if stddev=='nan':
				stddev='0'
			if locaname[loc] in locdict:
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			else:
				locdict[locaname[loc]]={}
				stddevdict[locaname[loc]]={}
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
			f.close()
		landdict[landmark]=(locdict,stddevdict)
	for landmark in landdict:
		mygraph=graphcontent4Hoplen
		mygraph=mygraph.replace('<ISPLIST>',';'.join(rank_hoplen[landmark]))
		mygraph=mygraph.replace('<LAND>',landmark)
		mygraph=mygraph.replace('<COLORS>',','.join(getcolors(rank_hoplen[landmark])))
		mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(rank_hoplen[landmark]))
		mygraph+='\n'
		for loc in locorder:#landdict[landmark][0]:
			mygraph+=(loc+'\t')
			for isp in rank_hoplen[landmark]:
				try:
					mygraph+=(landdict[landmark][0][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for loc in locorder:#landdict[landmark][1]:
			mygraph+=(loc+'\t')
			for isp in rank_hoplen[landmark]:
				try:
					mygraph+=(landdict[landmark][1][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		landfname=landmark.replace('.','-')+'.dat'
		f=open('charts/Hoplen/'+landfname,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/Hoplen/'+landfname+' > '+'charts/Hoplen/'+landmark.replace('.','-')+'.png')



	# for landmark in landlist:
	# 	print 'Landmark\tISP\treliance\tstddev\tidea\tstddev\tairtel\tstddev\tmtnl\tstddev'
	# 	for loc in landdict[landmark]:
	# 		sys.stdout.write(landmark+'\t'+loc+'\t')
	# 		for isp in rank:
	# 			try:
	# 				sys.stdout.write(landdict[landmark][loc][isp][0]+'\t'+landdict[landmark][loc][isp][1]+'\t')
	# 			except KeyError:
	# 				sys.stdout.write(' '+'\t'+' '+'\t')
	# 		print ''


def lastlen():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 lastlat/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('lastlat/'+landmark+'/'+fname,'r')
			lines=f.readlines()
			k=[float(x.strip()) for x in lines]
			ispdict={}
			val=str(numpy.mean(k))
			stddev=str(numpy.std(k))
			if val=='nan':
				val='0'
			if stddev=='nan':
				stddev='0'
			if locaname[loc] in locdict:
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			else:
				locdict[locaname[loc]]={}
				stddevdict[locaname[loc]]={}
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
			f.close()
		landdict[landmark]=(locdict,stddevdict)
	# for landmark in landlist:
	# 	print 'Landmark\tISP\treliance\tstddev\tidea\tstddev\tairtel\tstddev\tmtnl\tstddev'
	# 	for loc in landdict[landmark]:
	# 		sys.stdout.write(landmark+'\t'+loc+'\t')
	# 		for isp in rank:
	# 			try:
	# 				sys.stdout.write(landdict[landmark][loc][isp][0]+'\t'+landdict[landmark][loc][isp][1]+'\t')
	# 			except KeyError:
	# 				sys.stdout.write(' '+'\t'+' '+'\t')
	# 		print ''
	for landmark in landdict:
		mygraph=graphcontent4latency
		mygraph=mygraph.replace('<ISPLIST>',';'.join(rank_lat[landmark]))
		mygraph=mygraph.replace('<LAND>',landmark)
		mygraph=mygraph.replace('<COLORS>',','.join(getcolors(rank_lat[landmark])))
		mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(rank_lat[landmark]))
		mygraph+='\n'
		for loc in locorder:
			mygraph+=(loc+'\t')
			for isp in rank_lat[landmark]:
				try:
					mygraph+=(landdict[landmark][0][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for loc in landdict[landmark][1]:
			mygraph+=(loc+'\t')
			for isp in rank_lat[landmark]:
				try:
					mygraph+=(landdict[landmark][1][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		landfname=landmark.replace('.','-')+'.dat'
		f=open('charts/Lastlat/'+landfname,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/Lastlat/'+landfname+' > '+'charts/Lastlat/'+landmark.replace('.','-')+'.png')

def ASlen():
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 ASlen/'+landmark).split('\n')
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('ASlen/'+landmark+'/'+fname,'r')
			lines=f.readlines()
			k=[int(x.strip()) for x in lines]
			print locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
			f.close()

def pervalence():
	filelist_overall=commands.getoutput('ls -1 dom/overall').split('\n')
	filelist_inside=commands.getoutput('ls -1 dom/inside').split('\n')
	filelist_outside=commands.getoutput('ls -1 dom/outside').split('\n')
	locdict={}
	for fname in filelist_overall:
		loc=fname.split('_')[0]
		isp=fname.split('_')[1]
		f=open('dom/overall/'+fname,'r')
		lines=f.readlines()
		k=[float(x.strip()) for x in lines]
		if (locaname[loc],isp) in locdict:
			print "sdfdf"
			locdict[(locaname[loc],isp)]['overall']=(str(numpy.mean(k)),str(numpy.std(k)))
		else:
			locdict[(locaname[loc],isp)]={}
			locdict[(locaname[loc],isp)]['overall']=(str(numpy.mean(k)),str(numpy.std(k)))
		# print locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
		f.close()

	for fname in filelist_inside:
		loc=fname.split('_')[0]
		isp=fname.split('_')[1]
		f=open('dom/inside/'+fname,'r')
		lines=f.readlines()
		k=[float(x.strip()) for x in lines]
		if (locaname[loc],isp) in locdict:
			locdict[(locaname[loc],isp)]['inside']=(str(numpy.mean(k)),str(numpy.std(k)))
		else:
			locdict[(locaname[loc],isp)]={}
			locdict[(locaname[loc],isp)]['inside']=(str(numpy.mean(k)),str(numpy.std(k)))
		# print locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
		f.close()
	for fname in filelist_outside:
		loc=fname.split('_')[0]
		isp=fname.split('_')[1]
		f=open('dom/outside/'+fname,'r')
		lines=f.readlines()
		k=[float(x.strip()) for x in lines]
		if (locaname[loc],isp) in locdict:
			locdict[(locaname[loc],isp)]['outside']=(str(numpy.mean(k)),str(numpy.std(k)))
		else:
			locdict[(locaname[loc],isp)]={}
			locdict[(locaname[loc],isp)]['outside']=(str(numpy.mean(k)),str(numpy.std(k)))
		# print locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
		f.close()
	nlocdict={}
	for key in locdict:
		if key[0] in nlocdict:
			nlocdict[key[0]][key[1]]=locdict[key]
		else:
			nlocdict[key[0]]={}
			nlocdict[key[0]][key[1]]=locdict[key]
	# pprint.pprint(nlocdict)
	
	for loc in nlocdict:
		f=open('charts/pervalance/'+loc,'w')
		mygraph=graphcontent4prev
		mygraph=mygraph.replace('<TYPE>','inside;outside;overall')
		mygraph=mygraph.replace('<LOC>',loc)
		mygraph=mygraph.replace('<COLORS>','light_green,red,yellow')
		mygraph=mygraph.replace('<ISPLIST_TAB>','inside	outside	overall')
		mygraph+='\n'		
		for isp in nlocdict[loc]:
			mygraph+=(isp+'\t')
			for typ in ['inside','outside','overall']:
				try:
					mygraph+=(nlocdict[loc][isp][typ][0]+'\t')
				except KeyError:
					pass
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for isp in nlocdict[loc]:
			mygraph+=(isp+'\t')
			print loc
			for typ in ['inside','outside','overall']:
				try:
					mygraph+=(nlocdict[loc][isp][typ][1]+'\t')
				except KeyError:
					pass
			mygraph+='\n'
		# print mygraph
		f.write(mygraph)
		f.close()
		commands.getoutput('bargraph.pl -gnuplot -png -non-transparent charts/pervalance/'+loc+' > '+'charts/pervalance/'+loc+'.png')

def pervalence_overall():
	filelist_overall=commands.getoutput('ls -1 dom/overall').split('\n')
	locdict={}
	for fname in filelist_overall:
		loc=fname.split('_')[0]
		isp=fname.split('_')[1]
		f=open('dom/overall/'+fname,'r')
		lines=f.readlines()
		k=[float(x.strip()) for x in lines]
		val=str(numpy.mean(k))
		stddev=str(numpy.std(k))
		if val=='nan':
			val='0'
		if stddev=='nan':
			stddev='0'
		if (locaname[loc],isp) in locdict:
			locdict[(locaname[loc],isp)]['overall']=(val,stddev)
		else:
			locdict[(locaname[loc],isp)]={}
			locdict[(locaname[loc],isp)]['overall']=(val,stddev)
		# print locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
		f.close()
	nlocdict={}
	for key in locdict:
		if key[0] in nlocdict:
			nlocdict[key[0]][key[1]]=locdict[key]
		else:
			nlocdict[key[0]]={}
			nlocdict[key[0]][key[1]]=locdict[key]
	pprint.pprint(nlocdict)
	mygraph='\n'
	isplist=['reliance','airtel','mtnl','idea']	
	for loc in nlocdict:
		mygraph+=(loc+'\t')
		for isp in isplist:
			try:
				mygraph+=(nlocdict[loc][isp]['overall'][0]+'\t')
			except:
				mygraph+=('0'+'\t')
				pass
		mygraph+='\n'
	mygraph+='=yerrorbars\n'
	for loc in nlocdict:
		mygraph+=(loc+'\t')
		for isp in nlocdict[loc]:
			try:
				mygraph+=(nlocdict[loc][isp]['overall'][1]+'\t')
			except Exception as e:
				mygraph+=('0'+'\t')
				pass
		mygraph+='\n'
	mygraph=graphcontent4overall+mygraph
	mygraph=mygraph.replace('<ISP>',';'.join(isplist))
	f=open('charts/pervalance/overall','w')
	f.write(mygraph)
	f.close()
	commands.getoutput('bargraph.pl -gnuplot -png -non-transparent charts/pervalance/overall > charts/pervalance/overall.png')

xlimit={
'Delhi3G':1500,
'Jaipur':500,
'Dindori':1000,
'Delhi':700,
'Ukwa':1500,
'Paraswada':1000,
'Samanapur':1000,
'Lamta':1000,
'Sikar':500,
'Hanumanpura':700,
'Amarpur':1000,
}

def cdflats():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 lastlat/'+landmark).split('\n')
		ispdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('lastlat/'+landmark+'/'+fname,'r')
			lines=f.readlines()
			k=[float(x.strip()) for x in lines]
			if locaname[loc] in ispdict:
				ispdict[locaname[loc]][isp]=k
			else:
				ispdict[locaname[loc]]={}
				ispdict[locaname[loc]][isp]=k
			f.close()
		landdict[landmark]=ispdict
	for landmark in ['www.nation.co.ke']:#landdict:
		path='charts/Cdflats/'+landmark.replace('.','-')+'/'
		commands.getoutput('mkdir -p '+path)
		for loc in landdict[landmark]:
			fname=path+loc+'.png'
			title='Cdf of latency for '+loc
			xlabel='Latency in ms'
			ylabel='Prob.'
			cdf=CDF(title,fname,xlabel,ylabel)
			for isp in landdict[landmark][loc]:
				# print isp,loc
				slabel=loc+'-'+isp
				sdict={slabel:colorscdf[isp]}
				cdf.addSeries(landdict[landmark][loc][isp],slabel,colorscdf[isp],markerscdf[isp])
			pprint.pprint(cdf.outpath)
			try:
				cdf.draw(xlimit[loc])
			except MyError as e:
				print "here"
				pass
			del cdf

def cdflats_infra():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 infra/lastlat/'+landmark).split('\n')
		ispdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('infra/lastlat/'+landmark+'/'+fname,'r')
			lines=f.readlines()
			k=[float(x.strip()) for x in lines]
			if locaname[loc] in ispdict:
				ispdict[locaname[loc]][isp]=k
			else:
				ispdict[locaname[loc]]={}
				ispdict[locaname[loc]][isp]=k
			f.close()
		landdict[landmark]=ispdict
	for landmark in landdict:
		path='charts/infra/Cdflats/'+landmark.replace('.','-')+'/'
		commands.getoutput('mkdir -p '+path)
		for loc in landdict[landmark]:
			fname=path+loc+'.png'
			title='Cdf of latency for '+loc
			xlabel='Latency in ms'
			ylabel='Prob.'
			cdf=CDF(title,fname,xlabel,ylabel)
			for isp in landdict[landmark][loc]:
				# print isp,loc
				slabel=loc+'-'+isp
				sdict={slabel:colorscdf[isp]}
				cdf.addSeries(landdict[landmark][loc][isp],slabel,colorscdf[isp],markerscdf[isp])
			pprint.pprint(cdf.outpath)
			try:
				cdf.draw(xlimit[loc])
			except MyError as e:
				print "here"
				pass
			del cdf			


def hoplen_infra():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 infra/hoplen/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('infra/hoplen/'+landmark+'/'+fname,'r')	
			lines=f.readlines()
			# print lines
			k=[int(x.strip()) for x in lines if x!='None\n']
			ispdict={}
			val=str(numpy.mean(k))
			stddev=str(numpy.std(k))
			if val=='nan':
				val='0'
			if stddev=='nan':
				stddev='0'
			if locaname[loc] in locdict:
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			else:
				locdict[locaname[loc]]={}
				stddevdict[locaname[loc]]={}
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
			f.close()
		landdict[landmark]=(locdict,stddevdict)
	for landmark in landdict:
		mygraph=graphcontent4Hoplen_infra
		mygraph=mygraph.replace('<ISPLIST>',';'.join(rank_hoplen_infra[landmark]))
		mygraph=mygraph.replace('<LAND>',landmark)
		mygraph=mygraph.replace('<COLORS>',','.join(getcolors(rank_hoplen_infra[landmark])))
		mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(rank_hoplen_infra[landmark]))
		mygraph+='\n'
		for loc in landdict[landmark][0]:
			mygraph+=(loc+'\t')
			for isp in rank_hoplen_infra[landmark]:
				try:
					mygraph+=(landdict[landmark][0][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for loc in landdict[landmark][1]:
			mygraph+=(loc+'\t')
			for isp in rank_hoplen_infra[landmark]:
				try:
					mygraph+=(landdict[landmark][1][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		landfname=landmark.replace('.','-')+'.dat'
		f=open('charts/infra/Hoplen/'+landfname,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/infra/Hoplen/'+landfname+' > '+'charts/infra/Hoplen/'+landmark.replace('.','-')+'.png')

def lastlen_infra():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 infra/lastlat/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('infra/lastlat/'+landmark+'/'+fname,'r')
			# print f
			lines=f.readlines()
			k=[float(x.strip()) for x in lines]
			ispdict={}
			val=str(numpy.mean(k))
			stddev=str(numpy.std(k))
			if val=='nan':
				val='0'
			if stddev=='nan':
				stddev='0'
			if locaname[loc] in locdict:
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			else:
				locdict[locaname[loc]]={}
				stddevdict[locaname[loc]]={}
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
			f.close()
		landdict[landmark]=(locdict,stddevdict)
	# for landmark in landlist:
	# 	print 'Landmark\tISP\treliance\tstddev\tidea\tstddev\tairtel\tstddev\tmtnl\tstddev'
	# 	for loc in landdict[landmark]:
	# 		sys.stdout.write(landmark+'\t'+loc+'\t')
	# 		for isp in rank:
	# 			try:
	# 				sys.stdout.write(landdict[landmark][loc][isp][0]+'\t'+landdict[landmark][loc][isp][1]+'\t')
	# 			except KeyError:
	# 				sys.stdout.write(' '+'\t'+' '+'\t')
	# 		print ''
	for landmark in landdict:
		mygraph=graphcontent4latency_infra
		mygraph=mygraph.replace('<ISPLIST>',';'.join(rank_lat_infra[landmark]))
		mygraph=mygraph.replace('<LAND>',landmark)
		mygraph=mygraph.replace('<COLORS>',','.join(getcolors(rank_lat_infra[landmark])))
		mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(rank_lat_infra[landmark]))
		mygraph+='\n'
		for loc in landdict[landmark][0]:
			mygraph+=(loc+'\t')
			for isp in rank_lat_infra[landmark]:
				try:
					mygraph+=(landdict[landmark][0][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for loc in landdict[landmark][1]:
			mygraph+=(loc+'\t')
			for isp in rank_lat_infra[landmark]:
				try:
					mygraph+=(landdict[landmark][1][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		landfname=landmark.replace('.','-')+'.dat'
		f=open('charts/infra/Lastlat/'+landfname,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/infra/Lastlat/'+landfname+' > '+'charts/infra/Lastlat/'+landmark.replace('.','-')+'.png')



def ASlen():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 ASlen/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('ASlen/'+landmark+'/'+fname,'r')
			lines=f.readlines()
			k=[int(x.strip()) for x in lines]
			ispdict={}
			val=str(numpy.mean(k))
			stddev=str(numpy.std(k))
			if val=='nan':
				val='0'
			if stddev=='nan':
				stddev='0'
			if locaname[loc] in locdict:
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			else:
				locdict[locaname[loc]]={}
				stddevdict[locaname[loc]]={}
				locdict[locaname[loc]][isp]=val
				stddevdict[locaname[loc]][isp]=stddev
			# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
			f.close()
		landdict[landmark]=(locdict,stddevdict)
	for landmark in landdict:
		mygraph=graphcontent4ASlen
		mygraph=mygraph.replace('<ISPLIST>',';'.join(rank_ASlen[landmark]))
		mygraph=mygraph.replace('<LAND>',landmark)
		mygraph=mygraph.replace('<COLORS>',','.join(getcolors(rank_ASlen[landmark])))
		mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(rank_ASlen[landmark]))
		mygraph+='\n'
		for loc in landdict[landmark][0]:
			mygraph+=(loc+'\t')
			for isp in rank_ASlen[landmark]:
				try:
					mygraph+=(landdict[landmark][0][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for loc in landdict[landmark][1]:
			mygraph+=(loc+'\t')
			for isp in rank_ASlen[landmark]:
				try:
					mygraph+=(landdict[landmark][1][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		landfname=landmark.replace('.','-')+'.dat'
		f=open('charts/ASlen/'+landfname,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/ASlen/'+landfname+' > '+'charts/ASlen/'+landmark.replace('.','-')+'.png')

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def duration():
	landdict={}
	for landmark in landlist:
		filelist=commands.getoutput('ls -1 duration/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			f=open('duration/'+landmark+'/'+fname,'r')
			lines=f.readlines()
			k=sorted([int(x.strip()) for x in lines])
			# pprint.pprint(k)
			difflist=[y-x for x,y in pairwise(k)]
			ispdict={}
			val=str(numpy.median(difflist)/3600)
			# stddev=str(numpy.std(k))
			if val=='nan':
				val='0'
			# if stddev=='nan':
			# 	stddev='0'
			if locaname[loc] in locdict:
				locdict[locaname[loc]][isp]=val
				# stddevdict[locaname[loc]][isp]=stddev
			else:
				locdict[locaname[loc]]={}
				# stddevdict[locaname[loc]]={}
				locdict[locaname[loc]][isp]=val
				# stddevdict[locaname[loc]][isp]=stddev
			# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
			f.close()
		landdict[landmark]=locdict
	for landmark in landdict:
		mygraph=graphcontent4dur
		mygraph=mygraph.replace('<ISPLIST>',';'.join(rank_hoplen_infra[landmark]))
		mygraph=mygraph.replace('<LAND>',landmark)
		mygraph=mygraph.replace('<COLORS>',','.join(getcolors(rank_hoplen_infra[landmark])))
		mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(rank_hoplen_infra[landmark]))
		mygraph+='\n'
		for loc in landdict[landmark]:
			mygraph+=(loc+'\t')
			for isp in rank_hoplen_infra[landmark]:
				try:
					mygraph+=(landdict[landmark][loc][isp]+'\t')
				except KeyError:
					mygraph+=('0'+'\t')
			mygraph+='\n'
		landfname=landmark.replace('.','-')+'.dat'
		f=open('charts/duration/'+landfname,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/duration/'+landfname+' > '+'charts/duration/'+landmark.replace('.','-')+'.png')


def bufftrace_cdf():
	for fname in ['rnm2_airtel','rnm2_mtnl','rnm2_reliance']:
		isp=fname.split('_')[1]
		f2=open('bufftrace/2/'+fname,'r')
		f3=open('bufftrace/3/'+fname,'r')
		lines2=f2.readlines()
		k2=[float(x.strip()) for x in lines2]
		lines3=f3.readlines()
		k3=[float(x.strip()) for x in lines3]
		path='charts/buff/'
		chartname=path+isp+'.png'
		title='Cdf of latency for '+isp
		xlabel='Latency in ms'
		ylabel='Prob.'
		cdf=CDF(title,chartname,xlabel,ylabel)
		cdf.addSeries(k2,'Before','#DD1E2F','o')
		cdf.addSeries(k3,'After','#06A2CB','o')
		cdf.draw()

def bufftrace_cdf_server():
	for fname in ['rnm2_airtel','rnm2_mtnl','rnm2_reliance']:
		isp=fname.split('_')[1]
		f2=open('server_buff/2/'+fname,'r')
		f3=open('server_buff/3/'+fname,'r')
		lines2=f2.readlines()
		k2=[float(x.strip()) for x in lines2]
		lines3=f3.readlines()
		k3=[float(x.strip()) for x in lines3]
		path='charts/buffsever/'
		chartname=path+isp+'.png'
		title='Cdf of latency for '+isp
		xlabel='Latency in ms'
		ylabel='Prob.'
		cdf=CDF(title,chartname,xlabel,ylabel)
		cdf.addSeries(k2,'Before','#DD1E2F','o')
		cdf.addSeries(k3,'After','#06A2CB','o')
		cdf.draw()		

# def modifydict(d):
# 	nd={}
# 	for isp in d:

# 		for item in d[isp]:


def hoplenbyurbankeyland():
	landdict={}
	for landmark in landlist_wanted:
		filelist=commands.getoutput('ls -1 hoplen/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			if locaname[loc] in locorder:
				f=open('hoplen/'+landmark+'/'+fname,'r')
				lines=f.readlines()
				k=[int(x.strip()) for x in lines]
				ispdict={}
				val=str(numpy.mean(k))
				stddev=str(numpy.std(k))
				if val=='nan':
					val='0'
				if stddev=='nan':
					stddev='0'
				if isp in locdict:
					locdict[isp][locaname[loc]]=val
					stddevdict[isp][locaname[loc]]=stddev
				else:
					locdict[isp]={}
					stddevdict[isp]={}
					locdict[isp][locaname[loc]]=val
					stddevdict[isp][locaname[loc]]=stddev
				# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
				f.close()
		landdict[landmark]=(locdict,stddevdict)
	ispdict=defaultdict(dict)
	for landmark in landlist:
		for isp in landdict[landmark][0]:	
			for loc in landdict[landmark][0][isp]:
				try:
					ispdict[isp][loc][landmark]=(landdict[landmark][0][isp][loc],landdict[landmark][1][isp][loc])
				except Exception:
					ispdict[isp][loc]={landmark:(landdict[landmark][0][isp][loc],landdict[landmark][1][isp][loc])}
					# print "eredesdf"
					pass
	# pprint.pprint(ispdict['ide)				
	# sys.exit(0)
	mygraph=''
	for isp in ispdict:
		# print isp
		mygraph=graphcontent4HoplenbylandUrban
		mygraph=mygraph.replace('<LAND>',';'.join(rank_ASlen.keys()))
		mygraph=mygraph.replace('<ISP>',isp)
		# mygraph=mygraph.replace('<COLORS>',','.join(getcolors(rank_hoplen[landmark])))
		mygraph=mygraph.replace('<LAND_TAB>','\t'.join(rank_ASlen.keys()))
		mygraph+='\n'
		for loc in ispdict[isp]:
			mygraph+=(loc+'\t')
			for landmark in ispdict[isp][loc]:
				mygraph+=(ispdict[isp][loc][landmark][0]+'\t')
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for loc in ispdict[isp]:
			mygraph+=(loc+'\t')
			for landmark in ispdict[isp][loc]:
				mygraph+=(ispdict[isp][loc][landmark][1]+'\t')
			mygraph+='\n'			
		f=open('charts/urban/hoplen/'+isp,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/urban/hoplen/'+isp+' > '+'charts/urban/hoplen/'+isp+'.png')		


def hoplenbykeyloc(loctype):
	landdict={}
	for landmark in landlist_wanted_label:
		filelist=commands.getoutput('ls -1 hoplen/'+landmark).split('\n')
		locdict={}
		stddevdict={}
		for fname in filelist:
			loc=fname.split('_')[0]
			isp=fname.split('_')[1]
			if locaname[loc] in urban:
				f=open('hoplen/'+landmark+'/'+fname,'r')
				lines=f.readlines()
				k=[int(x.strip()) for x in lines]
				ispdict={}
				val=str(numpy.mean(k))
				stddev=str(numpy.std(k))
				if val=='nan':
					val='0'
				if stddev=='nan':
					stddev='0'
				if isp in locdict:
					locdict[isp][locaname[loc]]=val
					stddevdict[isp][locaname[loc]]=stddev
				else:
					locdict[isp]={}
					stddevdict[isp]={}
					locdict[isp][locaname[loc]]=val
					stddevdict[isp][locaname[loc]]=stddev
				# print landmark+'\t'+locaname[loc]+'\t'+isp+'\t'+str(numpy.mean(k))+'\t'+str(numpy.std(k))+'\t'+str(len(k))
				f.close()
		landdict[landmark]=(locdict,stddevdict)
	ispdict=defaultdict(dict)
	for landmark in landlist_wanted_label:		
		for isp in landdict[landmark][0]:			
			try:
				# print landdict[landmark][0][isp][loc]
				ispdict[isp][landmark]=(landdict[landmark][0][isp],landdict[landmark][1][isp])
			except Exception as e:
				# print e
				# raise
				pass
	mygraph=''
	for isp in ispdict:
		# print isp
		loclist=[]
		mygraph=graphcontent4HoplenbylandUrban
		for landmark in ispdict[isp]:
			mygraph+=(landlist_wanted_label[landmark]+'\t')
			for loc in ispdict[isp][landmark][0]:
				loclist.append(loc)	
				mygraph+=(ispdict[isp][landmark][0][loc]+'\t')
			mygraph+='\n'
		mygraph+='=yerrorbars\n'
		for landmark in ispdict[isp]:
			mygraph+=(landlist_wanted_label[landmark]+'\t')
			for loc in ispdict[isp][landmark][1]:			
				mygraph+=(ispdict[isp][landmark][1][loc]+'\t')
			mygraph+='\n'
		mygraph=mygraph.replace('<LOC>',';'.join(list(set(loclist))))
		mygraph=mygraph.replace('<ISP>',isp)
		mygraph=mygraph.replace('<TYPE>','Urban')
		mygraph=mygraph.replace('<LOC_TAB>','\t'.join(list(set(loclist))))
		mygraph+='\n'
		f=open('charts/urban/hoplen/'+isp,'w')
		f.write(mygraph)
		f.close()
		commands.getoutput('perl bargraph.pl -gnuplot -png -non-transparent charts/urban/hoplen/'+isp+' > '+'charts/urban/hoplen/'+isp+'.png')		


if __name__ == '__main__':
	# pervalence_overall()
	bufftrace_cdf_server()
	# hoplenbykeyloc()