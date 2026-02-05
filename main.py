# -*- coding: utf-8 -*-
# @Time    : 2026/2/5 13:19
# @Author  : cy1026
# @File    : main.py
# @Software: PyCharm

import time
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from typing import Dict, List
import uvicorn
import json

app = FastAPI(title="Visual Idea Incubator")

# --- 内存数据库 (V3.0 Structure) ---
tasks_db: Dict[int, dict] = {
    1: {
        "id": 1, "title": "AI 辅助写作助手", "status": "incubating",
        "tech_stack": "OpenAI API, React", "capability": 8, "revenue": 9, "user_view": "市场需求大，竞争激烈",
        "progress": 0, "logs": [], "created_at": time.time(),
        "radar_data": [8, 9, 5, 8, 6],
        "goal_description": "一个能自动生成周报的 Chrome 插件",
        "my_skills": "JavaScript,HTML,CSS,Python",
        "breakdown": [
            {
                "module": "用户界面 (Popup)",
                "priority": "P0",
                "io_input": "用户点击图标",
                "io_output": "配置参数 JSON",
                "tasks": [
                    {"name": "设计配置面板", "required_skill": "HTML", "usage_note": "使用 TailwindCSS", "difficulty": 1, "est_hours": 2, "io_input": "", "io_output": "HTML DOM", "completed": False},
                    {"name": "实现点击事件", "required_skill": "JavaScript", "usage_note": "绑定 onClick", "difficulty": 2, "est_hours": 3, "io_input": "DOM Event", "io_output": "Config Object", "completed": False}
                ]
            },
            {
                "module": "核心逻辑 (Background)",
                "priority": "P0",
                "io_input": "配置参数 JSON",
                "io_output": "生成的周报文本",
                "tasks": [
                    {"name": "调用 GPT API", "required_skill": "Fetch API", "usage_note": "注意处理超时", "difficulty": 3, "est_hours": 5, "io_input": "Prompt String", "io_output": "GPT Response", "completed": False},
                    {"name": "从网页提取文本", "required_skill": "DOM API", "usage_note": "document.body.innerText", "difficulty": 2, "est_hours": 2, "io_input": "Current Tab", "io_output": "Raw Text", "completed": False}
                ]
            }
        ]
    },
    2: {
        "id": 2, "title": "极简习惯追踪器", "status": "incubating",
        "tech_stack": "Vue3, LocalStorage", "capability": 10, "revenue": 4, "user_view": "适合个人开发者练手",
        "progress": 0, "logs": [], "created_at": time.time(),
        "radar_data": [10, 4, 3, 6, 2],
        "goal_description": "", "my_skills": "Vue,JavaScript", "breakdown": []
    },
    3: {
        "id": 3, "title": "独立游戏：迷宫探险", "status": "incubating",
        "tech_stack": "Unity, C#", "capability": 6, "revenue": 7, "user_view": "需要美术资源支持",
        "progress": 0, "logs": [], "created_at": time.time(),
        "radar_data": [6, 7, 8, 7, 9],
        "goal_description": "", "my_skills": "C#,Unity", "breakdown": []
    }
}

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
    cards = ""
    incubating_tasks = [t for t in tasks_db.values() if t["status"] != "active"]
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
                    <p>{t.get('tech_stack', '未定义')}</p>
                </div>
                <div class="bg-slate-900/50 p-3 rounded">
                    <p class="text-slate-500 mb-1">一句话描述</p>
                    <p>{t.get('goal_description', '未填写')[:30] + '...' if t.get('goal_description') else '未填写'}</p>
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

