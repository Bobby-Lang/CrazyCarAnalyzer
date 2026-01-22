# 🏎️ CrazyCarAnalyzer (赛车数据分析工具 Pro)

专业的赛车游戏数据抓取与分析看板工具。

![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-win.svg)

## ✨ 主要功能

- **📊 自动化数据抓取**: 一键登录游戏账号，自动抓取指定范围的比赛记录。
- **📈 可视化报表**: 生成精美的 HTML 交互式报表，包含胜率饼图、走势折线图、柱状图。
- **🏆 MVP/FMVP 分析**: 自动计算红蓝队 MVP 及 FMVP 选手。
- **⚙️ 高级配置**:
    - **角色替换**: 支持将游戏内昵称映射为统一名称，方便战队统计。
    - **自定义阶段**: 支持按地图范围划分比赛阶段（如“第一轮”、“决赛”）。
- **🔐 安全管理**: 本地加密存储账号密码，支持多账号切换。
- **🖥️ 现代化界面**: 采用 CustomTkinter 构建的暗色系电竞风格界面。

## 🚀 快速开始

### 方式一：下载可执行文件 (推荐)
1. 前往 [Releases](../../releases) 页面下载最新的 `CrazyCarAnalyzer.exe`。
2. 双击运行即可，无需安装 Python 环境。

### 方式二：源码运行
1. 安装 Python 3.10+。
2. 克隆仓库:
   ```bash
   git clone https://github.com/YourUsername/CrazyCarAnalyzer.git
   cd CrazyCarAnalyzer
   ```
3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```
4. 运行:
   ```bash
   python main.py
   ```

## 📖 使用指南

1. **登录账号**: 首次使用请进入"账号"页面，输入手机号和密码并保存。点击"测试登录"确保无误。
2. **抓取数据**:
   - 进入"主页"。
   - 选择游戏模式 (如"组队竞速")。
   - **结束地图**: 选择最新的一张地图 (作为开始点)。
   - **起始地图**: 选择最旧的一张地图 (作为停止点)。
   - 点击 **🚀 开始抓取并分析**。
3. **查看报表**: 抓取完成后会自动打开浏览器展示报表。也可以在"历史"页面查看过往报表。
4. **配置映射**: 在"配置"页面添加角色名替换规则 (例如: `新手01` -> `大神A`)。

## 🛠️ 构建指南

如果您想自己修改代码并打包：

1. 运行根目录下的 `build.bat` 脚本。
2. 等待构建完成。
3. 在 `dist` 文件夹中找到生成的 `.exe` 文件。

## 📄 License

MIT License
