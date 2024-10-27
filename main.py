# @Time    : 2023/8/9 23:23
# @Author  : Lan
# @File    : main.py
# @Software: PyCharm
import asyncio

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

from apps.base.models import KeyValue
from apps.base.utils import ip_limit
from apps.base.views import share_api
from apps.admin.views import admin_api
from core.response import APIResponse
from core.settings import data_root, settings, BASE_DIR, DEFAULT_CONFIG
from core.tasks import delete_expire_files

from contextlib import asynccontextmanager
from tortoise import Tortoise


async def init_db():
    await Tortoise.init(
        db_url=f'sqlite://{data_root}/filecodebox.db',
        modules={'models': ['apps.base.models']},
        use_tz=False,
        timezone="Asia/Shanghai"
    )
    await Tortoise.generate_schemas()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    await init_db()

    # 启动后台任务
    task = asyncio.create_task(delete_expire_files())

    # 加载配置
    await load_config()

    try:
        yield
    finally:
        # 清理操作
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        await Tortoise.close_connections()


async def load_config():
    user_config, _ = await KeyValue.get_or_create(key='settings', defaults={'value': DEFAULT_CONFIG})
    settings.user_config = user_config.value
    # 更新 ip_limit 配置
    ip_limit['error'].minutes = settings.errorMinute
    ip_limit['error'].count = settings.errorCount
    ip_limit['upload'].minutes = settings.uploadMinute
    ip_limit['upload'].count = settings.uploadCount


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/assets', StaticFiles(directory='./fcb-fronted/dist/assets'), name="assets")

<<<<<<< HEAD
@app.get('/assets/{file_path:path}')
async def assets(file_path: str):
    if settings.max_save_seconds > 0:
        if re.match(r'SendView-[\d|a-f|A-F]+\.js', file_path):
            with open(BASE_DIR / f'./FileCodeBoxFronted/dist/assets/{file_path}', 'r', encoding='utf-8') as f:
                # 删除永久保存选项
                content = f.read()
                content = content.replace('_(c,{label:e(r)("send.expireData.forever"),value:"forever"},null,8,["label"]),', '')
                return HTMLResponse(content=content, media_type='text/javascript')
        if re.match(r'index-[\d|a-f|A-F]+\.js', file_path):
            with open(BASE_DIR / f'./FileCodeBoxFronted/dist/assets/{file_path}', 'r', encoding='utf-8') as f:
                # 更改本文描述
                desc_zh, desc_en = await max_save_times_desc(settings.max_save_seconds)
                content = f.read()
                content = content.replace('天数<7', desc_zh)
                content = content.replace('Days <7', desc_en)
                return HTMLResponse(content=content, media_type='text/javascript')
    return FileResponse(f'./FileCodeBoxFronted/dist/assets/{file_path}')


=======
# 使用 register_tortoise 来添加异常处理器
>>>>>>> 9ba7d3779685b3e7be7e2e918c58ace143ad2bad
register_tortoise(
    app,
    config={
        'connections': {'default': f'sqlite://{data_root}/filecodebox.db'},
        'apps': {
            'models': {
                'models': ['apps.base.models'],
                'default_connection': 'default',
            },
        },
    },
    generate_schemas=False,  # 我们已经在 init_db 中生成了 schema
    add_exception_handlers=True,
)

app.include_router(share_api)
app.include_router(admin_api)


@app.get('/')
async def index():
    return HTMLResponse(
<<<<<<< HEAD
        content=open(BASE_DIR / './FileCodeBoxFronted/dist/index.html', 'r', encoding='utf-8').read()
=======
        content=open(BASE_DIR / 'fcb-fronted/dist/index.html', 'r', encoding='utf-8').read()
>>>>>>> 9ba7d3779685b3e7be7e2e918c58ace143ad2bad
        .replace('{{title}}', str(settings.name))
        .replace('{{description}}', str(settings.description))
        .replace('{{keywords}}', str(settings.keywords))
        .replace('{{opacity}}', str(settings.opacity))
        .replace('{{background}}', str(settings.background))
        , media_type='text/html', headers={'Cache-Control': 'no-cache'})


@app.get('/robots.txt')
async def robots():
    return HTMLResponse(content=settings.robotsText, media_type='text/plain')


@app.post('/')
async def get_config():
    return APIResponse(detail={
        'explain': settings.page_explain,
        'uploadSize': settings.uploadSize,
        'expireStyle': settings.expireStyle,
        'openUpload': settings.openUpload,
        'notify_title': settings.notify_title,
        'notify_content': settings.notify_content,
        'show_admin_address': settings.showAdminAddr,
    })


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app='main:app', host="0.0.0.0", port=settings.port, reload=False, workers=1)
