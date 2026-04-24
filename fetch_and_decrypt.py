import base64
import re
import requests
import os

# 替换为你实际想要抓取的网页地址
TARGET_URL = "https://iptv807.com/?act=play&token=053b6c92f9990e708b1670c29a65ffa1&tid=ty&id=1" 

def xor_decrypt(data_bytes, key_string):
    """标准的循环 XOR 解密算法"""
    key_bytes = key_string.encode('utf-8')
    out = []
    for i, byte in enumerate(data_bytes):
        out.append(byte ^ key_bytes[i % len(key_bytes)])
    return bytes(out)

def dump_hidden_script(xliyw_base64, secret_key):
    """三层剥壳解密"""
    try:
        # 第一层：解析最外层的 Base64
        layer1_bytes = base64.b64decode(xliyw_base64)
        
        # 第二层：使用提取到的密钥进行 XOR 解密
        layer2_str = xor_decrypt(layer1_bytes, secret_key).decode('utf-8')
        
        # 第三层：解密出来的结果是新的 Base64 字符串，再次解码
        layer3_bytes = base64.b64decode(layer2_str)
        
        # 得到最终被隐藏的明文 JS 代码
        return layer3_bytes.decode('utf-8')
    except Exception as e:
        print(f"剥壳失败: {e}")
        return None

def main():
    print(f"正在获取网页源码: {TARGET_URL}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        print(f"获取网页失败: {e}")
        return

    print("正在提取密文和动态密钥...")
    # 用正则提取 xliyw 变量 (外层密文)
    payload_match = re.search(r'var xliyw="([^"]+)"', html)
    # 用正则提取 jetvh 变量 (反转前的密钥)
    key_match = re.search(r'var jetvh="([^"]+)"', html)

    if not payload_match or not key_match:
        print("提取失败，网页结构可能已更改。")
        return

    xliyw_payload = payload_match.group(1)
    raw_key = key_match.group(1)
    
    # 还原真实密钥 (字符串反转)
    real_key = raw_key[::-1]
    print(f"提取成功！外层密文长度: {len(xliyw_payload)}, 真实密钥: {real_key}")

    print("开始剥壳解析...")
    hidden_script = dump_hidden_script(xliyw_payload, real_key)

    if hidden_script:
        output_file = "hidden_script.js"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(hidden_script)
        print(f"剥壳完成！已保存为 {output_file}")
        print("--- 核心代码预览 ---")
        print(hidden_script[:500] + "\n......")
    else:
        print("未能解密出有效内容。")

if __name__ == "__main__":
    main()
