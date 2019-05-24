import geocoder
import smtplib
import os
import ConfigParser
import time
import subprocess
import sys


# get config
myPath = os.path.dirname(os.path.abspath(__file__))

try: 
    config = ConfigParser.ConfigParser()
    config.read(myPath+"\config.ini")
    enabled = config.get('config','enabled')
    emailLogin = config.get('config','emailLogin')
    emailPassword = config.get('config','emailPassword')
    emailServer = config.get('config','emailServer')
    vpnScriptLocation = config.get('config','vpnScriptLocation')
    bitTorrentLocation = config.get('config','bitTorrentLocation')
    homeCity = config.get('config','homeCity')
    vpnKillApp = config.get('config','vpnKillApp')
    bittorrentApp = config.get('config','bittorrentApp')
    fromEmail = config.get('config','fromEmail')
    shortSleep = int(config.get('config','shortSleep'))
    longSleep = int(config.get('config','longSleep'))
    
    print("config loaded \n")

except:
    print ("Error reading the config file")


def sendEmail (message) :
    # spin up email server
    server = smtplib.SMTP(emailServer)
    server.ehlo()
    server.starttls()
    server.login(emailLogin,emailPassword)

    emailBody = message

    # compose the message
    msg = "\r\n".join([
        "From: " + fromEmail  ,
        "To: " + emailLogin ,
        "Subject: VPN Check" ,
        "MIME-Version: 1.0",
        "Content-type: text/html",
            "",
            emailBody
            ])
        
    # send the email
    server.sendmail("VPNcheck@noReply.com", emailLogin, msg)

    # close email server
    server.quit()


# process to ensure that VPN is connected.  If it isn't, abort and send an email
def VPNcheckRedundency() : 
    #fetch current location
    g = geocoder.ip('me')
    print(g.city + " was detected")

    # if the city is not in the current city, we assume the VPN is active
    if g.city == homeCity : 

        os.system("TASKKILL /F /IM "+bittorrentApp) # close bittorrent to prevent traffic

        sendEmail("VPN is not connected.  Script was aborted unexpectedly.")
        
        sys.exit(0) # kill the script

    else : 
        print ("VPN confirmed active")


def VPNisActive() :
    config.read(myPath+"\config.ini")
    homeCity = config.get('config','homeCity') #refresh the city (used for testing)

    g = geocoder.ip('me')
    print(g.city + " was detected")

    # if the city is not in the current city, we assume the VPN is active
    if g.city == homeCity :
        return False
    else :
        return True

# first turned on.  Enable VPN and start bittorrent
if enabled == "True" or enabled =="true" :
    print("VPN enabled flag discovered")
    subprocess.Popen(vpnScriptLocation,shell=True) # enables the VPN
    print ("VPN service started.  Awaiting connection.")
    time.sleep(longSleep) # wait 30 seconds to ensure the VPN connects
    VPNcheckRedundency() #ensure that connection is complete
    # subprocess.call([bitTorrentLocation])
    subprocess.Popen(bitTorrentLocation)
    sendEmail("VPN connection successful.  Disable in config file to terminate.")

else : 
    print ("config not enabled.  closing")
    sys.exit(0)


print ("waiting until disabled in the config file")
# keep the app running until the config is turned off, then kill bittorrent and kill the VPN
while enabled =="True" or enabled == "true" :
    
    time.sleep(longSleep) # wait 30 seconds
    config.read(myPath+"\config.ini")
    enabled = config.get('config','enabled') #check and see if it's still enabled
 

# torrenting complete and config change detected.  Kill VPN and bittorrent
if enabled != "True" and enabled != "true" :
    print ("change in config detected.  Shutting down")

    os.system("TASKKILL /F /IM "+bittorrentApp) # close bittorrent to prevent traffic
    time.sleep(shortSleep) # wait 15 seconds
    os.system("TASKKILL /F /IM "+ vpnKillApp) # close VPN
    time.sleep(longSleep) # wait 30 seconds
    if VPNisActive() == False :
        sendEmail("VPN successfully disconnected")
    else : 
        sendEmail("Error: expecting the VPN to be disconnected and it is still active")