# --- 路由：深度分析页面 V4.0 (Vue.js 重构) ---
@app.get("/deep_analyze/{tid}", response_class=HTMLResponse)
async def deep_analyze_page_v4(tid: int):
    if tid not in tasks_db:
        return HTMLResponse("Task not found", status_code=404)
    
    t = tasks_db[tid]
    # Prepare data for Vue app
    vue_data = {
        "goal_description": t.get("goal_description", ""),
        "my_skills": t.get("my_skills", ""),
        "breakdown": t.get("breakdown", []),
        "task_title": t['title'] # Pass task title for display
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
                        <div class="text-2xl font-mono font-bold text-green-400" id="totalHoursDisplay">{{{{ totalHours }}}}h</div>
                    </div>
                </nav>

                <form id="analysisForm" action="/save_analysis/{tid}" method="post" @submit.prevent="collectBreakdownData">
                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
                        
                        <!-- 左侧边栏：全局设定 -->
                        <div class="lg:col-span-3 space-y-6">
                            <div class="glass p-5">
                                <h3 class="font-bold mb-3 text-blue-400 text-sm uppercase">The Goal</h3>
                                <textarea name="goal_description" rows="4" class="text-sm" placeholder="一句话描述最终产物..." v-model="goal_description"></textarea>
                            </div>
                            <div class="glass p-5">
                                <h3 class="font-bold mb-3 text-purple-400 text-sm uppercase">My Skillset</h3>
                                <input type="text" name="my_skills" id="mySkillsInput" class="text-sm mb-2" placeholder="e.g., Python, Vue" v-model="my_skills" @keydown.enter.prevent>
                                <p class="text-xs text-slate-500">系统将自动比对任务所需技能，标记学习成本。</p>
                            </div>
                            
                            <!-- 实时统计面板 -->
                            <div class="glass p-5 bg-slate-800/50">
                                <h3 class="font-bold mb-3 text-slate-400 text-sm uppercase">Stats</h3>
                                <div class="space-y-2 text-sm">
                                    <div class="flex justify-between"><span>模块数</span> <span>{{{{ statModules }}}}</span></div>
                                    <div class="flex justify-between"><span>任务数</span> <span>{{{{ statTasks }}}}</span></div>
                                    <div class="flex justify-between text-red-400"><span>高难攻坚 (Diff>3)</span> <span>{{{{ statHard }}}}</span></div>
                                </div>
                            </div>
                        </div>

                        <!-- 右侧主区域：拆解树 -->
                        <div class="lg:col-span-9 space-y-6">
                            <div id="breakdown-container">
                                <template v-for="(mod, mod_idx) in breakdown" :key="mod_idx">
                                    <div class="glass p-5 mb-6 module-item relative">
                                        <div class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500/20 rounded-l-lg"></div>
                                        <div class="flex justify-between items-center mb-2 pl-2">
                                            <div class="flex items-center gap-3 flex-1">
                                                <span class="text-blue-400 font-mono text-sm">MODULE</span>
                                                <input type="text" placeholder="核心模块名称" class="module-name text-xl font-bold bg-transparent border-0 p-0 w-full focus:ring-0" v-model="mod.module" @keydown.enter.prevent>
                                            </div>
                                            <div class="flex items-center gap-2">
                                                <select class="module-priority bg-slate-800 text-xs border border-slate-700 rounded p-1" v-model="mod.priority">
                                                    <option value="P0">P0 核心</option>
                                                    <option value="P1">P1 重要</option>
                                                    <option value="P2">P2 待定</option>
                                                </select>
                                                <button type="button" @click="moveModule(mod_idx, -1)" class="text-slate-400 hover:text-white text-xs px-1" title="上移">⬆️</button>
                                                <button type="button" @click="moveModule(mod_idx, 1)" class="text-slate-400 hover:text-white text-xs px-1" title="下移">⬇️</button>
                                                <button type="button" @click="removeModule(mod_idx)" class="text-slate-600 hover:text-red-500 text-sm ml-2">删除</button>
                                            </div>
                                        </div>

                                        <!-- Module I/O -->
                                        <div class="flex gap-4 mb-4 pl-2 text-xs">
                                            <div class="flex-1 bg-slate-900/30 p-2 rounded border border-slate-800 flex items-center gap-2">
                                                <span class="io-badge io-input">MODULE IN</span>
                                                <input type="text" class="module-io-input bg-transparent w-full outline-none text-slate-300" placeholder="模块前置依赖..." v-model="mod.io_input" @keydown.enter.prevent>
                                            </div>
                                            <div class="flex-1 bg-slate-900/30 p-2 rounded border border-slate-800 flex items-center gap-2">
                                                <span class="io-badge io-output">MODULE OUT</span>
                                                <input type="text" class="module-io-output bg-transparent w-full outline-none text-slate-300" placeholder="模块最终产出..." v-model="mod.io_output" @keydown.enter.prevent>
                                            </div>
                                        </div>

                                        <div class="tree-line tasks-container space-y-2">
                                            <template v-for="(task, task_idx) in mod.tasks" :key="task_idx">
                                                <div class="task-card p-3 rounded bg-slate-900/50 task-item relative">
                                                    <div class="flex items-center gap-2 mb-2">
                                                        <span class="text-slate-500 text-xs">Task</span>
                                                        <input type="text" placeholder="具体任务名称" class="task-name flex-1 font-bold bg-transparent border-none p-0 focus:ring-0" v-model="task.name" @keydown.enter.prevent>
                                                        <input type="text" placeholder="所需技能" class="required-skill w-32 text-xs" v-model="task.required_skill" @keydown.enter.prevent>
                                                        <span :class="getSkillTagClass(task.required_skill)">{{{{ getSkillTagText(task.required_skill) }}}}</span>
                                                        <button type="button" @click="removeTask(mod_idx, task_idx)" class="text-slate-600 hover:text-red-500">×</button>
                                                    </div>

                                                    <div class="grid grid-cols-12 gap-2 text-xs mb-2">
                                                        <div class="col-span-2">
                                                            <label class="text-slate-500 block mb-1">预计工时(h)</label>
                                                            <input type="number" class="est-hours bg-slate-800 border-slate-700 p-1" v-model.number="task.est_hours" @keydown.enter.prevent>
                                                        </div>
                                                        <div class="col-span-2">
                                                            <label class="text-slate-500 block mb-1">难度(1-5)</label>
                                                            <input type="number" min="1" max="5" class="difficulty bg-slate-800 border-slate-700 p-1" v-model.number="task.difficulty" @keydown.enter.prevent>
                                                        </div>
                                                        <div class="col-span-8">
                                                            <label class="text-slate-500 block mb-1">关键用法 / 备注</label>
                                                            <input type="text" class="usage-note bg-slate-800 border-slate-700 p-1" placeholder="例如: 使用 xxx 库的 yyy 方法" v-model="task.usage_note" @keydown.enter.prevent>
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>
                                        </div>
                                        <div class="pl-6 mt-3 flex gap-4">
                                            <button type="button" @click="addTask(mod_idx)" class="text-xs flex items-center gap-1 text-slate-400 hover:text-blue-400 transition">
                                                <span class="text-lg">+</span> 添加原子任务
                                            </button>
                                        </div>
                                    </div>
                                </template>
                            </div>
                            
                            <button type="button" @click="addModule()" class="w-full py-4 border-2 border-dashed border-slate-700 rounded-xl text-slate-500 hover:text-white hover:border-slate-500 hover:bg-slate-800 transition flex items-center justify-center gap-2">
                                <span class="text-2xl">+</span> 新增核心模块 (Module)
                            </button>
                        </div>
                    </div>

                    <input type="hidden" name="breakdown_json" :value="JSON.stringify(breakdown)">

                    <div class="fixed bottom-0 left-0 w-full bg-slate-900/90 backdrop-blur border-t border-slate-800 p-4 flex justify-between items-center px-8 z-50">
                        <a href="/" class="px-6 py-2 rounded text-slate-400 hover:text-white transition">返回</a>
                        <button type="submit" class="bg-blue-600 px-8 py-2 rounded font-bold hover:bg-blue-500 shadow-lg shadow-blue-900/50 transition">保存全息分析</button>
                    </div>
                </form>
            </div>

            <script>
                const {{ createApp, ref, computed }} = Vue;
                createApp({{
                    setup() {{
                        const goal_description = ref({json.dumps(vue_data['goal_description'])});
                        const my_skills = ref({json.dumps(vue_data['my_skills'])});
                        const breakdown = ref({json.dumps(vue_data['breakdown'])});
                        const mySkillsArray = computed(() => my_skills.value.toLowerCase().split(',').map(s => s.trim()).filter(Boolean));
                        
                        const totalHours = computed(() => breakdown.value.reduce((sum, mod) => sum + (mod.tasks || []).reduce((taskSum, task) => taskSum + (parseFloat(task.est_hours) || 0), 0), 0));
                        const statModules = computed(() => breakdown.value.length);
                        const statTasks = computed(() => breakdown.value.reduce((sum, mod) => sum + (mod.tasks || []).length, 0));
                        const statHard = computed(() => breakdown.value.reduce((sum, mod) => sum + (mod.tasks || []).filter(t => (parseInt(t.difficulty) || 0) > 3).length, 0));

                        const getSkillTagClass = (skill) => {{
                            if (!skill) return 'skill-tag hidden';
                            const s = skill.toLowerCase().trim();
                            if (mySkillsArray.value.includes(s)) return 'skill-tag skill-matched';
                            return 'skill-tag skill-unknown';
                        }};
                        const getSkillTagText = (skill) => {{
                            if (!skill) return '';
                            return mySkillsArray.value.includes(skill.toLowerCase().trim()) ? 'COMFORT' : 'PANIC';
                        }};
                        const addTask = (mod_idx) => breakdown.value[mod_idx].tasks.push({{ name: "", required_skill: "", usage_note: "", difficulty: 1, est_hours: 0, completed: false }});
                        const removeTask = (mod_idx, task_idx) => breakdown.value[mod_idx].tasks.splice(task_idx, 1);
                        const addModule = () => breakdown.value.push({{ module: "", priority: "P0", tasks: [] }});
                        const removeModule = (mod_idx) => breakdown.value.splice(mod_idx, 1);
                        const moveModule = (idx, dir) => {{
                            const newIdx = idx + dir;
                            if (newIdx < 0 || newIdx >= breakdown.value.length) return;
                            [breakdown.value[idx], breakdown.value[newIdx]] = [breakdown.value[newIdx], breakdown.value[idx]];
                        }};
                        const collectBreakdownData = () => document.getElementById('analysisForm').submit();

                        return {{ goal_description, my_skills, breakdown, totalHours, statModules, statTasks, statHard, getSkillTagClass, getSkillTagText, addTask, removeTask, addModule, removeModule, moveModule, collectBreakdownData }};
                    }}
                }}).mount('#app');
            </script>
        </body>
    </html>
    """

# --- 路由：保存分析 ---
@app.post("/save_analysis/{tid}")
async def save_analysis(tid: int, goal_description: str = Form(""), my_skills: str = Form(""), breakdown_json: str = Form("[]")):
    if tid in tasks_db:
        try:
            breakdown = json.loads(breakdown_json)
            # Ensure all tasks have a 'completed' field
            for mod in breakdown:
                for task in mod.get("tasks", []):
                    task.setdefault("completed", False)
            tasks_db[tid].update({
                "goal_description": goal_description, "my_skills": my_skills, "breakdown": breakdown,
                "tech_stack": my_skills
            })
        except json.JSONDecodeError:
            pass
    return HTMLResponse("<script>window.location.href='/';</script>")

# --- 路由：执行看板 (V2.0 Vue.js) ---
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_v2():
    active_tasks = [t for t in tasks_db.values() if t["status"] == "active"]
    
    # Prepare data for Vue apps
    vue_data_map = {}
    for t in active_tasks:
        # Ensure all tasks have a 'completed' field before sending to frontend
        for mod in t.get("breakdown", []):
            for task in mod.get("tasks", []):
                task.setdefault("completed", False)
        vue_data_map[t['id']] = {
            "breakdown": t.get("breakdown", []),
            "logs": t.get("logs", [])
        }

    cards_html = ""
    for t in active_tasks:
        cards_html += f"""
        <div id="dashboard-app-{t['id']}" class="glass p-6 mb-8">
            <form :action="'/update_dashboard/' + {t['id']}" method="post" @submit.prevent="submitForm">
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-2xl font-bold text-green-400">{t['title']}</h3>
                        <p class="text-sm text-slate-400">当前进度: <span class="font-bold">{{{{ progressPercent }}}}%</span></p>
                    </div>
                    <button type="submit" class="bg-blue-600 px-6 py-2 rounded font-bold hover:bg-blue-500 transition">保存进度</button>
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
                                        <div class="flex items-center gap-2 text-xs">
                                            <input type="number" v-model.number="task.est_hours" class="bg-slate-800 border-slate-700 p-1 w-16 rounded text-center" @keydown.enter.prevent>
                                            <span class="text-slate-500">小时</span>
                                        </div>
                                        <div class="flex items-center gap-2 text-xs">
                                            <input type="number" v-model.number="task.difficulty" class="bg-slate-800 border-slate-700 p-1 w-12 rounded text-center" min="1" max="5" @keydown.enter.prevent>
                                            <span class="text-slate-500">难度</span>
                                        </div>
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
                                const totalHours = breakdown.value.reduce((sum, mod) => sum + (mod.tasks || []).reduce((taskSum, task) => taskSum + (parseFloat(task.est_hours) || 0), 0), 0);
                                if (totalHours === 0) return 0;
                                const completedHours = breakdown.value.reduce((sum, mod) => sum + (mod.tasks || []).filter(t => t.completed).reduce((taskSum, task) => taskSum + (parseFloat(task.est_hours) || 0), 0), 0);
                                return Math.round((completedHours / totalHours) * 100);
                            }});

                            const toggleTask = (mod_idx, task_idx) => {{
                                const task = breakdown.value[mod_idx].tasks[task_idx];
                                task.completed = !task.completed;
                            }};

                            const submitForm = (event) => {{
                                event.target.submit();
                            }};

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
    tasks_db[new_id] = {
        "id": new_id, "title": title, "status": "incubating", "tech_stack": "", "capability": 5, "revenue": 5, 
        "user_view": "", "progress": 0, "logs": [], "created_at": time.time(), "radar_data": [5, 5, 5, 5, 5],
        "goal_description": "", "my_skills": "", "breakdown": []
    }
    return HTMLResponse("<script>window.location.href='/';</script>")

