# Encoding1 图片 ID 探索性分析（训练/测试分离）

这不是 `primary-v1` 的主检验，而是独立的探索性分析。

## 问题

对每个 unit：第一张编码图片中，哪一张图片的 `response - baseline` 平均放电率最高？这张图片在未参与选择的 trial 中，是否仍高于其他四张图片？

## 固定流程

1. 每个 session 的每个图片 ID 都按 `SPLIT_SEED=20260906` 随机、分层地切为近似 50% 训练和 50% 测试 trial。
2. 对每个 unit，只用训练 trial 计算每张图片的平均 `rate_difference_hz`，并选取最大者为 `selected_pic_id`。
3. 只用测试 trial 比较 `selected_pic_id` 与其他四张图片的平均 `rate_difference_hz`。正值表示候选图片较强。
4. 用 10,000 次单尾置换检验该测试集差异是否大于随机标签下的差异；随后只在同一 session 的 unit 之间做 BH-FDR（`q < 0.05`）。

训练集和测试集分开，因此不会发生“用同一批 trial 先挑最强图片、又用同一批 trial 宣称它最强”的数据泄漏。但这仍是探索性结果：需要在新的、独立的数据中重复，不能反过来改变 `primary-v1` 的窗口、QC 或主结论。
