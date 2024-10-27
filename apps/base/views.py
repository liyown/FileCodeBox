from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from apps.admin.dependencies import admin_required
from apps.base.models import FileCodes
from apps.base.schemas import SelectFileModel
from apps.base.utils import get_expire_info, get_file_path_name, ip_limit
from core.response import APIResponse
from core.settings import settings
from core.storage import storages, FileStorageInterface
from core.utils import get_select_token
from pathlib import Path
import os
import hashlib
import shutil
from multiprocessing import Pool, Manager
from functools import partial

share_api = APIRouter(prefix='/share', tags=['分享'])


async def create_file_code(code, **kwargs):
    return await FileCodes.create(code=code, **kwargs)


@share_api.post('/text/', dependencies=[Depends(admin_required)])
async def share_text(
        text: str = Form(...),
        expire_value: int = Form(default=1, gt=0),
        expire_style: str = Form(default='day'),
        ip: str = Depends(ip_limit['upload'])
):
    text_size = len(text.encode('utf-8'))
    max_txt_size = 222 * 1024
    if text_size > max_txt_size:
        raise HTTPException(status_code=403, detail='内容过多,建议采用文件形式')

    expired_at, expired_count, used_count, code = await get_expire_info(expire_value, expire_style)
    await create_file_code(
        code=code,
        text=text,
        expired_at=expired_at,
        expired_count=expired_count,
        used_count=used_count,
        size=len(text),
        prefix='文本分享'
    )
    ip_limit['upload'].add_ip(ip)
    return APIResponse(detail={'code': code})
