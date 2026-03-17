# Azure OpenAI - Endpoint Deployment (GUI)

## Prerequisites
- Active Azure subscription
- Access granted to Azure OpenAI Service (requires approval at https://aka.ms/oai/access)

## Step 1: Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Create a resource**
3. Search for **Azure OpenAI** and select it
4. Click **Create** > **Foundry**
5. Fill in:
   - **Subscription**: select your subscription
   - **Resource group**: create new or select existing
   - **Region**: e.g., `Sweden Central` (check model availability per region)
   - **Name**: choose a unique name (this becomes part of your endpoint URL)
   - **Pricing tier**: `Standard S0`
6. Click **Review + create** → **Create**
7. Wait for deployment to complete

## Step 2: Deploy a Model

1. Go to your newly created Azure OpenAI resource
2. Click **Go to Azure AI Foundry portal** (opens the studio), and choose **Build** (top right)
3. In the left menu, click **Models**
4. Click **+ Deploy a base model**
5. Select **model**: `gpt-5-nano`
6. Click **Deploy** > **Default settings**

## Step 3: Get Connection Details

1. Go back to your Azure OpenAI resource in the Azure Portal
2. In the left menu, click **Resource Management > Keys and Endpoint**
3. Copy:
   - **Endpoint** → e.g., `https://your-resource-name.openai.azure.com/`
   - **KEY 1** → your API key
4. Add both to your `.env` file:

```
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
```

## Step 4: Run the Script

```bash
uv run "src/2. Models/1. LLMs/demo/4.AzureOpenAI_basic_call.py"
```
