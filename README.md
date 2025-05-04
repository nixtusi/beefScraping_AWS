## 使用ライブラリおよびバージョン情報

このプロジェクトは AWS Lambda 上で headless Chrome を動作させ、Selenium によるスクレイピングを実現しています。

### 🔧 使用バイナリ

| 名前              | バージョン                | 備考                                       |
|-------------------|----------------------------|--------------------------------------------|
| headless-chromium | v1.0.0-57                  | Amazon Linux 2 対応バイナリ               |
| chromedriver      | 86.0.4240.22               | 上記 headless-chromium に対応             |

> ※バージョンの組み合わせは互換性を意識して選定。  
> ※S3 バケット `my-kobe-univ-lambda` にアップロードして Lambda 関数内 `/tmp` にダウンロードして使用。

---

### 🐍 その他

- Python 3.8（AWS Lambda Docker イメージベース）
- Selenium / BeautifulSoup 使用