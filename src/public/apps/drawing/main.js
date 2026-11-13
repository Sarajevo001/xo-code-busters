// 画面の部品を取っておく
const peerIdInput = document.querySelector('#peer-id');
const hostButton = document.querySelector('#host');
const guestButton = document.querySelector('#guest');
const statusText = document.querySelector('#status');
const clearButton = document.querySelector('#clear');
const canvas = document.querySelector('#canvas');
const ctx = canvas.getContext('2d');

// つながった相手との通り道。まだつながっていないので null。
let conn = null;

// いま選んでいる道具と色とスタンプ
let tool = 'pen';
let color = '#333333';
let stamp = '🐱';

// これまでに描いた指示をぜんぶ覚えておく
const history = [];

// 画面の「あいことば」＝ ピア ID。ここから PeerJS Cloud で名乗る名前を作る。
// PeerJS Cloud は世界中の人と共有しているので「test」のような短い名前は
// すでに誰かに使われている。長めの前置きを付けてぶつかりにくくする。
function roomId(peerId) {
    return 'webrtc-handson-' + peerId;
}

// へやをつくる側（ホスト）。ピア ID を自分の名前として名乗り、誰かが来るのを待つ。
hostButton.addEventListener('click', function () {
    const peer = new Peer(roomId(peerIdInput.value));

    peer.on('open', function () {
        statusText.textContent = 'あいてを待っています…';
    });

    peer.on('connection', function (newConn) {
        conn = newConn;
        conn.on('open', ready);
    });

    peer.on('error', showError);
});

// へやにはいる側（ゲスト）。名前は名乗らず、ピア ID の相手に向かってつなぎに行く。
guestButton.addEventListener('click', function () {
    const peer = new Peer();

    peer.on('open', function () {
        conn = peer.connect(roomId(peerIdInput.value), { reliable: true });
        conn.on('open', ready);
    });

    peer.on('error', showError);
});

// PeerJS から届くエラーを、日本語のことばにして出す。
// err.type にどんなエラーかが入っている。
function showError(err) {
    if (err.type === 'unavailable-id') {
        statusText.textContent =
            'そのあいことばは使われています。別のあいことばにするか「へやにはいる」を押してください';
    } else if (err.type === 'peer-unavailable') {
        statusText.textContent =
            'そのあいことばのへやが見つかりません。相手が「へやをつくる」を押したか確かめてください';
    } else {
        statusText.textContent = 'つながりませんでした（' + err.type + '）';
    }
}

// ホストでもゲストでも、つながったあとにやることは同じ。
function ready() {
    statusText.textContent = 'つながりました';

    conn.on('close', function () {
        statusText.textContent = 'せつだんされました';
    });

    // 相手から届いた指示も、自分が出した指示と同じ apply に通す。
    conn.on('data', apply);

    // 自分がこれまでに描いたものを送り直して、相手の画面にも同じ絵を出す。
    // あとから入ってきた人にも、いまの絵が見えるようになる。
    history.forEach(function (data) {
        conn.send(data);
    });
}

// 指示のとおりにキャンバスへ描く。
// 自分が出した指示も、相手から届いた指示も、かならずここを通る。
function apply(data) {
    if (data.type === 'line') {
        drawLine(data.x1, data.y1, data.x2, data.y2, data.color, data.width);
    }
    if (data.type === 'stamp') {
        drawStamp(data.x, data.y, data.emoji);
    }
    if (data.type === 'clear') {
        clearCanvas();
    }
}

// 自分のキャンバスに描いてから、同じ指示を相手にも送る。
// 「描く」と「送る」を必ずセットにするので、2 つの画面が同じ絵になる。
function draw(data) {
    apply(data);

    // 出した指示は覚えておく（あとから来た相手に送り直すため）
    if (data.type === 'clear') {
        history.length = 0;
    } else {
        history.push(data);
    }

    if (conn) {
        conn.send(data);
    }
}

function drawLine(x1, y1, x2, y2, lineColor, lineWidth) {
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
}

function drawStamp(x, y, emoji) {
    ctx.font = '48px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(emoji, x, y);
}

function clearCanvas() {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// canvas は 800x600 のまま、空いている場所に合わせて縮めて表示している。
// クリックされた位置は「画面上の px」なので、縮めた比率で割って
// 800x600 の中での座標に戻す。これをやらないと 2 台で線がズレる。
function positionOf(event) {
    const rect = canvas.getBoundingClientRect();

    return {
        x: ((event.clientX - rect.left) / rect.width) * canvas.width,
        y: ((event.clientY - rect.top) / rect.height) * canvas.height,
    };
}

// 直前のペン先の位置。線は「前の点から今の点まで」をつなげて描く。
let last = null;

canvas.addEventListener('pointerdown', function (event) {
    const pos = positionOf(event);

    if (tool === 'stamp') {
        draw({ type: 'stamp', x: pos.x, y: pos.y, emoji: stamp });
        return;
    }

    last = pos;
});

canvas.addEventListener('pointermove', function (event) {
    if (last === null) return;

    const pos = positionOf(event);

    draw({
        type: 'line',
        x1: last.x,
        y1: last.y,
        x2: pos.x,
        y2: pos.y,
        // けしごむは「背景と同じ白い色で、太く描くペン」として作る
        color: tool === 'eraser' ? '#ffffff' : color,
        width: tool === 'eraser' ? 40 : 4,
    });

    last = pos;
});

canvas.addEventListener('pointerup', function () {
    last = null;
});

canvas.addEventListener('pointerleave', function () {
    last = null;
});

document.querySelectorAll('.tool').forEach(function (button) {
    button.addEventListener('click', function () {
        tool = button.dataset.tool;
        select(button, '.tool, .stamp');
    });
});

document.querySelectorAll('.stamp').forEach(function (button) {
    button.addEventListener('click', function () {
        tool = 'stamp';
        stamp = button.dataset.stamp;
        select(button, '.tool, .stamp');
    });
});

document.querySelectorAll('.color').forEach(function (button) {
    // ボタンの見た目の色を data-color から流し込む
    button.style.background = button.dataset.color;

    button.addEventListener('click', function () {
        color = button.dataset.color;
        select(button, '.color');
    });
});

clearButton.addEventListener('click', function () {
    draw({ type: 'clear' });
});

// 同じ仲間のボタンから選択の印を外して、押されたものだけに付ける
function select(button, group) {
    document.querySelectorAll(group).forEach(function (other) {
        other.classList.remove('selected');
    });
    button.classList.add('selected');
}

clearCanvas();