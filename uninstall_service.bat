@echo off
chcp 65001

set SERVICE_NAME=AutoHostsUpdater

:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员权限运行此脚本！
    pause
    exit /b 1
)

:: 停止服务
sc stop %SERVICE_NAME%

:: 等待服务停止
timeout /t 2 >nul

:: 删除服务
sc delete %SERVICE_NAME%

echo 服务卸载完成！
pause