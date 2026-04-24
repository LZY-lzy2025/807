import base64
import os
from Crypto.Cipher import DES
from urllib.parse import urlparse

# 从网页控制台拿到的全局 DES 密钥 (8字节)
SECRET_KEY = "iptv.com"

def unpad_pkcs7(data):
    """去除 PKCS7 填充"""
    pad_len = data[-1]
    # 校验填充是否合法
    if pad_len < 1 or pad_len > 8:
        return data
    return data[:-pad_len]

def smart_decode(encrypted_str):
    """智能处理 Base64：判断是否被反转并补齐填充位"""
    if encrypted_str.startswith('='):
        encrypted_str = encrypted_str[::-1]
    
    missing_padding = len(encrypted_str) % 4
    if missing_padding:
        encrypted_str += '=' * (4 - missing_padding)
        
    return base64.b64decode(encrypted_str)

def decrypt_stream_url(encrypted_str, key_str):
    if not encrypted_str.strip():
        return ""
    
    try:
        # 第一步：Base64 提取加密的二进制流
        encrypted_bytes = smart_decode(encrypted_str.strip())
        
        # 第二步：DES-ECB 解密
        key = key_str.encode('utf-8')[:8] 
        cipher = DES.new(key, DES.MODE_ECB)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        # 第三步：去除填充并转为文本
        decrypted_text = unpad_pkcs7(decrypted_bytes).decode('utf-8')
        
        # 第四步：CDN 协议降级拦截 (针对 bytefcdnrd.com 报 ERR_INVALID_RESPONSE 的问题)
        parsed = urlparse(decrypted_text)
        if "bytefcdnrd.com" in parsed.netloc and parsed.scheme == "https":
            decrypted_text = decrypted_text.replace("https://", "http://", 1)
            
        return decrypted_text
    except Exception as e:
        return f"解密失败 ({encrypted_str[:15]}...): {e}"

def main():
    input_file = 'value.txt'
    output_file = 'result.txt'
    
    if not os.path.exists(input_file):
        print(f"找不到 {input_file} 文件，请在同级目录创建并放入密文。")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results = []
    for line in lines:
        line = line.strip()
        if line:
            decrypted = decrypt_stream_url(line, SECRET_KEY)
            if decrypted:
                results.append(decrypted)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))
        
    print(f"成功解密 {len(results)} 条直播源，已保存至 {output_file}。")

if __name__ == "__main__":
    main()
