
import landiscover
import paramiko
import time
import sys
import subprocess
import os
import socket



def pinging():
	print "Stand by, it's gonna take a second or so..."
	
	base_input = ['ping','192.168.10']
	start_time = int(time.time()*1000)
	if 1 == len(base_input):
		pinged_address_list = landiscover.landiscover()
	elif 2 == len(base_input):
		pinged_address_list = landiscover.landiscover(base_input[1])
	else:
		# throw an error
		pass
	end_time = int(time.time()*1000)
	
	print ("In " + str(end_time-start_time) + " ms, found " + 
			str(len(pinged_address_list)) + " IP addresses:")
	print pinged_address_list
	return pinged_address_list
	
def readvoltages(r1): 
	r2 = r1[str.find (r1,"ppset"):] 
	r3 = r2[str.find (r2,","):] 
	r4 = r3[str.find (r3," ")+1:] 
	r5 = r4[str.find (r4," ")+1:] 
	r7 = r5[:str.find (r5," ")] 
	r6 = r4[:str.find (r4,",")] 
	return r6 , r7 
	
#-----------------------------------------------------LIBRARY CONNECTION TO TELNET---------------------------
def connect_ssh(IP, user, pss):
	print 'Connecting via SSH'
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	start_time = time.time()
	is_connected = False
	for attempt in range (60) :
                try:
					ssh.connect(IP, port=22, username=user, password=pss,timeout=4.0)
					is_connected = True
					break
                except:
                        print ("ssh not connected after %.0f s"%(time.time()-start_time))
						
	channel=ssh.invoke_shell()
		
	return channel ,ssh
#------------------------------------------------------FUNCTIONS----------------------------------------------------
#------------------------------------------------------FUNCTIONS----------------------------------------------------
#------------------------------------------------------FUNCTIONS----------------------------------------------------
#------------------------------------------------------FUNCTIONS----------------------------------------------------
#------------------------------------------------------FUNCTIONS----------------------------------------------------
#------------------------------------------------------FUNCTIONS----------------------------------------------------
	
def wait_for_stringa_until(stringa, tempo, channel):
	time.sleep(1)
	success = 0
	start_time = time.time()
	out=channel.recv(1000)
	print('Finding ' + stringa)
	try:
		while out.find(stringa) < 0 and time.time() < start_time + (tempo + 0.5):
			if channel.recv_ready():
				out += channel.recv(100)
			print "...\r",
			
	except KeyboardInterrupt :
		print('exit')
	if time.time () > start_time + tempo:
		print ('Could not find %s in %d seconds' % (stringa, tempo) )
		success = 0
	else:
		print ('Found %s in %d seconds' % (stringa, tempo) )
		success = 1
	return success
	
def wait_for_stringa_until_ISOFAULT(stringa, tempo, channel):
	time.sleep(.01)
	success = 0
	start_time = time.time()
	out=channel.recv(200)
	try:
		while out.find(stringa) < 0 and time.time() < start_time + (tempo + 0.5):
			if channel.recv_ready():
				out += channel.recv(200)
			print('Finding ' + stringa),
			print "...\r",
			
	except KeyboardInterrupt :
		print('exit')
	if time.time () > start_time + (tempo):
		print ('Could not find %s in %d seconds' % (stringa, tempo) )
		success = 0
	else:
		print ('Found %s in %d seconds' % (stringa, tempo) )
		success = 1
	return success

def wait_for_either_stringa_until(stringa, stringa2, stringa3, tempo, channel):
	time.sleep(1)
	success = 0
	start_time = time.time()
	out=channel.recv(1000)
	slacerr=0
	print('Finding ' + stringa)
	try:
		while out.find(stringa) < 0 and out.find(stringa2) < 0 and out.find(stringa3) < 0 and time.time() < start_time + (tempo + 0.5):
			if channel.recv_ready():
				out += channel.recv(50)
				if "SLAC failed" in out and slacerr < 3:
					out = ""
					slacerr = slacerr + 1
					print slacerr
					time.sleep(16)
			print '....\r',
			
			
	except KeyboardInterrupt :
		print('exit')
	
	if out.find(stringa) < 0:
		success = 0
		print (out)
	else:
		success = 1
		if time.time () > start_time + tempo:
			print ('Could not find %s in %d seconds' % (stringa, tempo) )
			success = 0
		else:
			print ('Found %s in %d seconds' % (stringa, tempo) )
			success = 1
	return success
	
