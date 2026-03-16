#!/bin/bash
# 批量视频处理脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 默认值
INPUT_FILE=""
OUTPUT_DIR="$PROJECT_ROOT/output/batch_$(date +%Y%m%d_%H%M%S)"
PARALLEL=2
AUDIO_ONLY=false
LANGUAGE="auto"
MODEL="base"

# 帮助信息
show_help() {
    cat << EOF
批量视频处理脚本

用法: $0 [选项] <输入文件>

选项:
  -i, --input FILE       包含URL列表的输入文件（必需）
  -o, --output DIR       输出目录（默认: $OUTPUT_DIR）
  -p, --parallel N       并行处理数量（默认: $PARALLEL）
  -a, --audio-only       仅处理音频（不下载视频）
  -l, --language LANG    语音识别语言（默认: $LANGUAGE）
  -m, --model MODEL      Whisper模型大小（默认: $MODEL）
  -h, --help             显示此帮助信息

输入文件格式:
  每行一个视频URL，空行和以#开头的行会被忽略

示例:
  $0 -i urls.txt
  $0 -i urls.txt -o ./results -p 3 -a
  $0 -i urls.txt -l zh -m medium

支持的平台:
  YouTube, Bilibili, 小红书, 抖音, Twitter, Instagram等
EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            INPUT_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -a|--audio-only)
            AUDIO_ONLY=true
            shift
            ;;
        -l|--language)
            LANGUAGE="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            # 如果没有指定-i，第一个非选项参数作为输入文件
            if [[ -z "$INPUT_FILE" && "$1" != -* ]]; then
                INPUT_FILE="$1"
            else
                echo "错误: 未知选项 $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# 检查输入文件
if [[ -z "$INPUT_FILE" ]]; then
    echo "错误: 需要指定输入文件"
    show_help
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "错误: 输入文件不存在: $INPUT_FILE"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/logs"

echo "🚀 开始批量处理"
echo "输入文件: $INPUT_FILE"
echo "输出目录: $OUTPUT_DIR"
echo "并行数量: $PARALLEL"
echo "仅音频: $AUDIO_ONLY"
echo "语言: $LANGUAGE"
echo "模型: $MODEL"
echo ""

# 读取URL并过滤
URLS=()
TOTAL_LINES=0
VALID_URLS=0

