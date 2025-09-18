"""Simple web interface for building PixelSociety agent teams."""
from __future__ import annotations

from typing import Dict, List

from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template_string,
    request,
    url_for,
)

from pixel_society import Agent, create_base_simulation
from pixel_society import mbti
from pixel_society.simulation import SimulationResult
from pixel_society.tasks import Task

app = Flask(__name__)
app.secret_key = "pixelsociety-demo"

simulation = create_base_simulation()
latest_history: List[SimulationResult] = []
latest_agent_reports: Dict[str, str] = {}
latest_world_report: str | None = None


TEMPLATE = """<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\">
  <title>PixelSociety · 代理创建流程</title>
  <style>
    body { font-family: 'Segoe UI', 'PingFang SC', sans-serif; background: #f4f7fa; margin: 0; padding: 2rem; color: #1f2a44; }
    h1 { margin-bottom: 0.5rem; }
    section { background: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; box-shadow: 0 8px 20px rgba(31,42,68,0.08); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
    label { display: block; font-weight: 600; margin-top: 1rem; }
    input[type=text], textarea, select { width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid #c7d0e1; box-sizing: border-box; }
    textarea { min-height: 80px; }
    button { margin-top: 1rem; padding: 0.75rem 1.5rem; border: none; border-radius: 999px; background: #5561ff; color: white; font-weight: 600; cursor: pointer; }
    button.secondary { background: #e4e7f5; color: #1f2a44; }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th, td { padding: 0.5rem; border-bottom: 1px solid #e1e6f3; text-align: left; }
    .messages { margin-bottom: 1rem; }
    .message { padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; }
    .success { background: #e8f8f0; color: #246b3d; }
    .error { background: #fdecea; color: #b23d33; }
    .info { background: #eef2ff; color: #3641a2; }
    .mbti-card { border: 1px solid #d9def2; border-radius: 12px; padding: 1rem; background: #f8f9ff; }
    .history-entry { border-left: 4px solid #5561ff; padding-left: 1rem; margin-bottom: 1rem; }
    pre { background: #0f172a; color: #f1f5ff; padding: 1rem; border-radius: 8px; overflow-x: auto; }
  </style>
</head>
<body>
  <h1>PixelSociety · 代理创建流程</h1>
  <p>按照下列步骤，为玩家快速搭建拥有不同 MBTI 个性的 AI 代理团队。</p>
  <div class=\"messages\">
    {% for category, message in messages %}
      <div class=\"message {{ category }}\">{{ message }}</div>
    {% endfor %}
  </div>
  <section>
    <h2>步骤一：配置新代理</h2>
    <form method=\"post\" action=\"{{ url_for('add_agent') }}\">
      <div class=\"grid\">
        <div>
          <label for=\"name\">代理名称</label>
          <input type=\"text\" id=\"name\" name=\"name\" placeholder=\"如：Lyra\" required>
        </div>
        <div>
          <label for=\"mbti_code\">MBTI 类型</label>
          <input type=\"text\" id=\"mbti_code\" name=\"mbti_code\" list=\"mbti_codes\" value=\"{{ default_mbti }}\" required>
          <datalist id=\"mbti_codes\">
            {% for code in mbti_codes %}
              <option value=\"{{ code }}\"></option>
            {% endfor %}
          </datalist>
        </div>
        <div>
          <label for=\"region\">所在区域</label>
          <select id=\"region\" name=\"region\">
            {% for region in regions %}
              <option value=\"{{ region.name }}\">{{ region.name }}</option>
            {% endfor %}
          </select>
        </div>
      </div>
      <label for=\"prompt\">个性化提示词（可选）</label>
      <textarea id=\"prompt\" name=\"prompt\" placeholder=\"描述行为风格、价值观或人生目标……\"></textarea>
      <div class=\"grid\">
        <div>
          <label for=\"motivations\">动机（逗号分隔，可选）</label>
          <input type=\"text\" id=\"motivations\" name=\"motivations\" placeholder=\"如：创业, 推动改革\">
        </div>
        <div>
          <label for=\"values\">价值观（逗号分隔，可选）</label>
          <input type=\"text\" id=\"values\" name=\"values\" placeholder=\"如：自由, 合作\">
        </div>
        <div>
          <label for=\"goal\">初始目标（可选）</label>
          <input type=\"text\" id=\"goal\" name=\"goal\" placeholder=\"如：创建社区工作坊\">
        </div>
      </div>
      <button type=\"submit\">➕ 添加代理</button>
    </form>
  </section>

  <section>
    <h2>步骤二：了解 MBTI 角色特征</h2>
    <div class=\"grid\">
      {% for code, profile in mbti_profiles.items() %}
        <div class=\"mbti-card\">
          <h3>{{ code }}</h3>
          <p>{{ profile.description }}</p>
          <ul>
            {% for trait, value in profile.trait_modifiers.items() %}
              <li>{{ trait }}：{{ '%0.1f'|format(value) }}</li>
            {% endfor %}
          </ul>
        </div>
      {% endfor %}
    </div>
  </section>

  <section>
    <h2>步骤三：已创建的代理</h2>
    {% if agents %}
      <table>
        <thead>
          <tr>
            <th>名称</th>
            <th>MBTI</th>
            <th>所在区域</th>
            <th>动机</th>
            <th>价值观</th>
          </tr>
        </thead>
        <tbody>
          {% for agent in agents %}
            <tr>
              <td>{{ agent.name }}</td>
              <td>{{ agent.mbti_code }}</td>
              <td>{{ world.agent_locations.get(agent.name, '未分配') }}</td>
              <td>{{ agent.motivations|join(', ') if agent.motivations else '—' }}</td>
              <td>{{ agent.values|join(', ') if agent.values else '—' }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>尚未创建任何代理。请在上方填写表单开始构建团队。</p>
    {% endif %}
    <form method=\"post\" action=\"{{ url_for('reset_simulation') }}\">
      <button type=\"submit\" class=\"secondary\">🔄 重置世界</button>
    </form>
  </section>

  <section>
    <h2>步骤四：运行模拟</h2>
    <form method=\"post\" action=\"{{ url_for('run_simulation') }}\">
      <label for=\"steps\">模拟时长（tick 数）</label>
      <input type=\"text\" id=\"steps\" name=\"steps\" value=\"3\">
      <button type=\"submit\">▶️ 开始模拟</button>
    </form>
    {% if history %}
      <h3>最新模拟输出</h3>
      {% for entry in history %}
        <div class=\"history-entry\">
          <strong>Tick {{ entry.tick }}</strong>
          {% if entry.events %}
            <p>触发事件：{{ entry.events|join('，') }}</p>
          {% endif %}
          {% for agent_name, feedback in entry.feedback.items() %}
            {% if feedback %}
              {% for message in feedback %}
                <p>{{ agent_name }}：{{ message }}</p>
              {% endfor %}
            {% else %}
              <p>{{ agent_name }}：保持日常状态。</p>
            {% endif %}
          {% endfor %}
        </div>
      {% endfor %}
    {% endif %}
  </section>

  {% if agent_reports %}
    <section>
      <h2>步骤五：导出报告</h2>
      {% for name, report in agent_reports.items() %}
        <h3>{{ name }}</h3>
        <pre>{{ report }}</pre>
      {% endfor %}
      {% if world_report %}
        <h3>世界总览</h3>
        <pre>{{ world_report }}</pre>
      {% endif %}
    </section>
  {% endif %}
</body>
</html>
"""


