#!/usr/bin/python -u

import serial
import time
import paramiko
import sys
from datetime import datetime
import os
import allfunction as fl

#from colorama import init
#init()
#from colorama import Fore, Back, Style

# this script connects to the terra application, and reads the most recent debug log file.
# it sets the charge current accordingly on the local low voltage power supplies
# This script is in use for testing the maraton chargepost

def find_temperature(contents, keyword):
	r7= contents[str.find(contents,keyword):]
	r8 = r7[str.find(r7,'= ')+2:]
	r9 = r8[:str.find(r8,'\r\n')]
	return r9

def find_SN(contents, keyword):
	r7= contents[str.find(contents,keyword):]
	r8 = r7[str.find(r7,': ')+2:]
	r9 = r8[:str.find(r8,'\n')]
	return r9	
	
def find_info(contents, keyword, splitter):
	r7= contents[str.find(contents,keyword):]
	r8 = r7[str.find(r7,splitter)+2:]
	r9 = r8[:str.find(r8,'\n')-1]
	return r9
	
def copy_from_keyword_and_split(contents, keyword, splitter):
	r7= contents[str.find(contents,keyword):]
	r8 = r7.split(splitter)
	
	return r8

	
	
def read_temperatures_from_Telnet(channel):
	cmd='cpiComboDc0/Outlet/stats\n'
	channel.send(cmd)

	[success, contents]=wait_for_stringa_until('Tcontactor.2 =',10,channel)
	print (contents)
	
	
	Tconnector1 = find_temperature(contents, 'Tconnector.1 =')
	print (Tconnector1)
	Tconnector2 = find_temperature(contents, 'Tconnector.2 =')
	print (Tconnector2)
	Tcable1 = find_temperature(contents, 'Tcable.1     =')
	print (Tcable1)
	Tcable2 = find_temperature(contents, 'Tcable.2     =')
	print (Tcable2)
	
	return Tconnector1, Tconnector2, Tcable1, Tcable2
	
def read_info_from_Telnet(cmd,channel, findword, keyword, splitter):
	channel.send(cmd)

	[success, contents]=wait_for_stringa_until(findword,10,channel)
	print (contents)
	
	info = find_info(contents, keyword, splitter)
	print float(info)
	
	return info
	
def read_temperatures_from_Text(contents):
	
	Tconnector1 = find_temperature(contents, 'Tconnector.1 =')
	print (Tconnector1)
	Tconnector2 = find_temperature(contents, 'Tconnector.2 =')
	print (Tconnector2)
	Tcable1 = find_temperature(contents, 'Tcable.1     =')
	print (Tcable1)
	Tcable2 = find_temperature(contents, 'Tcable.2     =')
	print (Tcable2)
	
	return Tconnector1, Tconnector2, Tcable1, Tcable2
	
def read_SN_from_Text(contents):
	
	SN = find_SN(contents, 'Running on host:')
	print SN
	return SN
	
def read_info_from_Text(contents, keyword, splitter):
	
	info = find_info(contents, keyword, splitter)
	print info
	return info

def set_current (PSU_interface, current) :
        
        control_voltage = current
        command = "VSET %.2f\n" % control_voltage
        print (command)  
        PSU_interface.write ('VSET 5.0\r\n')  #alternatively try with PSU_interface.write("VSET %s\n" % control_voltage)


# open the remote log file, and trace it
def wait_for_stringa_until(stringa, tempo, channel):
	start_time = time.time()
	out=channel.recv(10)
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
	
def wait_for_stringa_until2(stringa, stringa2, tempo, channel):
	start_time = time.time()
	out=channel.recv(10)
	try:
		while out.find(stringa) < 0 and out.find(stringa2) < 0 and time.time() < start_time + tempo:
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

def readlogline (channel) :
        retval = ""
        a = channel.recv(1)
        while a != '\n' :
                retval += a
                a = channel.recv(1)
        return retval
		
def connect_ssh(IP, user, pss):
	print 'Connecting to terra telnet'
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



f= open("out_py.txt","w")
f.write("-1\n")
f.write("BOARD=FAIL;SN=FAIL;node=FAIL;LOC=FAIL\n")
f.close()

f= open("out_py2.txt","w")

