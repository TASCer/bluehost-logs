cd /D "D:\PycharmProjects\bluehost-logs\src"
echo %cd%
call conda activate bluehost-logs311
python.exe "main.py"
if NOT ["%errorlevel%"] == ["0"] pause