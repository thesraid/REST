@echo off
REM joriordan@alienvault.com
set /p domain=Enter Domain: 
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/analyst_lab5_ex2.py -d %domain% -u usm-anywhere-training@alienvault.com -p Password1!
timeout /t 5
PsExec.exe \\win2k12-victim -u Administrator -p Password1! wusa C:\AV_Extra\windows8.1-kb4012213-x64_5b24b9ca5a123a844ed793e0f2be974148520349.msu  /quiet
timeout /t 5
plink.exe root@192.168.250.13 -pw Password1! /root/scripts/resetScripts/analyst_lab5_ex3.py -d %domain% -u usm-anywhere-training@alienvault.com -p Password1!
pause