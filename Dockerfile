# 使用官方的 Python 基础镜像
FROM python:3.9.5-slim-buster

# 设置标签信息
LABEL author="Lan"
LABEL email="vast@tom.com"
LABEL version="6"
COPY . /app
# 设置时区为上海
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' > /etc/timezone

# 设置工作目录
WORKDIR /app

# 安装依赖项（包括 PyTorch）
RUN pip install --no-cache-dir -r requirements.txt

# 暴露应用的端口
EXPOSE 12345

# 运行应用
CMD ["python", "main.py"]
