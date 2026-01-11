# AWS ECSを使用したCode Interpreter

**AWS上に構築されたLLMエージェントによるPython実行プログラム**

ユーザーのプロンプトをAPIにて送信、プログラムはAWSコンテナ内で実行

---

## 概要

主なフロー:

- **API Gateway**経由でユーザープロンプトを受信
- **AWS Lambda**からコンテナを起動
- [**Amazon Bedrock**](https://aws.amazon.com/jp/bedrock/?trk=1f887566-8561-4bf2-a30b-f383e290b094&sc_channel=ps&trk=1f887566-8561-4bf2-a30b-f383e290b094&sc_channel=ps&ef_id=CjwKCAiAjojLBhAlEiwAcjhrDgwdRX69uFpTJvwTIiBvmXyNUOGi9aVY6zYv0bqY8PpAVkOlJDNNRxoCPzgQAvD_BwE:G:s&s_kwcid=AL!4422!3!785447157291!e!!g!!aws%20bedrock!23296345364!189486864175&gad_campaignid=23296345364&gbraid=0AAAAADjHtp-XNqIWY7WgJItBjZL5RALbT&gclid=CjwKCAiAjojLBhAlEiwAcjhrDgwdRX69uFpTJvwTIiBvmXyNUOGi9aVY6zYv0bqY8PpAVkOlJDNNRxoCPzgQAvD_BwE)のClaude Sonnet 4.0を使用して**Amazon Redshift**データベースのテーブルに対するクエリと推論を実行し、Pythonコードを生成
- 生成したPythonコードを[**ECS Fargate**](https://aws.amazon.com/jp/ecs/)上で実行
- エージェントが生成した成果物を**S3**にて保存(`/results`ディレクトリに成果物の例を格納)

エージェントはデータベースのスキーマを[**DSPy**](https://dspy.ai/)を通じて理解、以下のような事が実装可能:

  - テーブルに関する分析的な質問への回答
  - SQLクエリの生成と実行
  - テーブルからの機械学習モデルの構築と実行
- **エラーが発生した場合、エージェントは自動的にコードを修正し再実行**

GitHubリポジトリは**CodePipeline**を経由しDockerイメージを自動作成、**ECR**に格納

---

## データソース

[**Amazon Redshift**](https://aws.amazon.com/jp/pm/redshift/?trk=73ffb485-6fc0-4153-b6aa-d1f3aa61a4fa&sc_channel=ps&trk=73ffb485-6fc0-4153-b6aa-d1f3aa61a4fa&sc_channel=ps&ef_id=CjwKCAiAjojLBhAlEiwAcjhrDlwYuXmP1TDhhMJOPnDsi1X7EDxgL8EQSUo4JIxo5GU355Ud5DUASxoCy1gQAvD_BwE:G:s&s_kwcid=AL!4422!3!785447301045!e!!g!!aws%20redshift!23296348016!187878269006&gad_campaignid=23296348016&gbraid=0AAAAADjHtp-UXAzkuYJDNpyj3o8Hfwqr1&gclid=CjwKCAiAjojLBhAlEiwAcjhrDlwYuXmP1TDhhMJOPnDsi1X7EDxgL8EQSUo4JIxo5GU355Ud5DUASxoCy1gQAvD_BwE)データベースに以下のテーブルを格納 (`/input`ディレクトリに同等のCSVを格納):

- **users** （ユーザー情報）
- **interactions** （ユーザーが取ったアクションを時系列で保持）

**LLMエージェントはこれらのスキーマを認識**、直接推論とクエリを実行可能

---

## アーキテクチャ
```mermaid
flowchart TD
    GitHub[📁 GitHub Repository] -->|Code Push | Merge| CodePipeline[🔄 AWS CodePipeline<br/>CI/CD Automation]
    CodePipeline -->|Build & Push| ECR[📦 Amazon ECR<br/>Docker Registry]
    
    Client([👤 ユーザー]) -->|POST /prompt| APIGW[🌐 API Gateway<br/>HTTP API]
    APIGW --> Lambda[⚡ AWS Lambda<br/>Request Handler]
    Lambda --> ECS[📦 ECS Fargate Task <br/>Execution Environment]
    ECR -->|Pull Docker Image| ECS
    ECS --> LLM[🤖 Agent / Program Execution <br/>Code Interpreter]
    
    LLM -->|Query data| Redshift[🗃️ Amazon Redshift<br/>users & interactions tables]
    Redshift -.->|Return data| LLM
    
    LLM -->|Store outputs| S3[🗄️ Amazon S3<br/>Output Storage]
    
    style GitHub fill:#f0f0f0
    style CodePipeline fill:#e1f0ff
    style ECR fill:#e1f0ff
    style Client fill:#e1f5ff
    style APIGW fill:#fff4e1
    style Lambda fill:#ffe1f5
    style ECS fill:#e1ffe1
    style Redshift fill:#e8e1ff
    style S3 fill:#ffe1e1
```

---

## 使い方:
以下のコード（Python例）でAPIを送信するとAWS上でプログラムが起動

```python
api_gateway_url = "https://<enter-API-here>/default/lambda_python_executor"

prompt = '''
    'interaction'テーブルから機械学習モデルを作成してください。'purchase'列をターゲット変数として使用してください。
    '''

payload = {"prompt": prompt}
headers = {"Content-Type": "application/json"}
response = requests.post(api_gateway_url, json=payload, headers=headers)
```

---

## 主な機能

### 🧠 スキーマ認識エージェント
エージェントは**データベーススキーマを完全に理解**しており、以下が可能です:
- テーブル構造とカラムの自動認識
- 適切なSQLクエリの生成
- データ型を考慮した分析コードの作成

### 🔄 自動エラー修正
**実行時にエラーが発生した場合、エージェントは自動的に:**
- エラーメッセージを分析
- コードを修正
- 再実行を試行

### 📊 データ駆動型分析
ユーザーはプロンプトを送信するだけで:
- 複雑なデータ分析
- 機械学習モデルの構築
- レポートの自動生成

が可能になります。

---
