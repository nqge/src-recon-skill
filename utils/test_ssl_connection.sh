#!/bin/bash
# 使用多种方法测试 SSL 连接
# 特别针对 legacy renegotiation 问题

test_url() {
    local url="$1"
    local hostname=$(echo "$url" | sed -e 's|https://||' -e 's|/.*||')

    echo "========================================="
    echo "测试 URL: $url"
    echo "========================================="
    echo ""

    # 方法 1: 标准 curl
    echo "方法 1: curl (标准)"
    echo "命令: curl -I $url"
    curl -I "$url" 2>&1 | head -5
    echo ""

    # 方法 2: curl -k
    echo "方法 2: curl -k (跳过证书验证)"
    echo "命令: curl -k -I $url"
    curl -k -I "$url" 2>&1 | head -5
    echo ""

    # 方法 3: curl + SSL 选项
    echo "方法 3: curl --ssl-no-revoke"
    echo "命令: curl --ssl-no-revoke -I $url"
    curl --ssl-no-revoke -I "$url" 2>&1 | head -5
    echo ""

    # 方法 4: wget
    echo "方法 4: wget --no-check-certificate"
    echo "命令: wget --no-check-certificate -qO- $url | head -20"
    wget --no-check-certificate -qO- "$url" 2>&1 | head -20
    echo ""

    # 方法 5: HTTP 而不是 HTTPS
    if [[ "$url" == https://* ]]; then
        http_url="${url/https:\/\//http:\/\/}"
        echo "方法 5: HTTP (非 HTTPS)"
        echo "命令: curl -I $http_url"
        curl -I "$http_url" 2>&1 | head -5
        echo ""
    fi

    # 方法 6: 使用 openssl s_client
    echo "方法 6: openssl s_client (获取证书)"
    echo "命令: openssl s_client -connect $hostname:443 -servername $hostname </dev/null 2>&1 | head -30"
    timeout 5 openssl s_client -connect "$hostname:443" -servername "$hostname" </dev/null 2>&1 | head -30
    echo ""

    echo "========================================="
    echo ""
}

# 如果提供了参数，测试指定的 URL
if [ -n "$1" ]; then
    test_url "$1"
else
    # 否则测试一些示例 URL
    echo "使用方法: $0 <url>"
    echo ""
    echo "示例:"
    echo "  $0 https://pbank.jshbank.com/"
    echo "  $0 https://vision.jshbank.com/"
fi
