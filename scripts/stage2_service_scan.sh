#!/bin/bash
# 阶段 2: 服务探测脚本
# 使用方法: ./scripts/stage2_service_scan.sh <target>

set -e

# 获取脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 设置变量
TARGET="$1"
STAGE1_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage1"
STAGE2_DIR="${PROJECT_ROOT}/output/recon/${TARGET}/stage2"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查参数
if [ -z "$TARGET" ]; then
    echo -e "${RED}[-] 请输入目标域名${NC}"
    echo "使用方法: $0 <target>"
    exit 1
fi

echo -e "${GREEN}[+] 阶段 2: 服务探测和 IP 解析${NC}"
echo -e "${GREEN}[+] 目标: $TARGET${NC}"
echo -e "${GREEN}[+] 输出目录: $STAGE2_DIR${NC}"

# 检查阶段 1 结果
if [ ! -d "$STAGE1_DIR" ]; then
    echo -e "${RED}[-] 阶段 1 结果不存在，请先运行: ./scripts/stage1_subs_collect.sh $TARGET${NC}"
    exit 1
fi

# 创建输出目录
mkdir -p "$STAGE2_DIR"

# ============================================
# HTTP/HTTPS 服务扫描
# ============================================
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}[*] HTTP/HTTPS 服务扫描${NC}"
echo -e "${BLUE}========================================${NC}"

if [ -f "${STAGE1_DIR}/all_subs_unique.txt" ]; then
    SUB_COUNT=$(wc -l < "${STAGE1_DIR}/all_subs_unique.txt")
    echo "[*] 扫描 $SUB_COUNT 个子域名"
    
    cd "$PROJECT_ROOT"
    python3 core/http_scanner_enhanced.py \
        "${STAGE1_DIR}/all_subs_unique.txt" \
        "${STAGE2_DIR}/http_services.txt" \
        "${STAGE2_DIR}/resolved_ips.txt" \
        "${STAGE2_DIR}/domain_ip_mapping.json"
    
    # 提取可访问的 URL
    if [ -f "${STAGE2_DIR}/http_services.txt" ]; then
        grep -E "^\[200\]|^\[30[0-9]\]|^\[403\]" "${STAGE2_DIR}/http_services.txt" | \
            awk '{print $2}' > "${STAGE2_DIR}/http_accessible_urls.txt" 2>/dev/null || touch "${STAGE2_DIR}/http_accessible_urls.txt"
        
        HTTP_COUNT=$(wc -l < "${STAGE2}/http_accessible_urls.txt" 2>/dev/null || echo "0")
        echo -e "${GREEN}[+] 发现 $HTTP_COUNT 个可访问的 HTTP 服务${NC}"
    fi
    
    cd - > /dev/null || true
else
    echo -e "${YELLOW}[!] 子域名列表不存在，跳过 HTTP 扫描${NC}"
fi

# ============================================
# IP 整合和去重
# ============================================
echo -e "\n${YELLOW}[*] IP 整合和去重${NC}"

> "${STAGE2_DIR}/all_ips.txt"
> "${STAGE2_DIR}/all_ips_unique.txt"

# 收集阶段 1 的 IP
if [ -f "${STAGE1_DIR}/all_ips_unique.txt" ]; then
    cat "${STAGE1_DIR}/all_ips_unique.txt" >> "${STAGE2_DIR}/all_ips.txt"
fi

# 添加阶段 2 解析的 IP
if [ -f "${STAGE2_DIR}/resolved_ips.txt" ]; then
    cat "${STAGE2_DIR}/resolved_ips.txt" >> "${STAGE2_DIR}/all_ips.txt"
fi

# 从域名重新解析 IP（如果需要）
if [ -f "${STAGE1_DIR}/all_subs_unique.txt" ]; then
    echo "[*] 从子域名重新解析 IP..."
    
    while IFS= read -r subdomain; do
        # 获取所有 A 记录
        host -t A "$subdomain" 2>/dev/null | grep "has address" | awk '{print $4}' >> "${STAGE2_DIR}/all_ips.txt"
    done < "${STAGE1_DIR}/all_subs_unique.txt"
fi

# 去重
sort -u "${STAGE2_DIR}/all_ips.txt" -o "${STAGE2_DIR}/all_ips_unique.txt"

IP_COUNT=$(wc -l < "${STAGE_DIR}/all_ips_unique.txt" 2>/dev/null || echo "0")
echo -e "${GREEN}[+] 汇总去重后得到 $IP_COUNT 个唯一 IP${NC}"

# ============================================
# 连接错误改进
# ============================================
echo -e "\n${YELLOW}[*] 连接错误改进${NC}"

if [ -f "${STAGE2_DIR}/http_services.txt" ]; then
    ERROR_COUNT=$(grep "\[ERROR\]" "${STAGE2_DIR}/http_services.txt" 2>/dev/null | wc -l || echo "0")
    
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "[*] 发现 $ERROR_COUNT 个有错误的 URL"
        
        # 提取错误 URL
        grep "\[ERROR\]" "${STAGE2_DIR}/http_services.txt" | awk '{print $2}' > "${STAGE2_DIR}/error_urls.txt"
        
        # 使用 HTTP 访问测试工具
        echo "[*] 尝试改进连接..."
        cd "$PROJECT_ROOT"
        python3 core/http_access_tester.py \
            "${STAGE2_DIR}/error_urls.txt" \
            "${STAGE2_DIR}/http_access_improvement.txt" 2>/dev/null || true
        
        # 合并新发现的 URL
        if [ -f "${STAGE2_DIR}/http_access_improvement.txt" ]; then
            echo "[*] 检查改进后的可访问 URL..."
            
            # 从改进报告中提取可访问的 URL
            grep -E "状态码 200|方法.*success" "${STAGE2_DIR}/http_access_improvement.txt" | \
                grep -oP "https?://[^\s]+" | sort -u >> "${STAGE2_DIR}/http_accessible_urls.txt" 2>/dev/null || true
            
            UPDATED_HTTP_COUNT=$(wc -l < "${STAGE2_DIR}/http_accessible_urls.txt" 2>/dev/null || echo "0")
            echo -e "${GREEN}[+] 更新后可访问的 HTTP 服务: $UPDATED_HTTP_COUNT${NC}"
        fi
        
        cd - > /dev/null || true
    else
        echo "[*] 没有发现连接错误"
    fi
else
    echo "[*] 没有发现 HTTP 扫描结果"
fi

# ============================================
# 输出摘要
# ============================================
echo -e "\n${GREEN}[+] 阶段 2 完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[*] 服务探测统计${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  HTTP 服务: $HTTP_COUNT 个"
echo -e "  唯一 IP: $IP_COUNT 个"
echo ""
echo -e "${YELLOW}[+] 下一阶段: 运行 ./scripts/stage3_port_scan.sh $TARGET"
echo -e "${YELLOW}[+] 或继续执行: ./scripts/stage2_service_scan.sh $TARGET"
echo -e "${YELLOW}[+] 完整流程: ./scripts/src-recon-auto-optimized.sh $TARGET"
echo -e "${BLUE}========================================${NC}"
