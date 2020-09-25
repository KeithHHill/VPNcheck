import geocoder
import os
import ConfigParser
import time
import subprocess
import sys
import psutil



# get config
myPath = os.path.dirname(os.path.abspath(__file__))
connectScript = myPath+"\VPNconnect.bat"
disconnectScript = myPath+"\VPNdisconnect.bat"

config = ConfigParser.ConfigParser()
config.read(myPath+"\config.ini")
vpnScriptLocation = config.get('config','vpnScriptLocation')
bitTorrentLocation = config.get('config','bitTorrentLocation')
homeCity = config.get('config','homeCity')
vpnKillApp = config.get('config','vpnKillApp')
bittorrentApp = config.get('config','bittorrentApp')
shortSleep = int(config.get('config','shortSleep'))
longSleep = int(config.get('config','longSleep'))
    
print("config loaded \n")



# process to ensure that VPN is connected.  If it isn't, kill the torrent app
def VPNcheckRedundency() : 
    #fetch current location
    g = geocoder.ip('me')
    print(g.city + " was detected")

    # if the city is not in the current city, we assume the VPN is active
    if g.city == homeCity : 

        os.system("TASKKILL /F /IM "+bittorrentApp) # close bittorrent to prevent traffic
        print ("Home City was detected.  VPN not confirmed, bailing on script.  Please try again.")
        sys.exit(0) # kill the script

    else : 
        print ("VPN confirmed active")


# Determines if a given process is running and returns True or False
def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;


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


# config file was found enabled or called directly from the cmd argument.  Starts the VPN and opens torrent app
def enable() :
    print("VPN enabled flag discovered. Opening VPN application")
    subprocess.Popen(vpnScriptLocation,shell=True) # runs the VPN application
    time.sleep(longSleep) # wait to ensure the VPN app opens
    print("Running VPN Script")
    args = [vpnScriptLocation, '--connect', 'US East.ovpn']
    subprocess.call(args)
    print ("VPN service started.  Awaiting connection.")
    time.sleep(longSleep) # wait to ensure the VPN connects
    VPNcheckRedundency() #ensure that connection is complete
    # subprocess.call([bitTorrentLocation])
    subprocess.Popen(bitTorrentLocation)
    print("Torrent app started")
    

# config file status changed or called directly from the cmd argument.  Stops the VPN and kills torrent app
def disable() : 
    os.system("TASKKILL /F /IM "+bittorrentApp) # close bittorrent to prevent traffic
    time.sleep(shortSleep) # wait

    #disconnect from the VPN
    args = [vpnScriptLocation, '--command', 'disconnect_all']
    subprocess.call(args)
    time.sleep(longSleep) # wait to ensure the connection gets disconnected

    os.system("TASKKILL /F /IM "+ vpnKillApp) # close VPN app
    time.sleep(longSleep) # wait 30 seconds
    




if __name__ == '__main__' :
    if len(sys.argv) == 2 : 
        if sys.argv[1] == "start" :
            enable() 
        elif sys.argv[1] == "stop" :
            disable()
        elif sys.argv[1] == "check" :
            print("VPN Active Status: " + str(VPNisActive()))
            if checkIfProcessRunning(bittorrentApp):
                print('Torrent app status: True')
            else:
                print('Torrent app status: False')

        else :
            print("Error.  You must provide argument start, stop, or check")

    else :
        print("Error.  You must provide argument start, stop, or check")




