import pydot
import json
from tracerouteparser import TracerouteParser
import pprint
import pickle
import commands
from datetime import datetime
import sys
from sets import Set
from itertools import groupby
import random
import time
import numpy
import requests
import thread
import itertools as it
from collections import Counter,OrderedDict
from IPy import IP
import networkx as nx

""" Create infra folder here"""


loc_isp={
	'rnm':['airtel','idea','mtnl'],
	# 'rnm0':['idea'],
	'rnm0':['airtel','idea','mtnl'],
	'rnm2':['airtel','mtnl','reliance'],
	'rnm3':['airtel','mtnl','reliance','idea'],
	'rnm7':['mtnl','reliance','idea'],
	'rnm11':['airtel','mtnl','idea'],
	'rnm13':['airtel','mtnl','idea'],
	'rnm14':['airtel','mtnl','idea'],
	# 'rnm15':['airtel','mtnl','reliance','idea'],
	'rnm18':['airtel','mtnl','reliance'],
	'rnm31':['airtel','mtnl','idea'],
	'rnm101':['airtel','mtnl','idea']
}


log_path='/home/amitsingh/logs/logs/'
# error_log_gw=open('error_ping_gw','w')
# error_log_linode=open('error_ping_linode','w')
error_log_tr=open('error_ping_tr','w')
ipasmap=pickle.load(open('ipasmap2','rb'))	



def lenok(f,l):
	for item in l:
		if len(item)<=1:
			error_log_tr.write(f+'\n')
			return False
	return True

def getnwinfo(ips,isp):
	try:
		ip = IP(ips)
	except ValueError:
		return 'x'
	try:
		nw=ipasmap[ips]
		nw=nw.strip()
	except KeyError:			
		if ip.iptype()!='PRIVATE':
				nw='unknown'
		else:
			nw='PRIVATE'
	if nw in ['AIRTELBROADBAND-AS-AP Bharti Airtel Ltd.- Telemedia Services-IN','BHARTI-MOBILITY-AS-AP Bharti Airtel Ltd. AS for GPRS Service-IN',\
	'BBIL-AP BHARTI Airtel Ltd.-IN','IDEANET1-IN Idea Cellular Limited-IN','MTNL-AP Mahanagar Telephone Nigam Ltd.-IN',\
	'RELIANCE-COMMUNICATIONS-IN Reliance Communications Ltd.DAKC MUMBAI-IN','BSNL-NIB National Internet Backbone-IN']:
		nw=isp
	return nw

def hoplen_lastlat(loc,tid):
	fileprefix='*traceroute_server*'
	# print "In Thread "+tid
	for isp in loc_isp[loc]:
		# print isp
		cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
		filelist=commands.getoutput(cmd).split('\n')
		# filelist=['/home/amitsingh/logs/logs/rnm/airtel/experiments/1392778839/tcptraceroute_server_www-uol-com-br_1392780238.txt']
		for f in filelist:
			# try:
			if f:
				domname=f.split('/')[-1:][0].split('_')[2].replace('-','.')
				# commands.getoutput('mkdir -p hoplen/'+domname)
				# commands.getoutput('mkdir -p lastlat/'+domname)						
				timestamp=int(f.split('/')[8])
				# if timestamp < 1377973800:
				# 	nloc='rnm2'
				# else:
				# 	nloc=loc
				ffile=open('hoplen/'+domname+'/'+loc+'_'+isp,'a')
				ffile_maxlat=open('lastlat/'+domname+'/'+loc+'_'+isp,'a')	
				trfile=open(f,'r')
				lines=trfile.readlines()
				ftimestamp=f.split('/')[9].split('_')[3].split('.')[0]
				lines=lines[2:-2]				
				if len(lines) > 2:
					# print f
					if 'Selected' in lines[0]:
						lines.pop(0)
					# if 'Tracing' in lines[0]:
					# 	lines.pop(0)
					# elif 'traceroute' in lines[0]:
					# 	lines.pop(0)
					if 'Destination' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'libnet_write' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'setsockopt' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'Cannot' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'connect:' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'send' in lines[-1:][0]:
						lines.pop(len(lines)-1) 
					tr_data=''.join(lines)
					# print f					
					trp=TracerouteParser(f)
					# print f
					trp.parse_data(tr_data)
					hlen=len(trp.hops)
					if trp.dest_hopid!=None:
						ffile.write(str(trp.dest_hopid)+'\n')
					avgrtt=[]
					if hlen > 0:
						for probe in trp.hops[-1].probes:							
							if probe.ipaddr!=None and probe.rtt!=None and probe.ipaddr==trp.dest_ip:
								avgrtt.append(probe.rtt)
								# print probe.rtt
					res=str(numpy.mean(avgrtt))
					for rtt in avgrtt:
						ffile_maxlat.write(str(rtt)+'\n')
					# if res!='nan':							
					# 	ffile_maxlat.write(res+'\n')
					# for hop in trp.hops:
					# 	for probe in hop.probes:
					# 			if probe.ipaddr!=None and probe.rtt!=None:
					# 				NS=getnwinfo(probe.ipaddr,isp)
					# 				if NS!='x':
					# 					ffile.write(loc+','+timestamp+','+ftimestamp+','+isp+','+str(hop.idx)+','+domname+','+probe.ipaddr+','+NS+','+str(probe.rtt)+'\n')
				ffile.close()
				ffile_maxlat.close()
		print tid+':'+loc+'_'+isp+' done'

