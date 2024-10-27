# 使用官方的 Python 基础镜像
FROM python:3.9.5-slim-buster

# 设置标签信息
LABEL author="Lan"
LABEL email="vast@tom.com"
<<<<<<< HEAD
LABEL version="6"

# 复制当前目录内容到容器内的 /app 目录
=======

>>>>>>> 9ba7d3779685b3e7be7e2e918c58ace143ad2bad
COPY . /app

# 设置时区为上海
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' > /etc/timezone

# 设置工作目录
WORKDIR /app

# 安装依赖项（包括 PyTorch）
RUN pip install --no-cache-dir -r requirements.txt

# 安装 PyTorch
# 对于 CPU 版本的 PyTorch
RUN pip install torch torchvision torchaudio

# 如果需要 GPU 版本，请使用以下命令并指定 CUDA 版本
# RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 暴露应用的端口
EXPOSE 12345

# 运行应用
CMD ["python", "main.py"]