f.write("nameParametro=Test_Aborted;type=10;value=Aborted;lower=0;upper=0;\n")
f.close()														


	
#print "Inserire ultimo numero dell'indirizzo IP:\n 192.160.10.x\n"
IP1=fl.pinging()

IP_TERRA = max(IP1)


#time.sleep(2)

#IP_TERRA = "192.168.10.%s" %IP
user_terra = 'ekanapari'
pss_terra = 'Welcome1234!'

#[channel, ssh] = connect_ssh(IP_TERRA,user_terra,pss_terra)

[channel, ssh] = connect_ssh(IP_TERRA,user_terra,pss_terra)
time.sleep(2)

GID = fl.get_GID() 


time.sleep(1)
[sux, stringSN]=fl.send_cmdtelnet_until('telnet localhost 2323\n','Welcome to the debug session',120,channel,channel)

SN = fl.find_SN(stringSN)
fl.send_cmd_telnet_until_c('ls\n','cpiComboDc0',120,channel,channel)

[succ, lettura]=fl.send_cmd_telnet_until_c('ls -b\n','/OutletComboDc0/Charger/Boxchecks',120,channel,channel)

machinetype = fl.machine_data (GID, "MachineType=")
if 'ELA' in machinetype:
	EMO = True
else:
	if "Emergency_button" in lettura:
		EMO = True
	else:
		EMO = False

if "LatchReadout" in lettura and "Door1" in lettura and EMO:
	interlock_test = "PASS"
	interlock_bool = 1
else:
	interlock_test = "FAIL"
	interlock_bool = 0
	
time.sleep(1)
#----------Temperature reading left plug		
time.sleep(1)
cmd='/cpiComboDc0/Outlet/stats\n'
channel.send(cmd)

[success, strin77]=wait_for_stringa_until('Tcontactor.2 =',10,channel)
print (strin77)

[T1, T2, T3, T4] = read_temperatures_from_Text(strin77)

if "nc" not in T1 and "nc" not in T2 and "nc" not in T3 and "nc" not in T4 and "err" not in T1 and "err" not in T2 and "err" not in T3 and "err" not in T4:
	if float(T1) < 30.0 and float(T2) < 30.0 and float(T3) < 30.0 and float(T4) < 30.0:
		tempe_pass = 'PASS'
	else:
		tempe_pass = 'FAIL'
else:
	tempe_pass = 'FAIL'

rightplug = fl.machine_data (GID, "RightPlug=")
if "CCS" in rightplug:	
	#----------Temperature reading right plug	
	time.sleep(1)
	cmd='/cpiComboDc1/Outlet/stats\n'
	channel.send(cmd)

	[success, strin772]=wait_for_stringa_until('Tcontactor.2 =',10,channel)
	print (strin772)

	[T5, T6, T7, T8] = read_temperatures_from_Text(strin772)

	if "nc" not in T5 and "nc" not in T6 and "nc" not in T7 and "nc" not in T8 and "err" not in T5 and "err" not in T6 and "err" not in T7 and "err" not in T8:
		if float(T5) < 30.0 and float(T6) < 30.0 and float(T7) < 30.0 and float(T8) < 30.0:
			tempe_pass2 = 'PASS'
		else:
			tempe_pass2 = 'FAIL'
	else:
		tempe_pass2 = 'FAIL'
else:	
	tempe_pass2 = 'PASS'
	
cmd='/Authorization/RfidReader/stats\n'
channel.send(cmd)


[success, strin]=wait_for_stringa_until('OK',20,channel)
print (strin)

print "PASS RFID and press Enter"
dkey=sys.stdin.readline()

cmd='/Authorization/RfidReader/stats\n'
channel.send(cmd)


[success, strin1]=wait_for_stringa_until('OK',20,channel)
print (strin1)

rfid = read_info_from_Text(strin1, 'LastRfidReceived     = ', '= ')

time.sleep(1)
if '866F' in rfid:
	rfidPass= 'PASS'
else:
	rfidPass = 'FAIL'

