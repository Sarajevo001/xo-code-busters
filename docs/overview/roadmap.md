# XO-Code Busters 開発ロードマップ

最終更新：2026-10-21

## 1. 目的

本資料は、XO-Code Busters の目的、決定事項、実装済みの範囲、および次の開発対象を短時間で確認するための概要資料です。詳細な仕様や過去の変更経緯は、それぞれ設計資料および [変更履歴](roadmap-changelog.md) で管理します。

## 2. 現在のフェーズ

**Web公開基盤・複数アプリ配信は完了。現在はユーザー管理の画面モックアップ開発・検証フェーズ。**

完了事項：

- Node.js 標準 `http` での基本通信検証から、Express への移行
- GET `/api/health`、POST `/api/hello` の Express 化
- Client と API の同一 Origin 化、API 呼び出しの相対 URL 化
- Caddy の Reverse Proxy、独自ドメイン `sarajevo.jp` での HTTPS 公開
- systemd による Express プロセスの常駐化
- `src/client`（メイン画面）と `src/apps`（個別アプリ）の分離、Express からの静的配信
- サンプルゲームおよび P2P お絵描きアプリの組み込み・公開

今回の追加実績：一般ユーザー向けのログイン・登録・設定モック、管理者向けのログイン・ユーザー一覧・登録・編集モック、共通ライブラリと独立管理者サーバーの骨組みをGitHubへ登録。**ブラウザでの動作確認・画面レビューは未実施**。本物の認証・認可・DB処理は未実装です。

## 3. 目指すシステム

Web アプリケーションとして設定画面、メンテナンス画面、認証・認可、データ永続化等を段階的に実装します。ゲームはゲーム開発技術の習得自体を目的とするのではなく、実際に操作できるショーケースとして位置付けます。

将来的には、次のユースケースを想定します。

```text
ゲームを遊ぶ → 欲しいものが生まれる → 購入・決済 → 権利付与 → ゲームへ反映
```

認証、ユーザー管理、商品管理、購入、決済、権利管理、ゲーム等を一つのシステムで連携させます。実課金を必須とせず、仮想決済も選択肢とします。

## 4. 開発・公開構成

開発環境は Ubuntu / VS Code。GitHub をソースコードとドキュメントの正本とし、VPS 側では原則直接編集しません。

```text
Ubuntu 開発環境
   ↓ Git commit / push
GitHub
   ↓ VPS 側で git pull、サービス再起動等
KAGOYA VPS（Debian）
   ├─ Caddy（HTTPS / Reverse Proxy）
   └─ Express（127.0.0.1:3000、systemd 管理）
       ├─ /api/health、/api/hello
       ├─ /apps/* → src/apps
       └─ その他の静的ファイル → src/client
```

公開ドメイン：<https://sarajevo.jp>\n\n次段階の設計：管理者向けは `admin.sarajevo.jp`、独立Express `127.0.0.1:3001` を予定。ソース骨組みとsystemd/Caddyドラフトのみで、**管理者サイトは未公開**。DBはPostgreSQLを候補として論理分離し、将来の物理分離に対応する。

GitHub への push だけで自動デプロイされる構成とはしていません。

## 5. 採用技術・今後の候補

| 分野 | 現在の採用・確認済み | 将来の検討対象 |
|---|---|---|
| フロントエンド | HTML、CSS、Vanilla JavaScript | TypeScript 等（必要性に応じて） |
| Web API | Node.js、Express | API・機能拡張 |
| インフラ | Debian、KAGOYA VPS、Caddy、HTTPS、systemd | 運用改善 |
| データ | 現段階で永続化基盤の採用完了は未確認 | PostgreSQL |
| 認証・認可 | 方式未確定 | OAuth 2.0、OpenID Connect 等 |
| ゲーム・アプリ | サンプルゲーム、P2P お絵描きアプリ | ゲームと業務機能の連携 |

技術選定は、必要性と責務を確認してから行います。既に知っている技術を、実装を通じて順に確認する方針です。

## 6. 現在のリポジトリ構成（概略）

```text
xo-code-busters/
├── docs/
│   ├── overview/
│   │   ├── roadmap.md
│   │   └── roadmap-changelog.md
│   └── ...
└── src/
    ├── client/   # メイン画面
    ├── apps/     # 個別アプリ
    ├── server/        # 既存一般ユーザー Express / API\n    ├── admin-client/  # 管理者画面モック\n    ├── admin-server/  # 管理者 Express 骨組み（未公開）\n    └── shared/        # サーバー側共通ライブラリ骨組み
```

アプリの増加に対応するため `src/apps` を設け、メイン画面と個別アプリを分離しました。

## 7. 公開・セキュリティ方針

既存一般ユーザーExpressの静的配信対象は、公開を意図した `src/client` と `src/apps` に限定します。`src/client/mock.html` はこの配信対象に含まれ得る試作画面であり、認証・アクセス制御を提供しません。管理者Expressは `/api/health` 以外をHTTP 503とし、管理画面を配信しません。`src/server`、`docs`、`.git`、秘密情報等は直接公開しません。ユーザー入力をファイルパスとして無制限に利用しない等の基本方針を維持し、詳細なセキュリティ設計は機能要件に応じて定義します。

## 8. 実績と根拠

- 2026-09-20：サンプルゲーム追加（[commit](https://github.com/Sarajevo001/xo-code-busters/commit/97900a7471f9acd4a8188530cda0d9c698783e44)）
- 2026-10-11：Express 化、同一 Origin 化（[merge commit](https://github.com/Sarajevo001/xo-code-busters/commit/2075acf71c2808dafee7749f5cbf178491d3ee49)）
- 2026-10-17：Caddy 設定、systemd サービス、運用手順（[Caddy](https://github.com/Sarajevo001/xo-code-busters/commit/8daca75bbf872038d044db43b5e96bd87045c8eb)、[systemd](https://github.com/Sarajevo001/xo-code-busters/commit/9ba049f2324b2ece08a4be5499bb21d7b6708141)、[運用手順](https://github.com/Sarajevo001/xo-code-busters/commit/f7d63b281be8ed2a181363425cc9dc9410551389)）
- 2026-10-18：複数アプリ対応の再編、お絵描きアプリ追加（[commit](https://github.com/Sarajevo001/xo-code-busters/commit/f5f6871e224b60e238b5a572bbe1fc0ef17dfdbe)）\n- 2026-10-21：ユーザー・管理者の画面モック追加（[一般ユーザー](https://github.com/Sarajevo001/xo-code-busters/commit/b6521dbeee0e5627628b1c8f96150b5412904b3c)、[管理者](https://github.com/Sarajevo001/xo-code-busters/commit/2f21db688728b683bf171d23de4e2b3bd11d89c9)）。管理者サーバー・共通ライブラリの骨組み追加（未公開）。

## 9. 次にやること

次の開発フェーズの内容が確定次第、目的、範囲、完了条件をここに記載します。現時点では、完了した Express 移行・Web 公開作業を未完了タスクとして再掲しません。

長期候補：設定・メンテナンス画面、PostgreSQL、認証・認可、商品・購入・決済・権利付与、ゲーム連携。順序は未確定です。

## 10. 関連資料

- [ロードマップ変更履歴](roadmap-changelog.md)
- `docs/operation/` 以下の運用資料
- [ユーザー管理画面仕様](../specification/user-management-screens.md)\n- [ユーザー管理システム構成](../specification/user-management-architecture.md)\n- [設計判断記録](../decisions/user-management-architecture-2026-10-21.md)\n- 今後作成するプレゼン資料
