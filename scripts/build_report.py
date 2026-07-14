#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供应商质量协议生成与评审器
读入结构化协议 JSON，生成纯文字版 (.txt) + Markdown (.md) 双件文档。
既支持"起草模板"，也支持"差距评审"（每条含现状状态与差距说明）。

用法：
  python build_report.py --input agreement.json --out-dir ./输出
  python build_report.py                                   # 内置小样本，直接产出差距评审示意双件

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
import os
import sys
from datetime import datetime


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


def build_txt(a):
    mode = a.get("mode", "gap")
    sep = "=" * 48
    sub = "-" * 48
    L = []
    L.append(sep)
    L.append(a.get("agreement_title", "供应商质量协议"))
    L.append(sep)
    L.append(f"甲方：{a.get('party_a','')}")
    L.append(f"乙方：{a.get('party_b','')}")
    L.append(f"适用范围：{a.get('scope','')}")
    L.append(f"模式：{'起草模板' if mode=='draft' else '差距评审'}")
    L.append(f"生成日期：{datetime.now().strftime('%Y-%m-%d')}")
    L.append("")
    L.append("一、条款清单")
    L.append(sub)
    for c in a.get("clauses", []) or []:
        tag = "【核心】" if c.get("core") else ""
        L.append(f"{c.get('no','')} {c.get('title','')} {tag}")
        L.append("关键要点：")
        for kp in c.get("key_points", []) or []:
            L.append(f"  - {kp}")
        if mode == "gap":
            st = STATUS_CN.get(c.get("status", ""), c.get("status", ""))
            L.append(f"现状：{st}")
            L.append(f"差距：{c.get('gap','（无）')}")
        L.append("")
    if mode == "gap":
        L.append("二、差距汇总")
        L.append(sub)
        L.append(a.get("gap_summary", "（待企业补充）"))
        L.append("")
        L.append("三、补全建议")
        L.append(sub)
        recs = a.get("recommendations", []) or ["（待企业补充）"]
        for r in recs:
            L.append(f"  - {r}")
        L.append("")
    L.append(f"本报告由供应商质量协议技能生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return "\n".join(L)


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
    ap = argparse.ArgumentParser(description="供应商质量协议生成与评审器（txt+md）")
    ap.add_argument("--input", help="结构化协议 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("--out-dir", default=os.getcwd(), help="输出目录（默认当前工作目录）")
    ap.add_argument("--format", choices=["txt", "md", "all"], default="all", help="输出格式，默认 all（txt+md）")
    args = ap.parse_args()

    try:
        agr = load_agreement(args.input) if args.input else SAMPLE_AGREEMENT
    except Exception as e:
        sys.stderr.write(f"读取输入失败：{e}\n")
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")
    base = f"供应商质量协议_{date_tag}"

    if args.format in ("md", "all"):
        md_path = os.path.join(args.out_dir, base + ".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(build_md(agr))
        sys.stderr.write(f"MD 已生成：{md_path}\n")
    if args.format in ("txt", "all"):
        txt_path = os.path.join(args.out_dir, base + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(build_txt(agr))
        sys.stderr.write(f"TXT 已生成：{txt_path}\n")


if __name__ == "__main__":
    main()