def hoplen_lat_inside(loc,tid):
	fileprefix='*traceroute_server*'
	# print "In Thread "+tid
	for isp in loc_isp[loc]:
		# print isp
		cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
		filelist=commands.getoutput(cmd).split('\n')
		# filelist=['/home/amitsingh/logs/logs/rnm/airtel/experiments/1392778839/tcptraceroute_server_www-uol-com-br_1392780238.txt']
		for f in filelist:
			# try:
			if f:
				domname=f.split('/')[-1:][0].split('_')[2].replace('-','.')
				commands.getoutput('mkdir -p infra/hoplen/'+domname)
				commands.getoutput('mkdir -p infra/lastlat/'+domname)						
				timestamp=int(f.split('/')[8])
				ffile=open('infra/hoplen/'+domname+'/'+loc+'_'+isp,'a')
				ffile_maxlat=open('infra/lastlat/'+domname+'/'+loc+'_'+isp,'a')	
				trfile=open(f,'r')
				lines=trfile.readlines()
				ftimestamp=f.split('/')[9].split('_')[3].split('.')[0]
				lines=lines[2:-2]				
				if len(lines) > 2:
					# print f
					if 'Selected' in lines[0]:
						lines.pop(0)
					# if 'Tracing' in lines[0]:
					# 	lines.pop(0)
					# elif 'traceroute' in lines[0]:
					# 	lines.pop(0)
					if 'Destination' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'libnet_write' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'setsockopt' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'Cannot' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'connect:' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'send' in lines[-1:][0]:
						lines.pop(len(lines)-1) 
					tr_data=''.join(lines)
					# print f					
					trp=TracerouteParser(f,isp)
					# print f
					trp.parse_data(tr_data)
					hlen=len(trp.hops)
					if trp.dest_hopid!=None:
						# print trp.infrahop,trp.dest_hopid
						ffile.write(str(trp.infrahop)+'\n')						
					avgrtt=[]
					# if trp.infrahop == None:
					# 	print f
					if hlen > 0:
						if trp.infrahop != None:
							for probe in trp.hops[trp.infrahop-1].probes:						
								if probe.ipaddr!=None and probe.rtt!=None:
									avgrtt.append(probe.rtt)
									# print probe.rtt
					res=str(numpy.mean(avgrtt))
					for rtt in avgrtt:
						ffile_maxlat.write(str(rtt)+'\n')
					# if res!='nan':							
					# 	ffile_maxlat.write(res+'\n')
					# for hop in trp.hops:
					# 	for probe in hop.probes:
					# 			if probe.ipaddr!=None and probe.rtt!=None:
					# 				NS=getnwinfo(probe.ipaddr,isp)
					# 				if NS!='x':
					# 					ffile.write(loc+','+timestamp+','+ftimestamp+','+isp+','+str(hop.idx)+','+domname+','+probe.ipaddr+','+NS+','+str(probe.rtt)+'\n')
				ffile.close()
				ffile_maxlat.close()
		print tid+':'+loc+'_'+isp+' done'		

