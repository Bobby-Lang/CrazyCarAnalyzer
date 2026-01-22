import pandas as pd
import json
import logging
import time
import shutil
from pathlib import Path
from src.utils.paths import get_assets_dir

# Set up logging to use a null handler by default, or just let the caller handle logging config
logger = logging.getLogger(__name__)

OFFICIAL_MAP_ORDER = [
    "绿色山谷", "黄昏小镇", "风车农场", "酋长部落", "钟楼魅影", "XTORM乐园", "城堡的冬天",
    "小赛车场", "火山", "长城", "A519公路", "恐龙乐园★", "藏宝海湾★", "月亮城堡★",
    "西部矿洞", "快乐农场", "海上大桥", "山谷要塞", "大赛车场", "U型山谷", "秋名山-下",
    "秋名山-上", "A1港口", "宇宙大帝", "精灵传说", "遥望迪拜", "沉默都市", "香港",
    "迷失沙漠", "雪邦", "决战山脊", "好运北京", "ZIC", "英伦秋色", "太空堡垒",
    "星际之门", "Intel乐园", "蒙特卡罗", "马尼拉", "星球大战", "飘渺之旅", "迷失森林",
    "迷宫", "酋长部落II", "雪域冰川", "海底世界", "楼兰古道", "吉祥万里", "龙珠蛇道",
    "上海世博", "加泰罗尼亚", "巴林", "大大乐园", "快乐圣诞", "穿山越岭", "空中城堡",
    "怪魔禁地", "旋云圣殿", "风车农场2", "太空驿站", "极限矿山", "蒸汽工厂", "29",
    "小柔的N乐园", "小柔的泰姬陵"
]

