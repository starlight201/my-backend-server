# backend_server/app/app.py
import os
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from . import config
from .database import get_db_connection

# 初始化Flask应用
app = Flask(__name__,
            static_folder='../static',
            static_url_path='/static'
            )
CORS(app)  # 允许跨域请求


# --- 辅助函数 ---
def get_latest_predictions():
    """从同步过来的JSON文件中读取最新的检测数据"""
    if not os.path.exists(config.PREDICTIONS_FILE_PATH):
        return None
    try:
        with open(config.PREDICTIONS_FILE_PATH, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing predictions file: {e}")
        return None


def calculate_congestion(count):
    """根据当前桥上车辆数计算拥挤度"""
    if count <= config.CONGESTION_THRESHOLDS['low'][1]:
        level, text = 'low', '畅通'
    elif count <= config.CONGESTION_THRESHOLDS['medium'][1]:
        level, text = 'medium', '中度拥挤'
    else:
        level, text = 'high', '严重拥挤'
    return level, text


# --- API 路由 ---

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    获取实时监控状态。
    此接口被调用时，会读取Atlas同步的数据，更新数据库，并返回最新状态。
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # 1. 读取Atlas同步过来的最新数据
        predictions = get_latest_predictions()
        if not predictions:
            return jsonify({"error": "Predictions data not available"}), 404

        # 2. 解析入口和出口的自行车数量
        entrance_count = 0
        exit_count = 0
        for item in predictions:
            if item.get('video_type') == 'entrance':
                entrance_count = item.get('count', 0)
            elif item.get('video_type') == 'exit':
                exit_count = item.get('count', 0)

        # 3. 获取上一次记录的桥上车辆数，用于计算当前数量
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_count_on_bridge FROM traffic_log ORDER BY timestamp DESC LIMIT 1")
            last_record = cursor.fetchone()
            last_count = last_record['current_count_on_bridge'] if last_record else 0

        # 4. 计算当前桥上车辆数和拥挤度
        current_count = last_count + entrance_count - exit_count
        if current_count < 0: current_count = 0  # 防止负数
        congestion_level, congestion_text = calculate_congestion(current_count)

        # 5. 将当前状态记录到数据库，作为历史数据
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO traffic_log (timestamp, current_count_on_bridge, congestion_level, entrance_count, exit_count)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                datetime.now(),
                current_count,
                congestion_level,
                entrance_count,
                exit_count
            ))
            conn.commit()

        # 6. 计算今日总流量
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(entrance_count) as total_in, SUM(exit_count) as total_out 
                FROM traffic_log WHERE DATE(timestamp) = CURDATE()
            """)
            daily_totals = cursor.fetchone()

        # 7. 构建并返回响应
        response = {
            "timestamp": datetime.now().isoformat() + "Z",
            "current_count_on_bridge": current_count,
            "congestion_level": congestion_level,
            "congestion_level_text": congestion_text,
            "total_in_today": daily_totals['total_in'] if daily_totals['total_in'] else 0,
            "total_out_today": daily_totals['total_out'] if daily_totals['total_out'] else 0,
            "entrance_count": entrance_count,
            "exit_count": exit_count,
            "latest_entrance_image_path": "/static/results/latest_entrance.jpg",
            "latest_exit_image_path": "/static/results/latest_exit.jpg"
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500
    finally:
        conn.close()


@app.route('/api/history', methods=['GET'])
def get_history():
    """获取过去一小时的流量历史数据"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # 获取过去一小时的数据
            one_hour_ago = datetime.now() - timedelta(hours=1)
            cursor.execute(
                "SELECT timestamp, current_count_on_bridge FROM traffic_log WHERE timestamp > %s ORDER BY timestamp ASC",
                (one_hour_ago,)
            )
            records = cursor.fetchall()

            data_points = []
            for record in records:
                data_points.append({
                    "time": record['timestamp'].strftime('%H:%M'),
                    "count": record['current_count_on_bridge']
                })

            return jsonify({"data_points": data_points})

    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500
    finally:
        conn.close()


# --- 错误处理 ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def home():
    return jsonify({
        "message": "Bicycle Bridge Monitoring API",
        "endpoints": [
            "/api/status",
            "/api/history"
        ]
    })