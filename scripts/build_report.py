#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供应商质量协议生成与评审器
读入结构化协议 JSON，生成 Markdown + 网页版 HTML（主色 #C8102E）。
既支持"起草模板"，也支持"差距评审"（每条含现状状态与差距说明）。

用法：
  python build_report.py --input agreement.json --md-out 供应商质量协议.md --html-out 供应商质量协议.html
  python build_report.py                                   # 内置小样本，直接产出差距评审示意双版

输入 JSON 结构：
{
  "agreement_title": "供应商质量协议",
  "party_a": "甲方（采购方）",
  "party_b": "乙方（供应商）",
  "scope": "适用产品/范围",
  "mode": "draft | gap",            # draft=起草模板, gap=差距评审
  "clauses": [
    {"no":"1","title":"质量标准","core":true,
     "key_points":["...","..."],
     "status":"included|partial|missing",   # 仅 gap 模式用
     "gap":"差距说明（仅 gap 模式用）"},
    ...
  ],
  "gap_summary": "整体覆盖度说明",
  "recommendations": ["建议1","建议2"]
}
"""

import argparse
import json
import sys
import html
from datetime import datetime

PRIMARY = "#C8102E"


def esc(s):
    return html.escape(str(s), quote=True)


def load_agreement(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


STATUS_CN = {"included": "已包含", "partial": "部分包含", "missing": "缺失"}


def clauses_md(items, mode):
    L = []
    for c in items or []:
        tag = "【核心】" if c.get("core") else ""
        L.append(f"### {c.get('no','')} {c.get('title','')} {tag}\n")
        L.append("**关键要点**：")
        for kp in c.get("key_points", []) or []:
            L.append(f"- {kp}")
        if mode == "gap":
            st = STATUS_CN.get(c.get("status", ""), c.get("status", ""))
            L.append(f"\n**现状**：{st}")
            L.append(f"**差距**：{c.get('gap','（无）')}")
        L.append("")
    return "\n".join(L)


def build_md(a):
    mode = a.get("mode", "gap")
    L = []
    L.append(f"# {a.get('agreement_title','供应商质量协议')}\n")
    L.append("## 一、协议基本信息\n")
    L.append(f"- 甲方：{a.get('party_a','')}")
    L.append(f"- 乙方：{a.get('party_b','')}")
    L.append(f"- 适用范围：{a.get('scope','')}")
    L.append(f"- 模式：{'起草模板' if mode=='draft' else '差距评审'}")
    L.append(f"- 生成日期：{datetime.now().strftime('%Y-%m-%d')}\n")
    L.append("## 二、条款清单\n")
    L.append(clauses_md(a.get("clauses", []), mode))
    if mode == "gap":
        L.append("## 三、差距汇总\n")
        L.append(a.get("gap_summary", "（待企业补充）"))
        L.append("\n## 四、补全建议\n")
        for r in a.get("recommendations", []) or []:
            L.append(f"- {r}")
        if not a.get("recommendations"):
            L.append("- （待企业补充）")
        L.append("")
    L.append(f"> 本报告由供应商质量协议技能生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(L)


CSS = f"""
:root{{--primary:{PRIMARY};--bg:#fafafa;--card:#ffffff;--ink:#1f2937;--muted:#6b7280;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.75;padding:32px}}
.wrap{{max-width:980px;margin:0 auto}}
header{{text-align:center;padding:26px 0 16px;border-bottom:3px solid var(--primary);margin-bottom:26px}}
header h1{{font-size:27px}}
header .meta{{color:var(--muted);font-size:14px;margin-top:10px}}
.sec{{background:var(--card);border-radius:14px;padding:22px 26px;box-shadow:0 4px 16px rgba(0,0,0,.05);margin-bottom:20px}}
.sec h2{{font-size:20px;margin-bottom:12px;border-left:5px solid var(--primary);padding-left:12px}}
.clause{{border:1px solid #eee;border-radius:10px;padding:14px 18px;margin:12px 0}}
.clause.core{{border-left:5px solid var(--primary)}}
.clause h3{{font-size:16px;margin-bottom:6px}}
.clause .badge{{display:inline-block;background:var(--primary);color:#fff;font-size:12px;border-radius:5px;padding:1px 7px;margin-left:6px}}
.kp{{margin:4px 0 4px 20px;font-size:14px}}
.st{{font-size:13px;margin-top:6px}}
.st.included{{color:#16a34a}} .st.partial{{color:#d97706}} .st.missing{{color:var(--primary);font-weight:700}}
.gap{{color:var(--muted);font-size:13px;margin-top:3px}}
footer{{text-align:center;color:var(--muted);font-size:12px;margin-top:18px}}
"""


def clause_html(c, mode):
    core_cls = " core" if c.get("core") else ""
    badge = '<span class="badge">核心</span>' if c.get("core") else ""
    kp = "\n".join(f"<li class='kp'>{esc(k)}</li>" for k in (c.get("key_points", []) or []))
    extra = ""
    if mode == "gap":
        st = c.get("status", "")
        stcn = STATUS_CN.get(st, st)
        extra = (f"<div class='st {st}'>现状：{stcn}</div>"
                 f"<div class='gap'>差距：{esc(c.get('gap','（无）'))}</div>")
    return (f"<div class='clause{core_cls}'><h3>{esc(c.get('no',''))} {esc(c.get('title',''))}{badge}</h3>"
            f"<ul>{kp}</ul>{extra}</div>")


def build_html(a):
    mode = a.get("mode", "gap")
    clauses_html = "\n".join(clause_html(c, mode) for c in (a.get("clauses", []) or []))
    rec_html = "\n".join(f"<li>{esc(r)}</li>" for r in (a.get("recommendations", []) or ["（待企业补充）"]))
    gap_sec = ""
    if mode == "gap":
        gap_sec = (f"<section class='sec'><h2>三、差距汇总</h2><p>{esc(a.get('gap_summary','（待企业补充）'))}</p></section>"
                   f"<section class='sec'><h2>四、补全建议</h2><ul>{rec_html}</ul></section>")
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(a.get('agreement_title','供应商质量协议'))}</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<header>
  <h1>{esc(a.get('agreement_title','供应商质量协议'))}</h1>
  <div class="meta">甲方：{esc(a.get('party_a',''))} ｜ 乙方：{esc(a.get('party_b',''))} ｜ 模式：{'起草模板' if mode=='draft' else '差距评审'}</div>
</header>
<section class="sec"><h2>一、协议基本信息</h2>
<p>适用范围：{esc(a.get('scope',''))}</p>
<p>生成：{datetime.now().strftime('%Y-%m-%d')}</p></section>
<section class="sec"><h2>二、条款清单</h2>{clauses_html}</section>
{gap_sec}
<footer>本报告由供应商质量协议技能生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>
</div></body></html>"""


SAMPLE_AGREEMENT = {
    "agreement_title": "供应商质量协议（差距评审示意）",
    "party_a": "甲方（采购方）示例公司",
    "party_b": "乙方（供应商）恒锐精密",
    "scope": "汽车冲压件，应用于A车型",
    "mode": "gap",
    "clauses": [
        {"no": "1", "title": "质量标准", "core": True,
         "key_points": ["质量责任归属", "技术规格与图纸管控", "检验标准与抽样方案(AQL)", "PPAP/样件批准", "质量目标(PPM/合格率/准时率待企业补充)"],
         "status": "partial", "gap": "缺少量化质量目标(PPM/合格率)的具体数值"},
        {"no": "2", "title": "不合格品处理", "core": True,
         "key_points": ["标识隔离与退货", "退货分析与8D时效", "召回/停止发货", "让步接收审批"],
         "status": "included", "gap": "（无）"},
        {"no": "3", "title": "索赔", "core": True,
         "key_points": ["索赔范围", "索赔计算(件数/运费/工时/信赖损失)", "违约金", "扣款机制"],
         "status": "missing", "gap": "协议完全缺失索赔条款，重大风险"},
        {"no": "4", "title": "审核权", "core": True,
         "key_points": ["二方审核权", "飞行检查", "资料提供义务", "不符合项整改与验证"],
         "status": "partial", "gap": "未明确飞行检查与资料提供时限"},
        {"no": "5", "title": "变更通知", "core": True,
         "key_points": ["4M1E变更提前通知", "客户书面批准", "变更验证与库存处理"],
         "status": "missing", "gap": "无4M1E变更通知义务，隐瞒变更风险高"},
        {"no": "6", "title": "保密与知识产权", "core": False,
         "key_points": ["技术资料保密", "知识产权归属"],
         "status": "included", "gap": "（无）"},
        {"no": "7", "title": "争议解决与有效期", "core": False,
         "key_points": ["适用法律", "争议解决方式", "协议有效期与终止"],
         "status": "partial", "gap": "未约定协议续签与终止触发条件"}
    ],
    "gap_summary": "7项条款中：完整2项、部分3项、缺失2项（索赔、变更通知均为核心缺失），覆盖度约43%。核心条款缺失将直接导致质量风险无合同约束。",
    "recommendations": [
        "立即补全『索赔』条款，明确索赔范围、计算方式与违约金（比例待法务确认）",
        "强制加入『4M1E变更通知』条款，约定提前通知天数与客户批准流程",
        "为『质量标准』补充量化质量目标(PPM/合格率/准时率)",
        "明确『审核权』中的飞行检查与资料提供时限"
    ]
}


def main():
    ap = argparse.ArgumentParser(description="供应商质量协议生成与评审器")
    ap.add_argument("--input", help="结构化协议 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("--md-out", default="供应商质量协议.md", help="输出 MD 路径")
    ap.add_argument("--html-out", default="供应商质量协议.html", help="输出 HTML 路径")
    args = ap.parse_args()

    try:
        agr = load_agreement(args.input) if args.input else SAMPLE_AGREEMENT
    except Exception as e:
        sys.stderr.write(f"读取输入失败：{e}\n")
        sys.exit(1)

    with open(args.md_out, "w", encoding="utf-8") as f:
        f.write(build_md(agr))
    sys.stderr.write(f"MD 已生成：{args.md_out}\n")

    with open(args.html_out, "w", encoding="utf-8") as f:
        f.write(build_html(agr))
    sys.stderr.write(f"HTML 已生成：{args.html_out}\n")


if __name__ == "__main__":
    main()
