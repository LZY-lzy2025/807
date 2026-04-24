import base64
import re
import os
from curl_cffi import requests

# 你的目标 URL
TARGET_URL = "https://iptv807.com/?act=play&token=053b6c92f9990e708b1670c29a65ffa1&tid=ty&id=1"

# 控制台拿到的真实 XOR 密钥
SECRET_KEY = "iptv.com"

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
        layer1_bytes = base64.b64decode(xliyw_base64)
        layer2_str = xor_decrypt(layer1_bytes, secret_key).decode('utf-8')
        layer3_bytes = base64.b64decode(layer2_str)
        return layer3_bytes.decode('utf-8')
    except Exception as e:
        print(f"剥壳失败: {e}")
        return None

def main():
    print(f"正在获取网页源码 (使用 Chrome 伪装): {TARGET_URL}")
    
    try:
        # 这里的 impersonate="chrome110" 是魔法核心，完美模拟 Chrome 110 的底层指纹
        response = requests.get(
            TARGET_URL, 
            impersonate="chrome110", 
            timeout=15
        )
        html = response.text
        
        if response.status_code != 200:
            print(f"获取失败，HTTP 状态码: {response.status_code}")
            return
            
    except Exception as e:
        print(f"网络请求报错: {e}")
        return

    print("正在提取密文和动态密钥...")
    payload_match = re.search(r'var xliyw="([^"]+)"', html)
    key_match = re.search(r'var jetvh="([^"]+)"', html)

    if not payload_match or not key_match:
        print("提取失败，网页结构可能已更改，或者抓到了验证码页面。")
        return

    xliyw_payload = payload_match.group(1)
    raw_key = key_match.group(1)
    real_key = raw_key[::-1]
    
    print(f"提取成功！外层密文长度: {len(xliyw_payload)}, 真实密钥: {real_key}")
    print("开始剥壳解析...")
    
    hidden_script = dump_hidden_script(xliyw_payload, real_key)

    if hidden_script:
        output_file = "hidden_script.js"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(hidden_script)
        print(f"剥壳完成！已保存为 {output_file}")
        print("--- 核心代码前 500 字符预览 ---")
        print(hidden_script[:500] + "\n......")
    else:
        print("未能解密出有效内容。")

if __name__ == "__main__":
    main()