echo "📋 解析输入文件..."
while IFS= read -r line || [[ -n "$line" ]]; do
    TOTAL_LINES=$((TOTAL_LINES + 1))
    
    # 跳过空行和注释
    line_trimmed=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    if [[ -z "$line_trimmed" || "$line_trimmed" == \#* ]]; then
        continue
    fi
    
    # 验证URL格式
    if [[ "$line_trimmed" =~ ^https?:// ]]; then
        URLS+=("$line_trimmed")
        VALID_URLS=$((VALID_URLS + 1))
        echo "  ✅ $line_trimmed"
    else
        echo "  ⚠️  无效URL格式（跳过）: $line_trimmed"
    fi
done < "$INPUT_FILE"

echo ""
echo "📊 统计信息:"
echo "  总行数: $TOTAL_LINES"
echo "  有效URL: $VALID_URLS"
echo "  跳过: $((TOTAL_LINES - VALID_URLS))"
echo ""

if [[ $VALID_URLS -eq 0 ]]; then
    echo "❌ 没有有效的URL，退出"
    exit 1
fi

read -p "开始处理 $VALID_URLS 个视频？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消处理"
    exit 0
fi

# 处理函数
process_url() {
    local url="$1"
    local index="$2"
    local total="$3"
    
    # 为每个URL创建单独的输出目录
    local url_safe=$(echo "$url" | tr -cd '[:alnum:]._-' | head -c 50)
    local item_output="$OUTPUT_DIR/$(printf "%03d" $index)_${url_safe}"
    local log_file="$OUTPUT_DIR/logs/$(printf "%03d" $index).log"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始处理 $index/$total: $url" | tee -a "$log_file"
    echo "输出目录: $item_output" | tee -a "$log_file"
    
    # 构建命令
    local cmd="python $SCRIPT_DIR/video_to_summary.py"
    cmd="$cmd --url \"$url\""
    cmd="$cmd --output-dir \"$item_output\""
    cmd="$cmd --language \"$LANGUAGE\""
    cmd="$cmd --model \"$MODEL\""
    
    if [[ "$AUDIO_ONLY" == true ]]; then
        cmd="$cmd --audio-only"
    fi
    
    # 执行命令
    {
        echo "执行命令: $cmd"
        echo "---"
        
        eval $cmd
        
        if [[ $? -eq 0 ]]; then
            echo "✅ 处理成功: $url"
        else
            echo "❌ 处理失败: $url"
        fi
        
        echo "---"
        echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    } 2>&1 | tee -a "$log_file"
    
    echo "" | tee -a "$log_file"
}

# 导出函数以便在并行中使用
export -f process_url
export SCRIPT_DIR OUTPUT_DIR AUDIO_ONLY LANGUAGE MODEL

# 使用parallel或for循环进行并行处理
echo "🔄 开始并行处理（最大 $PARALLEL 个进程）..."
echo ""

# 生成索引数组
INDICES=($(seq 1 $VALID_URLS))

# 使用GNU parallel（如果可用）
if command -v parallel &> /dev/null; then
    echo "使用GNU parallel进行并行处理"
    parallel --jobs $PARALLEL --progress --bar \
        process_url {1} {#} $VALID_URLS ::: "${URLS[@]}"
else
    echo "GNU parallel未安装，使用简单并行"
    echo ""
    
    # 简单的并行实现
    current_jobs=0
    declare -A pids
    
    for i in "${!URLS[@]}"; do
        index=$((i + 1))
        url="${URLS[$i]}"
        
        # 处理URL（在后台运行）
        process_url "$url" "$index" "$VALID_URLS" &
        pid=$!
        pids[$pid]=$index
        
        current_jobs=$((current_jobs + 1))
        
        echo "启动任务 $index/$VALID_URLS (PID: $pid)"
        
        # 如果达到并行限制，等待任意一个进程完成
        if [[ $current_jobs -ge $PARALLEL ]]; then
            wait -n
            current_jobs=$((current_jobs - 1))
            
            # 从pid数组中移除完成的进程
            for completed_pid in "${!pids[@]}"; do
                if ! kill -0 "$completed_pid" 2>/dev/null; then
                    echo "任务 ${pids[$completed_pid]} 完成 (PID: $completed_pid)"
                    unset pids[$completed_pid]
                fi
            done
        fi
    done
    
    # 等待所有剩余进程完成
    echo ""
    echo "等待剩余任务完成..."
    wait
fi

# 生成汇总报告
echo ""
echo "📊 生成汇总报告..."

SUMMARY_FILE="$OUTPUT_DIR/批量处理报告.md"

{
    echo "# 批量视频处理报告"
    echo ""
    echo "## 处理概要"
    echo "- 处理时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "- 输入文件: $(realpath "$INPUT_FILE")"
    echo "- 输出目录: $(realpath "$OUTPUT_DIR")"
    echo "- 总URL数: $VALID_URLS"
    echo "- 并行数量: $PARALLEL"
    echo "- 语言设置: $LANGUAGE"
    echo "- 模型设置: $MODEL"
    echo "- 仅音频模式: $AUDIO_ONLY"
    echo ""
    echo "## 处理结果"
    echo ""
    echo "| 序号 | URL | 状态 | 输出目录 |"
    echo "|------|-----|------|----------|"
    
    success_count=0
    fail_count=0
    
    for i in "${!URLS[@]}"; do
        index=$((i + 1))
        url="${URLS[$i]}"
        url_safe=$(echo "$url" | tr -cd '[:alnum:]._-' | head -c 50)
        item_output="$OUTPUT_DIR/$(printf "%03d" $index)_${url_safe}"
        log_file="$OUTPUT_DIR/logs/$(printf "%03d" $index).log"
        
        # 检查是否成功
        if [[ -f "$item_output/metadata.json" ]]; then
            status="✅ 成功"
            success_count=$((success_count + 1))
        else
            status="❌ 失败"
            fail_count=$((fail_count + 1))
        fi
        
        # 缩短URL显示
        display_url=$(echo "$url" | cut -c1-50)
        if [[ ${#url} -gt 50 ]]; then
            display_url="$display_url..."
        fi
        
        echo "| $index | $display_url | $status | $(basename "$item_output") |"
    done
    
    echo ""
    echo "## 统计"
    echo "- 成功: $success_count"
    echo "- 失败: $fail_count"
    echo "- 成功率: $(awk "BEGIN {printf \"%.1f%%\", $success_count/$VALID_URLS*100}")"
    echo ""
    echo "## 日志文件"
    echo "详细日志保存在: $OUTPUT_DIR/logs/"
    echo ""
    echo "---"
    echo "*报告由视频转文字总结工具自动生成*"
    
} > "$SUMMARY_FILE"

echo "✅ 批量处理完成！"
echo ""
echo "📋 汇总信息:"
echo "  成功: $success_count"
echo "  失败: $fail_count"
echo "  成功率: $(awk "BEGIN {printf \"%.1f%%\", $success_count/$VALID_URLS*100}")"
echo ""
echo "📁 输出目录: $OUTPUT_DIR"
echo "📄 汇总报告: $SUMMARY_FILE"
echo "📋 详细日志: $OUTPUT_DIR/logs/"
echo ""
echo "🎉 所有任务已完成！"