if "ELA" in machinetype:
	channel.send('/Factory/Gpio/input\n')
	if channel.recv_ready():
				out = channel.recv(1000)
	try:			
		while out.find('Inputs = 0111') < 0:
				print ('Push the RIGHT button on ELAM! If it does not work press ctrl+c')
				channel.send('/Factory/Gpio/input\n')
				if channel.recv_ready():
					out = channel.recv(1000)
				time.sleep(1)
	except KeyboardInterrupt :
		print('exit')
	if out.find('Inputs = 0111') > -1:
		gpio_in1 = "PASS"
	else: 
		gpio_in1 = "FAIL"
	
	try:	
		while out.find('Inputs = 1011') < 0:
				print ('Push the MIDDLE button on ELAM! If it does not work press ctrl+c')
				channel.send('/Factory/Gpio/input\n')
				if channel.recv_ready():
					out = channel.recv(1000)
				time.sleep(1)
	except KeyboardInterrupt :
		print('exit')
	if out.find('Inputs = 1011') > -1:
		gpio_in2 = "PASS"
	else: 
		gpio_in2 = "FAIL"
	try:	
		while out.find('Inputs = 1101') < 0:
				print ('Push the LEFT button on ELAM! If it does not work press ctrl+c')
				channel.send('/Factory/Gpio/input\n')
				if channel.recv_ready():
					out = channel.recv(1000)
				time.sleep(1)
	except KeyboardInterrupt :
		print('exit')
		
	if out.find('Inputs = 1101') > -1:
		gpio_in3 = "PASS"
	else: 
		gpio_in3 = "FAIL"
	if gpio_in1 == 'PASS' and gpio_in2 == 'PASS' and gpio_in3 == 'PASS':
		gpio_in_test = 'PASS'
	else:
		gpio_in_test = 'FAIL'
else:
	gpio_in_test = 'PASS'

print "Touch the touchscreen and check for pixel failures. Press 'y' if it responds accordingly or press 'n' if it does not."
touchs=sys.stdin.readline()

if 'y' in touchs:
		touchscreen_test = 'PASS'
else:
		touchscreen_test = 'FAIL'

	
if "ELA" in machinetype:
	cmd='/Factory/Gpio/output 1100\n'
	channel.send(cmd)

	print "Check if RED LED is ON. Press 'y' if true or press 'n' if false."
	dled=sys.stdin.readline()

	if 'y' in dled:
		gpio1_test = 'PASS'
	else:
		gpio1_test = 'FAIL'
		
	cmd='/Factory/Gpio/output 1010\n'
	channel.send(cmd)

	print "Check if GREEN LED is ON. Press 'y' if true or press 'n' if false."
	dled=sys.stdin.readline()

	if 'y' in dled:
		gpio2_test = 'PASS'
	else:
		gpio2_test = 'FAIL'
		
	cmd='/Factory/Gpio/output 1001\n'
	channel.send(cmd)

	print "Check if BLUE LED is ON. Press 'y' if true or press 'n' if false."
	dled=sys.stdin.readline()

	if 'y' in dled:
		gpio3_test = 'PASS'
	else:
		gpio3_test = 'FAIL'
		
	if gpio1_test == 'PASS' and gpio2_test == 'PASS' and gpio3_test == 'PASS':
		gpio_test = 'PASS'
	else: 
		gpio_test = 'FAIL'
else:
	gpio_test = 'PASS'


#cmd='/Factory/Gpio/output 0010\n'
#channel.send(cmd)

#print "Check if green LED is ON and press ENTER to continue."
#dkey=sys.stdin.readline()

#cmd='/Factory/Gpio/output 0001\n'
#channel.send(cmd)

#print "Check if blue LED is ON and press ENTER to continue."
#dkey=sys.stdin.readline()



cmd ='/Connectivity/TransportLayer_HoustonCore/stats\n'
channel.send(cmd)

[success, strin2]=wait_for_stringa_until('xmitping',20,channel)
print (strin2)

connectivity = read_info_from_Text(strin2, 'state                             =', '= ')

if 'StateConnectedAndPre' in connectivity:
	connectivityPass= 'PASS'
else:
	connectivityPass = 'FAIL'

print 'Telnet Disconnection\n'
cmd='exit\n'
channel.send(cmd)
time.sleep(1)

time.sleep(1)

cmd='candiscover CAN\n'
channel.send(cmd)
time.sleep(1)	


[success, strin5]=wait_for_stringa_until('t = terminated',20,channel)
print (strin5)

