# 講座共通デプロイ（静的公開 v1）

通常運用は `bash deploy/deploy.sh`。以下の個別コマンドは計画・プレビュー・検証用であり、実適用は末尾の現行手順を参照する。

## 範囲
`deploy/deploy_projects.py` はXO側の `projects.json` と各講座の `deploy.json` を検証し、公開計画をJSONで出力する。オプションで既存Gitチェックアウトを検証済みのGitHub mainへ同期し、Caddy設定の**プレビュー**を出力する。

## 実行
```bash
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub --update
python3 deploy/deploy_projects.py --checkout-root /srv/GitHub --caddy-preview /tmp/xo-projects.preview.caddy
python3 -m unittest discover -s deploy -p 'test_deploy_projects.py' -v
```

- `deploy/projects.json` には現在RPG講座が登録されている。空の登録一覧を講座の公開成功とみなさない。
- `--update` は**明示指定時のみ**既存のmainブランチを検証済みのGitHub mainへ同期する。新規cloneはしない。Gitリモートは指定したGitHubリポジトリと一致する必要がある。2026-11-19の承認済み方針により、HEADが異なる場合はGit管理対象をreset --hardで更新する。未追跡ファイルの一括削除は行わないが、更新対象と衝突するファイルの保存は保証しない。HEAD一致時の作業ツリーの一致は別途確認する。
- `--update` で複数のリポジトリを更新する場合、全体の原子的なロールバックは保証しない。更新失敗時は手動で状況を確認する。
- Caddy設定はプレビューのみ。稼働中の `/etc/caddy/Caddyfile` は上書きしない。Caddyの再起動・reloadもしない。
- URLのルート `/` はプレビュー生成対象外。既存XOサイトとの衝突を避けるため第4工程で統合設計する。
- 現状の `handle_path` はURLプレフィックスを取り除く。絶対URLに依存するコンテンツやCaddyの既存ルーティングとの整合は第4工程で確認する。
- `node` と `php` は将来案であり未対応。
- 実適用の現行方式は末尾を参照。旧コピー先の撤去実績は別途確認する。

## 判定条件
- 単体テスト成功：ローカルの正常系と異常系の期待結果が一致。
- 失敗：不正な入力が通る、または正常な入力が拒否される。
- 判定不能：テスト実行環境・結果が確認できない。
- VPSでの公開成功：この単体テストでは判定しない。

## demo.sarajevo.jp の玄関ページ（2026-11-26）
現行の共通デプロイは `bash deploy/deploy.sh`。この手順は自分自身をmainに同期し、登録講座を更新し、`apply_caddy.py` で構文検証・バックアップ・適用・reloadを行う。上記のプレビューは登録講座の経路のみを出力し、玄関ページは実適用用の生成処理が担当する。
RPG講座が demo.sarajevo.jp の /oop-rpg-workshop/ に登録されている場合に、完全一致の / のみをXO側の src/public/demo-portal/index.html に割り当てる。登録講座の接頭辞、sarajevo.jp のリバースプロキシ、その他ホストを変更しない。登録されていないパスを玄関の静的ルートとして公開しない。公開後は /、RPG講座への遷移、旧経路、非公開パスの拒否、XO本体の /api/health を確認し、不一致時は追加作業を停止して既存バックアップでの復旧を判断する。

初回CIでは玄関ページの追加検査は合格したが、旧方式のdirty checkout拒否を期待する既存テストが失敗した。2026-11-19に変更済みの実装（1504cc021bba53b14a7bb4c9581a5785f59e3071）および承認済み同期方針に合わせて、更新時の追跡対象の置換・非衝突の未追跡ファイルの維持・不正な取得先リビジョンでの停止を検証するようテストを修正した。デプロイの同期処理自体は変更していない。

## 2026-11-27 工程完了判定
静的公開v1の通常運用機構は完成とし、追加の実機再確認は今回の工程では要求しない。根拠：main `30ae57aa8cd30f2150c73e7aa31da36f55d2734f` のCI成功（run 45832165655、29テスト）、RPG側 `edbe0f8a358f05f3a9f375b3c84e8978ca793bc1` の docs/materials_audit.md に記録された11月26日のCaddy構文検証・適用成功と玄関・講座トップ・看板の表示・遷移確認。非公開パスの実HTTP検査、全公開ファイル一致、旧コピー先の撤去、実復旧試験は確認済みとはしない。C-1005の適合判定は証跡不足のため未確定であり、今回の運用機構の完成判定は規約適合全体の合格を意味しない。動的公開とExpress更新は別範囲。
