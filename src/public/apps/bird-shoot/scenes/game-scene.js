const BirdState = Object.freeze({
    READY: 'READY',
    ACTIVE: 'ACTIVE',
    FINISHED: 'FINISHED',
});

class BirdManager {
    constructor(totalBirds) {
        this.remaining = totalBirds;
        this.birds = [];
    }

    add(bird) {
        this.birds.push(bird);
    }

    launched() {
        this.remaining -= 1;
    }

    hasBirdToLaunch() {
        return this.remaining > 0;
    }

    hasActiveBird() {
        return this.birds.some(
            bird => bird.state === BirdState.ACTIVE
        );
    }

    getRemaining() {
        return this.remaining;
    }
}

class GameScene extends Phaser.Scene {
    constructor() {
        super('Game');
    }

    create() {
        this.birdManager = new BirdManager(5);
        const groundX = 360;
        const groundY = 440;
        const groundWidth = 720;
        const groundHeight = 80;
        const groundTop = groundY - groundHeight / 2; // 地面の上面。物はこの高さに乗る

        const ground = this.add.rectangle(
            groundX,
            groundY,
            groundWidth,
            groundHeight,
            0x888888,
        );

        this.matter.add.gameObject(ground, { isStatic: true });

        const boxSize = 40;
        const towerX = 560;
        for (let i = 0; i < 3; i++) {
            const boxY = groundTop - boxSize / 2 - i * boxSize;
            const box = this.add.rectangle(towerX, boxY, boxSize, boxSize, 0xdddddd);
            box.setStrokeStyle(3, 0x333333);
            this.matter.add.gameObject(box, { restitution: 0.1 });
        }

        const pigRadius = 16;
        const pigPositions = [
            { x: 460, y: groundTop - pigRadius }, // 手前のブタ
            { x: towerX, y: groundTop - boxSize * 3 - pigRadius }, // タワーの上のブタ
            { x: 660, y: groundTop - pigRadius }, // 奥のブタ
        ];
        for (const pos of pigPositions) {
            const pig = this.add.circle(pos.x, pos.y, pigRadius, 0xaaaaaa);
            pig.setStrokeStyle(3, 0x333333);
            this.matter.add.gameObject(pig, {
                shape: { type: 'circle', radius: pigRadius },
                restitution: 0.2,
            });
            pig.isPig = true; // 衝突したときに見分けるための目印。
        }

        this.pigsLeft = pigPositions.length;
        this.cleared = false;

        this.score = 0;
        this.scoreText = this.add
            .text(700, 30, 'スコア: 0', { fontSize: '20px', color: '#333333' })
            .setOrigin(1, 0.5);

        // 衝突中に消すと不安定なので、ためて update でまとめて消す。
        this.pendingRemoval = new Set();

        this.matter.world.on('collisionstart', (event) => {
            for (const pair of event.pairs) {
                const gameObjectA = pair.bodyA.gameObject;
                const gameObjectB = pair.bodyB.gameObject;
                if (!gameObjectA || !gameObjectB) continue;
                if (gameObjectA.isBird && gameObjectB.isPig)
                    this.pendingRemoval.add(gameObjectB);
                if (gameObjectB.isBird && gameObjectA.isPig)
                    this.pendingRemoval.add(gameObjectA);
            }
        });

        const anchor = { x: 140, y: 300 };
        const power = 0.22; // 引っ張った長さを速さに変える倍率
        const birdRadius = 18;

        this.add.circle(anchor.x, anchor.y, 6, 0xbbbbbb);

        const aim = this.add.graphics();

        const reserve = this.add.graphics();
        const drawReserve = () => {
            reserve.clear();
            for (let i = 0; i < this.birdManager.getRemaining(); i++) {
                const x = 30 + i * 26;
                reserve.fillStyle(0xffffff, 1);
                reserve.fillCircle(x, 40, 9);
                reserve.lineStyle(2, 0x333333, 1);
                reserve.strokeCircle(x, 40, 9);
            }
        };

        // いま操作できる鳥。発射中やリロード待ちのときは null。
        let bird = null;
        let dragging = false;

        const spawnBird = () => {
            if (!this.birdManager.hasBirdToLaunch()) return;
            bird = this.add.circle(anchor.x, anchor.y, birdRadius, 0xffffff);
            bird.setStrokeStyle(3, 0x333333);
            this.matter.add.gameObject(bird, {
                shape: { type: 'circle', radius: birdRadius },
                restitution: 0.2,
            });
            // 待機中は動かないように静的にしておく。
            bird.setStatic(true);
            bird.isBird = true;
            bird.state = BirdState.READY;

            this.birdManager.add(bird);
        };

        drawReserve();
        spawnBird();

        this.input.on('pointerdown', () => {
            if (!bird || dragging) return;
            dragging = true;
        });

        this.input.on('pointermove', (pointer) => {
            if (!dragging || !bird) return;

            bird.setPosition(pointer.x, pointer.y);

            const forwardX = anchor.x + (anchor.x - bird.x) * 1.5;
            const forwardY = anchor.y + (anchor.y - bird.y) * 1.5;
            aim.clear();
            aim.lineStyle(2, 0x333333, 0.5);
            aim.lineBetween(bird.x, bird.y, forwardX, forwardY);
        });

        this.input.on('pointerup', () => {
            if (!dragging || !bird) return;
            dragging = false;
            aim.clear();

            const vx = (anchor.x - bird.x) * power;
            const vy = (anchor.y - bird.y) * power;
            bird.setStatic(false);
            bird.setVelocity(vx, vy);
            bird.state = BirdState.ACTIVE;

            bird = null;
            this.birdManager.launched();
            drawReserve();

            this.time.delayedCall(1200, () => {
                if (this.birdManager.hasBirdToLaunch()) {
                    spawnBird();
                }
            });
        });
    }

    update() {
        for (const pig of this.pendingRemoval) {
            pig.destroy();
            this.pigsLeft -= 1;
            this.score += 1000;
            this.scoreText.setText('スコア: ' + this.score);
        }
        this.pendingRemoval.clear();

        // 何度も遷移しないよう、クリアは1回だけ。
        if (!this.cleared && this.pigsLeft <= 0) {
            this.cleared = true;
            this.scene.start('Clear', { score: this.score });
        }

        for (const bird of this.birdManager.birds) {
            if (bird.state !== BirdState.ACTIVE) continue;

            const stopped =
                bird.body.speed < 0.01;

            const escaped =
                bird.x < 0 ||
                bird.x > this.scale.width;

            if (stopped || escaped) {
                bird.state = BirdState.FINISHED;
            }
        }

        const noBirdToLaunch =
            !this.birdManager.hasBirdToLaunch();

        const noActiveBird =
            !this.birdManager.hasActiveBird();

        if (noBirdToLaunch && noActiveBird) {
            this.scene.start('GameOver', {
                score: this.score
            });
        }
    }
}