import socket
import csv
import asyncio
import yaml
import logging
from datetime import datetime
from pysnmp.hlapi.asyncio import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity

import os

# Get the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))
# 修改配置文件路径
config_path = os.path.join(script_dir, 'config.yaml')

# 读取 YAML 配置
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Construct absolute path for CSV file
CSV_FILE = os.path.join(script_dir, config['csv_file_name'])

# Configure logging
# 添加默认 logger 配置
logger = logging.getLogger('report_logger')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# 然后是现有的配置代码
if config['logging']['enabled']:
    import os
    from logging.handlers import TimedRotatingFileHandler
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(script_dir, config['logging']['directory'])
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure the logger
    logger = logging.getLogger('report_logger')
    logger.setLevel(getattr(logging, config['logging']['level']))
    
    # Create a timed rotating file handler
    log_file = os.path.join(log_dir, 'report.log')
    handler = TimedRotatingFileHandler(
        log_file,
        when='midnight',
        interval=1,
        backupCount=config['logging']['max_days']
    )
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)


async def check_network_connectivity(ip_address, community_string='public', port=161, timeout=2):
    """
    Check if the target IP address is reachable via SNMP.
    Uses a test SNMP GET request to verify connectivity.
    """
    try:
        # Use sysDescr.0 OID for testing - a basic system information query
        test_oid = ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
        
        error_indication, error_status, error_index, var_binds = await getCmd(
            SnmpEngine(),
            CommunityData(community_string),
            UdpTransportTarget((ip_address, port), timeout=timeout),
            ContextData(),
            test_oid
        )
        
        if error_indication:
            logger.error(f"SNMP connectivity test failed: {error_indication}")
            return False
        elif error_status:
            logger.error(f'SNMP error status: {error_status.prettyPrint()} at {error_index}')
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"SNMP connectivity test error: {e}")
        return False





def read_previous_page_count():
    """
    Reads the last stored page count from the CSV file.
    Returns (last_count, last_date) tuple. Returns (0, None) if file doesn't exist or is empty.
    """
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                return int(last_row[1]), last_row[0]  # Return (count, date)
            else:
                return 0, None
    except FileNotFoundError:
        return 0, None

def is_data_exists_for_date(date):
    """
    检查指定日期是否已有数据记录
    """
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0] == date:
                    return True
        return False
    except FileNotFoundError:
        return False

async def get_printer_page_count(ip_address, community_string):
    """
    Query the printer for the page count using SNMP.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    

    if not await check_network_connectivity(ip_address, community_string, port=161, timeout=timeout):
        logger.error(f"Printer at {ip_address} is not reachable. Please check the network connection.")
        # Use the previous page count when network is unreachable
        previous_page_count, previous_date = read_previous_page_count()
        if previous_page_count > 0:
            write_page_count(current_date, previous_page_count, 0)
            logger.info(f'Using previous page count from {previous_date}: {previous_page_count}')
        return

    oid = ObjectType(ObjectIdentity('1.3.6.1.2.1.43.10.2.1.4.1.1'))
    try:
        error_indication, error_status, error_index, var_binds = await getCmd(SnmpEngine(),
                   CommunityData(community_string),
                   UdpTransportTarget((ip_address, 161)),
                   ContextData(),
                   oid)
        if error_indication:
            logger.error(f'Query failed: {error_indication}')
            previous_page_count, previous_date = read_previous_page_count()
            if previous_page_count > 0:
                write_page_count(current_date, previous_page_count, 0)
                logger.info(f'Using previous page count from {previous_date}: {previous_page_count}')
            return
        elif error_status:
            logger.error(f'Query failed: {error_status.prettyPrint()} at index {error_index}')
            previous_page_count, previous_date = read_previous_page_count()
            if previous_page_count > 0:
                write_page_count(current_date, previous_page_count, 0)
                logger.info(f'Using previous page count from {previous_date}: {previous_page_count}')
        else:
            for var_bind in var_binds:
                page_count = int(var_bind[1])
                previous_page_count, _ = read_previous_page_count()
                net_increase = page_count - previous_page_count if previous_page_count >= 0 else 0
                write_page_count(current_date, page_count, net_increase)
                logger.info(f'Print page count: {page_count}, Net increase: {net_increase}')
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        previous_page_count, previous_date = read_previous_page_count()
        if previous_page_count > 0:
            write_page_count(current_date, previous_page_count, 0)
            logger.info(f'Using previous page count from {previous_date}: {previous_page_count}')





def write_page_count(date, total_page_count, net_increase):
    """
    Write date, total page count, and net increase to CSV file.
    """
    try:
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([date, total_page_count, net_increase])
        else:
            with open(CSV_FILE, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([date, total_page_count, net_increase])
        logger.info(f"Successfully wrote data for {date}")
    except Exception as e:
        logger.error(f"Failed to write to CSV file: {e}")
        raise





def fill_missing_dates(csv_file):
    """
    Check and fill missing dates in data.
    """
    try:
        # 读取现有数据
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
        if not rows:
            logger.warning("CSV file is empty")
            return
            
        # 获取数据的起始和结束日期
        try:
            start_date = datetime.strptime(rows[0][0], "%Y-%m-%d")
            end_date = datetime.strptime(rows[-1][0], "%Y-%m-%d")
        except (ValueError, IndexError) as e:
            logger.error(f"Invalid date format in CSV: {e}")
            return
        
        # 创建完整的日期列表
        dates_dict = {}
        for row in rows:
            try:
                if len(row) >= 3:  # Ensure row has all required fields
                    dates_dict[row[0]] = row
            except Exception as e:
                logger.error(f"Invalid row format: {row}, Error: {e}")
                continue
        
        # 检查每一天
        current_date = start_date
        new_rows = []
        prev_page_count = "0"
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str in dates_dict:
                new_rows.append(dates_dict[date_str])
                if dates_dict[date_str][1] != "-1":
                    prev_page_count = dates_dict[date_str][1]
            else:
                # For missing dates, use previous day's page count
                logger.warning(f"Found missing date: {date_str}, auto-filled")
                new_rows.append([date_str, prev_page_count, "0"])
            
            current_date = current_date + timedelta(days=1)
            
        # 备份原文件
        backup_file = f"{csv_file}.backup"
        try:
            import shutil
            shutil.copy2(csv_file, backup_file)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
        
        # 写回文件
        try:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(new_rows)
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")
            # 恢复备份
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, csv_file)
            
    except Exception as e:
        logger.error(f"Error while filling missing dates: {e}")

# 在文件顶部添加 timedelta 导入
from datetime import datetime, timedelta

# 在主函数中添加调用
if __name__ == "__main__":
    printer_config = config['printer']
    
    # Use configuration values
    printer_ip = printer_config['ip_address']
    port = printer_config['port']
    community = printer_config['community_string']
    timeout = printer_config['timeout']
    
    async def main():
        if not await check_network_connectivity(printer_ip, community, port, timeout):
            logger.error(f"Failed to connect to printer at {printer_ip}:{port}")
            exit(1)
            
        await get_printer_page_count(printer_ip, community)
        
        # 检查并填充缺失的日期
        fill_missing_dates(CSV_FILE)
    
    asyncio.run(main())
