# backend_server/app/config.py
import os

# Flask应用配置
SECRET_KEY = 'a_very_secret_key_for_bike_management'

# MySQL数据库配置
MYSQL_HOST = '192.168.10.100'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Wcy200523.'  # <--- 【必须修改】您的MySQL密码
MYSQL_DB = 'bike_management'
MYSQL_PORT = 3306

# Atlas设备同步文件路径 (相对于项目根目录)
# Atlas设备会将文件同步到 backend_server/static/results/ 目录
STATIC_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'results')
PREDICTIONS_FILE_PATH = os.path.join(STATIC_RESULTS_DIR, 'predictions.json')

# 拥挤度阈值定义
CONGESTION_THRESHOLDS = {
    'low': (0, 10),
    'medium': (11, 25),
    'high': (26, float('inf')) # high表示大于25
}