def _parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@app.route("/")
def index():
    messages = get_flashed_messages(with_categories=True)
    regions = list(simulation.world.regions.values())
    mbti_codes = sorted(mbti.MBTI_PROFILES.keys())
    default_mbti = mbti_codes[0] if mbti_codes else "INFP"
    return render_template_string(
        TEMPLATE,
        messages=messages,
        agents=list(simulation.agents.values()),
        regions=regions,
        mbti_codes=mbti_codes,
        default_mbti=default_mbti,
        mbti_profiles=mbti.MBTI_PROFILES,
        history=latest_history,
        agent_reports=latest_agent_reports,
        world_report=latest_world_report,
        world=simulation.world,
    )


@app.post("/add-agent")
def add_agent():
    global latest_history, latest_agent_reports, latest_world_report

    name = (request.form.get("name") or "").strip()
    mbti_code = (request.form.get("mbti_code") or "INFP").strip().upper()
    prompt = (request.form.get("prompt") or "").strip()
    region = (request.form.get("region") or "").strip()

    if not name:
        flash("请输入代理名称。", "error")
        return redirect(url_for("index"))

    if name in simulation.agents:
        flash("该名称已存在，请选择其他代理名称。", "error")
        return redirect(url_for("index"))

    if region and region not in simulation.world.regions:
        region = next(iter(simulation.world.regions.keys()), "")

    agent = Agent(name, mbti_code, prompt=prompt or None)

    motivations = _parse_csv(request.form.get("motivations") or "")
    values = _parse_csv(request.form.get("values") or "")
    agent.customize(motivations=motivations or None, values=values or None)

    goal = (request.form.get("goal") or "").strip()
    if goal:
        task = Task(
            goal,
            f"Player defined goal: {goal}",
            required_progress=2.0,
            difficulty=1.0,
        )
        agent.assign_task(task)

    simulation.add_agent(agent, region=region or None)

    latest_history = []
    latest_agent_reports = {}
    latest_world_report = None

    flash(f"已创建代理 {name}（{mbti_code}）。", "success")
    return redirect(url_for("index"))


@app.post("/run")
def run_simulation():
    global latest_history, latest_agent_reports, latest_world_report

    steps_raw = (request.form.get("steps") or "3").strip()
    try:
        steps = int(steps_raw)
    except ValueError:
        flash("请输入有效的模拟时长。", "error")
        return redirect(url_for("index"))

    steps = max(1, min(steps, 12))

    if not simulation.agents:
        flash("请先添加至少一位代理。", "error")
        return redirect(url_for("index"))

    latest_history = simulation.run(steps)
    latest_agent_reports = simulation.agent_reports()
    latest_world_report = simulation.world_report()

    flash(f"模拟完成，共执行 {steps} 个 tick。", "success")
    return redirect(url_for("index"))


@app.post("/reset")
def reset_simulation():
    global simulation, latest_history, latest_agent_reports, latest_world_report

    simulation = create_base_simulation()
    latest_history = []
    latest_agent_reports = {}
    latest_world_report = None

    flash("已重置模拟世界。", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
