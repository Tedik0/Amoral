import uuid
from services.xui_client import XUIClient
from config import XUI_URL, XUI_USERNAME, XUI_PASSWORD, INBOUND_ID

xui = XUIClient(XUI_URL, XUI_USERNAME, XUI_PASSWORD)


def test_flow():
    user_uuid = str(uuid.uuid4())
    user_email = f"customer_{uuid.uuid4().hex[:4]}"

    print(f"--- Создание клиента {user_email} ---")

    # 1. Добавляем в панель
    if xui.add_client(INBOUND_ID, user_uuid, user_email):
        print("✅ Клиент успешно добавлен в 3x-ui")

        # 2. Генерируем ссылку
        config_link = xui.get_link(INBOUND_ID, user_uuid, "MyVPN_Premium")

        print("\n🚀 ТВОЯ ССЫЛКА ДЛЯ ПОДКЛЮЧЕНИЯ:")
        print("-" * 50)
        print(config_link)
        print("-" * 50)
    else:
        print("❌ Не удалось добавить клиента. Проверь INBOUND_ID в config.py")


if __name__ == "__main__":
    test_flow()