import base64
import os
from urllib.parse import urlparse

def decrypt_stream_url(encrypted_str):
    if not encrypted_str.strip():
        return ""
        
    # 第一步：字符串反转
    reversed_str = encrypted_str.strip()[::-1]
    
    # 第二步：Base64 解码
    try:
        decoded_bytes = base64.b64decode(reversed_str)
        decoded_url = decoded_bytes.decode('utf-8')
        
        # 针对特定 CDN 节点的降级处理
        parsed = urlparse(decoded_url)
        if "bytefcdnrd.com" in parsed.netloc and parsed.scheme == "https":
            decoded_url = decoded_url.replace("https://", "http://", 1)
            
        return decoded_url
    except Exception as e:
        return f"解码失败 ({encrypted_str[:10]}...): {e}"

def main():
    input_file = 'value.txt'
    output_file = 'result.txt'
    
    if not os.path.exists(input_file):
        print(f"找不到 {input_file} 文件，请检查路径。")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    results = []
    for line in lines:
        decrypted = decrypt_stream_url(line)
        if decrypted:
            results.append(decrypted)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))
        
    print(f"成功解密 {len(results)} 条直播源，已保存至 {output_file}。")

if __name__ == "__main__":
    main()
