"use strict";
(() => {
  const initial = [
    { id:"U0001", name:"テストユーザー01", email:"test01@example.com", active:true },
    { id:"U0002", name:"テストユーザー02", email:"test02@example.com", active:true },
    { id:"U0003", name:"テストユーザー03", email:"test03@example.com", active:false }
  ];
  const users = initial.map(u => ({...u}));
  const screen = document.querySelector("#screen");
  let view="login", selected="U0001", query="", notice="", loggedIn=false;
  const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const user = () => users.find(u => u.id === selected);
  const badge = u => '<span class="badge '+(u.active?'':'off')+'">'+(u.active?'有効':'利用停止')+'</span>';
  const button = (label, target, css="") => '<button type="button" data-view="'+target+'" class="'+css+'">'+label+'</button>';
  function render() {
    document.querySelector("nav").hidden = !loggedIn;
    if(!loggedIn) view="login";
    document.querySelectorAll("nav [data-view]").forEach(b => b.setAttribute("aria-current", b.dataset.view===view?"page":"false"));
    let html="";
    if(view==="login") {
      html='<h1>管理者ログイン（モック）</h1><p class="hint">任意の文字を入力して画面遷移を確認できます。認証は行いません。</p><form id="mock-login"><label for="admin-id">管理者ID</label><input id="admin-id" required autocomplete="off"><label for="admin-password">パスワード</label><input id="admin-password" type="password" required autocomplete="off"><div class="actions"><button class="primary" type="submit">ログイン（仮）</button></div></form>';
    } else if(view==="list") {
      const found=users.filter(u => (u.id+" "+u.name+" "+u.email).toLowerCase().includes(query.toLowerCase()));
      html='<div class="toolbar"><h1>一般ユーザー一覧</h1>'+button("＋ 新規登録","new","primary")+'</div><label for="search">検索（ID・表示名・メールアドレス）</label><input id="search" type="search" value="'+escapeHtml(query)+'" placeholder="検索キーワード"><p class="hint">'+found.length+'件</p>'+found.map(u=>'<button class="user" data-user="'+escapeHtml(u.id)+'">'+badge(u)+'<strong>'+escapeHtml(u.name)+'（'+escapeHtml(u.id)+'）</strong><small>'+escapeHtml(u.email)+'</small></button>').join("")+(found.length?'':'<p>該当するユーザーはありません。</p>');
    } else if(view==="detail") {
      const u=user();
      html='<h1>一般ユーザー詳細</h1><dl><dt>ユーザーID</dt><dd>'+escapeHtml(u.id)+'</dd><dt>表示名</dt><dd>'+escapeHtml(u.name)+'</dd><dt>メールアドレス</dt><dd>'+escapeHtml(u.email)+'</dd><dt>状態</dt><dd>'+badge(u)+'</dd></dl><div class="actions">'+button("一覧に戻る","list")+button("編集する","edit","primary")+'</div>';
    } else if(view==="new"||view==="edit") {
      const creating=view==="new", u=creating?{name:"",email:""}:user();
      html='<h1>'+(creating?'一般ユーザー新規登録':'一般ユーザー編集')+'</h1><form id="account-form"><label for="email">メールアドレス</label><input id="email" name="email" type="email" required value="'+escapeHtml(u.email)+'"><label for="name">表示名</label><input id="name" name="name" required maxlength="100" value="'+escapeHtml(u.name)+'"><label for="password">'+(creating?'初期パスワード':'新しいパスワード（変更時のみ）')+'</label><input id="password" name="password" type="password" autocomplete="new-password" '+(creating?'required':'')+'><label for="confirm">パスワード確認</label><input id="confirm" name="confirm" type="password" autocomplete="new-password" '+(creating?'required':'')+'><p class="hint">このモックではパスワードを保存しません。</p><div class="actions">'+button("戻る",creating?"list":"detail")+'<button type="submit" class="primary">'+(creating?'登録する':'変更を保存')+'</button></div></form>';
      if(!creating)html+='<h2>アカウント状態</h2><p>'+badge(u)+'</p><button type="button" id="toggle" class="danger">'+(u.active?'利用停止にする':'利用停止を解除する')+'</button>';
    }
    screen.innerHTML=html+(notice?'<p class="notice" role="status">'+escapeHtml(notice)+'</p>':'');
    document.querySelector("#search")?.addEventListener("input", e => {
      query=e.target.value;
      const cursor=e.target.selectionStart;
      render();
      const input=document.querySelector("#search");
      input.focus();input.setSelectionRange(cursor,cursor);
    });
    document.querySelector("#mock-login")?.addEventListener("submit", e => {e.preventDefault();loggedIn=true;view="list";notice="モックログインしました。実際の認証は行っていません。";render();});
    document.querySelector("#account-form")?.addEventListener("submit", save);
    document.querySelector("#toggle")?.addEventListener("click", () => {
      user().active=!user().active;
      notice="アカウント状態を変更しました（仮データ）。";
      render();
    });
  }
  function save(e) {
    e.preventDefault();
    const data=new FormData(e.currentTarget);
    const email=String(data.get("email")||"").trim(), name=String(data.get("name")||"").trim();
    const password=String(data.get("password")||""), confirm=String(data.get("confirm")||"");
    if(!name||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { notice="表示名とメールアドレスを確認してください。";render();return; }
    if((view==="new"&&!password)||password!==confirm) { notice="パスワードと確認欄を確認してください。";render();return; }
    if(users.some(u=>u.email.toLowerCase()===email.toLowerCase()&&(view==="new"||u.id!==selected))) { notice="メールアドレスが重複しています。";render();return; }
    if(view==="new") {
      selected="U"+String(Math.max(0,...users.map(u=>Number(u.id.slice(1))))+1).padStart(4,"0");
      users.push({id:selected,name,email,active:true});
    } else Object.assign(user(),{name,email});
    view="detail";notice="仮データを更新しました。パスワードは保存していません。";render();
  }
  document.addEventListener("click", e => {
    const selectedButton=e.target.closest("[data-user]");
    if(selectedButton) {selected=selectedButton.dataset.user;view="detail";notice="";render();return;}
    if(e.target.closest("#mock-logout")) {loggedIn=false;view="login";notice="";render();return;}
    const nav=e.target.closest("[data-view]");
    if(nav) {view=nav.dataset.view;notice="";render();}
  });
  render();
})();
