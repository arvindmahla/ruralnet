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
import numpy
import requests
from collections import defaultdict
import itertools as it
from IPy import IP

"""TO BE RUN IN AMITSINGH. THIS GENERATES CSV OUTPUT.WHICH IS PASSED TO OTHER SCRIPT TO GET STATS"""
"""create a folder name tr in its directory"""


loc_isp={
	'rnm':['airtel','idea','mtnl'],
	'rnm0':['airtel','idea','mtnl'],
	'rnm2':['airtel','mtnl','reliance'],
	'rnm3':['airtel','mtnl','reliance','idea'],
	'rnm7':['mtnl','reliance','idea'],
	'rnm11':['airtel','mtnl','idea'],
	'rnm13':['airtel','mtnl','idea'],
	'rnm14':['airtel','mtnl','idea'],
	'rnm18':['airtel','mtnl','reliance'],
	'rnm31':['airtel','mtnl','idea'],
	'rnm101':['airtel','mtnl','idea']
}

log_path='/home/amitsingh/logs/logs/'
error_log_tr=open('error_ping_tr','w')
ipasmap=pickle.load(open('ipasmap1','rb'))	



def lenok(f,l):
	for item in l:
		if len(item)<=1:
			error_log_tr.write(f+'\n')
			return False
	return True

def ping_gw():
	fileprefix='ping_gw*'
	rttdict=defaultdict(dict)
	for loc in loc_isp:
		for isp in loc_isp[loc]:
			cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
			filelist=commands.getoutput(cmd).split('\n')
			for f in filelist:
				if f:
					timestamp=f.split('/')[8]
					rttlist=commands.getoutput('cat '+f+'| grep \"time=\" | cut -d\' \' -f7 | cut -d\'=\' -f2 ').split('\n')
					iplist=commands.getoutput('cat '+f+'| grep \"time=\" | cut -d\' \' -f4 | cut -d\':\' -f1 ').split('\n')
					l=len(rttlist)
					for i in range(0,l):
						if lenok(f,[timestamp,loc,isp,iplist[i],rttlist[i]]):
							print loc+','+timestamp+','+isp+','+iplist[i]+','+rttlist[i]

def ping_linode():
	fileprefix='ping_landmark_106-187-35-87*'
	for loc in loc_isp:
		# print loc
		for isp in loc_isp[loc]:
			# print isp
			cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
			#cmd='ls -1d '+log_path+loc+'/'+isp+'/experiments/*/* 2>/dev/null | grep '+fileprefix
			# print cmd
			filelist=commands.getoutput(cmd).split('\n')
			# print filelist
			for f in filelist:
				if f:
					timestamp=f.split('/')[8]
					rttlist=commands.getoutput('cat '+f+'| grep \"time=\" | cut -d\' \' -f7 | cut -d\'=\' -f2 ').split('\n')
					iplist=commands.getoutput('cat '+f+'| grep \"time=\" | cut -d\' \' -f4 | cut -d\':\' -f1 ').split('\n')
					l=len(rttlist)
					for i in range(0,l):
						if lenok(f,[timestamp,loc,isp,iplist[i],rttlist[i]]):
							print loc+','+timestamp+','+isp+','+iplist[i]+','+rttlist[i]


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
			try:
				ASinfo = requests.get('http://stat.ripe.net/data/prefix-overview/data.json?&resource='+ips).json()['data']['asns']
				# print ASinfo,ips
				if ASinfo:
					nw=ASinfo[0]['holder']
				else:
					nw='unknown'
			except requests.exceptions.ProxyError:
				nw='unknown'
		else:
			nw=isp
	if nw in ['AIRTELBROADBAND-AS-AP Bharti Airtel Ltd., Telemedia Services,IN','BHARTI-MOBILITY-AS-AP Bharti Airtel Ltd. AS for GPRS Service,IN',\
	'BBIL-AP BHARTI Airtel Ltd.,IN','IDEANET1-IN Idea Cellular Limited,IN','MTNL-AP Mahanagar Telephone Nigam Ltd.,IN',\
	'RELIANCE-COMMUNICATIONS-IN Reliance Communications Ltd.DAKC MUMBAI,IN','BSNL-NIB National Internet Backbone,IN']:
		nw=isp
	return nw

def latsinfra():
	fileprefix='*traceroute_server*'
	for loc in loc_isp:
		print loc
		for isp in loc_isp[loc]:
			ffile=open('tr/'+loc+'_'+isp+'.csv','w')
			print isp
			cmd='find '+log_path+loc+'/'+isp+'/experiments/ -name \"'+fileprefix+'\"'
			filelist=commands.getoutput(cmd).split('\n')
			for f in filelist:
				if f:
					timestamp=f.split('/')[8]
					domname=f.split('/')[-1:][0].split('_')[2].replace('-','.')
					trfile=open(f,'r')
					lines=trfile.readlines()
					lines=lines[2:-2]				
					if len(lines) > 2:
						if 'Selected' in lines[0]:
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
						trp=TracerouteParser(f,isp)
						trp.parse_data(tr_data)
						hlen=len(trp.hops)
						for hop in trp.hops:
							for probe in hop.probes:
									if probe.ipaddr!=None and probe.rtt!=None:
										NS=getnwinfo(probe.ipaddr,isp)
										if NS!='x':
											ffile.write(loc+','+timestamp+','+isp+','+str(hop.idx)+','+domname+','+probe.ipaddr+','+NS+','+str(probe.rtt)+'\n')
			ffile.close()											



if __name__ == '__main__':
	# latsinfra()
	# ping_gw()
	# ping_linode()