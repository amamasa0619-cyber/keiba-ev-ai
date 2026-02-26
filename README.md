# 競馬期待値分析アプリ (CLI)

競馬レースの出走馬情報と各馬の過去走（最大10走）から、ルールベースで推定勝率と単勝期待値(EV)を算出するPython CLIです。

> ⚠️ 期待値はモデル上の推定値であり、利益を保証しません。利用規約・robots.txt・法令を必ず遵守してください。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 実行方法

CSV入力（推奨・最優先）:

```bash
python main.py --csv data/sample_race.csv --output output.csv
```

保存済みHTML入力:

```bash
python main.py --html data/sample_race.html
```

URL入力（制限がない場合のみ。制限時はCSV/保存HTMLを利用）:

```bash
python main.py --url "https://example.com/race_page"
```

## 入力形式

### CSV
最低限、以下の列が必要です。

- horse_name
- horse_no
- frame_no
- sex_age
- weight
- jockey
- trainer
- odds
- popularity

加えて、`race_date`,`surface`,`distance`,`finish`,`corner_order` などの過去走列があれば特徴量に反映します。

### 保存HTML
`<script id="race-data" type="application/json">` のJSONを読み取ります。

## 出力

- コンソール: 期待値ランキング、推奨度、買い目（均等・簡易ケリー）
- CSV (`output.csv`):
  - 馬名
  - 馬番
  - 単勝オッズ
  - 市場確率
  - 推定勝率
  - 期待値
  - 推奨度
  - 推奨買い目金額（任意）
  - 芝/ダート実績要約
  - 距離実績要約
  - 脚質要約

## モデル概要（初期版）

`model.py` のルールベース重み付き合成で勝率を推定します。

- 単勝オッズ由来の市場確率
- 近走着順/平均着順
- 同条件（芝/ダート + 距離±200m）適性
- 脚質傾向
- 近走の改善/悪化
- 馬場適性

## 注意事項

- 利用規約・robots.txt・法令を尊重してください。
- 直接アクセスが禁止/制限される場合は、保存済みHTML・CSV・テキスト入力へ切り替えてください。
- このツールの期待値・推奨は参考情報であり、収益を保証しません。

## 今後の改善案

- 馬連/ワイド/複勝への拡張
- 騎手・調教師・血統などの詳細特徴量追加
- 競馬場バイアスやペース想定の導入
- 学習ベース（LightGBM/XGBoostなど）への移行