def wait_for_two_stringa_until(stringa, stringa2, tempo, channel):
	time.sleep(1)
	success = 0
	start_time = time.time()
	out=channel.recv(1000)
	slacerr=0
	try:
		while out.find(stringa) < 0 and out.find(stringa2) < 0 and time.time() < start_time + (tempo + 0.5):
			if channel.recv_ready():
				out += channel.recv(1000)
				if "SLAC failed" in out and slacerr < 3:
					out = ""
					slacerr = slacerr + 1
					print slacerr
			print('Finding ' + stringa)
			
			
	except KeyboardInterrupt :
		print('exit')
	
	if out.find(stringa) < 0 and out.find(stringa2) < 0:
		success = 0
		print (out)
	else:
		success = 1
		if time.time () > start_time + tempo:
			print ('Could not find %s in %d seconds' % (stringa, tempo) )
			success = 0
		else:
			print ('Found %s in %d seconds' % (stringa, tempo) )
			success = 1
	return success
	
def read_stringa_until(stringa, tempo, channel):
	
	start_time = time.time()
	success = 0
	out=channel.recv(100)
	try:
		while out.find(stringa) < 0 and time.time() < start_time + tempo:
			if channel.recv_ready():
				out += channel.recv(10)
			
			
	except KeyboardInterrupt :
		print('exit')
	if time.time () > start_time + tempo:
		print ('Could not find %s in %d seconds' % (stringa, tempo) )
		success = 0
	else:
		print ('Found %s in %d seconds' % (stringa, tempo) )
		success = 1
	return success, out
	
def find_SN(contents):
	r7= contents[str.find(contents,'Running on host:'):]
	r8 = r7[str.find(r7,': ')+2:]
	r9 = r8[:str.find(r8,'\r')]
	return r9

def send_cmd_until(cmd, stringa, tempo, channel_send, channel_read):
	channel_send.send(cmd)
	time.sleep(2)
	success = 0
	start_time = time.time()
	out=channel_read.recv(1000)
	try:
		while out.find(stringa) < 0 and time.time() < start_time + tempo:
			channel_send.send(cmd)
			if channel_read.recv_ready():
				out += channel_read.recv(1000)
			time.sleep(2)
	except KeyboardInterrupt :
		print('exit')
	if time.time () > start_time + tempo:
		print ('Could not send %s in %d seconds' % (cmd, tempo))
		success = 0
	else:
		print ('sent %s in %d seconds' % (cmd, tempo))
		success = 1
	time.sleep(0.1)
	return success

def send_cmd_telnet_until_c(cmd, stringa, tempo, channel_send, channel_read):
	channel_send.send(cmd)
	time.sleep(2)
	success = 0
	out=""
	start_time = time.time()
	out=channel_read.recv(1000)
	try:
		while out.find(stringa) < 0 and time.time() < start_time + tempo:
			channel_send.send(cmd)
			if channel_read.recv_ready():
				out += channel_read.recv(1000)
			time.sleep(2)
	except KeyboardInterrupt :
		print('exit')
	if time.time () > start_time + tempo:
		print ('Could not send %s in %d seconds' % (cmd, tempo))
		success = 0
	else:
		print ('sent %s in %d seconds' % (cmd, tempo))
		success = 1
	time.sleep(1)
	return success, out
	
def send_cmdtelnet_until(cmd, stringa, tempo, channel_send, channel_read):
	channel_send.send(cmd)
	time.sleep(1)
	success = 0
	start_time = time.time()
	out=channel_read.recv(1000)
	try:
		while out.find(stringa) < 0 and time.time() < start_time + tempo:
			channel_send.send(cmd)
			if channel_read.recv_ready():
				out += channel_read.recv(1000)
			time.sleep(1)
	except KeyboardInterrupt :
		print('exit')
	if time.time () > start_time + tempo:
		print ('Could not send %s in %d seconds' % (cmd, tempo))
		success = 0
	else:
		print ('sent %s in %d seconds' % (cmd, tempo))
		success = 1
	time.sleep(1)
	return success, out
		