@app.post("/activate/{tid}")
async def activate_task(tid: int):
    if tid in tasks_db:
        tasks_db[tid]["status"] = "active"
        # Initialize 'completed' field for all tasks upon activation
        for mod in tasks_db[tid].get("breakdown", []):
            for task in mod.get("tasks", []):
                task.setdefault("completed", False)
    return HTMLResponse("<script>window.location.href='/dashboard';</script>")

@app.post("/update_dashboard/{tid}")
async def update_dashboard(tid: int, breakdown_json: str = Form(...)):
    if tid in tasks_db:
        try:
            breakdown = json.loads(breakdown_json)
            
            # Calculate progress
            total_hours = sum(float(task.get('est_hours', 0)) for mod in breakdown for task in mod.get('tasks', []))
            completed_hours = sum(float(task.get('est_hours', 0)) for mod in breakdown for task in mod.get('tasks', []) if task.get('completed'))
            progress = round((completed_hours / total_hours) * 100) if total_hours > 0 else 0

            tasks_db[tid]['breakdown'] = breakdown
            tasks_db[tid]['progress'] = progress
            
            # Optional: Add a log entry
            timestamp = time.strftime("%H:%M", time.localtime())
            tasks_db[tid]['logs'].insert(0, f"[{timestamp}] Progress updated to {progress}%.")

        except (json.JSONDecodeError, KeyError):
            # Handle potential errors in JSON or data structure
            pass
    return HTMLResponse("<script>window.location.href='/dashboard';</script>")

