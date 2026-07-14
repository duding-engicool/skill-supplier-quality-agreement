# 供应商质量协议技能（supplier-quality-agreement）

> 主色：#C8102E ｜ 范式：混合式（Markdown + HTML 双版）
> 面向 SQE 与法务/商务的供应商质量协议起草与差距评审工具。

## 一句话说明
覆盖质量协议五大核心条款（质量标准/不合格处理/索赔/审核权/变更通知），并自动生成条款模板与差距评审双版文档。

## 适用角色
- SQE（供应商质量工程师）
- 法务 / 商务

## 使用场景
- 新供应商导入前起草《供应商质量协议》
- 年度续签查漏补缺
- 评审客户发来的质量条款（Customer Quality Requirements）
- 重大索赔/变更纠纷后补强协议

## 五大核心条款
1. 质量标准
2. 不合格品处理
3. 索赔
4. 审核权
5. 变更通知

补充条款：保密与知识产权、争议解决与适用法律、协议有效期与终止、持续改进义务。

## 文件清单
- `SKILL.md`：技能主文件
- `README.md`：本说明
- `scripts/build_report.py`：协议 JSON → MD + HTML（支持起草/差距评审两种模式）

## 使用方法
```bash
# 内置小样本直接跑通，产出差距评审示意双版
python scripts/build_report.py

# 用自有数据（mode: draft 或 gap）
python scripts/build_report.py --input agreement.json --md-out 供应商质量协议.md --html-out 供应商质量协议.html
```

## 联动技能
- supplier-management-plan（方案第7段协议落地）
- supplier-assessment（C/D级加重不合格处理与索赔）
- supplier-development（帮扶期特殊质量目标）
- customer-satisfaction-survey（客户条款与对下协议对齐）

## 注意事项
- 具体索赔比例、违约金、PPM 目标、提前通知天数标「待企业补充 / 待法务确认」；
- 本技能生成的是条款模板与差距清单，不替代法务正式审核与签署；
- 不编造法律法规条文编号。
