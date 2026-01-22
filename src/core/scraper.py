import requests
import ddddocr
import random
import csv
import time
from bs4 import BeautifulSoup
from datetime import datetime

class CrazyCarScraper:
    def __init__(self, username, password, log_callback=None):
        self.base_url = "https://ckfksc.com"
        self.username = username
        self.password = password
        self.log_callback = log_callback
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.base_url}/login",
        })
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.is_running = False

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def login(self):
        self.log(f"🚀 正在登录账号: {self.username} ...")
        try:
            self.session.get(f"{self.base_url}/login")
            captcha_resp = self.session.get(
                f"{self.base_url}/captcha?r={random.random()}")
            
            captcha_code = self.ocr.classification(
                captcha_resp.content).strip().upper()
            
            payload = {
                "areaCode": "86", 
                "mobileNo": self.username,
                "password": self.password, 
                "captcha": captcha_code
            }
            
            res = self.session.post(
                f"{self.base_url}/login", data=payload).json()
            
            if res.get("respCo") == "0000":
                self.log(f"✅ 登录成功! 验证码: [{captcha_code}]")
                return True
            
            self.log(f"❌ 登录失败: {res.get('respMsg')}")
            return False
        except Exception as e:
            self.log(f"❌ 登录异常: {e}")
            return False

    def clean_data(self, records, substitution_map):
        if not substitution_map:
            return records
        # Apply substitution map
        cleaned = []
        for r in records:
            new_row = []
            for item in r:
                s_item = str(item).replace('\xa0', ' ').strip()
                new_row.append(substitution_map.get(s_item, s_item))
            cleaned.append(new_row)
        return cleaned

    def start_crawl(self, game_type, start_maps, end_map, substitution_map=None):
        """
        :param game_type: Mode name or ID (e.g. "组队竞速" or "1")
        :param start_maps: list, Stop condition maps (oldest)
        :param end_map: str, Start condition map (newest), empty for immediate
        :param substitution_map: dict, Name replacement map
        """
        self.is_running = True
        
        # Map game type name to ID if needed (Simple mapping based on original code)
        game_modes = ["个人竞速", "组队竞速", "个人道具", "组队道具", "个人疾爽", "组队疾爽"]
        if game_type in game_modes:
            game_type_id = str(game_modes.index(game_type))
        else:
            game_type_id = game_type # Assume it's already an ID or handle it

        if isinstance(start_maps, str):
            start_maps = [start_maps]

        self.log(f"\n🕷️ [抓取开始] 模式: {game_type}")
        self.log(f"   🚩 触发开始(最新): {'直接开始' if not end_map else end_map}")
        self.log(f"   🛑 触发停止(最旧): {start_maps}")

        page = 1
        collecting = True if not end_map else False
        collected_records = []
        combined_header = None
        stop_signal = False

        while self.is_running and not stop_signal:
            self.log(f"📄 请求第 {page} 页数据...")
            url = f"{self.base_url}/user/game?pageNum={page}&gameType={game_type_id}&mapCode="
            
            try:
                resp = self.session.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")
            except Exception as e:
                self.log(f"❌ 请求异常: {e}")
                break

            rows = soup.select("table.table tbody tr")
            if not rows:
                self.log("📭 已无更多数据")
                break

            for row in rows:
                if not self.is_running: break
                
                cols = [td.text.strip() for td in row.find_all("td")]
                if not cols or "没有对局" in cols[0]:
                    continue

                current_map = cols[1] if len(cols) > 1 else ""

                # 1. Start Condition
                if not collecting:
                    if current_map == end_map:
                        collecting = True
                        self.log(f"✅ 找到结束地图 [{end_map}]，开始录制...")
                    else:
                        continue

                # 2. Collect Data
                if collecting:
                    summary = [cols[0], cols[1], cols[6]]  # Mode, Map, Time

                    # Fetch Details
                    dt_tag = row.find("a", string="详情")
                    if dt_tag and dt_tag.has_attr("href"):
                        try:
                            d_url = self.base_url + dt_tag["href"]
                            d_soup = BeautifulSoup(self.session.get(d_url, timeout=5).text, "html.parser")

                            if not combined_header:
                                h = d_soup.select_one("table.table thead tr")
                                if h:
                                    combined_header = ["模式", "地图", "开始时间"] + [th.text.strip() for th in h.find_all("th")]

                            for dr in d_soup.select("table.table tbody tr"):
                                row_data = summary + [td.text.strip() for td in dr.find_all("td")]
                                collected_records.append(row_data)
                        except Exception as e:
                            self.log(f"⚠️ 详情抓取失败: {e}")

                    # 3. Stop Condition
                    if current_map in start_maps:
                        self.log(f"🏁 找到起始地图 [{current_map}]，抓取结束！")
                        stop_signal = True
                        break

            if stop_signal:
                break

            if soup.select_one("ul.pagination li.active + li a"):
                page += 1
                time.sleep(0.5)
            else:
                self.log("⚠️ 已翻至最后一页，未找到指定的起始地图，但已停止。")
                break

        self.is_running = False
        self.log(f"📊 共抓取 {len(collected_records)} 条记录")
        
        final_data = self.clean_data(collected_records, substitution_map)

        if not combined_header and final_data:
            # Fallback header
            combined_header = ["模式", "地图", "开始时间", "角色", "车辆", "队伍", "排名", "成绩", "经验", "金币"]

        return combined_header, final_data

    def stop(self):
        self.is_running = False
        self.log("🛑 正在停止抓取...")

    def save_to_csv(self, header, records, output_dir):
        if not records:
            return None
            
        first = records[0]
        mode = first[0] if first else "未知"
        date_str = first[2].split()[0] if len(first) > 2 else "00-00"
        filename = f"{date_str}_{mode}.csv"
        
        # Ensure output dir exists
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        out_path = os.path.join(output_dir, filename)

        try:
            with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                if header:
                    writer.writerow(header)
                
                s_idx = header.index("成绩") if header and "成绩" in header else -1
                
                for row in records:
                    r = [str(x) for x in row]
                    # Format time to avoid Excel auto-format
                    if s_idx != -1 and s_idx < len(r) and ":" in r[s_idx]:
                        r[s_idx] = f"'{r[s_idx]}"
                    writer.writerow(r)
            
            self.log(f"✅ CSV保存成功: {filename}")
            return out_path
        except Exception as e:
            self.log(f"❌ 保存CSV失败: {e}")
            return None
