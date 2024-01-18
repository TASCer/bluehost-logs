cd /D "D:\PycharmProjects\bluehost-logs\src"
echo %cd%
call conda activate py10_BHlogs
python.exe "main.py"
if NOT ["%errorlevel%"] == ["0"] pause