# --- 网站地图 ---
@app.get("/sitemap", response_class=HTMLResponse)
async def sitemap():
    return f"""
    <html>
        <head>{STYLE}</head>
        <body class="p-8 max-w-4xl mx-auto">
            <nav class="flex justify-between items-center mb-10">
                <h1 class="text-3xl font-black italic">SITEMAP</h1>
                <div class="flex gap-4">
                    <a href="/" class="text-slate-400 hover:text-white">孵化池</a>
                    <a href="/dashboard" class="text-slate-400 hover:text-white">执行看板</a>
                    <a href="/sitemap" class="text-blue-400 font-bold border-b-2 border-blue-400">网站地图</a>
                </div>
            </nav>
            <div class="glass p-8">
                <h2 class="text-2xl font-bold mb-6">网站导航</h2>
                <ul class="space-y-4 text-lg">
                    <li><a href="/" class="flex items-center gap-3 text-blue-400 hover:text-blue-300 transition"><span class="text-2xl">🥚</span> 孵化池 (首页)</a></li>
                    <li><a href="/dashboard" class="flex items-center gap-3 text-green-400 hover:text-green-300 transition"><span class="text-2xl">🚀</span> 执行看板</a></li>
                    <li><a href="/docs" class="flex items-center gap-3 text-purple-400 hover:text-purple-300 transition"><span class="text-2xl">📄</span> API 文档</a></li>
                    <li><a href="/redoc" class="flex items-center gap-3 text-red-400 hover:text-red-300 transition"><span class="text-2xl">📘</span> ReDoc 文档</a></li>
                </ul>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)