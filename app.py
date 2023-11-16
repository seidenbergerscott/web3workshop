from flask import Flask, render_template, send_file, redirect, url_for
from web3 import Web3
import boto3
from botocore.exceptions import NoCredentialsError
from os.path import exists

app = Flask(__name__)

def get_eth_price():
    # Change this to use your own RPC URL
    web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth_goerli'))
    # AggregatorV3Interface ABI
    abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    # Price Feed address
    addr = '0xD4a33860578De61DBAbDc8BFdb98FD742fA7028e'

    # Set up contract instance
    contract = web3.eth.contract(address=addr, abi=abi)
    # Make call to latestRoundData()
    latestData = contract.functions.latestRoundData().call()

    eth_price = latestData[1] / (10 ** 8)

    # Format to 2 decimal places and convert to string
    formatted_price = "{:,.2f}".format(eth_price)
    
    return formatted_price

def download_from_storj_s3(bucket_name, file_key, destination_path, access_key, secret_key, endpoint_url):
    # Initialize a session using boto3
    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
    )

    try:
        s3_client.download_file(bucket_name, file_key, destination_path)
        print(f"File '{file_key}' downloaded successfully to '{destination_path}'.")
        #response = s3_client.list_objects(Bucket=bucket_name)
        #print(response)
    except NoCredentialsError:
        print("Credentials not available")


    

@app.route('/download')
def download_file():
    bucket_name = "demo-bucket"
    file_key = "web3 Workshop Poap.png"
    destination_path = "static/poap.png"
    access_key = "jwxwkd3pirkb77ngtiwxr4ajphoq"
    secret_key = "j3omtog5wlcyjudtdzq3krxchf5floizwzjinxljtjw77wouuhlpq"
    endpoint_url = "https://gateway.storjshare.io"

    download_from_storj_s3(bucket_name, file_key, destination_path, access_key, secret_key, endpoint_url)
    
    return redirect(url_for('index'))

@app.route('/')
def index():
    eth_price = get_eth_price()
    file_key = "poap.png"
    image_available = exists('static/' + file_key)
    return render_template('index.html', eth_price=eth_price, file_key=file_key, image_available=image_available)

if __name__ == '__main__':
    app.run(debug=True)
