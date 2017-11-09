@echo off
REM joriordan@alienvault.com
plink.exe root@192.168.2.15 -pw Password1! /root/scripts/SSH_Overload.sh
timeout /t 10
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/Malicious_Scan.sh
timeout /t 10
plink.exe root@192.168.2.15 -pw Password1! /usr/bin/nikto -h 192.168.250.14
timeout /t 10
START C:\Users\Administrator\Desktop\scripts\Backup_Delete_Event_Log.exe
pause