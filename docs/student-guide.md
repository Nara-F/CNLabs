# 学生指南

准备 Python 3.11+ 和 make，在仓库根目录运行 `make build`。依次阅读实验 README、api.py 与 test_public.py，再编辑对应 student.py。每次只实现一个可验证的行为；保存接口签名与指定异常。无需第三方库。

```sh
make grade LAB=lab02_reassembly
make grade LAB=lab03_transport
```

`make grade` 默认运行学生实现的公开测试；不传 LAB 运行全部实验。初始 starter 中的 `NotImplementedError` 是待完成的任务，测试失败时先阅读错误及实验契约。编译完成表示语法检查通过；接口导入和功能仍需通过测试验证。

编写自主测试时，用固定输入和可独立推导的预期结果，不只验证编码后再解码。覆盖边界、非法输入、重复事件、顺序变化、资源上界和状态转换。时间驱动实验使用注入的时间；代理实验使用实验指定的本地网络和资源清理方式。将设计、数据和实际用时写入 [模板](../writeups/template.md)。

按各实验要求提交 student.py 和报告，不修改公开 API 或评分测试，也不依赖其他实验的学生实现。完整评分与人工报告的关系见 [评分说明](grading.md)。
