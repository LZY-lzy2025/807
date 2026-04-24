import base64
import os
from urllib.parse import urlparse

# 这里的 key 是从网页源码 jetvh="mov" 反转得到的
# 如果未来网页更新了密钥，直接修改这里即可
SECRET_KEY = "vom"

def rc4_decrypt(data_bytes, key_string):
    """标准的 RC4 流密码解密算法"""
    # KSA (密钥调度)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + ord(key_string[i % len(key_string)])) % 256
        S[i], S[j] = S[j], S[i]
    
    # PRGA (伪随机生成)
    i = j = 0
    out = []
    for byte in data_bytes:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        out.append(chr(byte ^ K))
        
    return "".join(out)

def smart_decode(encrypted_str):
    """智能处理 Base64：判断是否被反转"""
    # 如果密文以 '=' 开头，说明是反转过的 Base64（比如线路 option 的值）
    if encrypted_str.startswith('='):
        encrypted_str = encrypted_str[::-1]
    
    # 补全 Base64 可能缺失的 '=' 填充位
    missing_padding = len(encrypted_str) % 4
    if missing_padding:
        encrypted_str += '=' * (4 - missing_padding)
        
    return base64.b64decode(encrypted_str)

def decrypt_stream_url(encrypted_str, key):
    if not encrypted_str.strip():
        return ""
    
    try:
        # 第一步：智能 Base64 解码提取加密的字节流
        encrypted_bytes = smart_decode(encrypted_str.strip())
        
        # 第二步：使用提取到的密钥进行 RC4 解密
        decrypted_text = rc4_decrypt(encrypted_bytes, key)
        
        # 第三步：兼容性拦截，修复特定 CDN 的握手失败问题
        parsed = urlparse(decrypted_text)
        if "bytefcdnrd.com" in parsed.netloc and parsed.scheme == "https":
            decrypted_text = decrypted_text.replace("https://", "http://", 1)
            
        return decrypted_text
    except Exception as e:
        return f"解码失败 ({encrypted_str[:15]}...): {e}"

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