def show_log_for(channel, tempo):
	time.sleep(1)
	SR_reason = "NO SR"
	timeout_start = time.time()
	try:
		while time.time() < timeout_start + tempo:
			if channel.recv_ready():
				out = channel.recv(300)
				print(out)
				err1 = out.find('SR_')
				err2 = out.find('SR_NO')
				if err1 >-1 and err2 < 0 : ################NEW LINE CODE##########################
					SR_reason1 = out[str.find (out, "SR_"):]
					SR_reason = SR_reason1[:str.find (out, "\n")]
					print SR_reason
					break
	except KeyboardInterrupt :
		print('exit')
	return SR_reason
# open the remote log file, and trace it

def readlogline (channel) :
        retval = ""
        a = channel.recv(1)
        while a != '\n' :
                retval += a
                a = channel.recv(1)
        return retval
		
# Read cpi setpoint current and pm measured current

def machine_data(globalid, parameter):
	with open("machinetypes.txt", "r") as fp:
		
	   for line in lines_that_contain(globalid, fp):   #per trovare la riga dove leggere l'informazione
			print line,     



	r7= line[str.find(line,parameter):]
	r8 = r7[str.find(r7,"=")+1:]
	r9 = r8[:str.find(r8,";")]
	print r9
	return r9

def get_GID():
	newpath = r'C:\Programmi\Zeta\3L10\Python27' 
	if not os.path.exists(newpath):
		os.makedirs(newpath)

#saving test in a different folder from the code
	completeName = os.path.join(newpath, "BarcodeReaderOut.txt") 
	with open(completeName, "r") as fp:
		
	   for line in lines_that_contain("GlobalId", fp):   #per trovare la riga dove leggere l'informazione
			print line,
	r8 = line[str.find(line,";")+1:]
	r9 = r8[:str.find(r8,"\n")]
	print r9
	return r9
	
def get_SN():
	newpath = r'C:\Programmi\Zeta\3L10\Python27' 
	if not os.path.exists(newpath):
		os.makedirs(newpath)

#saving test in a different folder from the code
	completeName = os.path.join(newpath, "BarcodeReaderOut.txt") 
	with open(completeName, "r") as fp:
		
	   for line in lines_that_contain("serialNumberNl", fp):   #per trovare la riga dove leggere l'informazione
			print line,
	r8 = line[str.find(line,";")+1:]
	r9 = r8[:str.find(r8,"\n")]
	print r9
	return r9
	
	
def readcurrents(r1):
				#this needs channel.send ("tail -f /home/bmterra/terra/*debug* | grep ppset\n") as well as r1 = readlogline (channel)
				# filter out the current, as reported by the power modules
                # a ppset logline consists of <cpi voltage setpoint, cpi current setpoint> <pm measured voltage, pm measured current> cpi measured voltage
                # but the log file does not register ppset lines after setvip 0 0, so the current never decreases if we take measured current
					r2 = r1[str.find (r1,"ppset"):]
					r3 = r2[str.find (r2, ",")+1:]
					r4 = r3[str.find (r3, ",")+1:]
					r6 = r3[:str.find (r3," ")]
					r5 = r4[:str.find (r4, " ")]
					return r6 , r5
					
def readcurrents_chademo(r1):
				#this needs channel.send ("tail -f /home/bmterra/terra/*debug* | grep ppset\n") as well as r1 = readlogline (channel)
				# filter out the current, as reported by the power modules
                # a ppset logline consists of <cpi voltage setpoint, cpi current setpoint> <pm measured voltage, pm measured current> cpi measured voltage
                # but the log file does not register ppset lines after setvip 0 0, so the current never decreases if we take measured current
					r2 = r1[str.find (r1,"mode) ("):]
					r3 = r2[str.find (r2, ",")+1:]
					r7 = r3[str.find(r3, ",(")+1:]
					r4 = r7[str.find (r7, ",")+1:]
					r6 = r3[:str.find (r3,")")]
					r5 = r4[:str.find (r4, "),")]
					return r6 , r5
				
