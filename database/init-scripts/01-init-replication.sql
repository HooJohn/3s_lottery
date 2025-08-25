-- 创建复制用户
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';

-- 创建应用数据库
CREATE DATABASE lottery_platform;

-- 切换到应用数据库
\c lottery_platform;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 创建应用用户并授权
GRANT ALL PRIVILEGES ON DATABASE lottery_platform TO lottery_user;
GRANT ALL ON SCHEMA public TO lottery_user;