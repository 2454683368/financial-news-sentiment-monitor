# Financial News Sentiment Monitor / 财经新闻情绪与市场波动监测

A lightweight, explainable, and continuously updating financial-tech project.

一个轻量、可解释、可持续更新的金融科技展示项目。

## What this project does / 项目做什么
- Collects financial news headlines daily / 每日抓取财经新闻标题
- Cleans noisy, duplicate, and low-value items / 清洗噪声、重复和低价值内容
- Builds a hybrid sentiment score / 构建混合情绪评分
- Fetches market index data such as HS300 and SH Index / 抓取沪深300与上证指数数据
- Generates charts, reports, and a GitHub Pages landing page / 生成图表、日报和 GitHub Pages 展示页
- Supports OpenClaw scheduled automation / 支持 OpenClaw 定时自动运行

## Core methodology / 核心方法
1. **Data ingestion / 数据抓取**  
   Collect headlines from a small set of relatively stable public sources.  
   从少量相对稳定的公开新闻源抓取标题。

2. **Cleaning / 数据清洗**  
   Remove roadshows, institution homepages, event pages, and duplicate titles.  
   过滤说明会、机构主页、活动页和重复标题。

3. **Sentiment scoring / 情绪打分**  
   Combine SnowNLP model output with finance-specific keyword rules.  
   用 SnowNLP 与财经关键词规则做混合评分。

4. **Market linkage / 市场联动**  
   Compare sentiment readings with HS300 / SH Index daily returns.  
   将情绪读数与沪深300 / 上证指数日收益进行对照。

5. **History accumulation / 历史积累**  
   Store daily snapshots for future multi-day trend analysis.  
   存储每日快照，为多日趋势分析做准备。

## Daily usage / 日常运行方式
```bash
source .venv/bin/activate
python scripts/run_daily.py
python scripts/publish_github.py
```

## Current stage / 当前阶段
- End-to-end pipeline is running / 全流程已跑通
- GitHub Pages is live / GitHub Pages 已上线
- Visual charts are available / 可视化图表已接入
- Historical accumulation has started / 历史数据积累已开始
- OpenClaw automation is configured / OpenClaw 自动调度已配置
- Source quality and sentiment robustness are still improving / 数据源质量和情绪稳健性仍在持续优化

## Repository structure / 仓库结构
- `scripts/` runnable pipeline scripts / 可执行脚本
- `data/` raw and processed data / 原始与处理后数据
- `reports/` generated markdown reports / 生成的日报
- `docs/` GitHub Pages content / Pages 页面内容
- `docs/assets/` charts and history files / 图表与历史快照
- `config/` source and settings config / 配置文件

## Why this project matters / 为什么这个项目有价值
This project is not trying to be a heavy production crawler. The goal is to build a stable, explainable, and continuously updating financial-tech system that is suitable for GitHub display and interview discussion.

这个项目不是重型生产爬虫，而是一个稳定、可解释、可持续更新的金融科技系统，适合 GitHub 展示，也适合在面试中清晰讲解。

## Status / 状态
See `docs/STATUS.md` for the latest status and next steps.  
最新状态见 `docs/STATUS.md`。
