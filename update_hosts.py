import os
import sys
import json
import requests
import datetime
import shutil
import logging
from pathlib import Path


def get_hosts_content():
    url = 'https://gitlab.com/ineo6/hosts/-/raw/master/next-hosts'
    logging.info(f'正在从 {url} 获取hosts内容...')
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info('成功获取hosts内容')
        return response.text
    except requests.RequestException as e:
        logging.error(f'获取hosts内容失败: {e}')
        return None


def load_config():
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

def setup_logging(config):
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent
    
    log_path = base_dir / config['log_file']
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def backup_hosts_file(hosts_path, config):
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent
    
    # 确保备份目录存在
    backup_dir = base_dir / config['backup_dir']
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_path = backup_dir / f'hosts.backup.{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    try:
        shutil.copy2(hosts_path, backup_path)
        logging.info(f'已备份hosts文件到: {backup_path}')
        return True
    except Exception as e:
        logging.error(f'备份hosts文件失败: {e}')
        return False


def update_hosts_file(config):
    # Windows系统hosts文件路径
    hosts_path = os.path.join(os.environ['SystemRoot'], 'System32', 'drivers', 'etc', 'hosts')

    # 获取新的hosts内容
    new_content = get_hosts_content()
    if not new_content:
        return False

    try:
        logging.info('准备更新hosts文件...')
        # 备份当前hosts文件
        if not backup_hosts_file(hosts_path, config):
            logging.error('备份hosts文件失败，终止更新')
            return False
        # 尝试不同编码读取hosts文件
        encodings = ['utf-8', 'gbk', 'ansi']
        current_content = None
        detected_encoding = None

        for encoding in encodings:
            try:
                with open(hosts_path, 'r', encoding=encoding) as f:
                    current_content = f.read()
                    detected_encoding = encoding
                break
            except UnicodeDecodeError:
                continue

        if current_content is None:
            logging.error('无法读取hosts文件，不支持的编码格式')
            return False
        logging.info(f'成功读取hosts文件，使用编码: {detected_encoding}')

        # 清理和规范化内容
        def clean_content(content):
            # 只过滤掉包含乱码的行，保留空行和注释
            lines = []
            for line in content.splitlines():
                # 检查行是否包含乱码（通过检查是否包含不可打印字符）
                if all(ord(c) < 128 for c in line):
                    lines.append(line)
            return '\n'.join(lines)

        # 更新hosts文件，使用检测到的编码
        try:
            with open(hosts_path, 'w', encoding=detected_encoding) as f:
                start_marker = '#GitHub Host Set Start'
                end_marker = '#GitHub Host Set End '

                # 分割并清理原有内容
                parts = current_content.split(start_marker)
                before_content = clean_content(parts[0])

                # 如果存在GitHub配置块，保留最后一个end_marker之后的内容
                after_content = ''
                if len(parts) > 1:
                    # 遍历所有部分，找到最后一个end_marker之后的内容
                    for part in parts[1:]:
                        if end_marker in part:
                            after_part = part.split(end_marker)[-1]
                            # 直接保留end_marker后的内容，不进行清理
                            if start_marker not in after_part:
                                after_content = after_part
                                break

                # 写入更新后的内容
                if before_content:
                    f.write(before_content)
                    if not before_content.endswith('\n\n'):
                        f.write('\n\n')

                f.write(f'{start_marker}\n')
                f.write(clean_content(new_content) + '\n')
                f.write(f'{end_marker}')

                if after_content:
                    if not after_content.startswith('\n'):
                        f.write('\n')
                    f.write(after_content)

            logging.info('hosts文件更新成功！')
            return True
        except Exception as e:
            logging.error(f'写入hosts文件失败: {e}')
            return False
    except Exception as e:
        logging.error(f'更新hosts文件失败: {e}')
        return False


def main():
    logging.info('开始执行hosts更新程序')
    # 加载配置文件
    config = load_config()
    if not config:
        logging.error('无法加载配置文件，程序退出')
        return
    
    # 设置日志
    setup_logging(config)
    
    try:
        if update_hosts_file(config):
            logging.info('hosts更新完成')
        else:
            logging.error('hosts更新失败')
    except Exception as e:
        logging.error(f'发生错误: {e}')


if __name__ == '__main__':
    # 检查是否具有管理员权限
    if os.name == 'nt':
        import ctypes

        if not ctypes.windll.shell32.IsUserAnAdmin():
            logging.warning('请以管理员权限运行此脚本')
            if sys.version_info[0] >= 3:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)

    main()