import io
async def adapt_chunked_upload(file: UploadFile, chunk_number: int, chunk_total: int, file_identifier: str):
    """处理分片上传的适配器"""
    # 创建临时文件夹存储分片
    temp_dir = data_root / "temp" / file_identifier
    os.makedirs(temp_dir, exist_ok=True)
    
    # 保存当前分片
    chunk_file = temp_dir / f"chunk_{chunk_number}"
    chunk_content = await file.read()
    
    # 验证分片大小
    if len(chunk_content) > settings.uploadSize:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise HTTPException(status_code=403, detail=f'分片大小超过限制,最大为{settings.uploadSize/(1024*1024):.2f} MB')
        
    with open(chunk_file, "wb") as f:
        f.write(chunk_content)
        
    # 检查已上传的分片
    uploaded_chunks = []
    missing_chunks = []
    for i in range(chunk_total):
        if os.path.exists(temp_dir / f"chunk_{i}"):
            uploaded_chunks.append(i)
        else:
            missing_chunks.append(i)
            
    if missing_chunks:
        return APIResponse(detail={
            'uploaded_chunks': uploaded_chunks,
            'missing_chunks': missing_chunks,
            'chunk_total': chunk_total
        })
        
    # 使用更大的缓冲区来提高性能
    buffer_size = 20 * 1024 * 1024  # 8MB buffer
    total_size = 0
    final_md5 = hashlib.md5()
    
    try:
        # 创建最终文件
        final_file_path = temp_dir / (file_identifier + os.path.splitext(file.filename)[1])
        
        with open(final_file_path, "wb") as final_file:
            for i in range(chunk_total):
                chunk_path = temp_dir / f"chunk_{i}"
                chunk_size = 0
                with open(chunk_path, "rb") as chunk:
                    while True:
                        data = chunk.read(buffer_size)
                        if not data:
                            break
                        final_file.write(data)
                        chunk_size += len(data)
                        final_md5.update(data)
                total_size += chunk_size
                    
        # 验证总文件大小
        if total_size > settings.uploadSize:
            shutil.rmtree(temp_dir)
            raise HTTPException(status_code=403, detail=f'文件总大小超过限制,最大为{settings.uploadSize/(1024*1024):.2f} MB')
        
        # 验证最终文件MD5
        if final_md5.hexdigest() != file_identifier:
            shutil.rmtree(temp_dir)
            raise HTTPException(status_code=400, detail='文件完整性校验失败')
                
        # 清理临时分片文件
        for i in range(chunk_total):
            os.remove(temp_dir / f"chunk_{i}")
            
        return str(final_file_path)
        
    except Exception as e:
        # 发生错误时清理文件
        if os.path.exists(final_file_path):
            os.remove(final_file_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e

from core.settings import data_root
@share_api.get('/upload/status/')
async def get_upload_status(file_identifier: str, chunk_total: int):
    """获取文件上传状态"""
    temp_dir = data_root / "temp" / file_identifier
    if not os.path.exists(temp_dir):
        return APIResponse(detail={
            'uploaded_chunks': [],
            'missing_chunks': list(range(chunk_total)),
            'chunk_total': chunk_total
        })
        
    uploaded_chunks = []
    missing_chunks = []
    for i in range(chunk_total):
        if os.path.exists(temp_dir / f"chunk_{i}"):
            uploaded_chunks.append(i)
        else:
            missing_chunks.append(i)
            
    return APIResponse(detail={
        'uploaded_chunks': uploaded_chunks,
        'missing_chunks': missing_chunks,
        'chunk_total': chunk_total
    })

import datetime
from core.settings import data_root
@share_api.post('/file/', dependencies=[Depends(admin_required)])
async def share_file(
        expire_value: int = Form(default=1, gt=0),
        expire_style: str = Form(default='day'),
        file: UploadFile = File(...),
        chunk_number: int = Form(default=0),
        chunk_total: int = Form(default=1), 
        chunk_size: int = Form(default=5242880),
        file_identifier: str = Form(default=None),
        ip: str = Depends(ip_limit['upload'])
):
    if expire_style not in settings.expireStyle:
        raise HTTPException(status_code=400, detail='过期时间类型错误')

    file_storage: FileStorageInterface = storages[settings.file_storage]()
    
    # 处理分片上传
    result = await adapt_chunked_upload(file, chunk_number, chunk_total, file_identifier)
    if isinstance(result, APIResponse):
        return result
    
    
    final_file = result 

    expired_at, expired_count, used_count, code = await get_expire_info(expire_value, expire_style)
    
    prefix = os.path.splitext(file.filename)[0]
    suffix = os.path.splitext(file.filename)[1] if os.path.splitext(file.filename)[1] else ''
    uuid_file_name = f"{file_identifier}{suffix}"
    today = datetime.datetime.now()
    path = f"share/data/{today.strftime('%Y/%m/%d')}"
    save_path = data_root / str(Path(path) / uuid_file_name)

    await file_storage.save_file(final_file, save_path)

    # 创建文件记录
    await create_file_code(
        code=code,
        prefix=prefix,
        suffix=suffix,
        uuid_file_name=uuid_file_name,
        file_path=path,
        size=os.path.getsize(save_path),
        expired_at=expired_at,
        expired_count=expired_count,
        used_count=used_count,
    )

    ip_limit['upload'].add_ip(ip)
    return APIResponse(detail={'code': code, 'name': file.filename})


async def get_code_file_by_code(code, check=True):
    file_code = await FileCodes.filter(code=code).first()
    if not file_code:
        return False, '文件不存在'
    if await file_code.is_expired() and check:
        return False, '文件已过期'
    return True, file_code


async def update_file_usage(file_code):
    file_code.used_count += 1
    if file_code.expired_count > 0:
        file_code.expired_count -= 1
    await file_code.save()


@share_api.get('/select/')
async def get_code_file(code: str, ip: str = Depends(ip_limit['error'])):
    file_storage: FileStorageInterface = storages[settings.file_storage]()
    has, file_code = await get_code_file_by_code(code)
    if not has:
        ip_limit['error'].add_ip(ip)
        return APIResponse(code=404, detail=file_code)

    await update_file_usage(file_code)
    return await file_storage.get_file_response(file_code)


@share_api.post('/select/')
async def select_file(data: SelectFileModel, ip: str = Depends(ip_limit['error'])):
    file_storage: FileStorageInterface = storages[settings.file_storage]()
    has, file_code = await get_code_file_by_code(data.code)
    if not has:
        ip_limit['error'].add_ip(ip)
        return APIResponse(code=404, detail=file_code)

    await update_file_usage(file_code)
    return APIResponse(detail={
        'code': file_code.code,
        'name': file_code.prefix + file_code.suffix,
        'size': file_code.size,
        'text': file_code.text if file_code.text is not None else await file_storage.get_file_url(file_code),
    })


@share_api.get('/download')
async def download_file(key: str, code: str, ip: str = Depends(ip_limit['error'])):
    file_storage: FileStorageInterface = storages[settings.file_storage]()
    if await get_select_token(code) != key:
        ip_limit['error'].add_ip(ip)
        raise HTTPException(status_code=403, detail='无效的下载链接')

    has, file_code = await get_code_file_by_code(code, False)
    if not has:
        return APIResponse(code=404, detail='文件不存在')

    return APIResponse(detail=file_code.text) if file_code.text else await file_storage.get_file_response(file_code)
