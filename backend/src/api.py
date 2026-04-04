import sys
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 确保 src 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator import generate_excel, continue_session, list_sessions

app = FastAPI(title="UI Test Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    url: str
    filepath: str
    username: Optional[str] = ""
    password: Optional[str] = ""
    description: str
    continue_excel: Optional[str] = None  # 可选：继续之前的 session


class ContinueRequest(BaseModel):
    excel_file: str


@app.post("/generate")
def generate_excel_api(req: GenerateRequest):
    """生成 Excel 测试用例

    调用 generator.py 中的 generate_excel 函数，通过 OpenCode 生成测试用例 Excel
    支持继续之前的 session（如果指定了 continue_excel 参数）
    """
    result = generate_excel(
        url=req.url,
        filepath=req.filepath,
        description=req.description,
        username=req.username or "",
        password=req.password or "",
        continue_excel=req.continue_excel
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.post("/continue")
def continue_session_api(req: ContinueRequest):
    """继续 session，读取 Excel 生成测试代码

    调用 generator.py 中的 continue_session 函数，通过 OpenCode 生成 pytest 测试代码
    会自动查找 Excel 文件对应的 session 进行继续
    """
    result = continue_session(req.excel_file)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@app.get("/sessions")
def get_sessions():
    """获取所有保存的 session 列表"""
    result = list_sessions()
    return result


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