def duration(loc,tid):
	fileprefix='*traceroute_server*'
	# print "In Thread "+tid
	for isp in loc_isp[loc]:
		# print isp
		cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
		filelist=commands.getoutput(cmd).split('\n')
		# filelist=['/home/amitsingh/logs/logs/rnm/airtel/experiments/1392778839/tcptraceroute_server_www-uol-com-br_1392780238.txt']
		for f in filelist:
			# try:
			if f:
				domname=f.split('/')[-1:][0].split('_')[2].replace('-','.')
				commands.getoutput('mkdir -p duration/'+domname)
				timestamp=int(f.split('/')[8])
				ffile=open('duration/'+domname+'/'+loc+'_'+isp,'a')
				ftimestamp=f.split('/')[9].split('_')[3].split('.')[0]
				ffile.write(ftimestamp+'\n')
				ffile.close()
		print tid+':'+loc+'_'+isp+' done'		

def ASlen(loc,tid):
	fileprefix='*traceroute_server*'
	# print "In Thread "+tid
	for isp in loc_isp[loc]:
		# print isp
		cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
		filelist=commands.getoutput(cmd).split('\n')
		# filelist=['/home/amitsingh/logs/logs/rnm/airtel/experiments/1392778839/tcptraceroute_server_www-uol-com-br_1392780238.txt']
		for f in filelist:
			# try:
			if f:
				domname=f.split('/')[-1:][0].split('_')[2].replace('-','.')
				commands.getoutput('mkdir -p ASlen/'+domname)
				# commands.getoutput('mkdir -p lastlat/'+domname)			
				ffile=open('ASlen/'+domname+'/'+loc+'_'+isp,'a')
				timestamp=f.split('/')[8]
				trfile=open(f,'r')
				lines=trfile.readlines()
				ftimestamp=f.split('/')[9].split('_')[3].split('.')[0]
				lines=lines[2:-2]				
				if len(lines) > 2:
					# print f
					if 'Selected' in lines[0]:
						lines.pop(0)
					# if 'Tracing' in lines[0]:
					# 	lines.pop(0)
					# elif 'traceroute' in lines[0]:
					# 	lines.pop(0)
					if 'Destination' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'libnet_write' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'setsockopt' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'Cannot' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'connect:' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'send' in lines[-1:][0]:
						lines.pop(len(lines)-1) 
					tr_data=''.join(lines)
					# print f					
					trp=TracerouteParser(f,isp)
					# print f
					trp.parse_data(tr_data)
					hlen=len(trp.hops)
					ASlist=[]
					for hop in trp.hops:
						for probe in hop.probes:
								if probe.ipaddr!=None and probe.rtt!=None:
									NS=getnwinfo(probe.ipaddr,isp)
									if NS!='x':							
										ASlist.append(NS)
					ffile.write(str(len(set(ASlist)))+'\n')
										# ffile.write(loc+','+timestamp+','+ftimestamp+','+isp+','+str(hop.idx)+','+domname+','+probe.ipaddr+','+NS+','+str(probe.rtt)+'\n')
				ffile.close()
		print tid+':'+loc+'_'+isp+' done'


