# base-note
基于pyqt的思源日记本git同步

```
:: 跳转到思源笔记的工作空间中
D: & cd D:\workspace\siyuan_workspace

tasklist |findstr /im "SiYuan"
if %errorlevel% == 0 (goto opened) else (goto closed)

:: ------------------如果思源笔记软件已开启--------------------
:opened

:: 必须软关闭思源笔记软件，等待3秒后，才能够正常提交
taskkill /im "SiYuan.exe"
timeout /T 3

:: 提交git，只提交data目录，其他目录不提交
:: gitignore文件中已提前忽略  /data/.siyuan
git add data/.
git commit -m %date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%%time:~3,2%%time:~6,2%
git push

:: 重启思源笔记软件
start D:/soft/SiYuan/SiYuan.exe
exit

:: ------------------如果思源笔记软件没有开启------------------
:closed

:: 提交git，只提交data目录，其他目录不提交
git add data/.
git commit -m %date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%%time:~3,2%%time:~6,2%
git push
exit
```
