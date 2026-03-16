# 🚀 部署指南

## 📋 部署前检查清单

### 必需条件
- [ ] Python 3.8 或更高版本
- [ ] FFmpeg 已安装
- [ ] 至少 10GB 可用磁盘空间
- [ ] 稳定的网络连接

### 推荐配置
- [ ] 多核 CPU（4核以上）
- [ ] 8GB+ 内存
- [ ] GPU（用于加速Whisper）
- [ ] SSD存储

## 🏗️ 部署方式

### 方式1：本地部署（推荐）
```bash
# 1. 克隆项目
git clone https://github.com/yourusername/video-to-summary-skill.git
cd video-to-summary-skill

# 2. 运行安装脚本
./install.sh

# 3. 验证安装
python scripts/video_to_summary.py --version
```

### 方式2：Docker部署
```dockerfile
# 使用预构建镜像
docker run -it \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  yourusername/video-to-summary:latest \
  python scripts/video_to_summary.py --url "URL"
```

### 方式3：云服务器部署
```bash
# 以Ubuntu 22.04为例
# 1. 登录服务器
ssh user@your-server

# 2. 安装基础依赖
sudo apt update
sudo apt install -y python3-pip python3-venv ffmpeg git

# 3. 部署应用
git clone https://github.com/yourusername/video-to-summary-skill.git
cd video-to-summary-skill
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 配置为系统服务
sudo tee /etc/systemd/system/video-summary.service << EOF
[Unit]
Description=Video to Summary Service
After=network.target

[Service]
Type=simple
User=你的用户
WorkingDirectory=/path/to/video-to-summary-skill
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python scripts/video_to_summary.py --url "URL"
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 5. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable video-summary
sudo systemctl start video-summary
```

## ⚙️ 生产环境配置

### 1. 配置文件
创建 `config/production.yaml`：
```yaml
# 生产环境配置
environment: "production"

# 下载配置
download:
  output_dir: "/data/video-analysis/output"
  cookies_browser: "chrome"
  max_quality: "best"
  timeout: 600
  max_retries: 5
  rate_limit: "10M"  # 带宽限制

# 语音识别
speech_to_text:
  default_model: "base"
  default_language: "auto"
  cache_dir: "/data/video-analysis/cache"
  max_audio_size_mb: 500
  
  # GPU加速（如果可用）
  use_gpu: true
  gpu_device: 0

# 资源限制
resources:
  max_concurrent_downloads: 3
  max_concurrent_transcriptions: 2
  max_memory_mb: 4096
  max_disk_gb: 100
  
# 监控和日志
monitoring:
  log_level: "INFO"
  log_file: "/var/log/video-summary.log"
  metrics_port: 9090
  enable_health_check: true
  
# 备份和清理
backup:
  keep_days: 30
  auto_cleanup: true
  backup_dir: "/data/video-analysis/backups"
```

### 2. 环境变量
```bash
# 生产环境变量
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export MAX_WORKERS=4

# API密钥（如果使用）
export OPENAI_API_KEY=""
export AZURE_SPEECH_KEY=""
export ANTHROPIC_API_KEY=""

# 存储路径
export OUTPUT_DIR="/data/video-analysis/output"
export CACHE_DIR="/data/video-analysis/cache"
export TEMP_DIR="/tmp/video-summary"

# 网络配置
export HTTP_PROXY=""
export HTTPS_PROXY=""
export NO_PROXY="localhost,127.0.0.1"
```

### 3. 安全配置
```bash
# 创建专用用户
sudo useradd -r -s /bin/false video-summary
sudo chown -R video-summary:video-summary /data/video-analysis

# 设置权限
chmod 750 /data/video-analysis
chmod 640 config/production.yaml

# 防火墙规则
sudo ufw allow 9090/tcp  # 监控端口
sudo ufw allow from 192.168.1.0/24  # 内网访问
```

## 📊 监控和维护

### 1. 健康检查
```bash
# 手动检查
curl http://localhost:9090/health

# 自动监控脚本
#!/bin/bash
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/health)
if [ "$HEALTH" != "200" ]; then
    echo "服务异常，重启中..."
    sudo systemctl restart video-summary
fi
```

### 2. 日志管理
```bash
# 查看实时日志
tail -f /var/log/video-summary.log

# 日志轮转配置
sudo tee /etc/logrotate.d/video-summary << EOF
/var/log/video-summary.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 640 video-summary video-summary
}
EOF
```

### 3. 性能监控
```bash
# 安装监控工具
sudo apt install -y htop iotop nmon

# 查看资源使用
htop  # CPU和内存
iotop  # 磁盘IO
nmon  # 综合监控
```

## 🔄 备份和恢复

