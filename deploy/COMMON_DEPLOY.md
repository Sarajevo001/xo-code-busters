# 講座共通デプロイ準備（静的公開 v1）

## 範囲
`deploy/deploy_projects.py` はXO側の `projects.json` と各講座の `deploy.json` を検証し、公開計画をJSONで出力する。オプションで既存Gitチェックアウトのmainをfast-forward更新し、Caddy設定の**プレビュー**を出力する。

## 実行
```bash
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub --update
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub --caddy-preview /tmp/xo-projects.preview.caddy
python3 -m unittest discover -s deploy -p 'test_deploy_projects.py' -v
```

- 初期状態の `deploy/projects.json` は空。これを公開成功とみなさない。
- `--update` は**明示指定時のみ**既存のcleanなmainブランチをfast-forwardする。新規cloneはしない。Gitリモートは指定したGitHubリポジトリと一致する必要がある。
- `--update` で複数のリポジトリを更新する場合、全体の原子的なロールバックは保証しない。更新失敗時は手動で状況を確認する。
- Caddy設定はプレビューのみ。稼働中の `/etc/caddy/Caddyfile` は上書きしない。Caddyの再起動・reloadもしない。
- URLのルート `/` はプレビュー生成対象外。既存XOサイトとの衝突を避けるため第4工程で統合設計する。
- 現状の `handle_path` はURLプレフィックスを取り除く。絶対URLに依存するコンテンツやCaddyの既存ルーティングとの整合は第4工程で確認する。
- `node` と `php` は将来案であり未対応。
- 実際の公開先・既存Caddy設定・RPG移行は第4工程の対象。

## 判定条件
- 単体テスト成功：ローカルの正常系と異常系の期待結果が一致。
- 失敗：不正な入力が通る、または正常な入力が拒否される。
- 判定不能：テスト実行環境・結果が確認できない。
- VPSでの公開成功：この単体テストでは判定しない。
