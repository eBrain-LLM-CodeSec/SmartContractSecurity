// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

struct Order {
    address offerer;
    uint256 amount;
}

contract Receiver {
    mapping(address => uint256) public received;

    // EXACT-tier match: full elementary-type ERC721 receiver signature.
    function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata data)
        external returns (bytes4)
    {
        received[from] = tokenId;
        return this.onERC721Received.selector;
    }

    // HEURISTIC-tier match: struct-param callback (Seaport-style zone), name
    // only -- full signature varies project-to-project since `Order` is a
    // locally-defined struct.
    function validateOrder(Order calldata order, bytes calldata extraData) external returns (bytes4) {
        received[order.offerer] = order.amount;
        return bytes4(0);
    }

    // Negative control: a public/external, state-writing function that is
    // NOT a recognized callback interface at all.
    function normalDeposit(uint256 amount) external {
        received[msg.sender] = amount;
    }

    // Negative control: same NAME as a curated EXACT-tier signature, but a
    // different parameter list -- full_name differs, so this must NOT
    // EXACT-match, and "onWrongSignatureReceived" isn't in the HEURISTIC
    // name-only tier either.
    function onWrongSignatureReceived(address operator, uint256 tokenId) external returns (bytes4) {
        received[operator] = tokenId;
        return bytes4(0);
    }
}
