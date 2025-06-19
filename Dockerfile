FROM python:3.10-slim

# 安装系统级依赖（支持 PyQt6 + WebEngine）
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libsm6 \
    libxrandr2 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libdbus-1-3 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxinerama1 \
    libxss1 \
    libasound2 \
    libegl1 \
    libpulse0 \
    x11-xserver-utils \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制代码到容器中
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt 

EXPOSE 5901

# 默认运行入口
CMD ["python", "Main.py"]
