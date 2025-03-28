# 自动更新 Hosts 工具

这是一个用于自动更新 Windows 系统 hosts 文件的 Python 脚本。该脚本会从 gitlab.com 获取最新的 hosts 数据，并自动更新到系统的 hosts 文件中。

## 功能特点

- 自动从 gitlab 获取最新 hosts 数据
- 自动备份当前 hosts 文件
- 自动更新系统 hosts 文件
- 需要管理员权限运行

## 使用方法

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 运行脚本

```bash
python update_hosts.py
```

注意：由于需要修改系统 hosts 文件，脚本需要以管理员权限运行。如果没有管理员权限，脚本会自动请求提升权限。

## 注意事项

- 每次更新前会自动备份当前的 hosts 文件
- 备份文件保存在 hosts 文件同目录下，格式为：hosts.backup.YYYYMMDD_HHMMSS
- 如果更新过程中出现错误，会保留原有 hosts 文件不变
