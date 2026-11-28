const { test, expect } = require('@playwright/test');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const url = file => pathToFileURL(path.resolve(__dirname, '../../', file)).href;
test('general user registration, validation, settings and logout', async ({page}) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(url('src/client/mock.html'));
  await page.getByRole('button',{name:'新規登録',exact:true}).click();
  await page.locator('[name=email]').fill('new@example.com');
  await page.locator('[name=name]').fill('   ');
  await page.locator('[name=password]').fill('example');
  await page.locator('[name=confirm]').fill('example');
  await page.getByRole('button',{name:'登録（仮）'}).click();
  await expect(page.getByRole('status')).toContainText('表示名を入力');
  await page.locator('[name=email]').fill('new@example.com');
  await page.locator('[name=name]').fill('New User');
  await page.locator('[name=password]').fill('example');
  await page.locator('[name=confirm]').fill('example');
  await page.getByRole('button',{name:'登録（仮）'}).click();
  await expect(page.getByRole('heading')).toContainText('New User');
  await page.getByRole('button',{name:'アカウント設定'}).click();
  await page.locator('[name=name]').fill('Updated User');
  await page.getByRole('button',{name:'変更を保存（仮）'}).click();
  await expect(page.getByRole('heading')).toContainText('Updated User');
  await page.getByRole('button',{name:'ログアウト'}).click();
  await page.getByRole('button',{name:'ログイン',exact:true}).click();
  await page.locator('[name=email]').fill('new@example.com');
  await page.locator('[name=password]').fill('example');
  await page.getByRole('button',{name:'ログイン（仮）'}).click();
  await expect(page.getByRole('heading')).toContainText('Updated User');
  expect(errors).toEqual([]);
});
test('admin search, registration, edit, suspension and logout', async ({page}) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(url('src/admin-client/index.html'));
  await page.locator('#admin-id').fill('admin');
  await page.locator('#admin-password').fill('example');
  await page.getByRole('button',{name:'ログイン（仮）'}).click();
  await page.locator('#search').fill('test02');
  await expect(page.locator('[data-user]')).toHaveCount(1);
  await page.locator('[data-user]').click();
  await expect(page.getByRole('heading')).toHaveText('一般ユーザー詳細');
  await page.getByRole('button',{name:'編集する'}).click();
  await page.locator('#name').fill('Updated');
  await page.getByRole('button',{name:'変更を保存'}).click();
  await expect(page.locator('dd').nth(1)).toHaveText('Updated');
  await page.getByRole('button',{name:'編集する'}).click();
  await page.locator('#toggle').click();
  await expect(page.locator('#toggle')).toHaveText('利用停止を解除する');
  await page.locator('#toggle').click();
  await expect(page.locator('#toggle')).toHaveText('利用停止にする');
  await page.locator('nav [data-view=new]').click();
  await page.locator('#email').fill('new@example.com');
  await page.locator('#name').fill('New User');
  await page.locator('#password').fill('example');
  await page.locator('#confirm').fill('example');
  await page.getByRole('button',{name:'登録する'}).click();
  await expect(page.locator('dd')).toContainText(['U0004','New User','new@example.com','有効']);
  await page.locator('#mock-logout').click();
  await expect(page.getByRole('heading')).toHaveText('管理者ログイン（モック）');
  expect(errors).toEqual([]);
});

test('general user invalid registration and test login', async ({page}) => {
  await page.goto(url('src/client/mock.html'));
  await page.getByRole('button',{name:'ログイン',exact:true}).click();
  await page.getByRole('button',{name:'テストユーザーでログイン'}).click();
  await expect(page.getByRole('heading')).toContainText('テストユーザー');
  await page.getByRole('button',{name:'ログアウト'}).click();
  await page.getByRole('button',{name:'新規登録',exact:true}).click();
  for (const [email,confirm,message] of [['test@example.com','example','重複'],['new@example.com','different','一致しません']]) {
    await page.locator('[name=email]').fill(email);
    await page.locator('[name=name]').fill('Example');
    await page.locator('[name=password]').fill('example');
    await page.locator('[name=confirm]').fill(confirm);
    await page.getByRole('button',{name:'登録（仮）'}).click();
    await expect(page.getByRole('status')).toContainText(message);
  }
});
test('admin invalid registration and reset on reload', async ({page}) => {
  await page.goto(url('src/admin-client/index.html'));
  await page.locator('#admin-id').fill('admin');
  await page.locator('#admin-password').fill('example');
  await page.getByRole('button',{name:'ログイン（仮）'}).click();
  await page.locator('nav [data-view=new]').click();
  for (const [email,confirm,message] of [['test01@example.com','example','重複'],['new@example.com','different','確認欄']]) {
    await page.locator('#email').fill(email);
    await page.locator('#name').fill('Example');
    await page.locator('#password').fill('example');
    await page.locator('#confirm').fill(confirm);
    await page.getByRole('button',{name:'登録する'}).click();
    await expect(page.getByRole('status')).toContainText(message);
  }
  await page.reload();
  await expect(page.getByRole('heading')).toHaveText('管理者ログイン（モック）');
});
