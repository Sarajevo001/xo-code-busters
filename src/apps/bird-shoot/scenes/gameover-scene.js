class GameOverScene extends Phaser.Scene {
    constructor() {
        super('GameOver');
    }

    create(data) {
        const score = data.score || 0;

        this.add
            .text(360, 180, 'ゲームオーバー', {
                fontSize: '36px',
                color: '#c0392b',
                fontStyle: 'bold',
            })
            .setOrigin(0.5);

        this.add
            .text(360, 250, 'スコア: ' + score, {
                fontSize: '28px',
                color: '#333333',
            })
            .setOrigin(0.5);

        this.add
            .text(360, 320, 'クリックでスタートに戻る', {
                fontSize: '18px',
                color: '#555555',
            })
            .setOrigin(0.5);

        this.input.once('pointerdown', () => this.scene.start('Start'));
    }
}