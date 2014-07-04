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
import operator
import scipy.stats


CDN_PROVIDER  = [
    [".akamai.net", "Akamai"],
    [".akafms.net","Akamai"],
    [".akamaiedge.net", "Akamai"],
    [".llnwd.net", "Limelight"],
    ["edgecastcdn.net", "EdgeCast"],
    ["hwcdn.net", "Highwinds"],
    [".panthercdn.com", "Panther"],
    [".simplecdn.net", "Simple CDN"],
    [".instacontent.net", "Mirror Image"],
    [".footprint.net", "Level3"],
    [".ay1.b.yahoo.com", "Yahoo"],
    [".yimg.", "Yahoo"],
    ["googlesyndication.", "Google"],
    [".gstatic.com", "Google"],
    [".googleusercontent.com", "Google"],
    [".internapcdn.net", "Internap"],
    [".cloudfront.net", "Amazon Cloudfront"],
    [".netdna-cdn.com", "MaxCDN"],
    [".netdna-ssl.com", "MaxCDN"],
    [".netdna.com", "MaxCDN"],
    [".cotcdn.net", "Cotendo"],
    [".cachefly.net", "Cachefly"],
    ["bo.lt", "BO.LT"],
    [".cloudflare.com", "Cloudflare"],
    [".afxcdn.net", "afxcdn.net"],
    [".lxdns.com", "lxdns.com"],
    [".att-dsa.net", "AT&T"],
    [".vo.msecnd.net", "Windows Azure"],
    [".voxcdn.net", "Voxel"],
    [".bluehatnetwork.com", "Blue Hat Network"],
    [".swiftcdn1.com", "SwiftCDN"],
    [".rncdn1.com", "Reflected Networks"],
    [".cdngc.net", "CDNetworks"],
    [".fastly.net", "Fastly"],
    [".gslb.taobao.com", "Taobao"],
    [".gslb.tbcache.com", "Alimama"],
    [".doubleclick.net", "Google Ad"],
    [".googlesyndication.com", "Google Ad"],
]

graphcontent4pltbyisp="""
=cluster;<ISPLIST>
=table<SORTED>
title=<TITLE>
yformat=%gsec
rotateby=-45
legendx=right
max=150
legendy=center
xlabelshift=0,-5
=nogridy
ylabel=<TITLE>
xlabel=Landmarks
# stretch it out in x direction
xscale=1.4
yscale=1.2
=table
#	<ISPLIST_TAB>
"""


def finder(host):
    result = None
    for cdn in CDN_PROVIDER:
        if cdn[0] in host:
            return cdn[1]
    return None

def findcdnfromhost(host, dnsip = "8.8.8.8"):
 	res = dns.resolver.Resolver()
	try:
		r = res.query(host)
		newhost=r.canonical_name.to_text()
	except Exception as e:
		return None
	return finder(newhost)

isplist=['mtnl3g1','airtel2g','airtel3g','reliancecdma']#,'reliancehsdpa']
f=open('landmarks.txt','r')
landmarkList=f.readlines()
f.close()
def main():
	ispdict={}
	for isp in isplist:
		folderdict={}
		urldict={}
		folderlist=commands.getoutput('ls -1 '+isp+'/').split('\n')
		for folder in folderlist:
			path=isp+'/'+folder+'/'
			filelist=commands.getoutput('ls -1d '+isp+'/'+folder+'/* | grep  navtimings_').split('\n')
			dumplist=commands.getoutput('ls -1d '+isp+'/'+folder+'/* | grep  cap').split('\n')
			for dumpfile in dumplist:
				print dumpfile
				urld={}
				landmarkname=dumpfile.split('/')[2].split('_')[0]
				rttlist=commands.getoutput('tcptrace -nlr '+dumpfile+' | grep \"RTT avg:\" | tr -s \' \' | cut -d\' \' -f4 2>/dev/null').split('\n')
				rttlist=[x for x in rttlist if ' ' not in x]
				urllist=commands.getoutput('tshark -n -r '+dumpfile+' -T fields -e http.request.full_uri -e tcp.stream 2>/dev/null').split('\n')
				for url in urllist:
					data=url.split('\t')
					if len(data[0]) > 1 and len(data[1])!=0:
						urld[data[0]]=float(rttlist[int(data[1])])
				urldict.setdefault(landmarkname,[]).append(urld)
			for navfile in filelist:
				landmarkname=navfile.split('/')[2].split('_')[1]
				data=pickle.load(open(navfile,'rb'))
				folderdict.setdefault(landmarkname,[]).append(data)
			# filelist=commands.getoutput('ls -1d '+isp+'/'+folder+'/* | grep cap').split('\n')
			# commands.getoutput('mkdir -p '+isp+'/'+folder+'/'+'dhttp')
			# for dumpfile in filelist:
			# 	landmarkname=dumpfile.split('/')[2].split('_')[0]
			# 	# print dumpfile.split('/')[2]
			# 	f=open(isp+'/'+folder+'/'+'dhttp/'+landmarkname+'_http','w')
			# 	p=sub.Popen(['tcptrace','--output_dir=``trace\'\'','-n','-xhttp',dumpfile],stdout=f)
			# 	p.wait()
			# 	f.close()
		ispdict[isp]=(folderdict,urldict)
	# pprint.pprint(ispdict)
	pickle.dump(ispdict,open('navresdata','wb'))


