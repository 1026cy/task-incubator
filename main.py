# -*- coding: utf-8 -*-
# @Time    : 2026/2/5 13:19
# @Author  : cy1026
# @File    : main.py
# @Software: PyCharm

import time
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import uvicorn

app = FastAPI(title="Idea Incubator System")

# --- 1. 内存数据库 ---
# 存放所有点子和任务
tasks_db: Dict[int, dict] = {}


# --- 2. 数据模型 ---
class IdeaAnalysis(BaseModel):
    capability: int = Field(..., ge=0, le=10)
    revenue: int = Field(..., ge=0, le=10)
    passion: int = Field(..., ge=0, le=10)
    difficulty: int = Field(..., ge=0, le=10)


# --- 3. 核心算法逻辑 ---
def get_current_weight(task: dict) -> float:
    if task["status"] == "draft":
        return 0.0

    # 计算孵化时长（小时）
    elapsed_hours = (time.time() - task["created_at"]) / 3600

    # 动态增长系数：难度越小，自然成熟（权重增长）越快
    # 设定：每小时基础增长 10 分，受难度调节
    diff = task["analysis"]["difficulty"]
    growth_rate = 10 / (diff if diff > 0 else 1)

    # 最终权重 = 初始分 + 礼物分 + (时间 * 增长率)
    weight = task["base_score"] + task["gift_score"] + (elapsed_hours * growth_rate)

    # 如果已手动标记为“执行中”，额外加 1000 分置顶
    if task["status"] == "active":
        weight += 1000

    return round(weight, 2)


# --- 4. 路由：前端界面 ---

@app.get("/", response_class=HTMLResponse)
async def index():
    """动态首页：如果没点子显示输入框，有点子显示排行榜"""

    # 样式部分 (使用 Tailwind CSS 增强视觉)
    style = """
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #0f172a; color: white; font-family: sans-serif; }
        .card { background: #1e293b; border: 1px solid #334155; }
        .gradient-text { background: linear-gradient(90deg, #60a5fa, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
    """

    if not tasks_db:
        # 初始“增加想法”页面
        content = """
        <div class="flex flex-col items-center justify-center min-h-screen">
            <h1 class="text-6xl font-black mb-4 gradient-text">IDEA INCUBATOR</h1>
            <p class="text-slate-400 mb-8 text-xl">目前孵化器是空的，捕捉你的第一个灵感种子...</p>
            <form action="/quick_propose" method="post" class="w-full max-w-md space-y-4">
                <input type="text" name="title" required placeholder="输入项目点子 (如: 物理效果弹幕插件)" 
                       class="w-full p-4 rounded-xl bg-slate-800 border border-slate-700 focus:ring-2 focus:ring-blue-500 outline-none text-lg">
                <button type="submit" class="w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold text-lg transition-all shadow-lg shadow-blue-500/20">
                    发射灵感 🚀
                </button>
            </form>
        </div>
        """
    else:
        # 排行榜页面
        rank_list = []
        for tid, tdata in tasks_db.items():
            if tdata["status"] != "draft":
                w = get_current_weight(tdata)
                rank_list.append(f"""
                <div class="card p-6 rounded-2xl mb-4 flex justify-between items-center">
                    <div>
                        <span class="text-slate-500 text-sm">#{tid}</span>
                        <h3 class="text-xl font-bold">{tdata['title']}</h3>
                        <p class="text-slate-400 text-sm">状态: {tdata['status']} | 孵化时长: {round((time.time() - tdata['created_at']) / 3600, 2)}h</p>
                    </div>
                    <div class="text-right">
                        <div class="text-3xl font-black text-blue-400">{w}</div>
                        <div class="text-xs text-slate-500">DYNAMIC WEIGHT</div>
                    </div>
                </div>
                """)

        content = f"""
        <div class="max-w-3xl mx-auto py-12">
            <div class="flex justify-between items-end mb-10">
                <h1 class="text-4xl font-black gradient-text">INCUBATION RANK</h1>
                <a href="/docs" class="text-slate-400 hover:text-white border-b border-slate-700">管理后台 (API Docs)</a>
            </div>
            {''.join(rank_list) if rank_list else '<p class="text-slate-500">所有点子尚在草稿状态，请去后台进行 /analyze</p>'}
            <div class="mt-12 p-8 border-2 border-dashed border-slate-800 rounded-3xl text-center">
                <form action="/quick_propose" method="post" class="flex gap-4">
                    <input type="text" name="title" required placeholder="追加新灵感..." class="flex-1 bg-slate-800 rounded-xl p-3 outline-none">
                    <button type="submit" class="bg-slate-700 px-6 py-2 rounded-xl">记录</button>
                </form>
            </div>
        </div>
        """

    return f"<html><head>{style}</head><body>{content}</body></html>"


# --- 5. 接口逻辑 ---

@app.post("/quick_propose")
async def quick_propose(title: str = Form(...)):
    new_id = len(tasks_db) + 1
    tasks_db[new_id] = {
        "id": new_id,
        "title": title,
        "status": "draft",
        "analysis": None,
        "base_score": 0,
        "gift_score": 0,
        "created_at": time.time()
    }
    return HTMLResponse(
        f"<script>alert('灵感已捕获！请前往 /docs 对 ID:{new_id} 进行 analyze 分析以激活孵化。'); window.location.href='/';</script>")


@app.post("/analyze/{id}")
async def analyze_idea(id: int, a: IdeaAnalysis):
    if id not in tasks_db:
        raise HTTPException(status_code=404, detail="未找到点子")

    # 计算基础分：收益(5) + 冲动(3) + 能力(2) - 难度(1)
    base = (a.revenue * 5 + a.passion * 3 + a.capability * 2 - a.difficulty * 1)

    tasks_db[id].update({
        "analysis": a.dict(),
        "base_score": base,
        "status": "incubating",
        "created_at": time.time()
    })
    return {"msg": "分析完成，开始孵化", "base_score": base}


@app.post("/gift/{id}")
async def add_gift(id: int, gold: int):
    if id not in tasks_db: raise HTTPException(status_code=404)
    tasks_db[id]["gift_score"] += gold * 10
    return {"msg": "能量注入成功"}


# --- 6. 运行入口 ---
if __name__ == "__main__":
    # 需要先安装: pip install fastapi uvicorn python-multipart
    uvicorn.run(app, host="127.0.0.1", port=8000)