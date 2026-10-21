# XO-Code Busters ロードマップ変更履歴

本資料は `roadmap.md` の重要な変更を開発上の節目単位で記録します。ソースコードの全コミットを転載するものではありません。

## 2026-10-21：ユーザー管理モックアップと構成設計

| 変更対象 | 変更前 | 変更後 | 理由・影響 |
|---|---|---|---|
| 開発フェーズ | Web公開・複数アプリ対応完了 | ユーザー管理画面モックの実装・検証段階 | 今回の作業範囲を明確化 |
| 一般ユーザー画面 | 既存トップと個別アプリ | 別ファイル `mock.html` にログイン・登録・設定等の試作画面 | 既存公開トップを維持して画面確認 |
| 管理者画面 | なし | 仮ログイン、一覧・検索、詳細、登録、編集・停止等のモック | 管理者操作を仮データで検証 |
| サーバー構成 | 一般ユーザーExpressのみ | 独立管理者Express（3001）骨組み、共通ライブラリ `src/shared` | 将来のサービス分離に備える |
| 管理者公開 | 未設定 | `admin.sarajevo.jp` を設計上決定。公開設定はドラフトのみ | 認証未実装のため非公開を維持 |
| 次工程 | 詳細未確定 | モックの実機検証、画面レビュー、完成判定 | 本実装の認証・DBと切り分け |

詳細：[画面仕様](../specification/user-management-screens.md)、[構成設計](../specification/user-management-architecture.md)、[設計判断](../decisions/user-management-architecture-2026-10-21.md)。

## 2026-10-19：2026-09-21版からの改訂

| 変更対象 | 変更前 | 変更後 | 理由・影響 | 根拠 |
|---|---|---|---|---|
| 現在のフェーズ | Node.js標準HTTPでの基本通信確認完了、Express移行準備 | Express移行、Web公開、複数アプリ配信対応まで完了 | 現在地を実装実績に一致させる | [Express移行](https://github.com/Sarajevo001/xo-code-busters/commit/2075acf71c2808dafee7749f5cbf178491d3ee49)、[アプリ再編](https://github.com/Sarajevo001/xo-code-busters/commit/f5f6871e224b60e238b5a572bbe1fc0ef17dfdbe) |
| API・静的配信 | Node.js標準http、別Origin、CORS対応 | Express、同一Origin、`src/client` 静的配信 | 接続先切替や独自のHTTP処理を簡素化 | [Express移行](https://github.com/Sarajevo001/xo-code-busters/commit/dfd62baff77cd63b4a242896dde975753935dae1)、[相対URL](https://github.com/Sarajevo001/xo-code-busters/commit/db27e84453643e3fe0dc813e42f8a66bccd2102d) |
| 公開構成 | Caddyは第一候補、HTTPSは予定 | Caddy / HTTPS / systemd による公開運用 | 公開基盤の整備完了を反映 | [Caddy](https://github.com/Sarajevo001/xo-code-busters/commit/8daca75bbf872038d044db43b5e96bd87045c8eb)、[systemd](https://github.com/Sarajevo001/xo-code-busters/commit/9ba049f2324b2ece08a4be5499bb21d7b6708141) |
| リポジトリ構成 | `src/client` と `src/server` を中心とする構成 | `src/apps` を追加し、メイン画面と個別アプリを分離 | 複数アプリを追加できるようにする | [再編・お絵描き追加](https://github.com/Sarajevo001/xo-code-busters/commit/f5f6871e224b60e238b5a572bbe1fc0ef17dfdbe) |
| 公開対象 | 静的配信は `src/client` のみ | `src/client` および `src/apps` | 個別アプリ公開に対応。非公開領域の制限方針は維持 | [再編・お絵描き追加](https://github.com/Sarajevo001/xo-code-busters/commit/f5f6871e224b60e238b5a572bbe1fc0ef17dfdbe) |
| アプリ実績 | ロードマップ上のアプリ実績の記述が不足 | サンプルゲームとP2Pお絵描きアプリを記載 | 実際に公開している成果物を反映 | [ゲーム](https://github.com/Sarajevo001/xo-code-busters/commit/97900a7471f9acd4a8188530cda0d9c698783e44)、[お絵描き](https://github.com/Sarajevo001/xo-code-busters/commit/f5f6871e224b60e238b5a572bbe1fc0ef17dfdbe) |
| 次にやること | Express移行、Caddy、HTTPS等が未完了として列挙 | 完了事項を除外。次フェーズ詳細は別途確定 | 完了タスクの重複管理を避ける | 上記コミット群 |

### 変更の方針

- `roadmap.md` は「現時点の正しい状態」を記載する。
- 過去の状態と改訂理由は本変更履歴に残す。
- 未確定の次フェーズ内容は推測で補わない。
- P2Pお絵描きアプリの設計レビューと未実施の改修は、今回の完了実績には含めない。
