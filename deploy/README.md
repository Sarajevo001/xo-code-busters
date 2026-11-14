# XO-Code Busters: ワンコマンドデプロイ

## 初回も2回目以降も同じ1コマンド

VPSに通常のデプロイユーザー（Git作業ツリー所有者、通常は debian）でSSHログインし、以下を**1行だけ**実行する。

```bash
bash -c 'f=$(mktemp); curl -fsSL https://raw.githubusercontent.com/Sarajevo001/xo-code-busters/main/deploy/deploy-xo.sh -o "$f" && bash "$f"; rc=$?; rm -f "$f"; exit "$rc"'
```

GitHub上の最新のスクリプトを一時ファイルに取得するため、初回に手動で git pull する必要はない。実行するスクリプトの取得先は公開GitHubの main ブランチ。**実行前に信頼するリポジトリと変更内容を確認すること**。厳密にスクリプト版を固定したい場合はコミットSHAをURLに指定する。

## スクリプトの処理

1. Git作業ツリーが clean/main で、origin が所定のGitHubリポジトリか検査。flock で二重実行防止。
2. GitHubの main を fetch。Fast-Forwardできない場合は停止。
3. Caddy定義に変更があれば停止。systemd定義はGitHubの対象コミットとVPSの実ファイルを比較し、違いがあれば検証してバックアップ後に反映。
4. サーバー依存関係の変更時に npm ci --omit=dev。
5. systemd daemon-reload（ユニット変更時）、Express再起動。
6. ローカルAPIの応答を確認。異常時は元のGitコミットとユニットの復旧を試行。

sudoは必要に応じてパスワード入力する。rootとしてスクリプトを実行しない。Git作業ツリーにローカル変更がある場合は勝手に破棄せず停止する。

## 検証の目的・判断条件

**目的**：初回も通常更新も1コマンドで安全に反映できるか検証する。

- 成功：対象コミットの反映、systemd設定の整合、ローカルAPIがHTTP 200かつ status=ok。
- 失敗：異常を検出できない、更新できない、APIが異常、または切り戻し不能。
- 判定不能：実機設定・権限・通信のため観測できない。

**実施順序**：①静的構文検査 ②初回実機試験1回 ③通常更新試験1回 ④異常時復旧試験1回。失敗・判定不能時は以降の試験を停止し、原因を確認する。

**未検証**：VPSでの実行、sudo権限、ロールバックの実効性、公開HTTPS、ブラウザ・P2P、DB移行。システム設定の差分を自動反映するため、初回はサービス再起動が発生する。既存ユニットのバックアップは /etc/systemd/system/ に残す。

## 制約

- VPSに git、npm、curl、flock、sudo、systemctl、systemd-analyze が必要。
- systemdユニットの変更は自動反映するが、Caddy変更・DB移行は対象外。
- 更新前の作業ツリーの未コミット変更は許容しない。
- ロールバックは**試行**であり、正常性まで保証しない。
- 実行ログは標準出力。永続ログとデプロイ対象SHAの承認UIは未実装。
