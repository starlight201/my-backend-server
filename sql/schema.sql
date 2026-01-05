-- backend_server/sql/schema.sql

-- 创建数据库 (如果不存在)
CREATE DATABASE IF NOT EXISTS bike_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE bike_management;

-- 创建流量记录表 (如果不存在)
CREATE TABLE IF NOT EXISTS traffic_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    current_count_on_bridge INT NOT NULL DEFAULT 0,
    congestion_level ENUM('low', 'medium', 'high') NOT NULL,
    entrance_count INT NOT NULL DEFAULT 0,
    exit_count INT NOT NULL DEFAULT 0,
    -- 为时间戳字段创建索引，以加速历史数据查询
    INDEX idx_timestamp (timestamp)
);
