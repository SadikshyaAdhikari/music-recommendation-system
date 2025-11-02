@echo off
echo Checking recent logs for recommendations...
echo.
type app.log | findstr /i "ML Genre fallback Dashboard recommendation similarity"
echo.
echo Full recent logs:
powershell -Command "Get-Content app.log -Tail 30"
pause


