import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from croniter import croniter
import win32serviceutil
import win32service
import win32event
import servicemanager
from update_hosts import main as update_hosts

class AutoHostsService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'AutoHostsUpdater'
    _svc_display_name_ = 'Auto Hosts Updater Service'
    _svc_description_ = 'Automatically update hosts file periodically'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        
        # 初始化日志配置
        try:
            # 获取可执行文件所在目录
            if getattr(sys, 'frozen', False):
                base_dir = Path(sys.executable).parent
            else:
                base_dir = Path(__file__).parent

            config = self.load_config()
            if config:
                # 确保日志目录存在
                log_dir = Path(config['work_dir'])
                if not log_dir.is_absolute():
                    log_dir = base_dir / log_dir
                log_dir.mkdir(parents=True, exist_ok=True)
                
                # 设置日志
                log_path = log_dir / config['log_file']
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_path, encoding='utf-8', mode='a'),
                        logging.StreamHandler()
                    ]
                )
                logging.info('日志配置初始化成功，日志文件路径：%s', log_path)
        except Exception as e:
            print(f'初始化日志配置失败: {e}')
            # 如果日志配置失败，至少确保有基本的控制台输出
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler()]
            )

    def SvcStop(self):
        logging.info('正在停止服务...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        logging.info('服务正在启动...')
        try:
            self.main()
        except Exception as e:
            logging.error(f'服务运行时发生错误: {e}')
            self.SvcStop()

    def load_config(self):
        # 获取可执行文件所在目录
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent

        config_path = base_dir / 'config.json'
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 确保工作目录是绝对路径
                work_dir = Path(config['work_dir'])
                if not work_dir.is_absolute():
                    work_dir = base_dir / work_dir
                config['work_dir'] = str(work_dir)
                return config
        except Exception as e:
            logging.error(f'加载配置文件失败: {e}')
            return None

    def main(self):
        logging.info('正在加载配置文件...')
        config = self.load_config()
        if not config:
            logging.error('无法加载配置文件，服务退出')
            return
        logging.info('配置文件加载成功')



        # 获取cron表达式，默认每6小时执行一次
        cron_expr = config.get('cron_expression', '0 */6 * * *')
        
        try:
            # 验证cron表达式
            base = datetime.now()
            iter = croniter(cron_expr, base)
        except Exception as e:
            logging.error(f'无效的cron表达式 {cron_expr}: {e}')
            return

        logging.info(f'服务启动成功，使用cron表达式: {cron_expr}')

        while self.running:
            try:
                # 计算下次执行时间
                next_run = iter.get_next(datetime)
                now = datetime.now()
                logging.info(f'下次执行时间: {next_run}')
                
                # 等待到下次执行时间
                while now < next_run and self.running:
                    # 每60秒检查一次是否需要停止服务
                    time.sleep(60)
                    now = datetime.now()
                    logging.debug(f'当前时间: {now}, 距离下次执行还有: {next_run - now}')

                if not self.running:
                    break

                # 执行更新hosts操作
                logging.info('开始执行定时更新任务')
                update_hosts()
                
                # 更新下次执行时间
                iter = croniter(cron_expr, datetime.now())

            except Exception as e:
                logging.error(f'执行定时任务时发生错误: {e}')
                # 发生错误时等待5分钟后继续
                time.sleep(300)

        logging.info('服务已停止')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AutoHostsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AutoHostsService)