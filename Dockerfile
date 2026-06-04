# 使用轻量级基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口（如果机器人需要 webhook 或 http 服务，否则可省略）
EXPOSE 8000

# 启动命令
CMD ["python", "bot.py"]