# 既存VPS環境の標準配置への移行計画（案・未実施）

状態：調査・設計段階。GitHubリポジトリ、VPSの実ファイル、Caddy、systemdには未反映。
関連: https://github.com/Sarajevo001/xo-code-busters/issues/7

## 1. 目的と対象
合意済みの配置規則へ、既存の `Sarajevo001/xo-code-busters` と `Sarajevo001/oop-rpg-workshop` を移行する。公開URLと既存機能を維持し、ソースと実行時データの分離、静的公開範囲、権限を整合させる。

| 対象 | 現在のGit作業ツリー（既存記録） | 目標Git作業ツリー | 永続データ配置 |
|---|---|---|---|
| XO-Code Busters | `/srv/xo-code-busters` | `/srv/GitHub/Sarajevo001/xo-code-busters` | `/var/lib/projects/Sarajevo001/xo-code-busters` |
| RPG教材 | `/home/debian/oop-rpg-workshop` | `/srv/GitHub/Sarajevo001/oop-rpg-workshop` | 必要な場合のみ `/var/lib/projects/Sarajevo001/oop-rpg-workshop` |

RPG教材の旧公開用コピーは `/var/www/demo/oop-rpg-workshop`。これはGit作業ツリーではない。実際のCaddy設定は未取得。ここに記した現状は既存の会話・文書に基づき、移行直前のVPS実測とは区別する。

## 2. 事前確認（読み取り専用）
目的：移行の影響先と現在の正本・参照先を確定する。
- VPSのGit remote、ブランチ、HEAD、未追跡ファイル、実行時データの有無、ファイル所有者・権限
- 稼働中の `/etc/caddy/Caddyfile` と追加設定、Caddyのsystemd設定、公開ルートとURLマッピング
- XO-Code Bustersの `/etc/systemd/system/xo-code-busters.service`、drop-in、実行ユーザー、Node依存ファイル
- HTML/CSS/JSの相対・絶対URL、静的参照先、API、アップロード経路、symlink
- RPG教材の `presentations/` を含む公開範囲、公開コピーにだけあるファイル、除外対象

成功：上記の参照・差分・権限・公開範囲が追跡できる。
失敗：想定外の変更・参照・データ混在を確認。
判定不能：実機・設定・参照先を取得できない。
手順：両プロジェクトの設定とディレクトリを各1回取得し、リポジトリ記録と照合。停止条件：不一致の原因不明、権限不足、稼働中の設定未取得。判定不能時は変更工程へ進まない。

## 3. XO-Code Busters 個別変更案
1. `src/client/` と `src/apps/` の公開コンテンツを `src/public/` に整理する。現行 `src/server/server.js` の `express.static` は `../client` と `../apps` を参照しているため、配信URLを維持するルーティング変更が必要。
2. `src/admin-client/` は管理者認証・DB・API未実装のプロトタイプであり、現時点では公開対象外とする。`src/admin-server/` も管理用の別プロセス（既定127.0.0.1:3001）で、ヘルスチェック以外は503を返す設計。公開サイトの `src/public/` に管理画面を混入させず、将来の認証・認可実装と公開承認まで隔離する。`src/shared/` は用途と参照を確認してから配置を決める。
3. `deploy/systemd/xo-code-busters.service` の `WorkingDirectory` と `ExecStart` を新パスへ変更する。VPS実際のunit・drop-inと差分照合。
4. Caddyの `sarajevo.jp` → `127.0.0.1:3000` リバースプロキシは、必要性がない限り維持。既存公開URL `/`、`/apps/bird-shoot/`、`/apps/drawing/`、`/api/health` 等は変更前に実際の有効ルートを列挙する。`/game/` は廃止済みの旧URLであり、移行後の互換性維持・リダイレクト対象としない。
5. Git更新ユーザーは作業ツリーを書き込める必要がある一方、Caddy/ExpressはGit作業ツリーを書き込めないよう所有者・グループ・ACL・サービスの制限を設計する。Nodeの依存ファイル更新手順を確認する。

