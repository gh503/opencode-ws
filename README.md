# AE-OS Enterprise Secure Edition v2.0

本项目包含企业级安全规范的 OpenCode 配置文件和 Skills。

## 目录结构

```
.
├── AGENTS.md                           # 全局企业安全规则
├── README.md                           # 本文档
└── skills/
    ├── python-quality/                 # Python 企业级规范
    ├── rust-error-handling/            # Rust 错误与安全处理
    ├── go-best-practices/             # Go 企业级规则
    ├── cpp-modern-architecture/       # C++ 现代安全架构
    ├── frontend-architecture/         # 前端企业级架构
    ├── enterprise-error-model/        # 企业级错误建模
    ├── enterprise-logging-standard/   # 企业级日志规范
    └── evolution-policy/              # 进化策略
```

## 安装说明

### 方法一：符号链接（推荐）

将 skills 目录链接到 OpenCode 配置目录：

```bash
# Linux/macOS
ln -s /path/to/opencode-ws/skills ~/.config/opencode/skills

# Windows (管理员权限)
mklink /D %USERPROFILE%\.config\opencode\skills D:\code\opencode-ws\skills
```

同时链接 AGENTS.md：

```bash
# Linux/macOS
ln -s /path/to/opencode-ws/AGENTS.md ~/.config/opencode/AGENTS.md

# Windows
mklink %USERPROFILE%\.config\opencode\AGENTS.md D:\code\opencode-ws\AGENTS.md
```

### 方法二：复制文件

直接复制到 OpenCode 配置目录：

```bash
# Linux/macOS
cp -r skills/* ~/.config/opencode/skills/
cp AGENTS.md ~/.config/opencode/AGENTS.md

# Windows
xcopy /E /I skills "%USERPROFILE%\.config\opencode\skills\"
copy AGENTS.md "%USERPROFILE%\.config\opencode\AGENTS.md"
```

## Skills 列表

| Skill Name | 描述 |
|------------|------|
| python-quality | Python 后端质量与安全标准 |
| rust-error-handling | Rust 错误处理与安全实践 |
| go-best-practices | Go 代码结构与安全规范 |
| cpp-modern-architecture | C++ 现代安全架构 |
| frontend-architecture | 前端 UI 标准 |
| enterprise-error-model | 跨语言结构化错误建模 |
| enterprise-logging-standard | 结构化安全日志规范 |
| evolution-policy | 错误模式抽象为规则 |

## 使用方法

在 OpenCode 中使用时，可以通过 `load_skills` 参数加载相关技能：

```typescript
task(
  category="...",
  load_skills=["python-quality", "enterprise-error-model"],
  prompt="..."
)
```

## AGENTS.md 规则

AGENTS.md 包含以下企业级安全规范：

1. **Security-First Principle** - 安全优先原则
2. **Threat & Risk Modeling** - 威胁与风险建模
3. **Unified Error Modeling** - 统一错误建模
4. **Error Exposure Policy** - 错误暴露策略
5. **Structured Logging** - 结构化日志
6. **Input Validation** - 输入验证
7. **Secrets & Credentials** - 密钥与凭证管理
8. **Concurrency & Determinism** - 并发与确定性
9. **Performance Discipline** - 性能纪律
10. **Response Format Protocol** - 响应格式协议

---

**注意**: 本配置需链接到 OpenCode 全局配置目录才能生效。
