# -*- coding: utf-8 -*-
# @Time    : 2026/2/5 13:19
# @Author  : cy1026
# @File    : main.py
# @Software: PyCharm

import time
import sqlite3
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from typing import Dict, List

app = FastAPI(title="Visual Idea Incubator")

# --- 数据库设置 ---
DB_NAME = "task_incubator.db"

def db_connect():
    """创建数据库连接"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # 允许通过列名访问数据
    return conn

def init_db():
    """初始化数据库，创建表并插入初始数据"""
    conn = db_connect()
    cursor = conn.cursor()
    
    # 检查表是否已存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    if cursor.fetchone() is None:
        print("Creating 'tasks' table...")
        # 创建 tasks 表
        cursor.execute("""
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'incubating',
            tech_stack TEXT,
            goal_description TEXT,
            my_skills TEXT,
            breakdown TEXT, -- JSON string
            progress INTEGER DEFAULT 0,
            logs TEXT, -- JSON string
            created_at REAL
        )
        """)
        
        # 插入初始数据
        initial_tasks = [
            {
                "id": 1, "title": "AI 辅助写作助手", "status": "active", "tech_stack": "OpenAI API, React",
                "goal_description": "一个能自动生成周报的 Chrome 插件", "my_skills": "JavaScript,HTML,CSS,Python",
                "breakdown": json.dumps([
                    {"module": "用户界面 (Popup)", "priority": "P0", "tasks": [
                        {"name": "设计配置面板", "required_skill": "HTML", "usage_note": "使用 TailwindCSS", "difficulty": 1, "est_hours": 2, "completed": True},
                        {"name": "实现点击事件", "required_skill": "JavaScript", "usage_note": "绑定 onClick", "difficulty": 2, "est_hours": 3, "completed": False}
                    ]},
                    {"module": "核心逻辑 (Background)", "priority": "P0", "tasks": [
                        {"name": "调用 GPT API", "required_skill": "Fetch API", "usage_note": "注意处理超时", "difficulty": 3, "est_hours": 5, "completed": False}
                    ]}
                ]),
                "progress": 20, "logs": json.dumps([]), "created_at": time.time()
            },
            {
                "id": 2, "title": "极简习惯追踪器", "status": "incubating", "tech_stack": "Vue3, LocalStorage",
                "goal_description": "", "my_skills": "Vue,JavaScript", "breakdown": json.dumps([]),
                "progress": 0, "logs": json.dumps([]), "created_at": time.time()
            }
        ]
        
        for task in initial_tasks:
            cursor.execute("""
            INSERT INTO tasks (id, title, status, tech_stack, goal_description, my_skills, breakdown, progress, logs, created_at)
            VALUES (:id, :title, :status, :tech_stack, :goal_description, :my_skills, :breakdown, :progress, :logs, :created_at)
            """, task)
        
        print("Initial data inserted.")
        conn.commit()
    else:
        print("'tasks' table already exists.")
        
    conn.close()

# --- 样式 (V4.0 Dashboard Update) ---
STYLE = """
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
<style>
    body { background: #0f172a; color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .glass { background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 1rem; backdrop-filter: blur(10px); }
    textarea, input[type='text'], input[type='number'] { background: #0f172a; border: 1px solid #334155; color: white; border-radius: 0.5rem; padding: 0.5rem; width: 100%; }
    textarea:focus, input:focus { outline: 2px solid #3b82f6; border-color: transparent; }
    .skill-tag { display: inline-block; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 10px; font-weight: bold; border: 1px solid transparent; text-transform: uppercase; }
    .skill-matched { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border-color: #059669; }
    .skill-learning { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border-color: #d97706; }
    .skill-unknown { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border-color: #b91c1c; }
    .tree-line { border-left: 2px solid #334155; margin-left: 1rem; padding-left: 1rem; }
    .io-badge { font-size: 10px; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
    .io-input { background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .io-output { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    
    /* Dashboard Specific Styles */
    .progress-track { background: #1e293b; border-radius: 99px; height: 10px; overflow: hidden; }
    .progress-bar { background: #22c55e; height: 100%; transition: width 0.5s ease-in-out; }
    .task-item-exec { background: #1e293b; border-radius: 0.75rem; transition: all 0.2s; }
    .task-item-exec.completed { background: #111827; }
    .task-item-exec.completed .task-name { text-decoration: line-through; color: #475569; }
    .custom-checkbox { width: 20px; height: 20px; background-color: #334155; border-radius: 5px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background-color 0.2s; }
    .custom-checkbox.checked { background-color: #22c55e; }
    .custom-checkbox.checked::after { content: '✔'; color: white; font-size: 12px; }
</style>
"""

# --- 路由：首页 (孵化池) ---
@app.get("/", response_class=HTMLResponse)
async def index():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status != 'active' ORDER BY created_at DESC")
    incubating_tasks = cursor.fetchall()
    conn.close()

    cards = ""
    for t in incubating_tasks:
        cards += f"""
        <div class="glass p-6 mb-6">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-bold text-blue-400">{t['title']}</h3>
                <span class="text-xs font-mono text-slate-500">#{t['id']}</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mb-4">
                <div class="bg-slate-900/50 p-3 rounded">
                    <p class="text-slate-500 mb-1">技术栈</p>
                    <p>{t['tech_stack'] or '未定义'}</p>
                </div>
                <div class="bg-slate-900/50 p-3 rounded">
                    <p class="text-slate-500 mb-1">一句话描述</p>
                    <p>{(t['goal_description'] or '未填写')[:30] + '...' if t['goal_description'] else '未填写'}</p>
                </div>
            </div>
            <div class="flex gap-2">
                <a href="/deep_analyze/{t['id']}" class="flex-1 text-center py-2 border border-slate-600 rounded hover:bg-slate-800 transition">智能拆解</a>
                <form action="/activate/{t['id']}" method="post" class="flex-1">
                    <button class="w-full py-2 bg-green-600 rounded font-bold hover:bg-green-500 transition">确认执行 🚀</button>
                </form>
            </div>
        </div>
        """
    return f"""
    <html>
        <head>{STYLE}</head>
        <body class="p-8 max-w-4xl mx-auto">
            <nav class="flex justify-between items-center mb-10">
                <h1 class="text-3xl font-black italic">INCUBATOR</h1>
                <div class="flex gap-4">
                    <a href="/" class="text-blue-400 font-bold border-b-2 border-blue-400">孵化池</a>
                    <a href="/dashboard" class="text-slate-400 hover:text-white">执行看板</a>
                    <a href="/sitemap" class="text-slate-400 hover:text-white">网站地图</a>
                </div>
            </nav>
            <form action="/quick_propose" method="post" class="flex gap-2 mb-10">
                <input type="text" name="title" placeholder="有什么新想法？" class="flex-1 bg-slate-800 p-3 rounded-lg outline-none border border-slate-700" required>
                <button type="submit" class="bg-blue-600 px-8 rounded-lg font-bold">捕获</button>
            </form>
            {cards if cards else '<p class="text-center text-slate-500 mt-20">孵化池空空如也...</p>'}
        </body>
    </html>
    """

# --- 路由：深度分析页面 ---
@app.get("/deep_analyze/{tid}", response_class=HTMLResponse)
async def deep_analyze_page(tid: int):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (tid,))
    t = cursor.fetchone()
    conn.close()

    if not t:
        return HTMLResponse("Task not found", status_code=404)
    
    breakdown = json.loads(t['breakdown']) if t['breakdown'] else []
    
    vue_data = {
        "goal_description": t["goal_description"] or "",
        "my_skills": t["my_skills"] or "",
        "breakdown": breakdown,
    }

    return f"""
    <html>
        <head>{STYLE}</head>
        <body class="p-8 max-w-6xl mx-auto pb-40">
            <div id="app">
                <nav class="flex justify-between items-center mb-8">
                    <div class="flex items-center gap-4">
                        <a href="/" class="text-slate-400 hover:text-white text-2xl">←</a>
                        <div>
                            <h1 class="text-3xl font-black">{t['title']}</h1>
                            <p class="text-slate-500 text-sm">全息逆向拆解树 (Holographic Breakdown Tree)</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs text-slate-500 uppercase tracking-wider mb-1">Total Estimate</div>
                        <div class="text-2xl font-mono font-bold text-green-400">{{{{ totalHours }}}}h</div>
                    </div>
                </nav>

                <form id="analysisForm" action="/save_analysis/{tid}" method="post">
                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
                        <div class="lg:col-span-3 space-y-6">
                            <div class="glass p-5"><h3 class="font-bold mb-3 text-blue-400 text-sm uppercase">The Goal</h3><textarea name="goal_description" rows="4" class="text-sm" placeholder="一句话描述最终产物..." v-model="goal_description"></textarea></div>
                            <div class="glass p-5"><h3 class="font-bold mb-3 text-purple-400 text-sm uppercase">My Skillset</h3><input type="text" name="my_skills" class="text-sm mb-2" placeholder="e.g., Python, Vue" v-model="my_skills" @keydown.enter.prevent><p class="text-xs text-slate-500">用于评估任务难度和学习成本。</p></div>
                        </div>
                        <div class="lg:col-span-9 space-y-6">
                            <template v-for="(mod, mod_idx) in breakdown" :key="mod_idx">
                                <div class="glass p-5 mb-6">
                                    <div class="flex justify-between items-center mb-3"><input type="text" placeholder="核心模块名称" class="text-xl font-bold bg-transparent" v-model="mod.module"><button type="button" @click="removeModule(mod_idx)" class="text-slate-600 hover:text-red-500">删除模块</button></div>
                                    <div class="tree-line space-y-2">
                                        <template v-for="(task, task_idx) in mod.tasks" :key="task_idx">
                                            <div class="p-3 rounded bg-slate-900/50">
                                                <div class="flex items-center gap-2 mb-2"><input type="text" placeholder="具体任务" class="flex-1 font-bold bg-transparent" v-model="task.name"><button type="button" @click="removeTask(mod_idx, task_idx)" class="text-slate-600 hover:text-red-500">×</button></div>
                                                <div class="grid grid-cols-12 gap-2 text-xs">
                                                    <div class="col-span-3"><label class="text-slate-500">预计工时(h)</label><input type="number" v-model.number="task.est_hours"></div>
                                                    <div class="col-span-3"><label class="text-slate-500">难度(1-5)</label><input type="number" min="1" max="5" v-model.number="task.difficulty"></div>
                                                    <div class="col-span-6"><label class="text-slate-500">所需技能</label><input type="text" v-model="task.required_skill"></div>
                                                    <div class="col-span-12"><label class="text-slate-500">备注</label><input type="text" v-model="task.usage_note"></div>
                                                </div>
                                            </div>
                                        </template>
                                    </div>
                                    <button type="button" @click="addTask(mod_idx)" class="text-xs mt-3 text-slate-400 hover:text-blue-400">+ 添加原子任务</button>
                                </div>
                            </template>
                            <button type="button" @click="addModule()" class="w-full py-3 border-2 border-dashed border-slate-700 rounded-xl text-slate-500 hover:bg-slate-800">+ 新增模块</button>
                        </div>
                    </div>
                    <input type="hidden" name="breakdown_json" :value="JSON.stringify(breakdown)">
                    <div class="fixed bottom-0 left-0 w-full bg-slate-900/90 p-4 flex justify-end px-8"><button type="submit" class="bg-blue-600 px-8 py-2 rounded font-bold">保存分析</button></div>
                </form>
            </div>
            <script>
                const {{ createApp, ref, computed }} = Vue;
                createApp({{
                    setup() {{
                        const data = {json.dumps(vue_data)};
                        const goal_description = ref(data.goal_description);
                        const my_skills = ref(data.my_skills);
                        const breakdown = ref(data.breakdown);
                        const totalHours = computed(() => breakdown.value.reduce((sum, mod) => sum + (mod.tasks || []).reduce((ts, t) => ts + (t.est_hours || 0), 0), 0));
                        const addTask = (mod_idx) => breakdown.value[mod_idx].tasks.push({{ name: "", est_hours: 0, difficulty: 1, required_skill: "", usage_note: "", completed: false }});
                        const removeTask = (mod_idx, task_idx) => breakdown.value[mod_idx].tasks.splice(task_idx, 1);
                        const addModule = () => breakdown.value.push({{ module: "新模块", tasks: [] }});
                        const removeModule = (mod_idx) => breakdown.value.splice(mod_idx, 1);
                        return {{ goal_description, my_skills, breakdown, totalHours, addTask, removeTask, addModule, removeModule }};
                    }}
                }}).mount('#app');
            </script>
        </body>
    </html>
    """

# --- 路由：保存分析 ---
@app.post("/save_analysis/{tid}")
async def save_analysis(tid: int, goal_description: str = Form(""), my_skills: str = Form(""), breakdown_json: str = Form("[]")):
    breakdown = json.loads(breakdown_json)
    for mod in breakdown:
        for task in mod.get("tasks", []):
            task.setdefault("completed", False)
    
    conn = db_connect()
    cursor = conn.cursor()
    
    # 获取当前状态以决定跳转目标
    cursor.execute("SELECT status FROM tasks WHERE id = ?", (tid,))
    result = cursor.fetchone()
    current_status = result['status'] if result else 'incubating'

    cursor.execute("""
        UPDATE tasks 
        SET goal_description = ?, my_skills = ?, breakdown = ?, tech_stack = ?
        WHERE id = ?
    """, (goal_description, my_skills, json.dumps(breakdown), my_skills, tid))
    conn.commit()
    conn.close()
    
    target_url = "/dashboard" if current_status == 'active' else "/"
    return RedirectResponse(url=target_url, status_code=303)

# --- 路由：执行看板 ---
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_v2():
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status = 'active' ORDER BY created_at DESC")
    active_tasks = cursor.fetchall()
    conn.close()
    
    vue_data_map = {}
    for t in active_tasks:
        breakdown = json.loads(t['breakdown']) if t['breakdown'] else []
        for mod in breakdown:
            for task in mod.get("tasks", []):
                task.setdefault("completed", False)
        vue_data_map[t['id']] = {"breakdown": breakdown}

    cards_html = ""
    for t in active_tasks:
        cards_html += f"""
        <div id="dashboard-app-{t['id']}" class="glass p-6 mb-8">
            <form :action="'/update_dashboard/' + {t['id']}" method="post" @submit.prevent="submitForm">
                <div class="flex justify-between items-start mb-4">
                    <div><h3 class="text-2xl font-bold text-green-400">{t['title']}</h3><p class="text-sm text-slate-400">当前进度: <span class="font-bold">{{{{ progressPercent }}}}%</span></p></div>
                    <div class="flex gap-2">
                        <a href="/deep_analyze/{t['id']}" class="bg-slate-700 px-4 py-2 rounded font-bold hover:bg-slate-600 transition text-sm flex items-center">⚙️ 调整拆解</a>
                        <button type="submit" class="bg-blue-600 px-6 py-2 rounded font-bold hover:bg-blue-500 transition">保存进度</button>
                    </div>
                </div>
                <div class="progress-track mb-6"><div class="progress-bar" :style="'width: ' + progressPercent + '%'"></div></div>
                <div class="space-y-4">
                    <template v-for="(mod, mod_idx) in breakdown" :key="mod_idx">
                        <div class="p-4 bg-slate-900/50 rounded-lg">
                            <p class="font-bold text-blue-400 mb-3 text-sm uppercase tracking-wider">{{{{ mod.module }}}}</p>
                            <div class="space-y-2">
                                <template v-for="(task, task_idx) in mod.tasks" :key="task_idx">
                                    <div class="task-item-exec p-3 flex items-center gap-4" :class="{{ 'completed': task.completed }}">
                                        <div @click="toggleTask(mod_idx, task_idx)" class="custom-checkbox" :class="{{ 'checked': task.completed }}"></div>
                                        <div class="flex-1">
                                            <p class="task-name font-semibold">{{{{ task.name }}}}</p>
                                            <p class="text-xs text-slate-500">{{{{ task.usage_note }}}}</p>
                                        </div>
                                        <div class="flex items-center gap-2 text-xs"><input type="number" v-model.number="task.est_hours" class="bg-slate-800 w-16 text-center"><span class="text-slate-500">h</span></div>
                                        <div class="flex items-center gap-2 text-xs"><input type="number" v-model.number="task.difficulty" class="bg-slate-800 w-12 text-center"><span class="text-slate-500">diff</span></div>
                                    </div>
                                </template>
                            </div>
                        </div>
                    </template>
                </div>
                <input type="hidden" name="breakdown_json" :value="JSON.stringify(breakdown)">
            </form>
        </div>
        """

    return f"""
    <html>
        <head>{STYLE}</head>
        <body class="p-8 max-w-5xl mx-auto">
            <nav class="flex justify-between items-center mb-12">
                <h1 class="text-3xl font-black italic">DASHBOARD</h1>
                <div class="flex gap-4">
                    <a href="/" class="text-slate-400 hover:text-white">孵化池</a>
                    <a href="/dashboard" class="text-green-400 font-bold border-b-2 border-green-400">执行看板</a>
                    <a href="/sitemap" class="text-slate-400 hover:text-white">网站地图</a>
                </div>
            </nav>
            {cards_html if cards_html else '<div class="text-center py-20 border-2 border-dashed border-slate-800 rounded-3xl text-slate-600">没有正在执行的任务，去孵化池激活一个吧！</div>'}
            <script>
                const {{ createApp, ref, computed }} = Vue;
                const vueDataMap = {json.dumps(vue_data_map)};
                for (const tid in vueDataMap) {{
                    createApp({{
                        setup() {{
                            const breakdown = ref(vueDataMap[tid].breakdown);
                            const progressPercent = computed(() => {{
                                const total = breakdown.value.reduce((s, m) => s + m.tasks.reduce((ts, t) => ts + (t.est_hours || 0), 0), 0);
                                if (total === 0) return 0;
                                const completed = breakdown.value.reduce((s, m) => s + m.tasks.filter(t => t.completed).reduce((ts, t) => ts + (t.est_hours || 0), 0), 0);
                                return Math.round((completed / total) * 100);
                            }});
                            const toggleTask = (m, t) => {{ breakdown.value[m].tasks[t].completed = !breakdown.value[m].tasks[t].completed; }};
                            const submitForm = (e) => e.target.submit();
                            return {{ breakdown, progressPercent, toggleTask, submitForm }};
                        }}
                    }}).mount('#dashboard-app-' + tid);
                }}
            </script>
        </body>
    </html>
    """

# --- 逻辑接口 ---
@app.post("/quick_propose")
async def quick_propose(title: str = Form(...)):
    new_id = int(time.time())
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (id, title, created_at, breakdown, logs) VALUES (?, ?, ?, ?, ?)",
        (new_id, title, time.time(), json.dumps([]), json.dumps([]))
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/activate/{tid}")
async def activate_task(tid: int):
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'active' WHERE id = ?", (tid,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/update_dashboard/{tid}")
async def update_dashboard(tid: int, breakdown_json: str = Form(...)):
    breakdown = json.loads(breakdown_json)
    total_hours = sum(float(task.get('est_hours', 0)) for mod in breakdown for task in mod.get('tasks', []))
    completed_hours = sum(float(task.get('est_hours', 0)) for mod in breakdown for task in mod.get('tasks', []) if task.get('completed'))
    progress = round((completed_hours / total_hours) * 100) if total_hours > 0 else 0

    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET breakdown = ?, progress = ? WHERE id = ?",
        (json.dumps(breakdown), progress, tid)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/dashboard", status_code=303)

# --- 网站地图 ---
@app.get("/sitemap", response_class=HTMLResponse)
async def sitemap():
    return f"""
    <html><head>{STYLE}</head><body class="p-8 max-w-4xl mx-auto"><nav class="flex justify-between items-center mb-10"><h1 class="text-3xl font-black italic">SITEMAP</h1><div class="flex gap-4"><a href="/" class="text-slate-400 hover:text-white">孵化池</a><a href="/dashboard" class="text-slate-400 hover:text-white">执行看板</a><a href="/sitemap" class="text-blue-400 font-bold border-b-2 border-blue-400">网站地图</a></div></nav><div class="glass p-8"><h2 class="text-2xl font-bold mb-6">网站导航</h2><ul class="space-y-4 text-lg"><li><a href="/" class="flex items-center gap-3 text-blue-400">🥚 孵化池</a></li><li><a href="/dashboard" class="flex items-center gap-3 text-green-400">🚀 执行看板</a></li><li><a href="/docs" class="flex items-center gap-3 text-purple-400">📄 API 文档</a></li></ul></div></body></html>
    """

# --- App 启动 ---
if __name__ == "__main__":
    init_db() # 初始化数据库
    uvicorn.run(app, host="127.0.0.1", port=39001)