def hashresd(resd):
	d={}
	for i in range(0,len(resd)):
		d[resd[i]['url']]=i
	return d

class InvalidRecord(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return self.value

def process(item,origin):
	urldict=item[1]
	# pprint.pprint(len(urldict.keys()))
	# pprint.pprint(urldict)
	# sys.exit(0)
	hardata=item[0][2]
	resD=item[0][1]
	plt=item[0][0]['duration']
	totObj=len(hardata['log']['entries'])
	pSize=0.0
	hashrsd=hashresd(resD)
	cdndict={}
	for entry in hardata['log']['entries']:
		if entry['response']['status']==200:
			pSize+=float(entry['response']['bodySize'])/1024
			url=entry['request']['url'].replace(',','-')
			hostname=url.split('/')[2]
			cdn=findcdnfromhost(hostname)
			# print cdn,hostname
			if cdn==None:
				cdn=hostname
			try:
				time=resD[hashrsd[entry['request']['url']]]['duration']
			except KeyError:
				time=entry['time']
			try:
				rtt=urldict[str(entry['request']['url'])]
			except KeyError:
				frdict={}
				for urls in urldict.keys():
					r=fuzz.ratio(urls,str(entry['request']['url']))
					frdict[r]=urls
				rtt=urldict[frdict[max(frdict.keys())]]
			try:
				cdndict.setdefault(cdn,[]).append((time,rtt,float(entry['response']['bodySize'])/1024))
			except ZeroDivisionError:
				pass

	if not cdndict:
		raise InvalidRecord('InvalidRecord')
	m=0
	for key in cdndict:
		if m < len(cdndict[key]):
			m=len(cdndict[key])
			k=key
	# print cdndict.keys()
	clubcdndict={}
	if cdndict:
		for key in cdndict:
			if key==k:
				clubcdndict['primary']=cdndict[key]
			elif key==origin or key=='www.'+origin:
				clubcdndict['origin']=cdndict[key]
			else:
				tlist=[]
				for p in cdndict[key]:
					tlist.append(p)
				clubcdndict['nonprimary']=tlist
            
	# pprint.pprint(clubcdndict)
	if 'primary' not in clubcdndict.keys():
		clubcdndict['primary']=[]
	if 'nonprimary' not in clubcdndict.keys():
		clubcdndict['nonprimary']=[]
	nprimecdn=len(clubcdndict['primary'])
	n_primecdn=len(clubcdndict['nonprimary'])
	sprimecdn=sum([z for (x,y,z) in clubcdndict['primary']])
	s_primecdn=sum([z for (x,y,z) in clubcdndict['nonprimary']])
	try:
		origintime=numpy.median([y for (x,y,z) in clubcdndict['origin']])
		cdntime=numpy.median([y for (x,y,z) in clubcdndict['primary']])
		cdnimp=(origintime-cdntime)*100/origintime
	except KeyError:
		origintime=numpy.median([y for (x,y,z) in clubcdndict['primary']])
		cdnimp=0
	# O=[]
	# C=[]
	#for (a,b) in clubcdndict['origin']:
	# 	if b!=0:
	# 		O.append(a/b)
	# for (a,b) in clubcdndict['primary']:
	# 	if b!=0:
	# 		C.append(a/b)
	# avgTimePerByteOrigin=numpy.mean(O)
	# avgTimePerByteCDN=numpy.mean(C)
	#origintime=0#avgTimePerByteOrigin*100
	#CDNTime=avgTimePerByteCDN*100
	#cdnimp=0#((origintime-CDNTime)*100)/origintime
	return plt,totObj,pSize,k,nprimecdn,sprimecdn,n_primecdn,s_primecdn,origintime,cdnimp

aftboundry={
'airindia.com':'http://airindia.com/Images/f-button.gif',
'espncricinfo.com':'http://i.imgci.com/espncricinfo/ciSprites58.gif',
# 'flipkart.com':'http://s3-ap-southeast-1.amazonaws.com/wk-static-files/webengage/feedbacktab/~537e09f.png',
'flipkart.com':'http://b.scorecardresearch.com/beacon.js',
'incometaxreview.com':'http://incometaxindia.gov.in/ITPrototype/images/rmenu11.jpg',
'incredibleindia.org':'http://incredibleindia.org/images/home/black-slider/calendar.jpg',
'jharkhand.gov.in':'http://jharkhand.gov.in/documents/12205/0/acts.jpg?t=1387523290512',
'makemytrip.com':'http://d6tizftlrpuof.cloudfront.net/live/resources/buttons/usabilla_black_rightSideImprove.png',
'morth.nic.in':'http://morth.nic.in/images/bullet1.gif',
'mponline.gov.in':'http://www.mponline.gov.in/Quick%20Links/PortalImages/MenuImages/CitizenS.png',
'nrega.nic.in':'http://nrega.nic.in/netnrega/images/middle_s.gif',
'passportindia.gov.in':'http://passportindia.gov.in/AppOnlineProject/images/bt_grey.gif',
'timesofindia.indiatimes.com':'https://ssl.gstatic.com/images/icons/gplus-16.png',
'uk.gov.in':'http://uk.gov.in/files/icons/morearrow.jpg',
'wikipedia.org':'http://upload.wikimedia.org/wikipedia/meta/0/08/Wikipedia-logo-v2_1x.png',
'yatra.com':'http://css.yatra.com/content/fresco/default/images/FareFinder-graph.png',
'irctc.co.in':'http://irctc.co.in/beta_images/plus_icon_home.gif',
'youtube.com':'http://i1.ytimg.com/i/Ah9DbAZny_eoGFsYlH2JZw/1.jpg'

}




def PLT(item,landmark):
	hardata=item[2]
	pageStart=iso8601.parse_date(hardata['log']['pages'][0]['startedDateTime'])
	dtlist=[]
	for entry in hardata['log']['entries']:
		entryStart=iso8601.parse_date(entry['startedDateTime'])
		entrytime=entry['time']
		dtlist.append((entryStart,entrytime))
	dtlist.sort(key=lambda x: x[0])
	last=dtlist[-1:][0]
	tottime=float((last[0]-pageStart).total_seconds())+float(last[1])/1000
	return tottime


def AFT(item,landmark,isp):
	hardata=item[2]
	tottime=PLT(item,landmark)
	if landmark not in aftboundry:
		return tottime
	afturl=aftboundry[landmark]
	aft=None
	pageStart=iso8601.parse_date(hardata['log']['pages'][0]['startedDateTime'])	
	for entry in hardata['log']['entries']:
		if entry['request']['url']==afturl:
			# print entry['request']['url']
			# print landmark,entry['request']['url']
			entryStart=iso8601.parse_date(entry['startedDateTime'])
			entrytime=entry['time']
			elapsedTime=entryStart-pageStart
			aft=float(elapsedTime.total_seconds())+float(entrytime)/1000
	# sys.exit(0)
	if aft==None:		
		# return hardata['log']['pages'][0]['pageTimings']['onLoad']
		return tottime
	return aft

def detectBottleneck(item,landmark):
	hardata=item[2]
	percentage={}
	blocked=0
	wait=0
	ssl=0
	dns=0
	connect=0
	time=0
	for entry in hardata['log']['entries']:
		if 'timings' in entry:
			blocked+=entry['timings']['blocked']
			wait+=entry['timings']['wait']
			ssl+=entry['timings']['ssl']
			dns+=entry['timings']['dns']
			connect+=entry['timings']['connect']
			time+=entry['time']
	if time!=0:
		percentage[float(blocked)/time]='blocked'
		percentage[float(wait)/time]='wait'
		percentage[float(ssl)/time]='ssl'
		percentage[float(dns)/time]='dns'
		percentage[float(connect)/time]='connect'
		mkey=sorted(percentage.keys())[-1:][0]
		return percentage[mkey]
	else:
		return '\t'



def maxBottle(l):
	c=Counter(l).most_common(len(l))
	return c[0][0]

urldict={
'facebook.com':'facebook.com',
'timesofindia.indiatimes.com':'timesofindia.indiatimes.com',
'google.co.in':'google.co.in',
'youtube.com':'youtube.com',
'irctc.co.in':'irctc.co.in',
'wikipedia.org':'wikipedia.org',
'espncricinfo.com':'espncricinfo.com',
'flipkart.com':'flipkart.com',
'mponline.gov.in':'mponline.gov.in/portal/index.aspx?langid=en-US',
'nrega.nic.in':'nrega.nic.in/netnrega/home.aspx',
'jharkhand.gov.in':'jharkhand.gov.in',
'uk.gov.in':'uk.gov.in/home/index1',
'morth.nic.in':'morth.nic.in',
'airindia.com':'airindia.com',
'yatra.com':'yatra.com',
'makemytrip.com':'makemytrip.com',
'incredibleindia.org':'incredibleindia.org',
'passportindia.gov.in':'passportindia.gov.in/AppOnlineProject/welcomeLink',
'incometaxindia.gov.in':'incometaxindia.gov.in/home.asp'
}

website={
	'gov':[
		'irctc.co.in',
		'mponline.gov.in',
		'nrega.nic.in',
		'jharkhand.gov.in',
		'uk.gov.in',
		'morth.nic.in',
		'airindia.com',
		'passportindia.gov.in',
		'incometaxindia.gov.in'
	],
	'non-gov':[
		'facebook.com',
		'timesofindia.indiatimes.com',
		'google.co.in',
		'youtube.com',
		'wikipedia.org',
		'espncricinfo.com',
		'flipkart.com',
		'makemytrip.com',
		'yatra.com',
		'incredibleindia.org'
	],
	'cdn':[
		'facebook.com',
		'timesofindia.indiatimes.com',
		'espncricinfo.com',
		'flipkart.com',
		'google.co.in',
		'youtube.com',
		'makemytrip.com',
		'yatra.com',
		'incredibleindia.org',
		'irctc.co.in',
		'mponline.gov.in',
		'nrega.nic.in',
		'jharkhand.gov.in',
		'uk.gov.in',
		'morth.nic.in',
		'airindia.com',
		'passportindia.gov.in',
		'incometaxindia.gov.in'
	]

}

def redirectpenalty(item,landmark):
	hardata=item[2]
	firstreq=None
	secreq=None
	for entry in hardata['log']['entries']:
		if entry['request']['url']=='http://'+urldict[landmark]+'/' and entry['response']['status']==301:
			firstreq=entry['startedDateTime']
			# print entry['request']['url']
	# print firstreq
	if firstreq!=None:
		for entry in hardata['log']['entries']:
			if entry['request']['url']=='http://www.'+urldict[landmark]+'/' and entry['response']['status']==200:
				secreq=entry['startedDateTime']
				# print entry['request']['url']
	# print secreq
	if secreq!=None:
		return (iso8601.parse_date(secreq)-iso8601.parse_date(firstreq)).total_seconds()
	else:
		return 0


def hardata():
	resdata=pickle.load(open('navresdata','rb'))
	# pprint.pprint(resdata['reliancecdma'][0]['incredibleindia.org'][15])
	# sys.exit(0)
	urllist=[]
	for isp in resdata:
		for landmark in resdata[isp][0]:#:['facebook.com']:#
			l={}
			for i in range(0,len(resdata[isp][0][landmark])):
				# print resdata[isp][0][landmark][i]	
				item=resdata[isp][0][landmark][i]
				pLoadTime=PLT(item,landmark)
				AboveFoldTime=AFT(item,landmark,isp)
				Bottleneck=detectBottleneck(item,landmark)
				RedirectPenalty=redirectpenalty(item,landmark)#RedirectPenalty=
				l.setdefault('PLT',[]).append(pLoadTime)
				l.setdefault('AFT',[]).append(AboveFoldTime)
				l.setdefault('Btlneck',[]).append(Bottleneck)
				l.setdefault('RedirectPenalty',[]).append(RedirectPenalty)

			# pprint.pprint(l['RedirectPenalty'])
			f=open('PLT/PLT/'+landmark+'_'+isp,'w')
			for item in l['PLT']:
				f.write(str(item)+'\n')
			f.close()
			f=open('PLT/AFT/'+landmark+'_'+isp,'w')
			for item in l['AFT']:
				f.write(str(item)+'\n')
			f.close()
			f=open('PLT/redPen/'+landmark+'_'+isp,'w')
			for item in l['RedirectPenalty']:
				f.write(str(item)+'\n')
			f.close()						
			MBottleneck=maxBottle(l['Btlneck'])			
			# print isp+'\t'+landmark+'\t'+str(numpy.mean(l['PLT']))+'\t'+str(numpy.std(l['PLT']))#+'\t'+isp+'\t'+landmark+'\t'+str(numpy.mean(l['AFT']))+'\t'+str(numpy.std(l['AFT']))+'\t'+isp+'\t'+landmark+'\t'+str(numpy.mean(l['RedirectPenalty']))+'\t'+str(numpy.std(l['RedirectPenalty']))+'\t'+MBottleneck

def resData():
	resdata=pickle.load(open('navresdata','rb'))
	# pprint.pprint(resdata)
	# sys.exit(0)
	urllist=[]
	for isp in resdata:
		for landmark in resdata[isp]:
			for item in resdata[isp][landmark]:
				resDataa=item[1]
				# print isp,landmark
				for entry in resDataa:
					url=entry['url'].replace(',','-')
					print isp+','+landmark+','+url+','+str(entry['duration'])
	# pprint.pprint(set(urllist))

isplabel={
	'airtel3g':'Airtel UMTS',
	'airtel2g':'Airtel EDGE',
	'mtnl3g1':'MTNL UMTS',
	'reliancecdma':'Reliance 1xEVDO'
}

def stat(typ,maxY,param,title,sort=False,time=True):
	resdata=pickle.load(open('navresdata','rb'))
	urllist=[]
	landdict=defaultdict(dict)
	isplist=[]
	for isp in resdata:
		for landmark in resdata[isp][0]:
			l={}
			for i in range(0,len(resdata[isp][0][landmark])):
				item=resdata[isp][0][landmark][i]
				pLoadTime=PLT(item,landmark)
				AboveFoldTime=AFT(item,landmark,isp)
				Bottleneck=detectBottleneck(item,landmark)
				RedirectPenalty=redirectpenalty(item,landmark)
				l.setdefault('PLT',[]).append(pLoadTime)
				l.setdefault('AFT',[]).append(AboveFoldTime)
				l.setdefault('Btlneck',[]).append(Bottleneck)
				l.setdefault('RedirectPenalty',[]).append(RedirectPenalty)
				l.setdefault('NumObjs',[]).append(len(item[2]['log']['entries']))
				l.setdefault('UX',[]).append(AboveFoldTime/pLoadTime)
			landdict[landmark][isplabel[isp]]=l
		isplist.append(isplabel[isp])
	mygraph=graphcontent4pltbyisp
	if sort==True:
		mygraph=mygraph.replace('<SORTED>','\n=sortdata_ascend\n')
	if time==False:
		mygraph=mygraph.replace('sec','')
	if maxY==-1:
		mygraph=mygraph.replace('\nmax=150\n','\n')
	else:
		mygraph=mygraph.replace('\nmax=150\n','\nmax='+str(maxY)+'\n')
	mygraph=mygraph.replace('<TITLE>',title)
	mygraph=mygraph.replace('<ISPLIST>',';'.join(isplist))
	mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(isplist))
	mygraph+='\n'
	for landmark in website[typ]:
		mygraph+=(landmark+avgObj[landmark]+'\t')
		for isp in landdict[landmark]:
			mygraph+=(str(numpy.mean(landdict[landmark][isp][param]))+'\t')
		mygraph+='\n'
	mygraph+='=yerrorbars\n'
	for landmark in website[typ]:
		mygraph+=(landmark+avgObj[landmark]+'\t')
		for isp in landdict[landmark]:
			mygraph+=(str(numpy.std(landdict[landmark][isp][param]))+'\t')
		mygraph+='\n'
	fname='charts/'+param+'_'+typ
	pprint.pprint(fname)
	f=open(fname,'w')
	f.write(mygraph)
	f.close()
	commands.getoutput('bargraph.pl -gnuplot -png -non-transparent '+fname+' > '+fname+'.png')	

