# 自动更新 Hosts 工具

这是一个用于自动更新 Windows 系统 hosts 文件的 Python 脚本。该脚本会从 gitlab.com 获取最新的 hosts 数据，并自动更新到系统的 hosts 文件中。

## 功能特点

- 自动从 gitlab 获取最新 hosts 数据
- 自动备份当前 hosts 文件
- 支持一次性更新和定时自动更新
- 自动保留原有 hosts 配置
- 支持作为 Windows 服务运行
- 详细的日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

在 `config.json` 文件中配置以下参数：

```json
{
    "work_dir": ".",           # 工作目录，可以是相对路径或绝对路径
    "backup_dir": "backup",    # hosts文件备份目录
    "log_file": "runtime.log", # 日志文件路径
    "cron_expression": "0 */6 * * *"  # 定时更新的cron表达式，默认每6小时更新一次
}
```

## 使用方法

### 方法一：直接运行更新

使用 `update_hosts.py` 脚本进行一次性更新：

```bash
python update_hosts.py
```

注意：由于需要修改系统 hosts 文件，脚本需要以管理员权限运行。如果没有管理员权限，脚本会自动请求提升权限。

### 方法二：安装为 Windows 服务

1. 使用 `install_service.bat` 安装服务（需要管理员权限）：

   - 双击运行 `install_service.bat`
   - 或在管理员命令提示符中运行：`python auto_hosts_service.py install`

2. 服务安装后会自动启动，并按照配置文件中的 `cron_expression` 定时更新 hosts

3. 如需卸载服务，可以：
   - 双击运行 `uninstall_service.bat`
   - 或在管理员命令提示符中运行：`python auto_hosts_service.py remove`

## 注意事项

- 每次更新前会自动备份当前的 hosts 文件到配置的备份目录中
- 备份文件格式为：hosts.backup.YYYYMMDD_HHMMSS
- 更新过程中会保留原有的自定义 hosts 配置
- 如果更新过程中出现错误，会保留原有 hosts 文件不变
- 运行日志保存在配置文件指定的日志文件中
- Windows 服务模式下，可以在服务管理器中查看服务状态