class ReportGenerator:
    def __init__(self):
        self.default_year = 2026
        self.template_path = get_assets_dir() / "report_template.html"
        
    def load_template(self):
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found at {self.template_path}")
        with open(self.template_path, "r", encoding="utf-8") as f:
            return f.read()

    def process_dataframe(self, file_path, sub_map):
        try:
            file_path = Path(file_path)
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path, encoding='utf-8-sig')

            df.columns = df.columns.str.strip()
            if "角色" not in df.columns:
                if file_path.suffix.lower() == '.xlsx':
                    df = pd.read_excel(file_path, header=1)
                else:
                    df = pd.read_csv(file_path, encoding='utf-8-sig', header=1)
                df.columns = df.columns.str.strip()

            df["角色"] = df["角色"].astype(str).str.replace(r"\xa0", " ", regex=True).str.strip()
            df["显示名称"] = df["角色"].map(lambda x: sub_map.get(x, x))

            score_map = {1: 10, 2: 8, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1}
            df["得分"] = df["排名"].map(score_map).fillna(0).astype(int)
            df.loc[df["成绩"].astype(str).str.contains("未完成|00:00|0-1"), "得分"] = 0
            return df
        except Exception as e:
            logger.error(f"处理数据出错: {e}")
            return None

    def generate_report(self, target_file, sub_map, custom_pages, output_dir):
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            
        target_file = Path(target_file)
        if not target_file.exists():
            logger.error(f"指定文件不存在: {target_file}")
            return None

        logger.info(f"正在分析文件: {target_file.name}")
        df = self.process_dataframe(target_file, sub_map)
        if df is None:
            return None

        m_date = "未知日期"
        if "开始时间" in df.columns and not df["开始时间"].empty:
            raw = str(df["开始时间"].iloc[0]).strip()
            date_part = raw.split(' ')[0]
            if len(date_part.split('-')) == 2:
                m_date = f"{self.default_year}-{date_part}"
            elif "/" in date_part:
                m_date = date_part.replace("/", "-")
            else:
                m_date = date_part

        m_mode = df["模式"].iloc[0] if "模式" in df.columns else "未知模式"
        m_car = df["车辆"].dropna().mode()[0] if "车辆" in df.columns and not df["车辆"].dropna().empty else "未知车辆"

        summary = []
        for (t, m), g in df.groupby(["开始时间", "地图"], sort=False):
            sc = g.groupby("队伍")["得分"].sum()
            r, b = int(sc.get("红队", 0)), int(sc.get("蓝队", 0))
            if r > b:
                win = "红队"
            elif b > r:
                win = "蓝队"
            else:
                rank1 = g[g["排名"] == 1]
                win = rank1["队伍"].iloc[0] if not rank1.empty else "红队"
            summary.append({"map": m, "red": r, "blue": b, "win": win})

        r_wins_total = sum(1 for x in summary if x["win"] == "红队")
        b_wins_total = sum(1 for x in summary if x["win"] == "蓝队")
        r_score_total = sum(x["red"] for x in summary)
        b_score_total = sum(x["blue"] for x in summary)

        global_winner = "红队" if r_wins_total >= b_wins_total else "蓝队"
        red_cls = "winner" if r_wins_total >= b_wins_total else ""
        blue_cls = "winner" if b_wins_total > r_wins_total else ""

        ranks = pd.crosstab(df["显示名称"], df["排名"]).reindex(columns=range(1, 9), fill_value=0)
        player_teams = df.groupby("显示名称")["队伍"].first()
        stats = df.groupby("显示名称").agg({"得分": "sum", "地图": "count"}).rename(columns={"地图": "场次", "得分": "总分"})
        report = pd.concat([ranks, stats, player_teams], axis=1).sort_values("总分", ascending=False)

        try:
            mvp_row = report[report["队伍"] == global_winner].iloc[0]
            mvp_name = mvp_row.name
            mvp_score = mvp_row["总分"]
            mvp_1st = mvp_row[1]
            loser_team = "蓝队" if global_winner == "红队" else "红队"
            fmvp_row = report[report["队伍"] == loser_team].iloc[0]
            fmvp_name = fmvp_row.name
            fmvp_score = fmvp_row["总分"]
            fmvp_1st = fmvp_row[1]
        except Exception as e:
            logger.warning(f"MVP计算异常: {e}")
            mvp_name = fmvp_name = "N/A"
            mvp_score = fmvp_score = mvp_1st = fmvp_1st = 0

        rows_html = ""
        for n, r in report.iterrows():
            t_bg = "bg-red" if r["队伍"] == "红队" else "bg-blue"
            tds = "".join([f"<td>{r[i] if r[i]>0 else '-'}</td>" for i in range(1, 9)])
            rows_html += f"<tr><td class='player-name' title='{n}'>{n}</td><td><span class='team-badge {t_bg}'>{r['队伍']}</span></td>{tds}<td>{r['场次']}</td><td class='total-score'>{r['总分']}</td></tr>"

        map_idx = {n: i for i, n in enumerate(OFFICIAL_MAP_ORDER)}
        pages_data = []
        
        if not custom_pages:
            custom_pages = [{"name": "全场统计", "start_map": "", "end_map": ""}]

        bar_cats, bar_r, bar_b = [], [], []

        for pc in custom_pages:
            p_name = pc.get("name", "未命名")
            s_map, e_map = pc.get("start_map", ""), pc.get("end_map", "")
            s_idx = map_idx.get(s_map, 0) if s_map else 0
            e_idx = map_idx.get(e_map, 9999) if e_map else 9999
            subset = [m for m in summary if s_idx <= map_idx.get(m["map"], -1) <= e_idx]
            if subset:
                subset.sort(key=lambda x: map_idx.get(x["map"], 9999))
                pages_data.append({"name": p_name, "data": subset})
                bar_cats.append(p_name)
                bar_r.append(sum(1 for x in subset if x["win"] == "红队"))
                bar_b.append(sum(1 for x in subset if x["win"] == "蓝队"))

        dyn_html = ""
        all_charts = []
        for i, p in enumerate(pages_data):
            div_id = f"chart_dynamic_{i}"
            dyn_html += f'<div class="card chart-row"><div class="chart-header">{p["name"]} 走势图</div><div id="{div_id}" class="echart-box"></div></div>'
            all_charts.append({
                "maps": [x["map"] for x in p["data"]],
                "red": [x["red"] for x in p["data"]],
                "blue": [x["blue"] for x in p["data"]]
            })

        html_template = self.load_template()
        html = html_template.replace("{DATE}", m_date)\
            .replace("{MODE}", m_mode)\
            .replace("{CAR}", m_car)\
            .replace("{R_WINS}", str(r_wins_total))\
            .replace("{B_WINS}", str(b_wins_total))\
            .replace("{RED_CLS}", red_cls)\
            .replace("{BLUE_CLS}", blue_cls)\
            .replace("{R_SCORE}", str(r_score_total))\
            .replace("{B_SCORE}", str(b_score_total))\
            .replace("{MVP_N}", str(mvp_name))\
            .replace("{MVP_S}", str(mvp_score))\
            .replace("{MVP_1}", str(mvp_1st))\
            .replace("{FMVP_N}", str(fmvp_name))\
            .replace("{FMVP_S}", str(fmvp_score))\
            .replace("{FMVP_1}", str(fmvp_1st))\
            .replace("{ROWS}", rows_html)\
            .replace("{BAR_CATS}", json.dumps(bar_cats, ensure_ascii=False))\
            .replace("{BAR_R}", json.dumps(bar_r))\
            .replace("{BAR_B}", json.dumps(bar_b))\
            .replace("{DYNAMIC_CHARTS_HTML}", dyn_html)\
            .replace("{ALL_CHARTS_DATA}", json.dumps(all_charts, ensure_ascii=False))

        timestamp = int(time.time())
        safe_date_filename = m_date.replace(":", "-").replace(" ", "_")
        out_filename = f"Report_{safe_date_filename}_{timestamp}.html"
        out_path = output_dir / out_filename
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Copy echarts.min.js to output dir
        echarts_src = get_assets_dir() / "echarts.min.js"
        echarts_dst = output_dir / "echarts.min.js"
        if echarts_src.exists() and not echarts_dst.exists():
            shutil.copy(echarts_src, echarts_dst)

        logger.info(f"报表已生成: {out_path.name}")
        return out_path