### 备份策略
```bash
#!/bin/bash
# 每日备份脚本
BACKUP_DIR="/data/backups/video-summary"
DATE=$(date +%Y%m%d)

# 备份配置
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# 备份重要输出（最近7天）
find /data/video-analysis/output -type f -mtime -7 -name "*.md" -o -name "*.json" | \
    tar -czf $BACKUP_DIR/output_$DATE.tar.gz -T -

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR/*_$DATE.tar.gz"
```

### 灾难恢复
```bash
# 恢复配置
tar -xzf backup/config_20240101.tar.gz -C /

# 恢复数据
tar -xzf backup/output_20240101.tar.gz -C /data/video-analysis/

# 重建虚拟环境
cd /path/to/video-to-summary-skill
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📈 扩展和优化

### 横向扩展（多节点）
```yaml
# docker-compose.cluster.yml
version: '3.8'
services:
  downloader:
    image: video-summary-downloader:latest
    deploy:
      replicas: 3
    environment:
      ROLE: downloader
      REDIS_HOST: redis

  transcriber:
    image: video-summary-transcriber:latest  
    deploy:
      replicas: 2
    environment:
      ROLE: transcriber
      REDIS_HOST: redis
      GPU: "true"

  summarizer:
    image: video-summary-summarizer:latest
    deploy:
      replicas: 2
    environment:
      ROLE: summarizer
      REDIS_HOST: redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 性能优化
```python
# 1. 使用GPU加速
import whisper
model = whisper.load_model("medium", device="cuda")

# 2. 批量处理优化
BATCH_SIZE = 4
audio_batch = [audio1, audio2, audio3, audio4]
transcripts = model.transcribe(audio_batch)

# 3. 缓存优化
from functools import lru_cache

@lru_cache(maxsize=100)
def transcribe_cached(audio_hash: str) -> str:
    # 如果相同音频已处理过，直接返回缓存结果
    pass

# 4. 异步处理
import asyncio
async def process_video_async(url: str):
    download_task = asyncio.create_task(download_video_async(url))
    audio_task = asyncio.create_task(extract_audio_async(url))
    await asyncio.gather(download_task, audio_task)
```

## 🔧 故障排除

### 常见问题解决方案

#### 问题1: 下载速度慢
```bash
# 解决方案
# 1. 增加超时时间
python scripts/video_to_summary.py --url "URL" --timeout 600

# 2. 使用代理
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"

# 3. 限制质量
python scripts/video_to_summary.py --url "URL" --quality 720p
```

#### 问题2: 内存不足
```bash
# 解决方案
# 1. 使用更小模型
python scripts/video_to_summary.py --url "URL" --model tiny

# 2. 增加swap空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. 限制并发数
export MAX_WORKERS=1
```

#### 问题3: 磁盘空间不足
```bash
# 解决方案
# 1. 定期清理
find /data/video-analysis/output -type f -mtime +7 -delete

# 2. 使用外部存储
export OUTPUT_DIR="/mnt/external-drive/output"

# 3. 压缩存储
tar -czf old_output.tar.gz /data/video-analysis/output/*
```

#### 问题4: 服务不可用
```bash
# 诊断步骤
# 1. 检查服务状态
sudo systemctl status video-summary

# 2. 查看日志
sudo journalctl -u video-summary -f

# 3. 检查端口
netstat -tulpn | grep :9090

# 4. 检查依赖
python -c "import yt_dlp, whisper; print('依赖正常')"
```

## 📞 支持和维护

### 支持渠道
- **文档**: [README.md](README.md), [QUICK_START.md](QUICK_START.md)
- **问题跟踪**: GitHub Issues
- **社区支持**: Discord/Slack频道
- **紧急支持**: 运维团队联系方式

### 维护计划
```bash
# 每日维护任务
0 2 * * * /opt/scripts/daily_maintenance.sh

# 每周维护任务
0 3 * * 0 /opt/scripts/weekly_maintenance.sh

# 每月维护任务
0 4 1 * * /opt/scripts/monthly_maintenance.sh
```

### 升级指南
```bash
# 1. 备份当前配置和数据
./scripts/backup.sh

# 2. 更新代码
git pull origin main

# 3. 更新依赖
pip install -U -r requirements.txt

# 4. 迁移数据（如有需要）
./scripts/migrate.py

# 5. 重启服务
sudo systemctl restart video-summary
```

---

**生产就绪检查清单**
- [ ] 所有服务有监控
- [ ] 日志系统就绪
- [ ] 备份策略配置
- [ ] 安全配置完成
- [ ] 性能测试通过
- [ ] 灾难恢复计划

**部署完成！** 🎉 现在你的视频转文字总结工具已准备好处理生产环境任务。