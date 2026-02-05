# -*- coding: utf-8 -*-
# @Time    : 2026/2/5 13:19
# @Author  : cy1026
# @File    : main.py
# @Software: PyCharm





import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from typing import Dict, List

app = FastAPI(title="Task Incubator")

# --- 内存数据库 ---
# 结构: { id: {title, base_score, gift_score, created_at} }
tasks_db: Dict[int, dict] = {
    1: {"title": "开发游戏核心逻辑", "base_score": 50, "gift_score": 0, "created_at": time.time() - 36000}, # 10小时前
    2: {"title": "直播写网页代码", "base_score": 30, "gift_score": 0, "created_at": time.time() - 3600},  # 1小时前
}

# --- 核心算法 ---
def calculate_weight(task: dict) -> float:
    """
    动态权重公式：基础分 + 礼物分 + (搁置时间h * 增长系数)
    这里设定每小时自然增长 10 分
    """
    elapsed_hours = (time.time() - task["created_at"]) / 3600
    growth_score = elapsed_hours * 10
    return round(task["base_score"] + task["gift_score"] + growth_score, 2)

# --- API 接口 ---

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <h1>任务孵化引擎已启动</h1>
    <p>访问 <a href="/docs">/docs</a> 进行接口交互测试</p>
    <p>访问 <a href="/rank">/rank</a> 查看实时权重排序</p>
    """

@app.get("/rank")
async def get_rank():
    """获取按动态权重排序后的列表"""
    items = []
    for tid, data in tasks_db.items():
        current_w = calculate_weight(data)
        items.append({
            "id": tid,
            "title": data["title"],
            "current_weight": current_w,
            "born_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["created_at"]))
        })
    # 按权重降序排列
    return sorted(items, key=lambda x: x["current_weight"], reverse=True)

@app.post("/gift/{task_id}")
async def send_gift(task_id: int, gold: int):
    """观众刷礼物接口：1金币 = 5权重"""
    if task_id in tasks_db:
        tasks_db[task_id]["gift_score"] += gold * 5
        return {"msg": f"老板大气！任务 {task_id} 权重提升了 {gold*5}"}
    return {"msg": "找不到该任务"}, 404

@app.post("/add")
async def add_task(task_id: int, title: str, base_score: int):
    """新增任务接口"""
    tasks_db[task_id] = {
        "title": title,
        "base_score": base_score,
        "gift_score": 0,
        "created_at": time.time()
    }
    return {"msg": "任务已入库，开始孵化..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)