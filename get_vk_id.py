import urllib.request
import json
import ssl

token = "vk1.a.GZqjYnIiyHtMKq7UfWz3-SzU5KabyxA40z0cu-FHiQ7_wxHTl5rSXRwm0IcLR2gk0ebpDhmZNsoIcDTIvMAcHJL1EOAJB87HSIjUdqpmdO7_BK2UR5wNfVHI1D2EmcSJs-Q_tolKJI41OwPubAGcyUc5HGcRewdp8kq0fD67OvxsW4PC4ICijUiolvzRZPdluCT1jKsEMn0AbGI3VbPEXQ"
url = f"https://api.vk.com/method/messages.getConversations?count=1&access_token={token}&v=5.131"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(url)
try:
    response = urllib.request.urlopen(req, context=ctx)
    data = json.loads(response.read().decode())
    if "response" in data and data["response"]["count"] > 0:
        user_id = data["response"]["items"][0]["conversation"]["peer"]["id"]
        with open("vk_config.json", "w") as f:
            json.dump({"user_id": user_id}, f)
        print(f"Saved user_id {user_id} to vk_config.json")
    else:
        print("No conversations found.")
except Exception as e:
    print("Error:", e)
