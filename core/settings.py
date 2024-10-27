# @Time    : 2023/8/15 09:51
# @Author  : Lan
# @File    : settings.py
# @Software: PyCharm
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
data_root = BASE_DIR / 'data'

if not data_root.exists():
    data_root.mkdir(parents=True, exist_ok=True)

DEFAULT_CONFIG = {
    'file_storage': 'local',
    'name': '文件快递柜 - FileCodeBox',
    'description': '开箱即用的文件快传系统',
    'notify_title': '系统通知',
    'notify_content': '欢迎使用 FileCodeBox，本程序开源于 <a href="https://github.com/vastsa/FileCodeBox" target="_blank">Github</a> ，欢迎Star和Fork。',
    'page_explain': '请勿上传或分享违法内容。根据《中华人民共和国网络安全法》、《中华人民共和国刑法》、《中华人民共和国治安管理处罚法》等相关规定。 传播或存储违法、违规内容，会受到相关处罚，严重者将承担刑事责任。本站坚决配合相关部门，确保网络内容的安全，和谐，打造绿色网络环境。',
    'keywords': 'FileCodeBox, 文件快递柜, 口令传送箱, 匿名口令分享文本, 文件',
    's3_access_key_id': '',
    's3_secret_access_key': '',
    's3_bucket_name': '',
    's3_endpoint_url': '',
    's3_region_name': 'auto',
    's3_signature_version': 's3v2',
    's3_hostname': '',
    's3_proxy': 0,
    'max_save_seconds': 0,
    'aws_session_token': '',
    'onedrive_domain': '',
    'onedrive_client_id': '',
    'onedrive_username': '',
    'onedrive_password': '',
    'onedrive_root_path': 'filebox_storage',
    'onedrive_proxy': 0,
    'admin_token': 'FileCodeBox2023',
    'openUpload': 1,
    'uploadSize': 1024 * 1024 * 10,
    'expireStyle': ['day', 'hour', 'minute', 'forever', 'count'],
    'uploadMinute': 1,
    'opacity': 0.9,
    'background': '',
    'uploadCount': 10,
    'errorMinute': 1,
    'errorCount': 1,
    'port': 12345,
    'showAdminAddr': 0,
    'robotsText': 'User-agent: *\nDisallow: /',
}


import sqlite3
import json

class Settings:
    __instance = None
    DB_NAME = str(data_root / 'settings.db')

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, config):
        if not hasattr(self, '_initialized'):
            self._initialize_settings()
            self._initialized = True
            self.default_config = config

    def _initialize_settings(self):
        self._create_table()
        self._load_settings()

    def _create_table(self):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings
            (key TEXT PRIMARY KEY, value TEXT)
        ''')
        conn.commit()
        conn.close()

    def _load_settings(self):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM settings')
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self._insert_default_settings()
        else:
            for key, value in rows:
                setattr(self, key, json.loads(value))

    def _insert_default_settings(self):
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()
        for key, value in DEFAULT_CONFIG.items():
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                           (key, json.dumps(value)))
        conn.commit()
        conn.close()
        self._load_settings()

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            conn = sqlite3.connect(self.DB_NAME)
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                           (key, json.dumps(value)))
            conn.commit()
            conn.close()
        super().__setattr__(key, value)

    def items(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}.items()


settings = Settings(DEFAULT_CONFIG)