def checkcurrent(channel,tempo, ch_o_ccs):
		channel.send ("tail -f /home/bmterra/charger/logs/$(ls -t /home/bmterra/charger/logs/ | head -1) | grep ppset\n")
		time.sleep(1)
		success = 0
		current = 0.0
		min = 0.0
		max = 1.0
		timeout_start = time.time()
		try:
			while time.time() < timeout_start + tempo*.33:
				r1 = readlogline (channel)
				print(r1)
			while time.time() > timeout_start + (tempo * 0.33) and time.time() < timeout_start + tempo:
				r1 = readlogline (channel)
				print(r1)
				if ch_o_ccs =='ch':
					[setp,curr]=readcurrents_chademo(r1)
				else:
					[setp,curr]=readcurrents(r1)
				
				current = float(curr)
				min = float(setp) - (float(setp) * 0.1)
				max = float(setp) + (float(setp) * 0.1)
				if float(setp) + (float(setp) * 0.1) > float(curr) and float(setp) - (float(setp) * 0.1) < float(curr) :
					success = 1
				else: 
					success = 0
					break
				print (success)
		except KeyboardInterrupt :
			print('exit')
		if success == 1:
			print('Current equal to setpoint: PASS')
		else: 
			print('Current equal to setpoint: FAIL')
		time.sleep(1)
		return success, current, min, max

def checkcurrent_WAT(channel,tempo, ch_o_ccs):
		channel.send ("tail -f /home/bmterra/charger/logs/$(ls -t /home/bmterra/charger/logs/ | head -1) | grep ppset\n")
		time.sleep(1)
		global current_DC_WAT 
		current_DC_WAT = 0.0
		#global start_meas
		success = 0
		current = 0.0
		min = 0.0
		max = 1.0
		timeout_start = time.time()
		try:
			while time.time() < timeout_start + tempo*.33:
				r1 = readlogline (channel)
				#print(r1)
				print (current_DC_WAT)
				#print (current)
				current_DC_WATmA = current_DC_WAT * 1000.0
			while time.time() > timeout_start + (tempo * 0.33) and time.time() < timeout_start + tempo:
				r1 = readlogline (channel)
				print(r1)
				if ch_o_ccs =='ch':
					[setp,curr]=readcurrents_chademo(r1)
				else:
					[setp,curr]=readcurrents(r1)
				
				current = float(curr)
				min = float(setp) - (float(setp) * 0.1)
				max = float(setp) + (float(setp) * 0.1)
				print (current_DC_WAT)
				print (current)
				current_DC_WATmA = current_DC_WAT * 1000.0
				
				if (float(setp) + (float(setp) * 0.1) > float(curr) and float(setp) - (float(setp) * 0.1) < float(curr)) and (float(setp) + (float(setp) * 0.1) > float(current_DC_WATmA) and float(setp) - (float(setp) * 0.1) < float(current_DC_WATmA)):
					success = 1
				else: 
					success = 0
					break
				print (success)
		except KeyboardInterrupt :
			print('exit')
		if success == 1:
			print('Current equal to setpoint: PASS')
		else: 
			print('Current equal to setpoint: FAIL')
		time.sleep(1)
		return success, current, min, max

		
def my_IP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	myIP = s.getsockname()[0]
	print(myIP)
	s.close()
	return myIP
		
def get_IP(myIP):
 Address=""
 with open(os.devnull, "wb") as limbo:
        for n in xrange(105, 111):
                ip="192.168.10.{0}".format(n)
                result=subprocess.Popen(["ping", "-n", "1", "-w", "200", ip],
                        stdout=limbo, stderr=limbo).wait()
                if result:
                        print ip, "inactive"
                else:
					print ip, "active"
					if ip != myIP:
						Address = ip
 return Address
		

#-------------functions to read from file------------------

def lines_that_equal(line_to_match, fp):
    return [line for line in fp if line == line_to_match]
	
def lines_that_contain(string, fp):
    return [line for line in fp if string in line]

def lines_that_start_with(string, fp):
    return [line for line in fp if line.startswith(string)]

def lines_that_end_with(string, fp):
    return [line for line in fp if line.endswith(string)]