# XO-Code Busters 開発ロードマップ

最終更新：2026-11-14

## 1. 目的

本資料は、XO-Code Busters の目的、決定事項、実装済みの範囲、および次の開発対象を短時間で確認するための概要資料です。詳細な仕様や過去の変更経緯は、それぞれ設計資料および [変更履歴](roadmap-changelog.md) で管理します。

## 2. 現在のフェーズ

**Web公開基盤・複数アプリ配信は完了。ユーザー管理画面モックアップの検証・完成判定は一時保留し、現在は複数プロジェクトで参照・適用する共通規約・言語別コーディング規約の整備を優先する。**

計画変更の経緯：プレゼン工房でソースコードを実装する過程で、プロジェクトを横断して利用できるコーディング規約の必要性を認識したため、従来の計画に規約整備工程を意図的に追加した。規約整備後はプレゼン工房の作業を再開・完了させ、その後にXO-Code Bustersのアプリケーション開発へ戻る。

規約整備の実績：標準管理規程1.1.0、標準管理運用仕様1.1.0、共通システム開発標準1.0.0は正本に反映済み（CHG-000002、CHG-000003）。具体的な言語別コーディング規約の制定、および複数プロジェクトからの参照・適用の整備は今後の作業であり、完了扱いにしない。

完了事項：

- Node.js 標準 `http` での基本通信検証から、Express への移行
- GET `/api/health`、POST `/api/hello` の Express 化
- Client と API の同一 Origin 化、API 呼び出しの相対 URL 化
- Caddy の Reverse Proxy、独自ドメイン `sarajevo.jp` での HTTPS 公開
- systemd による Express プロセスの常駐化
- `src/public`（メイン画面・個別アプリ）の分離、Express からの静的配信
- サンプルゲームおよび P2P お絵描きアプリの組み込み・公開

2026-10-21の追加実績：一般ユーザー向けのログイン・登録・設定モック、管理者向けのログイン・ユーザー一覧・登録・編集モック、共通ライブラリと独立管理者サーバーの骨組みをGitHubへ登録。**ブラウザでの動作確認・画面レビューは未実施**。本物の認証・認可・DB処理は未実装です。

2026-11-14の公開再確認：XOトップページ、Bird Shootのゲーム進行、Drawingの描画、APIヘルスチェックを確認。Drawingの端末間P2P接続、全機能・全端末の動作は未検証。

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
       ├─ /apps/* → src/public/apps
       └─ その他の静的ファイル → src/public
```

公開ドメイン：<https://sarajevo.jp>

次段階の設計：管理者向けは `admin.sarajevo.jp`、独立Express `127.0.0.1:3001` を予定。ソース骨組みとsystemd/Caddyドラフトのみで、**管理者サイトは未公開**。DBはPostgreSQLを候補として論理分離し、将来の物理分離に対応する。

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
    ├── public/   # 静的公開対象（メイン画面、apps/以下の個別アプリ）
    ├── client/   # 旧一般ユーザーモック（静的公開対象外）
    ├── server/        # 既存一般ユーザー Express / API
    ├── admin-client/  # 管理者画面モック
    ├── admin-server/  # 管理者 Express 骨組み（未公開）
    └── shared/        # サーバー側共通ライブラリ骨組み
```

個別アプリは `src/public/apps` に配置し、公開対象を `src/public` に集約しています。

## 7. 公開・セキュリティ方針

既存一般ユーザーExpressの静的配信対象は、`src/public` に限定します。`src/client/mock.html` は非公開の試作ファイルであり、現在のExpress静的配信対象外です。認証・アクセス制御を提供しません。管理者Expressは `/api/health` 以外をHTTP 503とし、管理画面を配信しません。`src/server`、`docs`、`.git`、秘密情報等は直接公開しません。ユーザー入力をファイルパスとして無制限に利用しない等の基本方針を維持し、詳細なセキュリティ設計は機能要件に応じて定義します。

## 8. 実績と根拠

- 2026-09-20：サンプルゲーム追加（[commit](https://github.com/Sarajevo001/xo-code-busters/commit/97900a7471f9acd4a8188530cda0d9c698783e44)）
- 2026-10-11：Express 化、同一 Origin 化（[merge commit](https://github.com/Sarajevo001/xo-code-busters/commit/2075acf71c2808dafee7749f5cbf178491d3ee49)）
- 2026-10-17：Caddy 設定、systemd サービス、運用手順（[Caddy](https://github.com/Sarajevo001/xo-code-busters/commit/8daca75bbf872038d044db43b5e96bd87045c8eb)、[systemd](https://github.com/Sarajevo001/xo-code-busters/commit/9ba049f2324b2ece08a4be5499bb21d7b6708141)、[運用手順](https://github.com/Sarajevo001/xo-code-busters/commit/f7d63b281be8ed2a181363425cc9dc9410551389)）
- 2026-10-18：複数アプリ対応の再編、お絵描きアプリ追加（[commit](https://github.com/Sarajevo001/xo-code-busters/commit/f5f6871e224b60e238b5a572bbe1fc0ef17dfdbe)）
- 2026-10-21：ユーザー・管理者の画面モック追加（[一般ユーザー](https://github.com/Sarajevo001/xo-code-busters/commit/b6521dbeee0e5627628b1c8f96150b5412904b3c)、[管理者](https://github.com/Sarajevo001/xo-code-busters/commit/2f21db688728b683bf171d23de4e2b3bd11d89c9)）。管理者サーバー・共通ライブラリの骨組み追加（未公開）。

## 9. 次にやること

確定した作業順序：

1. 複数プロジェクトから参照・適用できる共通規約及び必要な言語別コーディング規約を整備する。既に制定済みの管理規程・運用仕様・共通システム開発標準と、未整備の言語別規約・参照適用手段を区別する。対象言語、具体的な範囲、完了条件は作業内で確定する。
2. 整備した規約を参照・適用してプレゼン工房の開発を再開し、完成させる。プレゼン工房の完成条件は別途確認する。
3. プレゼン工房の完成後、XO-Code Bustersのアプリケーション開発へ戻る。保留中のユーザー管理画面モックアップの実機検証・画面レビュー・完成判定を含む残作業を再確認する。

ユーザー管理画面モックアップは中止ではなく一時保留とする。再開時期の具体的な日付は未定。完了済みのExpress移行・Web公開作業は未完了タスクとして再掲しない。

長期候補：設定・メンテナンス画面、PostgreSQL、認証・認可、商品・購入・決済・権利付与、ゲーム連携。これらの内部の実装順序は未確定。

## 10. 関連資料

- [ロードマップ変更履歴](roadmap-changelog.md)
- `docs/operation/` 以下の運用資料
- [ユーザー管理画面仕様](../specification/user-management-screens.md)
- [ユーザー管理システム構成](../specification/user-management-architecture.md)
- [設計判断記録](../decisions/user-management-architecture-2026-10-21.md)
- 今後作成するプレゼン資料
