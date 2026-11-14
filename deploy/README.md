# 手動ワンコマンドデプロイ（XO-Code Busters）

VPS上で `debian` 等のGit作業ツリー所有ユーザーとして実行：

```bash
bash /srv/GitHub/Sarajevo001/xo-code-busters/deploy/deploy-xo.sh
```

**GitHubに登録しただけではVPSに反映されません。** 初回は既存の手動手順でスクリプトを取得する必要があります。直近のGitHub更新にはsystemd定義の変更も含まれるため、VPS実機の定義との照合と必要な設定反映を先に実施してください。

## 動作

- `flock` で二重起動を防止。作業ツリーの汚れ、ブランチ、origin、Fast-Forward可能性を検査。
- `deploy/caddy/` と `deploy/systemd/` に変更がある場合、Git更新前に停止。インフラ設定は自動適用しない。
- `src/server/package*.json` 変更時は `npm ci --omit=dev`、`src/server/` または `src/shared/` 変更時はサービスを再起動。
- ローカル `/api/health` のHTTP 200および `status=ok` を確認。
- 更新後のエラー時は元のコミットへ戻し、依存関係とサービスの復旧を試行する。ただし復旧の成功は保証しない。

## 前提と制約

- `git`、`npm`、`curl`、`flock`、`sudo` が利用できる。
- Git更新権限と、`sudo -n systemctl restart xo-code-busters.service` の実行権限が必要。実機で未確認。
- 実行時点の `origin/main` 最新コミットを対象とする。指定SHAの選択・承認ゲートは未実装。
- ログは標準出力に表示。独立した永続デプロイ履歴は未実装。
- Caddy、systemd、DB移行、外部HTTPS、UI、P2Pの自動検証は対象外。

## 検証と停止条件

目的：意図した更新と異常時停止を確認する。成功：対象SHA一致、ローカルAPI正常。失敗：異常でも処理が進む、またはヘルスチェック異常。判定不能：VPSの権限・実設定・通信条件が未確認。

手順：①シェル構文確認 ②VPS実設定・権限確認 ③復旧可能な状態の保全 ④試験デプロイ1回 ⑤必要なら切り戻し確認。各段階で失敗・判定不能なら次へ進まない。

**現時点でVPS実行・復旧試験は未実施。**
