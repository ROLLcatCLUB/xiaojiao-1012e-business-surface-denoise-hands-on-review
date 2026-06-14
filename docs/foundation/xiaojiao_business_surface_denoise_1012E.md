# 1012E Business Surface Denoise And Hands-On Review Polish

## 结论

`1012E` 已对 `frontend/xiaojiao-preview.html` 做教师可见层去噪。页面继续保留 1012D 已接入的业务能力，但普通教师视图不再直接露出 `home_light_entry`、`candidate_review_surface`、`teacher_review_required=true`、`formal_apply_performed=false`、`stub_only` 等工程或合同标记。

## 去噪范围

| 页面 | 1012E 处理 |
| --- | --- |
| 首页 | 改成“今天先处理这一课”的教师工作入口，显示当前单课、业务进度、待确认数量和小教建议 |
| 单课焦点 | 保留教学目标、课时结构、探究环节建议、本课材料夹和轻记录，不露工程对象名 |
| 本课材料夹 | 学习单、评价量规、资源参考、证据反思改成教师材料语言 |
| 候选审核页 | 改成“这是一版候选稿 / 你确认后才放入本课材料”的审核体验 |
| 旧入口 | 只保留“需要长任务？打开旧工作台”的弱入口表达 |

## 保留能力

- 首页进入单课焦点
- 单课焦点进入材料夹
- 学习单查看候选
- 进入教师审核门
- 评价量规候选
- 资源参考候选
- 轻记录
- Intent Bar
- reset preview store
- export snapshot
- localStorage / backend sandbox fallback
- teacher review gate
- event log

## 边界

- `visible_engineering_labels_removed=true`
- `business_model_applied=true`
- `material_folder_enabled=true`
- `review_gate_enabled=true`
- `legacy_entry_enabled=true`
- `preview_route_only=true`
- `default_route_changed=false`
- `formal_apply_performed=false`
- `real_database_written=false`
- `memory_written=false`
- `Feishu_written=false`
- `new_live_provider_call=false`

## 状态

```text
XIAOJIAO_BUSINESS_SURFACE_DENOISE_AND_HANDS_ON_REVIEW_POLISH_PASS
ALL_1012E_BUSINESS_SURFACE_DENOISE_AND_HANDS_ON_REVIEW_POLISH_CHECKS_OK
```
