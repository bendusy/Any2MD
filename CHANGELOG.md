# CHANGELOG

<!-- version list -->

## v1.5.4 (2026-01-13)

### Bug Fixes

- 移除未使用的 QMutex 导入
  ([`d5b875e`](https://github.com/bendusy/Any2MD/commit/d5b875e9f3c4276d473ed8cb90f691427183281e))

### Refactoring

- 优化 prune_qt.py 路径查找逻辑和日志输出
  ([`1d370af`](https://github.com/bendusy/Any2MD/commit/1d370af77f64ad4c601a184c711634a7f2853048))

- 全面优化代码质量和性能
  ([`ac7bc57`](https://github.com/bendusy/Any2MD/commit/ac7bc57c01fa0dd7541873de241ea5af39220b42))


## v1.5.3 (2026-01-13)

### Bug Fixes

- 同时清理 Frameworks 和 Resources 下的 translations 符号链接
  ([`86de91b`](https://github.com/bendusy/Any2MD/commit/86de91ba5523bf35093a8ec550eb20170ea7302c))


## v1.5.2 (2026-01-13)

### Bug Fixes

- 修复 prune_qt.py 删除 translations 目录后遗留死链接的问题
  ([`11f3864`](https://github.com/bendusy/Any2MD/commit/11f3864befe14fcf5a0729e81abb0765663981ff))


## v1.5.1 (2026-01-13)

### Bug Fixes

- 修复 prune_qt.py 脚本在构建时未正确处理软链接的问题
  ([`ee593f7`](https://github.com/bendusy/Any2MD/commit/ee593f7d5348e60174746313103a52dad10b54d8))

### Code Style

- 修复 Ruff 代码质量问题 (imports, formatting)
  ([`900cdd8`](https://github.com/bendusy/Any2MD/commit/900cdd8aeabb80f9684910c90ca1ed0931699b90))


## v1.5.0 (2026-01-13)

### Features

- 升级GUI至'Morning Light'主题，增强状态反馈与macOS兼容性
  ([`ff79d73`](https://github.com/bendusy/Any2MD/commit/ff79d739b7af9d6b4af8d96cb7785d49daf744d4))


## v1.4.0 (2026-01-13)

### Features

- GUI support selecting files and folders
  ([`64923b9`](https://github.com/bendusy/Any2MD/commit/64923b9da64cca0c836e9e149f05b8b079422a4d))


## v1.3.0 (2026-01-13)

### Features

- Default output on Desktop and merge into single markdown
  ([`56f5039`](https://github.com/bendusy/Any2MD/commit/56f50395048b35b322133cac044ba37427e5be85))


## v1.2.2 (2026-01-13)

### Bug Fixes

- Publish GitHub releases only after successful builds
  ([`b4b061b`](https://github.com/bendusy/Any2MD/commit/b4b061b65b6dad17af0a7f732d8a5537fcb664b9))


## v1.2.1 (2026-01-13)

### Bug Fixes

- Resolve semver tag for workflow_run releases
  ([`0d9ebe5`](https://github.com/bendusy/Any2MD/commit/0d9ebe574a635fb63fabea823de0b1fc9f78a35e))


## v1.2.0 (2026-01-13)

### Features

- Windows fallback via Office/WPS for legacy formats
  ([`1992f82`](https://github.com/bendusy/Any2MD/commit/1992f82ab7a9c8c01a3c870b12237e82b8a6be77))


## v1.1.4 (2026-01-13)

### Bug Fixes

- Allow configuring soffice path for legacy formats
  ([`7717758`](https://github.com/bendusy/Any2MD/commit/77177586bf2beff006048303885424a214ac2a41))


## v1.1.3 (2026-01-13)

### Bug Fixes

- Build releases from semantic-release tags
  ([`5099b8b`](https://github.com/bendusy/Any2MD/commit/5099b8bd87821667849ee72e24c3a1929dc92a88))


## v1.1.2 (2026-01-13)

### Bug Fixes

- Release workflow only for version tags
  ([`0e4c976`](https://github.com/bendusy/Any2MD/commit/0e4c976cb6fd1e6a8452cfc5328ae647a5cb79f8))


## v1.1.1 (2026-01-13)

### Bug Fixes

- Make Qt pruning path robust
  ([`47624c8`](https://github.com/bendusy/Any2MD/commit/47624c8de61187f72e8012df2bdaf051d35bcd5e))


## v1.1.0 (2026-01-13)

### Features

- 支持 doc/ppt/xls 旧格式(需LibreOffice)
  ([`dcac869`](https://github.com/bendusy/Any2MD/commit/dcac869b78326c11e5c44792f9220b145bdea1f9))


## v1.0.5 (2026-01-13)

### Bug Fixes

- 修复 ZIP 中文名与输出目录权限
  ([`1d98f60`](https://github.com/bendusy/Any2MD/commit/1d98f603a3853a7557a088d3ccb94c320784187a))

- 精简 GUI 打包并升级 markitdown
  ([`77ff4cd`](https://github.com/bendusy/Any2MD/commit/77ff4cd7b444fba8db9f2d70241cfcf84a0c728e))

### Chores

- Update uv lockfile
  ([`62bbb66`](https://github.com/bendusy/Any2MD/commit/62bbb664e46ce4f8dedcadee79a41659f725c115))


## v1.0.0 (2026-01-12)

### Continuous Integration

- Setup semantic release
  ([`adecb27`](https://github.com/bendusy/Any2MD/commit/adecb27f18b5f168bd44bdba5c7c86df379c16d0))

### Features

- Trigger automatic release v0.2.0
  ([`c458548`](https://github.com/bendusy/Any2MD/commit/c45854829721820b748accab95435e7a24748db6))


## v0.1.0 (2026-01-12)

- Initial Release
