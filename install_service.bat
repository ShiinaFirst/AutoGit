@echo off
chcp 65001

set SERVICE_NAME=AutoHostsUpdater
set DISPLAY_NAME="Auto Hosts Updater Service"
set DESCRIPTION="Automatically update hosts file periodically"
set EXE_PATH="%~dp0dist\auto_hosts_service.exe"

:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员权限运行此脚本！
    pause
    exit /b 1
)

:: 停止并删除已存在的服务
sc query %SERVICE_NAME% >nul 2>&1
if %errorLevel% equ 0 (
    sc stop %SERVICE_NAME% >nul 2>&1
    sc delete %SERVICE_NAME% >nul 2>&1
    timeout /t 2 >nul
)

:: 创建服务
sc create %SERVICE_NAME% binPath= %EXE_PATH% start= auto DisplayName= %DISPLAY_NAME%
if %errorLevel% neq 0 (
    echo 创建服务失败！
    pause
    exit /b 1
)

:: 设置服务描述
sc description %SERVICE_NAME% %DESCRIPTION%

:: 启动服务
sc start %SERVICE_NAME%

echo 服务安装完成！
pause