## 4. RPG教材 個別変更案
1. `index.html`、`examples/` はVPSの現行Git作業ツリーと公開コピーで存在確認済み。`presentations/` は2026-11-11のVPS実測ではGit追跡一覧にも公開コピー一覧にも現れなかったため、GitHub側の別リビジョンとの相違を確認するまで存在を前提にしない。`index.html` には `presentations/chapter0/` から `chapter4/` および `summary/` へのリンクが実装されているため、これらを公開対象に含めて `src/public/` へ移動する。 `archive/`、`docs/`、`ci/`、`tests/`、`.github/` 等は公開しない。
2. `https://demo.sarajevo.jp/oop-rpg-workshop/` のURLを維持するよう、実際のCaddyのhandle/path処理を確認してから公開ルートを変更する。既存 `/var/www/demo/oop-rpg-workshop` の配信コピーは、新方式の確認完了まで削除しない。
3. `presentations/` は以前確認したGitHub上の `index.html` にリンクが存在するが、2026-11-11のVPS実測ではディレクトリが確認されなかった。VPSのHEADとGitHub `main` の差分、実際の `index.html` のリンク、公開URLの応答を照合し、存在する場合のみ公開対象に追加する。
4. `verify_handoffs.py`、CI、リンク・パス参照を更新する。テストはルート `tests/` を維持する。

## 5. 切替の共通順序（案）
1. 規約改訂・適用版・対象コミットを確定。
2. 事前調査、既存URL/HTTP応答の記録、Git/設定/永続データのバックアップ取得と復旧可能性確認。
3. 作業ブランチで構成変更・テスト修正を作成し、CIと公開URL互換性を検証。
4. VPS上に新しいGit作業ツリーと必要な永続データ領域を用意し、所有権・アクセス制限を設定。旧作業ツリーは保持。
5. RPG教材の静的公開先を切替・検証。独立性が確認できればXO-Code Bustersのsystemd・Express参照先を切替。
6. 検証結果を記録。旧領域の削除は別途判断し、同一作業では行わない。

## 6. 検証・停止・切り戻し
目的：新配置で旧機能と公開URLを維持し、非公開領域を外部から取得できず、Web実行ユーザーがGit領域を書けないことを確認する。
- 成功：各プロジェクトの事前記録したURLが同じ機能を提供し、API正常系・主要画面操作が成功。公開対象外のファイルは取得不可。実行ユーザーのGit領域書込が拒否され、必要な `/var/lib/projects/...` への書込は成功。永続データの欠損なし。
- 失敗：主要URL/API/画面が動かない、意図しない公開・書込、データ欠損、想定外の変更。
- 判定不能：VPS状態、公開レスポンス、権限、データ完全性のいずれかが確認不能。
- 手順・比較：移行前後で同一のURL・API・主要画面を各1回以上照合。非公開パスと書込拒否は代表ケースを各1回以上実施し、条件・実測値を記録。異常があれば後続作業を停止。
- 切り戻し：切替前に保存したCaddy/unit設定と旧Git作業ツリーへの参照に戻し、旧URL/APIを再検証。永続データの破壊的巻戻しは行わず、更新が発生した場合は整合性を個別評価する。

## 7. 未確定事項
- VPS実機のCaddy全体設定・RPG教材の配信方法、現在の実行時データの有無
- XO-Code Bustersの `src/shared/` の参照関係、管理画面の将来配置（現時点では公開しない）
- RPG教材 `presentations/` の現行VPS配信状況（公開対象に含める方針はコードから確認済み）
- デプロイ主体とCaddy/ExpressのLinuxユーザー・ACLの具体値
- 変更作業の日程・他作業との順序、復旧可能なバックアップの取得方法
- GitHub Actionsによるデプロイ自動化の導入時期。今回の配置移行と同時実施を前提としない

未確定事項を推測で埋めて本番切替を行わない。

## 8. 追加調査の根拠（GitHub現行main）
- `xo-code-busters/src/admin-client/README.md`：管理者画面はブラウザメモリ上の仮データのみ。管理者認証、DB、API通信、パスワード保存なし。公開環境で使わないと明記。
- `xo-code-busters/src/admin-server/README.md` および `server.js`：別プロセス、既定ポート3001、管理API非公開。ヘルスチェック以外503。
- `oop-rpg-workshop/index.html`：講義スライド6件への相対リンクを確認。
- 上記はリポジトリ上の設計・コードに関する確認であり、稼働VPSの現況確認ではない。

