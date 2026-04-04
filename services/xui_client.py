import time
import requests
import json
from urllib.parse import urlparse, quote  # Добавь вот эту строку!

# Отключаем предупреждения об отсутствии SSL-сертификата (у тебя в логах они были)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class XUIClient:
    def __init__(self, base_url, username, password):
        # Оставляем URL как есть, просто убираем слеш в конце если он есть
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False  # Игнорируем SSL
        self.login(username, password)

    def login(self, username, password):
        try:
            # В 3x-ui логин обычно идет по адресу {base_url}/login
            # Если не сработает, попробуем {base_url}/panel/login
            url = f"{self.base_url}/login"
            r = self.session.post(url, data={"username": username, "password": password}, timeout=10)

            if r.status_code != 200:
                # Пробуем альтернативный путь для старых версий
                url = f"{self.base_url}/panel/login"
                r = self.session.post(url, data={"username": username, "password": password}, timeout=10)

            print(f"📡 Статус логина: {r.status_code}")
            return r.cookies
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")

    def add_client(self, inbound_id, client_uuid, email, days=30):
        expiry_time = int((time.time() + (days * 86400)) * 1000)

        client_settings = {
            "id": client_uuid,
            "alterId": 0,
            "email": email,
            "limitIp": 1,
            "totalGB": 0,
            "expiryTime": expiry_time,
            "enable": True,
            "tgId": "",
            "subId": ""
        }

        params = {
            "id": inbound_id,
            "settings": json.dumps({"clients": [client_settings]})
        }

        try:
            # ВАЖНО: API путь всегда идет ПОСЛЕ твоего секретного пути jqBZ...
            r = self.session.post(
                f"{self.base_url}/panel/api/inbounds/addClient",
                data=params,
                timeout=10
            )

            # Проверяем, что пришел именно JSON
            if "application/json" in r.headers.get("Content-Type", ""):
                res = r.json()
                if res.get("success"):
                    return True
                else:
                    print(f"❌ Ошибка панели: {res.get('msg')}")
            else:
                print(f"❌ Сервер вернул не JSON. Скорее всего, неверный URL или путь. Ответ: {r.text[:100]}")

            return False
        except Exception as e:
            print(f"❌ Ошибка запроса addClient: {e}")
            return False

    from urllib.parse import urlparse, quote
    import json

    def get_link(self, inbound_id, client_uuid, remark):
        """Собирает Reality-ссылку, вытягивая ключи прямо из панели"""
        try:
            # 1. Запрашиваем данные инбаунда
            url = f"{self.base_url}/panel/api/inbounds/get/{inbound_id}"
            r = self.session.get(url, timeout=10)

            if r.status_code != 200:
                r = self.session.post(url, timeout=10)

            res = r.json()
            if not res.get("success"):
                return f"❌ Ошибка API: {res.get('msg')}"

            obj = res.get("obj")
            port = obj.get("port")
            protocol = obj.get("protocol")

            # 2. Парсим настройки сети
            stream_settings = json.loads(obj.get("streamSettings", "{}"))
            net_type = stream_settings.get("network", "tcp")
            security = stream_settings.get("security", "none")

            # Теперь urlparse будет работать, так как мы его импортировали выше
            server_host = urlparse(self.base_url).hostname

            # 3. Собираем параметры
            params = {
                "type": net_type,
                "security": security
            }

            if security == "reality":
                reality_settings = stream_settings.get("realitySettings", {})
                settings = reality_settings.get("settings", {})

                pbk = settings.get("publicKey") or reality_settings.get("publicKey", "")
                sni = reality_settings.get("serverNames", [""])[0]

                sid_list = reality_settings.get("shortIds", [""])
                sid = sid_list[0] if sid_list else ""

                params.update({
                    "pbk": pbk,
                    "sni": sni,
                    "sid": sid,
                    "fp": settings.get("fingerprint", "chrome"),
                    "flow": "xtls-rprx-vision"
                })

            # Склеиваем всё в одну строку
            query_string = "&".join([f"{k}={v}" for k, v in params.items() if v])

            # quote(remark) сделает название ссылки безопасным для браузеров
            return f"{protocol}://{client_uuid}@{server_host}:{port}?{query_string}#VPN_{quote(remark)}"

        except Exception as e:
            return f"❌ Ошибка генерации: {str(e)}"