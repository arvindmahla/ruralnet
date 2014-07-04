import sys
def main(locid):
	f=open('tests','r')
	lines=f.readlines()
	newtxt=''
	for line in lines:
		newtxt+=line.replace('LOCID',locid)
	print newtxt

if __name__ == '__main__':
	main(sys.argv[1])