def mergedict(l):
	d={}
	for item in l:
		key=item.keys()[0]
		d[key]=item[key]
	return d

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
 
    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)
 
    previous_row = xrange(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
 
    return previous_row[-1]

def paths(tree, cur=()):
    if not tree:
        yield cur
    else:
        for n, s in tree.items():
            for path in paths(s, cur+(n,)):
                yield path


def getpaths_gaps_overall(trp):
	child={}
	hoplist=[]
	for hop in reversed(trp.hops):
		node={}
		for probe in hop.probes:
			if probe.ipaddr!=None and probe.rtt!=None:
				node[probe.ipaddr]=child
				if hop.idx not in hoplist:
					hoplist.append(hop.idx)
		child=node
	gap=max(hoplist)-len(hoplist)
	a=paths(child)
	return list(paths(child)),gap

def getpaths_gaps_inside(trp,pos):
	child={}
	hoplist=[]
	for hop in reversed(trp.hops[:pos]):
		node={}
		hoplist.append(hop.idx)
		for probe in hop.probes:
			if probe.ipaddr!=None and probe.rtt!=None:
				node[probe.ipaddr]=child
		child=node
	gap=sorted(hoplist)[-1]-len(hoplist)
	return list(paths(child)),gap

def getpaths_gaps_outside(trp,pos):
	child={}
	hoplist=[]
	for hop in reversed(trp.hops[pos:]):
		node={}		
		for probe in hop.probes:
			if probe.ipaddr!=None and probe.rtt!=None:
				node[probe.ipaddr]=child
				hoplist.append(hop.idx)
		child=node
	# print len(trp.hops[pos:])
	gap=sorted(hoplist)[-1]-len(hoplist)
	pmap=paths(child)
	# pprint.pprint(child)
	return list(pmap),gap

def difference(s1,s2):
	if len(s1)==0:
		return True
	for item in s1:
		if item in s2:
			return True
	return False

def Isdiffpath(trp1,trp2,typ,pos):
	res=True
	s1=trp1.setlist(typ,pos)
	s2=trp2.setlist(typ,pos)
	for i in range(0,min(len(s1),len(s2))):
		if res==False:
			break
		res = res and difference(s1,s2)
	return res
	


def pathprevalance(domdict,isp,loc,typ):
	# ffile=open('dom/'+typ+'/'+loc+'_'+isp,'a')	
	for domname in domdict:

		paths=[]
		diffcount=0
		difflist=[]
		ipdict={}
		timedict=OrderedDict(sorted(mergedict(domdict[domname]).items()))
		i=0
		hopdict={}
		# print len(timedict.values())
		for trp in timedict.values():
			pos=0
			for hop in trp.hops:
				pos+=1
				if hop.idx==trp.infrahop:
					break
			# print pos,trp.infrahop,trp.fname
			if pos > 3 and trp.infrahop!=None:
				if len(trp.hops) > 0:
					if i!=0:
						if Isdiffpath(trp,paths[i-1],typ,pos):
							diffcount+=1
						pprint.pprint(trp.fname)
						pprint.pprint(trp.setlist('overall',pos))
						pprint.pprint(paths[i-1].fname)						
						pprint.pprint(paths[i-1].setlist('overall',pos))
						time.sleep(15)
					paths.append(trp)
					difflist.append(diffcount)
					i+=1
		c = Counter(difflist)
		# pprint.pprint(c)
		# sys.exit(0)
		m=max(c.values())
		tot=sum(c.values())
		# print domname+' '+str(float(m)/tot)+' '+str(len(domdict[domname]))
	# 	ffile.write(str(float(m)/tot)+'\n')
	# ffile.close()
		# print domname+'\t'+str(float(m)/tot)+'\n'
		# sys.exit(0)

def pervalence(loc,tid):
	fileprefix='*traceroute_server*'
	# print "In Thread "+tid
	for isp in loc_isp[loc]:
		print isp,loc
		cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
		filelist=commands.getoutput(cmd).split('\n')
		domdict={}
		# filelist=['/home/amitsingh/logs/logs/rnm/airtel/experiments/1392778839/tcptraceroute_server_www-uol-com-br_1392780238.txt']
		for f in filelist:
			# try:
			if f:
				domname=f.split('/')[-1:][0].split('_')[2].replace('-','.')
				# commands.getoutput('mkdir -p ASlen/'+domname)
				# commands.getoutput('mkdir -p lastlat/'+domname)			
				timestamp=f.split('/')[8]
				trfile=open(f,'r')
				lines=trfile.readlines()
				ftimestamp=f.split('/')[9].split('_')[3].split('.')[0]
				lines=lines[2:-2]				
				if len(lines) > 2:
					# print f
					if 'Selected' in lines[0]:
						lines.pop(0)
					# if 'Tracing' in lines[0]:
					# 	lines.pop(0)
					# elif 'traceroute' in lines[0]:
					# 	lines.pop(0)
					if 'Destination' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'libnet_write' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'setsockopt' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'Cannot' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'connect:' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'send' in lines[-1:][0]:
						lines.pop(len(lines)-1) 
					tr_data=''.join(lines)
					# print f					
					trp=TracerouteParser(f,isp)
					# print f
					trp.parse_data(tr_data)
					hlen=len(trp.hops)
					path=[]
					domdict.setdefault(domname,[]).append({int(ftimestamp):trp})
		pathprevalance(domdict,isp,loc,'overall')
		# pathprevalance(domdict,isp,loc,'inside')
		# pathprevalance(domdict,isp,loc,'outside')
		print tid+':'+loc+'_'+isp+' done'

def getmaxpairbyone(l):
	m=1
	val=''
	for (a,b) in l:
		if m < a:
			m=a
			val=b
	return (m,val)

def strongly_connected_components_iterative(vertices, edges):
    """
    This is a non-recursive version of strongly_connected_components_path.
    See the docstring of that function for more details.

    Examples
    --------
    Example from Gabow's paper [1]_.

    >>> vertices = [1, 2, 3, 4, 5, 6]
    >>> edges = {1: [2, 3], 2: [3, 4], 3: [], 4: [3, 5], 5: [2, 6], 6: [3, 4]}
    >>> for scc in strongly_connected_components_iterative(vertices, edges):
    ...     print(scc)
    ...
    set([3])
    set([2, 4, 5, 6])
    set([1])

    Example from Tarjan's paper [2]_.

    >>> vertices = [1, 2, 3, 4, 5, 6, 7, 8]
    >>> edges = {1: [2], 2: [3, 8], 3: [4, 7], 4: [5],
    ...          5: [3, 6], 6: [], 7: [4, 6], 8: [1, 7]}
    >>> for scc in  strongly_connected_components_iterative(vertices, edges):
    ...     print(scc)
    ...
    set([6])
    set([3, 4, 5, 7])
    set([8, 1, 2])

    """
    identified = set()
    stack = []
    index = {}
    boundaries = []

    for v in vertices:
        if v not in index:
            to_do = [('VISIT', v)]
            while to_do:
                operation_type, v = to_do.pop()
                if operation_type == 'VISIT':
                    index[v] = len(stack)
                    stack.append(v)
                    boundaries.append(index[v])
                    to_do.append(('POSTVISIT', v))
                    # We reverse to keep the search order identical to that of
                    # the recursive code;  the reversal is not necessary for
                    # correctness, and can be omitted.
                    to_do.extend(
                        reversed([('VISITEDGE', w) for w in edges[v]]))
                elif operation_type == 'VISITEDGE':
                    if v not in index:
                        to_do.append(('VISIT', v))
                    elif v not in identified:
                        while index[v] < boundaries[-1]:
                            boundaries.pop()
                else:
                    # operation_type == 'POSTVISIT'
                    if boundaries[-1] == index[v]:
                        boundaries.pop()
                        scc = set(stack[index[v]:])
                        del stack[index[v]:]
                        identified.update(scc)
                        yield scc

def longest_common_prefix(seq1, seq2):
	start = 0
	while start < min(len(seq1), len(seq2)):
		if seq1[start] != seq2[start]:
			break
		start += 1
	return len(seq1[:start])

bin8 = lambda x : ''.join(reversed( [str((x >> i) & 1) for i in range(8)] ) )

def chunks(l, n):
    if n < 1:
        n = 1
    return [l[i:i + n] for i in range(0, len(l), n)]

def getbinrep(ip32):
	l=chunks(ip32,8)
	return '.'.join([str(int(x,2)) for x in l])

def get32rep(ip):
	return ''.join([bin8(int(x)) for x in ip.split('.')])

def getprefix(ip,k):
	iprep=get32rep(ip)	
	return iprep[:k]

ans=None
def clusterIP(l):
	a={}
	ans=[]
	for i in range(0,len(l)):
		b={}
		ip1=l[i]
		for j in range(0,len(l)):
			if i!=j:
				ip2=l[j]
				b.setdefault(longest_common_prefix(get32rep(ip1),get32rep(ip2)),[]).append(ip2)
		for key in b:
			if key>=15:
				for item in b[key]:
					a.setdefault(ip1,[]).append(item)
		if ip1 not in a:
			a[ip1]=[]
	vertices=a.keys()
	edges=a
	for scc in strongly_connected_components_iterative(vertices,edges):
		ipl=list(scc)
		m=32
		for i in range(0,len(ipl)-1):
			k=longest_common_prefix(get32rep(ipl[i]),get32rep(ipl[i+1]))
			if m > k:
				m=k
		rest=''
		for i in range(0,32-m):
			rest+='0'
		ip=getprefix(ipl[0],m)
		ans.append(getbinrep(ip+rest))
	return ans


def draw(loc,ispdict):	
	graph = pydot.Dot('G', rankdir='LR',graph_type='digraph')
	for isp in ispdict:
		fname='PoP/'+loc+'_'+isp
		overallcluster=[]
		for domname in ispdict[isp]:
			a=''
			b=domname
			cluster=clusterIP(list(set(ispdict[isp][domname])))
			for item in cluster:
				a+=item+'\n'
				overallcluster.append(item)
			edge1=pydot.Edge(a,b)
			graph.add_edge(edge1)
			edgemain=pydot.Edge(loc,a)
			graph.add_edge(edgemain)
		f=open('PoP/'+loc+'_'+isp+'.txt','w')
		for ip in clusterIP(overallcluster):
			f.write(ip+'\n')
		f.close()
		# print [getnwinfo(x,isp) for x in clusterIP(overallcluster)]
		graph.write_png(fname+'.png')


def fun(loc,tid):
	fileprefix='*traceroute_server*'
	print "In Thread "+tid
	ispdict={}
	for isp in loc_isp[loc]:
		print isp
		cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
		filelist=commands.getoutput(cmd).split('\n')
		# filelist=['/home/amitsingh/logs/logs/rnm/airtel/experiments/1392778839/tcptraceroute_server_www-uol-com-br_1392780238.txt']
		PoPcandidate={}
		for f in filelist:
			# try:
			if f:
				
				timestamp=f.split('/')[8]
				domname=f.split('/')[-1:][0].split('_')[2].replace('-','.')
				trfile=open(f,'r')
				lines=trfile.readlines()
				ftimestamp=f.split('/')[9].split('_')[3].split('.')[0]
				lines=lines[3:-2]
				if lines:
					# print f
					if 'Selected' in lines[0]:
						lines.pop(0)
					if 'Tracing' in lines[0]:
						lines.pop(0)
					elif 'traceroute' in lines[0]:
						lines.pop(0)
					if 'Destination' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'libnet_write' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'setsockopt' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'Cannot' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'connect:' in lines[-1:][0]:
						lines.pop(len(lines)-1)
					elif 'send' in lines[-1:][0]:
						lines.pop(len(lines)-1) 
					tr_data=''.join(lines)
					trp=TracerouteParser()
					# print f
					trp.parse_data(tr_data)
					hlen=len(trp.hops)
					m=0
					val=None
					for hop in trp.hops:
						for probe in hop.probes:
								if probe.ipaddr!=None and probe.rtt!=None:
									NS=getnwinfo(probe.ipaddr,isp)
									if NS!='x':
										if NS==isp:
											if m <=hop.idx:
												m=hop.idx
												val=probe.ipaddr
					if val:			
						PoPcandidate.setdefault(domname,[]).append(val)
			# pprint.pprint(set(PoPcandidate['8.8.8.8']))
			# sys.exit(0)
		ispdict[isp]=PoPcandidate
		# pprint.pprint(set(PoPcandidate[]))
		# sys.exit(0)
		print tid+': PoP/'+loc+'_'+isp+'.csv done'
	draw(loc,ispdict)

def latsinfra():
	i=0
	for loc in loc_isp:
		try:
			i+=1
			thread.start_new_thread(hoplen_lat_inside,(loc,str(i)))
		except Exception as e:
		   print "Error: unable to start thread"

	while 1:
	    pass



if __name__ == '__main__':
	# for loc in loc_isp:
	# 	pervalence(loc,'2')
	# hoplen_lastlat('rnm3','2')
	# clusterIP(['182.79.247.50', '182.79.247.106', '182.79.247.54', '203.101.100.74'])
	latsinfra()