## 9. 2026-11-11 VPS読み取り専用調査の実測結果
- ユーザーによるVPS上での実行。Caddyと `xo-code-busters` は共に active / enabled。
- 現行Git作業ツリーはXO `/srv/xo-code-busters`（main、HEAD `b6521dbeee0e5627628b1c8f96150b5412904b3c`）、RPG `/home/debian/oop-rpg-workshop`（main、HEAD `0c5182d0160636d8872ceaf953929f79576d42a5`）。両者とも追跡対象の変更なし、未追跡ファイルなし。
- RPG公開コピー `/var/www/demo/oop-rpg-workshop` が存在。Caddy設定には `reverse_proxy 127.0.0.1:3000` と `root * /var/www/demo` の参照あり。全設定内容と公開コピーの差分は未確認。
- 移行先 `/srv/GitHub/Sarajevo001/{xo-code-busters,oop-rpg-workshop}` は未作成。永続データ領域 `/var/lib/projects/Sarajevo001/...` も未作成。
- 公開HTTP: `https://sarajevo.jp/` 200、`https://sarajevo.jp/api/health` 200、`https://demo.sarajevo.jp/oop-rpg-workshop/` 200。ローカルExpress: `/apps/bird-shoot/` 200、`/apps/drawing/` 200、`/game/` 404。公開 `/game/` も404。
- **ユーザー確定判断**：`/game/` は旧設定であり不要。復旧やリダイレクトは行わず、現行アプリのURLを移行前後の比較対象とする。
- HTTP 200は取得成功を示すだけで、画面操作・リンク先・公開権限の正常性を保証しない。VPS切替前にCaddy全設定、RPGの公開コピーとGitの差分、ファイル参照、バックアップ・復旧手順を確認する。
- この調査でVPSの設定変更・サービス再起動・ディレクトリ移動は行っていない。

## 10. 2026-11-11 RPG公開コピー・Caddy設定の実測
- VPS `/etc/caddy/Caddyfile` は `sarajevo.jp { reverse_proxy 127.0.0.1:3000 }` と `demo.sarajevo.jp { root * /var/www/demo; file_server }` の2サイト。RPGの公開URL `/oop-rpg-workshop/` は `/var/www/demo/oop-rpg-workshop` に対応する。
- VPSのGit作業ツリー `/home/debian/oop-rpg-workshop` は `git status --short` 出力なし。`git ls-files index.html examples presentations` では `index.html` と `examples/` のみ確認され、`presentations/` は出力されなかった。
- 公開コピーの通常ファイル一覧は `index.html` と `examples/` 以下のみ。`diff -qr`（`.git`除外）はGit側にのみ `README.md`、`archive/`、`docs/` があると報告し、共通ファイルの内容差は報告しなかった。
- **保留事項**：過去のGitHub調査では `presentations/` へのリンクを確認していたため、GitHub `main` とVPSのHEADの差分、VPSの `index.html` のリンク、公開URLを追加照合する。現時点で `presentations/` を実機に存在するものとして扱わない。
- `diff -qr` の比較結果は通常ファイルの差分確認であり、シンボリックリンク・HTTP配信可否・画面操作・非公開領域の検証は別途必要。
- 本調査は読み取り専用であり、VPS側のファイル・設定は変更していない。

## 11. 2026-11-11 VPSとGitHub mainのリビジョン相違
- VPS RPGの `git rev-parse HEAD` は `0c5182d0160636d8872ceaf953929f79576d42a5`。`git ls-remote origin refs/heads/main` は `git@github.com: Permission denied (publickey)` で失敗。SSH認証問題はデプロイ前の別途対処事項であり、公開サイト障害とは同一視しない。
- VPSの `index.html` は `examples/` のみ参照し、`presentations/` は存在しない。
- GitHub連携による直接参照ではRPG `main` のHEADは `f00c2fdce12db17c224273b513483be7107342b4`、`presentations/` ディレクトリが存在。**VPSとGitHubのリビジョンが異なることが確定**。追加された時点と全変更内容は未調査。
- GitHub最新版を本番へ自動反映せず、差分と公開URLを評価してからデプロイ対象を決める。