CANDISC = copy_from_keyword_and_split(strin5, 'Board and revision info', '|')

CPCD = (CANDISC[12],CANDISC[13],CANDISC[15], CANDISC[16])
CPJD = (CANDISC[22],CANDISC[23],CANDISC[25], CANDISC[26])
IMI1 = (CANDISC[32],CANDISC[33],CANDISC[35], CANDISC[36])
if "none" not in rightplug:
	IMI2 = (CANDISC[42],CANDISC[43],CANDISC[45], CANDISC[46])
	CCB2 = (CANDISC[52],CANDISC[53],CANDISC[55], CANDISC[56])
print (CPCD)
print (CPJD)
print (IMI1)
if "none" not in rightplug:
	print (IMI2)
	print (CCB2)

	
	
time.sleep(2)
cmd='mmcli -L\n'
channel.send(cmd)

machinetype = fl.machine_data (GID, "MachineType=")
[success, strin3]=wait_for_stringa_until2('INCORPORATED]','Incorporated]',20,channel)
print (strin3)


if ('[Sierra Wireless, Incorporated]' in strin3 and 'ELA' in machinetype) or ('QUALCOMM INCORPORATED] 0' in strin3 and 'ELA' not in machinetype) or 'No modems were found' in strin3:
	modem_pass = 'PASS'
	r7= strin3[str.find(strin3,' [')+2:]
	modem_model = r7[:str.find(r7,']')]
	 
else:
	modem_pass = 'FAIL'
	modem_model = "None_or_wrong"

sim_pass = "FAIL"
sim_pass2 = "FAIL"
sim_pass3 = "FAIL"
lock_sim = "None"
state_sim = "None"
sig_quality = "None"	

if modem_pass == 'PASS':
	r7= strin3[str.find(strin3,'Modem/'):]
	r8 = r7[str.find(r7,'/')+1:]
	r9 = r8[:str.find(r8,' [')]

	print '%i' % int(r9)

	time.sleep(2)
	cmd='mmcli -m %i\n' % int(r9)
	channel.send(cmd)


	[success, strin4]=wait_for_stringa_until('Bearers',20,channel)
	print (strin4)
	sim_pass = "FAIL"
	sim_pass2 = "FAIL"
	sim_pass3 = "FAIL"
	lock_sim = "None"
	state_sim = "None"
	sig_quality = "None"
	if success == 1:
		r7= strin4[str.find(strin4,"lock: "):]
		r8 = r7[str.find(r7," '")+1:]
		lock_sim = r8[:str.find(r8,"\n")-1]
	
	

		if 'sim-pin2' in lock_sim:
			sim_pass = 'PASS'
		else:
			sim_pass = 'FAIL' 
	
		r7= strin4[str.find(strin4,"state: "):]
		r8 = r7[str.find(r7,": ")+1:]
		state_sim = r8[:str.find(r8,"\n")-1]
	
		if 'enabled' in state_sim or 'connected' in state_sim:
			sim_pass2 = 'PASS'
		else:
			sim_pass2 = 'FAIL'
		
		r7= strin4[str.find(strin4,'signal quality:'):]
		r8 = r7[str.find(r7," '")+2:]
		sig_quality = r8[:str.find(r8,"' ")]
	
		if float(sig_quality) > 40.0:
			sim_pass3 = 'PASS'
		else:
			sim_pass3 = 'FAIL'
	
	

if sim_pass is 'PASS' and sim_pass2 is 'PASS' and sim_pass3 is 'PASS' :
	sim_pass = 'PASS'

else:
	sim_pass = 'FAIL'
	
print "Press RCD button. Press 'y' if the charger switches-off or press 'n' if it does not."
RCD = sys.stdin.readline()

if 'y' in RCD:
		rcd_test = 'PASS'
else:
		rcd_test = 'FAIL'	
		
if success == 1 and connectivityPass == "PASS" and rfidPass == "PASS" and modem_pass == "PASS" and tempe_pass == "PASS" and tempe_pass2 == "PASS" and sim_pass == "PASS" and gpio_test == 'PASS' and gpio_in_test == 'PASS' and touchscreen_test == 'PASS' and rcd_test == 'PASS':
	aux_test = 1
