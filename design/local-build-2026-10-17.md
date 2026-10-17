# 本地验证：怎么不用每次都等整站构建（2026-10-17）

同一个站，GitHub Actions 上整站构建 3.5 分钟，这台 Windows 机器上 14–16 分钟，机器忙的时候 40 多分钟。
P: 盘是 NVMe、CPU 闲着；Defender 已把 `P:\WEBSITE` 加进排除项（10-16），之后列 1.3 万个输出文件从 2 分多钟降到 2 秒，
但整站构建几乎没变——慢在 Windows 上 Ruby 的文件系统调用（每页几十个 include，每个都要查文件在不在），构建时 ruby 只用到约三分之一个核。

所以按要看的范围选工具：

| 要看什么 | 用什么 | 实测 |
|---|---|---|
| 改了一两篇文章、一个页面、一段样式 | `tools/preview-pages.rb` + `tools/preview-serve.py` | 20–30 s（机器忙时约 1 分钟）；`--full` 约 3 分钟 |
| 整站会不会坏（链接、生成页、全站检查） | 推一个非 main 分支 → GitHub「Check a branch」 | 约 5–6 分钟，不占本机 |
| 本机要一份完整的 _site | `tools/docker-build.sh`（Linux 容器） | Jekyll 5.8–7.1 分钟（机器负载 40–62% 时）+ 拷回 Windows 几分钟；第一次另要约 10 分钟拉镜像装 gems |
| （不推荐）Windows 原生整站构建 | 见 memory 里的那行命令 | 14–16 分钟，忙时 40+ |

## 1. 只渲染要看的页

```bash
# Ruby 环境同整站构建：C:/Ruby33-x64，去掉 RUBYOPT / GEM_HOME / BUNDLE_GEMFILE，gems 在主工作树的 vendor/bundle
ruby tools/preview-pages.rb _posts/2026-10-12-interview-….md _pages/timeline.md
ruby tools/preview-pages.rb --css /timeline/2010/ /games/        # 也认网址；--css 顺带重编 main.css
ruby tools/preview-pages.rb --layout interview-editorial --limit 3
python tools/preview-serve.py                                    # http://127.0.0.1:4759/
```

载入的东西和整站构建一样（全部帖子与集合文档、_data、版式、include、插件），只是不读其他页面、不跑生成器，然后只渲染点名的页。
结果写进 `.preview-build/pages/`（git 已忽略）。`preview-serve.py` 先找渲染出来的页，找不到就从源码目录拿（图片、脚本、字体整站构建也是原样拷），所以页面和线上一样完整。
差别：没点名的页不存在（预览里点过去是 404）；页面类的面包屑和「列出所有页面」的地方会少东西，要和线上一模一样就加 `--full`（读全站、跑生成器）。
Git Bash 会把 `/games/` 这种参数改写成 `C:/Program Files/Git/games/`，脚本认得这种改写，不用管。

## 2. 推分支让 GitHub 检查

`.github/workflows/check.yml`：推到 main 以外的任何分支就跑——和部署同样的 App 数据导出与 Jekyll 构建，再跑 `tools/check-build.py`、App 数据检查（和线上比计数）、英文 SEO 基准；不上传、不部署。
同一分支连推两次，前一次自动取消。

## 3. Linux 容器里整站构建

```bash
tools/docker-build.sh               # HEAD → P:/WEBSITE/.docs-verify/docker/_site
tools/docker-build.sh --worktree    # 连同已跟踪文件的未提交改动（git stash create，不动 stash 列表）
python tools/check-build.py P:/WEBSITE/.docs-verify/docker/_site
```

用 `git archive` 把源码流进容器（不挂载共享目录，那又会慢），Ruby 版本和部署一致（3.2），gems 存在 volume `pokeamice-docs-gems`。
10-17 用它构建的 _site 过了全站检查（ALL OK，12,975 个文件，与 Windows 构建一致）。拷回 Windows 那一步（880 MB、1.3 万个文件）要几分钟，只需要看几页时用第 1 种更快。
要先开 Docker Desktop；未跟踪的新文件不会进去（先 `git add`）。
