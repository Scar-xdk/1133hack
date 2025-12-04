import json
import os
from datetime import datetime

class BotManager:
    def __init__(self):
        self.config = json.load(open('config.json', encoding='utf-8'))
        self.users_file, self.gifts_file, self.menu_image = 'data/users.json', 'data/gifts.json', 'data/menu.jpg'
        os.makedirs('data', exist_ok=True)
        for f in [self.users_file, self.gifts_file]:
            if not os.path.exists(f): 
                json.dump({}, open(f, 'w', encoding='utf-8'))

    def _load(self, file):
        return json.load(open(file, encoding='utf-8'))

    def _save(self, file, data):
        json.dump(data, open(file, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)

    def load_users(self): 
        return self._load(self.users_file)

    def save_users(self, users):
        self._save(self.users_file, users)

    def load_gifts(self): 
        return self._load(self.gifts_file)

    def save_gifts(self, gifts):
        self._save(self.gifts_file, gifts)

    def is_admin(self, user_id):
        adm = self.config['admin_id']
        return user_id in adm if isinstance(adm, list) else user_id == adm

    def get_or_create_user(self, user):
        users, uid = self.load_users(), str(user.id)
        if uid not in users:
            users[uid] = {
                "id": user.id,
                "nome": user.first_name or "Usuário",
                "username": user.username or "sem_username",
                "data_start": datetime.now().strftime("%Y-%m-%d"),
                "max_comandos": 0, 
                "ultimo_comando": datetime.now().strftime("%Y-%m-%d"),
                "saldo": 0.0,
                "numeros_comprados": 0,
                "recargas_feitas": 0.0,
                "gifts_resgatados": 0.0,
                "saldo_afiliado": 0.0,
                "indicacoes": 0
            }
            self.save_users(users)
        return users[uid]

# instância global para o projeto inteiro
bot_manager = BotManager()