else:
	aux_test = 0


	
f= open("out_py.txt","w")
f.write("%i\n" % aux_test)
f.write("%i\n" % aux_test)
f.write("\n-------------CAN Discover and Auxiliary values -----------\n\n")
f.write("BOARD=%s;SN=%s;node=%s;LOC=%s;\n" % (CANDISC[12],CANDISC[13],CANDISC[15], CANDISC[16]))
f.write("BOARD=%s;SN=%s;node=%s;LOC=%s;\n" % (CANDISC[22],CANDISC[23],CANDISC[25], CANDISC[26]))
f.write("BOARD=%s;SN=%s;node=%s;LOC=%s;\n" % (CANDISC[32],CANDISC[33],CANDISC[35], CANDISC[36]))
if "none" not in rightplug:
	f.write("BOARD=%s;SN=%s;node=%s;LOC=%s;\n" % (CANDISC[42],CANDISC[43],CANDISC[45], CANDISC[46]))
	f.write("BOARD=%s;SN=%s;node=%s;LOC=%s;\n" % (CANDISC[52],CANDISC[53],CANDISC[55], CANDISC[56]))
f.close()

f= open("out_py2.txt","w")
f.write("nameParametro=Tconnector1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T1, 0.0, 25.0))
f.write("nameParametro=Tconnector2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T2, 0.0, 25.0))
f.write("nameParametro=Tcable1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T3, 0.0, 25.0))
f.write("nameParametro=Tcable2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T4, 0.0, 25.0))
if "CCS" in rightplug:	
	f.write("nameParametro=T2connector1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T5, 0.0, 25.0))
	f.write("nameParametro=T2connector2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T6, 0.0, 25.0))
	f.write("nameParametro=T2cable1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T7, 0.0, 25.0))
	f.write("nameParametro=T2cable2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T8, 0.0, 25.0))
f.write("nameParametro=RFID;type=10;value=%s;lower=0;upper=0;\n" % (rfidPass))
f.write("nameParametro=RFIDRead;type=10;value=%s;lower=0;upper=0;\n" % (rfid))
f.write("nameParametro=MODEM;type=10;value=%s;lower=0;upper=0;\n" % (modem_pass))
f.write("nameParametro=MODEMmodel;type=10;value=%s;lower=0;upper=0;\n" % (modem_model))
f.write("nameParametro=SIM;type=10;value=%s;lower=0;upper=0;\n" % (sim_pass))
f.write("nameParametro=SIMlock;type=10;value=%s;lower=0;upper=0;\n" % (lock_sim))
f.write("nameParametro=SIMstate;type=10;value=%s;lower=0;upper=0;\n" % (state_sim))
f.write("nameParametro=SIMsignal_quality;type=10;value=%s;lower=0;upper=0;\n" % (sig_quality))
f.write("nameParametro=Connectivity;type=10;value=%s;lower=0;upper=0;\n" % (connectivityPass))
f.write("nameParametro=Connectivity_value;type=10;value=%s;lower=0;upper=0;\n" % (connectivity))
f.write("nameParametro=Temperature_Sensing;type=10;value=%s;lower=0;upper=0;\n" % (tempe_pass))
f.write("nameParametro=TouchScreen;type=10;value=%s;lower=0;upper=0;\n" % (touchscreen_test))
f.write("nameParametro=RCDTest;type=10;value=%s;lower=0;upper=0;\n" % (rcd_test))
if "CCS" in rightplug:	
	f.write("nameParametro=Temperature2_Sensing;type=10;value=%s;lower=0;upper=0;\n" % (tempe_pass2))
if "ELA" in machinetype:
	f.write("nameParametro=GPIO_OUTPUT;type=10;value=%s;lower=0;upper=0;\n" % (gpio_test))
	f.write("nameParametro=GPIO_INPUT;type=10;value=%s;lower=0;upper=0;\n" % (gpio_in_test))

f.close() 

namefile = SN+".log"
newpath = r'C:/testresults' 
if not os.path.exists(newpath):
    os.makedirs(newpath)

#saving test in a different folder from the code
completeName = os.path.join(newpath, namefile)

f= open(completeName,"a+")
f.write("\n-------------CAN Discover and Auxiliary values -----------\n\n")
f.write("%i\n" % aux_test)
f.write("%i\n" % aux_test)
f.write("\n-------------CAN Discover and Auxiliary values -----------\n\n")
f.write("BOARD=%s;SN=%s;node=%s;LOC=%s\n" % (CANDISC[12],CANDISC[13],CANDISC[15], CANDISC[16]))
f.write("BOARD=%s;SN=%s;node=%s;LOC=%s\n" % (CANDISC[22],CANDISC[23],CANDISC[25], CANDISC[26]))
f.write("BOARD=%s;SN=%s;node=%s;LOC=%s\n" % (CANDISC[32],CANDISC[33],CANDISC[35], CANDISC[36]))
if "none" not in rightplug:
	f.write("BOARD=%s;SN=%s;node=%s;LOC=%s;\n" % (CANDISC[42],CANDISC[43],CANDISC[45], CANDISC[46]))
	f.write("BOARD=%s;SN=%s;node=%s;LOC=%s;\n" % (CANDISC[52],CANDISC[53],CANDISC[55], CANDISC[56]))
f.write(rfid + "\n")
f.write(connectivity +"\n")
f.write("Tcontactor1 = %s , Tcontacor2 = %s , Tcable1 = %s , Tcable2 = %s \n" % (T1, T2, T3, T4))
f.write(strin3 + "\n")
f.write(strin4 + "\n")
f.write("nameParametro=Tconnector1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T1, 0.0, 25.0))
f.write("nameParametro=Tconnector2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T2, 0.0, 25.0))
f.write("nameParametro=Tcable1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T3, 0.0, 25.0))
f.write("nameParametro=Tcable2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T4, 0.0, 25.0))
if "CCS" in rightplug:	
	f.write("nameParametro=T2connector1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T5, 0.0, 25.0))
	f.write("nameParametro=T2connector2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T6, 0.0, 25.0))
	f.write("nameParametro=T2cable1;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T7, 0.0, 25.0))
	f.write("nameParametro=T2cable2;type=10;value=%s;lower=%.f;upper=%.f;\n" % (T8, 0.0, 25.0))
f.write("nameParametro=RFID;type=10;value=%s;lower=0;upper=0;\n" % (rfidPass))
f.write("nameParametro=RFIDRead;type=10;value=%s;lower=0;upper=0;\n" % (rfid))
f.write("nameParametro=MODEM;type=10;value=%s;lower=0;upper=0;\n" % (modem_pass))
f.write("nameParametro=MODEMmodel;type=10;value=%s;lower=0;upper=0;\n" % (modem_model))
f.write("nameParametro=SIM;type=10;value=%s;lower=0;upper=0;\n" % (sim_pass))
f.write("nameParametro=SIMlock;type=10;value=%s;lower=0;upper=0;\n" % (lock_sim))
f.write("nameParametro=SIMstate;type=10;value=%s;lower=0;upper=0;\n" % (state_sim))
f.write("nameParametro=SIMsignal_quality;type=10;value=%s;lower=0;upper=0;\n" % (sig_quality))
f.write("nameParametro=Connectivity;type=10;value=%s;lower=0;upper=0;\n" % (connectivityPass))
f.write("nameParametro=Connectivity_value;type=10;value=%s;lower=0;upper=0;\n" % (connectivity))
f.write("nameParametro=Temperature_Sensing;type=10;value=%s;lower=0;upper=0;\n" % (tempe_pass))
f.write("nameParametro=TouchScreen;type=10;value=%s;lower=0;upper=0;\n" % (touchscreen_test))
f.write("nameParametro=RCDTest;type=10;value=%s;lower=0;upper=0;\n" % (rcd_test))
if "CCS" in rightplug:	
	f.write("nameParametro=Temperature2_Sensing;type=10;value=%s;lower=0;upper=0;\n" % (tempe_pass2))
if "ELA" in machinetype:
	f.write("nameParametro=GPIO_OUTPUT;type=10;value=%s;lower=0;upper=0;\n" % (gpio_test))
	f.write("nameParametro=GPIO_INPUT;type=10;value=%s;lower=0;upper=0;\n" % (gpio_in_test))
f.write(str(datetime.now()))
print(str(datetime.now()))
f.close() 

ssh.close()
