import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import ssl
import sys
import os

PORT = int(os.environ.get("PORT", 8000))
VK_TOKEN = "vk1.a.GZqjYnIiyHtMKq7UfWz3-SzU5KabyxA40z0cu-FHiQ7_wxHTl5rSXRwm0IcLR2gk0ebpDhmZNsoIcDTIvMAcHJL1EOAJB87HSIjUdqpmdO7_BK2UR5wNfVHI1D2EmcSJs-Q_tolKJI41OwPubAGcyUc5HGcRewdp8kq0fD67OvxsW4PC4ICijUiolvzRZPdluCT1jKsEMn0AbGI3VbPEXQ"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        if self.path == "/link_vk.php":
            try:
                data = json.loads(post_data.decode('utf-8'))
                if data.get('secret_key') == 'super_secret_wedding_key_2024':
                    user_id = data.get('user_id')
                    with open("vk_config.json", "w") as f:
                        json.dump({"user_id": user_id}, f)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success"}).encode())
                    return
            except Exception as e:
                pass
                
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")
            return
            
        if self.path == "/submit_form":
            try:
                form_data = json.loads(post_data.decode('utf-8'))
                
                # Format message
                message = "🔔 Новая анкета от гостя!\n\n"
                for key, val in form_data.items():
                    if val and str(val).strip():
                        message += f"• {key}: {val}\n"
                
                # Send to VK
                user_id = os.environ.get("VK_CLIENT_ID", "156300398") # ID клиента по умолчанию
                
                if not user_id and os.path.exists("vk_config.json"):
                    try:
                        with open("vk_config.json", "r") as f:
                            conf = json.load(f)
                            if conf.get("user_id"):
                                user_id = conf.get("user_id")
                    except:
                        pass
                        
                if user_id:
                    vk_url = "https://api.vk.com/method/messages.send"
                    params = urllib.parse.urlencode({
                        'message': message,
                        'peer_id': user_id,
                        'access_token': VK_TOKEN,
                        'v': '5.131',
                        'random_id': 0
                    })
                    req = urllib.request.Request(f"{vk_url}?{params}")
                    urllib.request.urlopen(req)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
                
            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()
            return
            
        # For Eventrix proxying
        if self.path.startswith("/api/"):
            print("RECEIVED NATIVE API POST REQUEST:", self.path)
            print("DATA:", post_data.decode('utf-8'))
            
            # Попытаемся отправить эти данные в VK, если это сабмит формы
            if "submit" in self.path or "form" in self.path:
                try:
                    form_data = json.loads(post_data.decode('utf-8'))
                    user_id = os.environ.get("VK_CLIENT_ID", "156300398") # ID клиента по умолчанию
                    
                    if not user_id and os.path.exists("vk_config.json"):
                        try:
                            with open("vk_config.json", "r") as f:
                                conf = json.load(f)
                                if conf.get("user_id"):
                                    user_id = conf.get("user_id")
                        except:
                            pass
                            
                    if user_id:
                        message = "🔔 Новая анкета от гостя (Native)!\n\n"
                        # Eventrix usually sends {"fields": {...}} or similar
                        if "fields" in form_data:
                            for key, val in form_data["fields"].items():
                                if val: message += f"• {key}: {val}\n"
                        else:
                            for key, val in form_data.items():
                                if val: message += f"• {key}: {val}\n"
                                
                        vk_url = "https://api.vk.com/method/messages.send"
                        params = urllib.parse.urlencode({
                            'message': message,
                            'peer_id': user_id,
                            'access_token': VK_TOKEN,
                            'v': '5.131',
                            'random_id': 0
                        })
                        req = urllib.request.Request(f"{vk_url}?{params}")
                        urllib.request.urlopen(req)
                except Exception as e:
                    print("Error forwarding native form to VK:", e)
            
            # Фейковый успешный ответ для внутренней формы Eventrix
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": False, "data": True}).encode())
            return
            
        url = f"https://eventrix.pro{self.path}"
        req = urllib.request.Request(url, data=post_data, headers={'User-Agent': 'Mozilla/5.0'})
        if 'Content-Type' in self.headers:
            req.add_header('Content-Type', self.headers['Content-Type'])
            
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                self.send_response(200)
                for k, v in response.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

    def do_GET(self):
        if self.path == '/' or (not '.' in self.path.split('/')[-1] and not self.path.startswith('/api/')):
            self.path = '/index.html'
            super().do_GET()
            return
            
        if self.path == '/index.html':
            super().do_GET()
            return

        url = f"https://eventrix.pro{self.path}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(req, context=ctx) as response:
                content_type = response.headers.get('Content-Type', '')
                
                if self.path.startswith("/api/invites/get/byURL"):
                    data = json.loads(response.read().decode())
                    if "data" in data:
                        data["data"]["purchased"] = True
                        data["data"]["published"] = True
                        
                        if "blocks" in data["data"]:
                            blocks = data["data"]["blocks"]
                            wishes_idx = next((i for i, b in enumerate(blocks) if b.get("id") == "Wishes"), -1)
                            if wishes_idx != -1:
                                w_block = blocks.pop(wishes_idx)
                                d_idx = next((i for i, b in enumerate(blocks) if b.get("id") == "DressCode"), -1)
                                if d_idx != -1:
                                    blocks.insert(d_idx + 1, w_block)
                            
                            for block in blocks:
                                if block.get("id") == "Place":
                                    if "address" in block.get("blocks", {}):
                                        block["blocks"]["address"]["data"] = "ул. Карла Маркса, 23, Киров, Кировская обл.,"
                                    if "time" in block.get("blocks", {}):
                                        block["blocks"]["time"]["data"] = "14:00"
                                elif block.get("id") == "Map":
                                    if "map" in block.get("blocks", {}) and "data" in block["blocks"]["map"] and "d" in block["blocks"]["map"]["data"]:
                                        block["blocks"]["map"]["data"]["d"]["address"] = "ул. Карла Маркса, 23, Киров, Кировская обл.,"
                                        block["blocks"]["map"]["data"]["d"]["coords"] = "58.6137, 49.6662"
                                elif block.get("id") == "Program":
                                    if "PR" in block.get("blocks", {}) and "data" in block["blocks"]["PR"] and "items" in block["blocks"]["PR"]["data"]:
                                        for item in block["blocks"]["PR"]["data"]["items"]:
                                            if item.get("time") == "16:00" and "Фуршет" in item.get("title", ""):
                                                item["desc"] = "Октябрьский пр., 49"
                                elif block.get("id") == "Contacts":
                                    if "cts" in block.get("blocks", {}) and "data" in block["blocks"]["cts"] and "cts" in block["blocks"]["cts"]["data"]:
                                        for ct in block["blocks"]["cts"]["data"]["cts"]:
                                            for link in ct.get("links", []):
                                                if link.get("d") == "+7 (912) 333-19-46":
                                                    link["d"] = "+7 (912) 331-94-61"
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                else:
                    body = response.read()
                    if self.path.endswith(".css"):
                        try:
                            css_text = body.decode('utf-8')
                            css_text = css_text.replace("font-display:swap", "font-display:block").replace("font-display: swap", "font-display: block")
                            body = css_text.encode('utf-8')
                        except:
                            pass
                    
                    self.send_response(200)
                    if content_type:
                        self.send_header('Content-type', content_type)
                    self.end_headers()
                    self.wfile.write(body)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

with ThreadedTCPServer(("", PORT), ProxyHandler) as httpd:
    print(f"Serving at port {PORT} with threads")
    httpd.serve_forever()
