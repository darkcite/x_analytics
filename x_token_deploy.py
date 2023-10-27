from web3 import Web3
from eth_account import Account
from google.cloud import secretmanager, storage
import sqlalchemy
from sqlalchemy import text
from google.cloud.sql.connector import Connector, IPTypes

def get_secret(secret_name):
    project_name = storage.Client().project
    secret_client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_name}/secrets/{secret_name}/versions/latest"
    response = secret_client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')
  
INFURA_WEB3_APIKEY = get_secret('INFURA_WEB3_APIKEY')

RPC_URL = f"https://goerli.infura.io/v3/{INFURA_WEB3_APIKEY}"
X_DEPLOYMENT_PRIVATE_KEY = get_secret('X_DEPLOYMENT_PRIVATE_KEY')
X_DEPLOYMENT_PUBLIC_KEY = get_secret('X_DEPLOYMENT_PUBLIC_KEY')

X_DEPLOYMENT_MASTER_CONTRACT_ADDRESS = get_secret('X_DEPLOYMENT_MASTER_CONTRACT_ADDRESS')

# Database connection details for Google Cloud Function
CLOUD_DB_USER = get_secret("CLOUD_DB_USER")
CLOUD_DB_PASSWORD = get_secret("CLOUD_DB_PASSWORD")
CLOUD_DB_NAME = get_secret("CLOUD_DB_NAME")
INSTANCE_CONNECTION_NAME = get_secret("INSTANCE_CONNECTION_NAME")

#####################
ip_type = IPTypes.PUBLIC  # Assuming you're using the public IP
connector = Connector(ip_type)
connect_args = {}  # Add any additional connection arguments if needed

def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pytds",
        user=CLOUD_DB_USER,
        password=CLOUD_DB_PASSWORD,
        db=CLOUD_DB_NAME,
        **connect_args
    )
    print("Successfully connected to the database!")
    return conn

engine = sqlalchemy.create_engine(
    "mssql+pytds://",
    creator=getconn,
)
######################

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# The contract ABI is necessary to encode/decode data
CONTRACT_ABI = [
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_uniswapV2RouterAddress",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_symbol",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_totalSupply",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_treasuryWallet",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_refSystemWallet",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_tokensForLiquidity",
          "type": "uint256"
        }
      ],
      "name": "deployToken",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "uniswapV2Router",
      "outputs": [
        {
          "internalType": "contract IUniswapV2Router",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
]

# Set up the contract
contract = w3.eth.contract(address=X_DEPLOYMENT_MASTER_CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def deploy_token(token_name, token_symbol):
    """Deploy a token to the Ethereum network."""
    account = Account.from_key(X_DEPLOYMENT_PRIVATE_KEY)
    
    # Prepare the transaction details
    txn_details = {
        'chainId': 5, # 5 - Goerli, 1 - Mainnet 
        'gas': 6000000,
        'gasPrice': 80000,
        'nonce': w3.eth.get_transaction_count(account.address),
        'from': account.address,
        'to': X_DEPLOYMENT_MASTER_CONTRACT_ADDRESS,
        'value': w3.to_wei(0.015, 'ether'),
        'data': contract.encodeABI(fn_name="deployToken", args=[
            token_name, token_symbol, 1000000000, account.address, account.address, 10000
        ])
    }
    
    # 2. Sign the transaction
    signed_txn = w3.eth.account.sign_transaction(txn_details, X_DEPLOYMENT_PRIVATE_KEY)
    
    # 3. Send the signed transaction
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    
    return txn_receipt

def main():
  with engine.connect() as connection:
      # Fetch entries with 'awaiting deployment' status
      results = connection.execute(text("SELECT keyword_id, token_name, token_symbol FROM Keywords WHERE token_deployment_status = 'awaiting deployment'"))
      rows = list(results)
      if not rows:
          print("No keywords with status 'awaiting deployment' found.")
          exit()

      for row in rows:
          keyword_id, token_name, token_symbol = row
          print(f"Starting deployment for token {token_name} ({token_symbol})...")
          
          # Update status to "deploying"
          update_params = {
              "keyword_id": keyword_id
          }
          
          stmt_update = text("UPDATE Keywords SET token_deployment_status = 'deploying' WHERE keyword_id = :keyword_id")
          connection.execute(stmt_update, update_params)
          
          connection.commit()
          
          try:
              # Deploy the token
              receipt = deploy_token(token_name, token_symbol)
              if receipt.status == 1:
                  # If deployment was successful
                  update_success_params = {
                      "keyword_id": keyword_id
                  }
                  stmt_success = text("UPDATE Keywords SET token_deployment_status = 'successfully deployed' WHERE keyword_id = :keyword_id")
                  connection.execute(stmt_success, update_success_params)
                  
                  print(f"Token {token_name} ({token_symbol}) deployed successfully! Tx Reciept: {receipt}")
              else:
                  # If the deployment failed for some reason
                  update_failed_params = {
                      "keyword_id": keyword_id
                  }
                  
                  stmt_failed = text("UPDATE Keywords SET token_deployment_status = 'deployment failed: ' WHERE keyword_id = :keyword_id")
                  connection.execute(stmt_failed, update_failed_params)
                  
                  print(f"Token {token_name} ({token_symbol}) deployment failed!")
          except Exception as e:
              # Catch any exceptions during deployment and update the status
              update_exception_params = {
                  "error_message": str(e),
                  "keyword_id": keyword_id
              }
              
              stmt_exception = text("UPDATE Keywords SET token_deployment_status = 'deployment failed: ' + :error_message WHERE keyword_id = :keyword_id")
              connection.execute(stmt_exception, update_exception_params)
              
              print(f"Token {token_name} ({token_symbol}) deployment failed with error: {e}")

      connection.commit()


  print("Finished processing tokens!")
  if __name__ == "__main__":
    main()