def statbynumobj(typ,maxY,param,title,sort=False,time=True):
	resdata=pickle.load(open('navresdata','rb'))
	urllist=[]
	landdict=defaultdict(dict)
	isplist=[]
	for isp in resdata:
		for landmark in resdata[isp][0]:
			l={}
			for i in range(0,len(resdata[isp][0][landmark])):
				item=resdata[isp][0][landmark][i]
				pLoadTime=PLT(item,landmark)
				AboveFoldTime=AFT(item,landmark,isp)
				Bottleneck=detectBottleneck(item,landmark)
				RedirectPenalty=redirectpenalty(item,landmark)
				l.setdefault('PLT',[]).append(pLoadTime)
				l.setdefault('AFT',[]).append(AboveFoldTime)
				l.setdefault('Btlneck',[]).append(Bottleneck)
				l.setdefault('RedirectPenalty',[]).append(RedirectPenalty)
				l.setdefault('NumObjs',[]).append(len(item[2]['log']['entries']))
				l.setdefault('UX',[]).append(AboveFoldTime/pLoadTime)
			landdict[landmark][isplabel[isp]]=l
	mygraph=graphcontent4pltbyisp
	if sort==True:
		mygraph=mygraph.replace('<SORTED>','\n=sortdata_ascend\n')
	if time==False:
		mygraph=mygraph.replace('sec','')
	if maxY==-1:
		mygraph=mygraph.replace('\nmax=150\n','\n')
	else:
		mygraph=mygraph.replace('\nmax=150\n','\nmax='+str(maxY)+'\n')
	pprint.pprint(isplist)
	mygraph=mygraph.replace('<TITLE>',title)
	mygraph=mygraph.replace('<ISPLIST>',';'.join(isplist))
	mygraph=mygraph.replace('<ISPLIST_TAB>','\t'.join(isplist))
	mygraph+='\n'
	avgObj={}
	for landmark in website[typ]:
		objs=[]
		for isp in landdict[landmark]:
			print isp
			objs.append(numpy.mean(landdict[landmark][isp]['NumObjs']))
		avgObj[landmark]=round(numpy.mean(objs),2)
	sorted_Obj = sorted(avgObj.iteritems(), key=operator.itemgetter(1))
	pprint.pprint(avgObj)
	# sys.exit(0)
	for (landmark,avg) in sorted_Obj:
		mygraph+=(landmark+'('+str(avg)+')\t')
		for isp in landdict[landmark]:
			mygraph+=(str(numpy.mean(landdict[landmark][isp][param]))+'\t')
		mygraph+='\n'
	mygraph+='=yerrorbars\n'
	for (landmark,avg) in sorted_Obj:
		mygraph+=(landmark+'('+str(avg)+')\t')
		for isp in landdict[landmark]:
			mygraph+=(str(numpy.std(landdict[landmark][isp][param]))+'\t')
		mygraph+='\n'
	fname='charts/'+param+'_'+typ
	pprint.pprint(fname)
	f=open(fname,'w')
	f.write(mygraph)
	f.close()
	commands.getoutput('bargraph.pl -gnuplot -png -non-transparent '+fname+' > '+fname+'.png')	


