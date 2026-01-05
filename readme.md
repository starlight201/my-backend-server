# 自行车桥实时监控系统 - 后端服务

基于 Flask 的 RESTful API 服务，为自行车桥监控系统提供数据接口和业务逻辑处理。

## 功能特性

- 🔄 **实时数据同步** - 从 Atlas 设备同步自行车检测数据
- 📊 **流量统计** - 实时计算桥上自行车数量和拥堵状态
- 💾 **数据持久化** - 使用 MySQL 存储历史流量数据
- 📈 **历史查询** - 提供过去一小时的流量趋势数据
- 🖼️ **图像服务** - 提供最新的入口和出口监控图像
- 🌐 **跨域支持** - 内置 CORS 支持，方便前端集成

## 技术栈

### 后端框架
- **Flask 2.2.2** - 轻量级 Python Web 框架
- **Flask-CORS** - 跨域资源共享支持

### 数据库
- **MySQL** - 关系型数据库
- **PyMySQL** - MySQL Python 客户端

### 其他依赖
- **Werkzeug** - WSGI 工具库
- **python-dotenv** - 环境变量管理（可选）

## 项目结构

```
backend_server/
├── app/                          # 应用主目录
│   ├── __init__.py              # 包初始化文件
│   ├── app.py                   # Flask 应用和路由定义
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库连接模块
│   └── __pycache__/            # Python 缓存文件
├── static/                      # 静态文件目录
│   └── results/                 # Atlas 同步的结果文件
│       ├── predictions.json    # 最新的检测数据
│       ├── latest_entrance.jpg  # 入口最新图像
│       └── latest_exit.jpg      # 出口最新图像
├── sql/                         # 数据库脚本
│   └── schema.sql              # 数据库表结构
├── requirements.txt             # Python 依赖包
└── run.py                      # 应用启动入口
```

## 快速开始

### 环境要求

- Python 3.7+
- MySQL 5.7+
- 推荐使用虚拟环境（venv）

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd backend_server
```

2. **创建虚拟环境**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **数据库配置**
   - 创建 MySQL 数据库 `bike_management`
   - 执行 SQL 脚本初始化表结构：
```bash
mysql -u root -p bike_management < sql/schema.sql
```

5. **修改配置文件**
编辑 `app/config.py`，更新数据库连接信息：
```python
MYSQL_HOST = 'localhost'        # 数据库主机
MYSQL_USER = 'root'             # 数据库用户
MYSQL_PASSWORD = 'your_password' # 数据库密码
MYSQL_DB = 'bike_management'    # 数据库名称
MYSQL_PORT = 3306              # 数据库端口
```

6. **启动服务**
```bash
python run.py
```

服务将在 `http://localhost:5000` 启动

## 配置说明

### 主要配置参数

在 `app/config.py` 中可配置以下参数：

```python
# Flask 应用配置
SECRET_KEY = 'a_very_secret_key_for_bike_management'

# MySQL 数据库配置
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'
MYSQL_DB = 'bike_management'
MYSQL_PORT = 3306

# 文件路径配置
STATIC_RESULTS_DIR = 'static/results'  # Atlas 同步文件目录
PREDICTIONS_FILE_PATH = 'static/results/predictions.json'  # 预测数据文件

# 拥挤度阈值
CONGESTION_THRESHOLDS = {
    'low': (0, 10),      # 0-10辆：畅通
    'medium': (11, 25),  # 11-25辆：中度拥挤
    'high': (26, float('inf'))  # 26+辆：严重拥挤
}
```

### 环境变量配置（可选）

支持通过 `.env` 文件配置环境变量：

```bash
# 创建 .env 文件
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=bike_management
```

## API 文档

### 根端点
- **URL**: `/`
- **方法**: GET
- **描述**: 服务状态检查
- **响应**:
```json
{
  "message": "Bicycle Bridge Monitoring API",
  "endpoints": [
    "/api/status",
    "/api/history"
  ]
}
```

### 获取实时状态
- **URL**: `/api/status`
- **方法**: GET
- **描述**: 获取当前桥上车辆状态和拥堵信息
- **响应**:
```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "current_count_on_bridge": 15,
  "congestion_level": "medium",
  "congestion_level_text": "中度拥挤",
  "total_in_today": 120,
  "total_out_today": 105,
  "entrance_count": 5,
  "exit_count": 3,
  "latest_entrance_image_path": "/static/results/latest_entrance.jpg",
  "latest_exit_image_path": "/static/results/latest_exit.jpg"
}
```

### 获取历史数据
- **URL**: `/api/history`
- **方法**: GET
- **描述**: 获取过去一小时的流量历史数据
- **响应**:
```json
{
  "data_points": [
    {
      "time": "11:00",
      "count": 12
    },
    {
      "time": "11:05", 
      "count": 15
    }
  ]
}
```

## 数据库设计

### 数据表结构

**traffic_log** - 流量日志表
```sql
CREATE TABLE traffic_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    current_count_on_bridge INT NOT NULL,
    congestion_level VARCHAR(10) NOT NULL,
    entrance_count INT NOT NULL,
    exit_count INT NOT NULL
);
```

### 字段说明

- `id` - 主键，自增ID
- `timestamp` - 记录时间戳
- `current_count_on_bridge` - 当前桥上车辆数
- `congestion_level` - 拥挤度级别（low/medium/high）
- `entrance_count` - 入口检测到的车辆数
- `exit_count` - 出口检测到的车辆数

## 数据流程

### 实时数据同步流程

1. **数据采集**: Atlas 设备进行自行车检测
2. **文件同步**: 检测结果保存到 `predictions.json`
3. **API 调用**: 前端调用 `/api/status` 接口
4. **数据处理**: 后端读取预测数据，更新数据库
5. **响应返回**: 返回最新的状态信息给前端

### 拥堵度计算逻辑

```python
def calculate_congestion(count):
    if count <= 10:    # 0-10辆
        return 'low', '畅通'
    elif count <= 25:  # 11-25辆  
        return 'medium', '中度拥挤'
    else:              # 26+辆
        return 'high', '严重拥挤'
```

## 部署说明

### 开发环境部署

```bash
# 直接运行（调试模式）
python run.py

# 或使用 Flask 命令行
export FLASK_APP=run.py
flask run --host=0.0.0.0 --port=5000
```

### 生产环境部署

推荐使用 Gunicorn + Nginx：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker 部署（示例）

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "run.py"]
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 MySQL 服务是否运行
   - 验证数据库配置信息
   - 确认网络连接和防火墙设置

2. **文件读取错误**
   - 确保 `static/results/` 目录存在
   - 检查文件权限设置
   - 验证 Atlas 设备同步正常

3. **跨域问题**
   - 确认 Flask-CORS 已正确安装
   - 检查前端请求的 Origin 头

### 日志调试

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 监控与维护

### 健康检查

定期检查服务状态：
```bash
curl http://localhost:5000/
```

### 数据备份

建议定期备份 MySQL 数据库：
```bash
mysqldump -u root -p bike_management > backup.sql
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/app.py` 中添加新的路由函数
2. 实现相应的业务逻辑
3. 添加错误处理
4. 更新 API 文档

### 扩展数据模型

1. 修改数据库表结构
2. 更新相应的数据操作逻辑
3. 确保向后兼容性

## 许可证

MIT License

## 支持与贡献

如有问题或建议，请提交 Issue 或 Pull Request。

---

**注意**: 确保 Atlas 设备正确配置并同步数据到指定目录，后端服务才能正常工作。