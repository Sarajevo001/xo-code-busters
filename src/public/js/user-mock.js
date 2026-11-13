"use strict";
(()=>{
const root=document.querySelector("#screen");
let users=[{email:"test@example.com",name:"テストユーザー"}], me=null, page="landing", message="";
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const btn=(label,to,cls="")=>'<button type="button" data-page="'+to+'" class="'+cls+'">'+label+'</button>';
function render(){
let h="";
if(page==="landing")h='<h1>XO-Code Bustersへようこそ</h1><p class="note">ゲームやアプリを楽しむための入口です。</p>'+btn("ログイン","login","primary")+btn("新規登録","signup");
if(page==="login")h='<h1>ログイン（モック）</h1><p class="note">登録済みのメールアドレスと任意のパスワードを入力してください。実際のパスワード照合は行いません。</p><form id="login"><label>メールアドレス<input name="email" type="email" required></label><label>パスワード<input name="password" type="password" required></label><button class="primary">ログイン（仮）</button></form>'+btn("テストユーザーでログイン","test")+btn("新規登録","signup")+btn("戻る","landing");
if(page==="signup")h='<h1>新規登録（モック）</h1><form id="signup"><label>メールアドレス<input name="email" type="email" required></label><label>表示名<input name="name" required></label><label>パスワード<input name="password" type="password" required></label><label>パスワード確認<input name="confirm" type="password" required></label><button class="primary">登録（仮）</button></form>'+btn("戻る","landing");
if(page==="home")h='<h1>ようこそ、'+esc(me.name)+'さん</h1><p class="note">アプリへのリンクは現状の公開ページを維持しています。アクセス制御は今後の実装対象です。</p><a class="button" href="/apps/bird-shoot/">BIRD SHOOT GAME</a><a class="button" href="/apps/drawing/">DRAWING APP</a><p>'+btn("アカウント設定","settings")+btn("ログアウト","logout")+'</p>';
if(page==="settings")h='<h1>アカウント設定</h1><form id="settings"><label>メールアドレス<input name="email" type="email" required value="'+esc(me.email)+'"></label><label>表示名<input name="name" required value="'+esc(me.name)+'"></label><button class="primary">変更を保存（仮）</button></form>'+btn("ホームへ戻る","home");
root.innerHTML=h+(message?'<p class="message" role="status">'+esc(message)+'</p>':'');
for(const id of ["login","signup","settings"])document.getElementById(id)?.addEventListener("submit",submit);
}
function submit(e){
e.preventDefault();const id=e.currentTarget.id,d=new FormData(e.currentTarget);
const email=String(d.get("email")||"").trim(),name=String(d.get("name")||"").trim();
if(id==="login"){me=users.find(u=>u.email.toLowerCase()===email.toLowerCase());if(!me){message="仮登録されたメールアドレスではありません。新規登録かテストログインを利用してください。";render();return;}page="home";}
if(id==="signup"){if(d.get("password")!==d.get("confirm")){message="パスワード確認が一致しません。";render();return;}if(users.some(u=>u.email.toLowerCase()===email.toLowerCase())){message="メールアドレスが重複しています。";render();return;}me={email,name};users.push(me);page="home";}
if(id==="settings"){if(users.some(u=>u!==me&&u.email.toLowerCase()===email.toLowerCase())){message="メールアドレスが重複しています。";render();return;}Object.assign(me,{email,name});page="home";}
message="仮データで画面遷移しました。パスワードは保存していません。";render();
}
document.addEventListener("click",e=>{const b=e.target.closest("[data-page]");if(!b)return;const to=b.dataset.page;
if(to==="test"){me=users[0];page="home";message="テストユーザーとして仮ログインしました。";}
else if(to==="logout"){me=null;page="landing";message="ログアウトしました（モック）。";}
else{if(["home","settings"].includes(to)&&!me)return;page=to;message="";}
render();});
render();
})();