def correlation():
	resdata=pickle.load(open('navresdata','rb'))
	urllist=[]
	landdict=defaultdict(dict)
	isplist=[]
	for isp in resdata:
		for landmark in resdata[isp][0]:
			l={}
			for i in range(0,len(resdata[isp][0][landmark])):
				item=resdata[isp][0][landmark][i]
				pLoadTime=PLT(item,landmark)
				AboveFoldTime=AFT(item,landmark,isp)
				Bottleneck=detectBottleneck(item,landmark)
				RedirectPenalty=redirectpenalty(item,landmark)
				l.setdefault('PLT',[]).append(pLoadTime)
				l.setdefault('AFT',[]).append(AboveFoldTime)
				l.setdefault('Btlneck',[]).append(Bottleneck)
				l.setdefault('RedirectPenalty',[]).append(RedirectPenalty)
				l.setdefault('NumObjs',[]).append(len(item[2]['log']['entries']))
				l.setdefault('UX',[]).append(AboveFoldTime/pLoadTime)
			landdict[landmark][isplabel[isp]]=l
	ldict=defaultdict(dict)
	idict=defaultdict(dict)
	for land in landdict:		
		for isp in landdict[land]:
			ldict[isp][land]=numpy.mean(landdict[land][isp]['UX'])
			idict[land][isp]=numpy.mean(landdict[land][isp]['UX'])
	ldict=dict(ldict)
	idict=dict(idict)
	# pprint.pprint(dict(ldict))
	for (x,y) in [('Airtel UMTS','Reliance 1xEVDO'),('Airtel UMTS','Airtel EDGE'),('Airtel UMTS','MTNL UMTS'),\
	('Reliance 1xEVDO','Airtel EDGE'),('Reliance 1xEVDO','MTNL UMTS'),('Airtel EDGE','MTNL UMTS')]:
		X=[]
		Y=[]
		# print '-------------------------------------------------------'
		# print 'Landmark'+'\t'+x+'\t'+y
		# print '-------------------------------------------------------'
		for land in ldict[x]:
			if ldict[x][land] < 1:
				# print land+'\t'+str(ldict[x][land])+'\t'+str(ldict[y][land])
				X.append(ldict[x][land])
				# print ldict[x][land]
		# print '-------------------------------------------------------'				
		for land in ldict[x]:
			if ldict[x][land] < 1:
				# print land+'\t'+str(ldict[x][land])+'\t'+str(ldict[y][land])
				Y.append(ldict[y][land])
				# print ldict[y][land]

		# print '-------------------------------------------------------'
		print x+'\t'+y+'\t'+str(scipy.stats.spearmanr(X,Y)[0])
		# print '-------------------------------------------------------'

	# print idict.keys()
	# for (x,y) in [('airindia.com','incredibleindia.org'),('incredibleindia.org','flipkart.com')\
	# ,('irctc.co.in','makemytrip.com'),('wikipedia.org','passportindia.gov.in'),('incometaxindia.gov.in', 'timesofindia.indiatimes.com')\
	# ,('irctc.co.in', 'yatra.com'),('uk.gov.in', 'incometaxindia.gov.in'),('jharkhand.gov.in', 'wikipedia.org')]:
	# 	X=[]
	# 	Y=[]
	# 	for isp in idict[x]:
	# 		# print land
	# 		X.append(idict[x][isp])
	# 	# print "dsdsds"
	# 	for isp in idict[y]:
	# 		# print land
	# 		Y.append(idict[y][isp])	
	# 	# pprint.pprint(X)
	# 	# pprint.pprint(Y)
	# 	print x+'\t'+y
	# 	print scipy.stats.spearmanr(X,Y)
		# for 
		# pprint.pprint(scipy.stats.spearmanr(landdict[land]['Airtel UMTS']['UX'],landdict[land]['Airtel EDGE']['UX']))


if __name__ == '__main__':
	correlation()
	# main()
	# stat('gov',150,'AFT','Above The Fold Time',True)
	# stat('non-gov',150,'AFT','Above The Fold Time',True)
	# stat('gov',150,'PLT','Page Load Time',True)
	# stat('non-gov',150,'PLT','Page Load Time',True)
	# stat('cdn',150,'PLT','Page Load Time')
	# stat('gov',-1,'NumObjs','Number of Objects fetched',True,False)
	# stat('non-gov',-1,'NumObjs','Number of Objects fetched',True,False)
	# stat('cdn',-1,'NumObjs','Number of Objects fetched',False,False)
	# stat('gov',-1,'UX','PLT / AFT ratio',True,False)
	# stat('non-gov',-1,'UX','PLT / AFT ratio',True,False)
	# stat('cdn',-1,'UX','PLT / AFT ratio',False,False)
	# statbynumobj('cdn',300,'PLT','Page Load Time',True)
	# resData()