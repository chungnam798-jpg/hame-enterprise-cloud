FROM python:3.10-slim

# Cài đặt các thư viện hệ thống cần thiết cho Playwright & Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    curl \
    git \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium || true

# Copy toàn bộ mã nguồn
COPY . .

# Khởi tạo CSDL SQLite nội bộ
RUN python -c "import database; database.init_db(); import customer_memory; customer_memory.init_customer_memory_db()"

ENV PORT=5000
ENV HEADLESS_MODE=true
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "server.py"]
