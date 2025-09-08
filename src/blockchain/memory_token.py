#!/usr/bin/env python3
"""
Memory Token Backend Integration
Handles $MEM token operations, rewards, and buyback mechanisms
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from eth_account import Account
from flask import Blueprint, jsonify, request
from web3 import Web3

# Token Reward Constants
REWARDS = {
    "reflection_saved": 1.0,  # 1 $MEM per reflection
    "pattern_recognized": 5.0,  # 5 $MEM per pattern
    "pattern_shared": 10.0,  # 10 $MEM per anonymous share
    "milestone_10_reflections": 10.0,  # 10 $MEM bonus
    "milestone_50_reflections": 50.0,  # 50 $MEM bonus
    "milestone_100_reflections": 100.0,  # 100 $MEM bonus
}


class MemoryTokenService:
    def __init__(self):
        self.web3 = None
        self.contract = None
        self.account = None
        self.initialize_blockchain()

    def initialize_blockchain(self):
        """Initialize Web3 connection and contract"""
        try:
            # Polygon Mumbai RPC
            rpc_url = os.getenv("POLYGON_RPC_URL", "https://rpc-mumbai.maticvigil.com")
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))

            # Load contract ABI and address
            contract_address = os.getenv("MEMORY_TOKEN_ADDRESS")
            private_key = os.getenv("DEPLOYER_PRIVATE_KEY")

            if not contract_address or not private_key:
                print("❌ Memory Token contract address or private key not configured")
                return False

            # Load contract ABI
            with open("contracts/MemoryToken.json", "r") as f:
                contract_data = json.load(f)
                abi = contract_data["abi"]

            self.contract = self.web3.eth.contract(
                address=Web3.toChecksumAddress(contract_address), abi=abi
            )

            # Setup account
            self.account = Account.from_key(private_key)

            print(f"✅ Memory Token service initialized")
            print(f"Contract: {contract_address}")
            print(f"Account: {self.account.address}")

            return True

        except Exception as e:
            print(f"❌ Memory Token initialization failed: {e}")
            return False

    def get_balance(self, user_address: str) -> Dict:
        """Get user's $MEM token balance"""
        try:
            if not self.contract:
                return {"error": "Contract not initialized"}

            balance_wei = self.contract.functions.balanceOf(
                Web3.toChecksumAddress(user_address)
            ).call()

            balance = self.web3.fromWei(balance_wei, "ether")

            return {
                "balance": float(balance),
                "balance_wei": str(balance_wei),
                "address": user_address,
            }

        except Exception as e:
            return {"error": str(e)}

    def reward_user(self, user_address: str, amount: float, reason: str) -> Dict:
        """Reward user with $MEM tokens"""
        try:
            if not self.contract or not self.account:
                return {"error": "Service not initialized"}

            # Convert amount to Wei (18 decimals)
            amount_wei = self.web3.toWei(amount, "ether")

            # Build transaction
            transaction = self.contract.functions.rewardUser(
                Web3.toChecksumAddress(user_address), amount_wei, reason
            ).buildTransaction(
                {
                    "from": self.account.address,
                    "nonce": self.web3.eth.get_transaction_count(self.account.address),
                    "gas": 200000,
                    "gasPrice": self.web3.toWei("20", "gwei"),
                }
            )

            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, self.account.privateKey
            )

            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            # Wait for confirmation
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                "success": True,
                "tx_hash": receipt.transactionHash.hex(),
                "amount": amount,
                "reason": reason,
                "user": user_address,
            }

        except Exception as e:
            return {"error": str(e)}

    def execute_buyback(self, usdc_amount: float) -> Dict:
        """Execute buyback mechanism"""
        try:
            if not self.contract or not self.account:
                return {"error": "Service not initialized"}

            # Convert USDC amount to Wei (6 decimals for USDC)
            usdc_wei = int(usdc_amount * 10**6)

            # Build transaction
            transaction = self.contract.functions.executeBuyback(
                usdc_wei
            ).buildTransaction(
                {
                    "from": self.account.address,
                    "nonce": self.web3.eth.get_transaction_count(self.account.address),
                    "gas": 300000,
                    "gasPrice": self.web3.toWei("20", "gwei"),
                }
            )

            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, self.account.privateKey
            )

            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                "success": True,
                "tx_hash": receipt.transactionHash.hex(),
                "usdc_amount": usdc_amount,
            }

        except Exception as e:
            return {"error": str(e)}

    def get_contract_stats(self) -> Dict:
        """Get contract statistics"""
        try:
            if not self.contract:
                return {"error": "Contract not initialized"}

            total_supply = self.contract.functions.totalSupply().call()
            total_burned = self.contract.functions.totalBurned().call()
            user_minted = self.contract.functions.userTokensMinted().call()
            dev_minted = self.contract.functions.devTokensMinted().call()
            dao_minted = self.contract.functions.daoTokensMinted().call()

            available = self.contract.functions.getAvailableTokens().call()

            return {
                "total_supply": float(self.web3.fromWei(total_supply, "ether")),
                "total_burned": float(self.web3.fromWei(total_burned, "ether")),
                "user_tokens_minted": float(self.web3.fromWei(user_minted, "ether")),
                "dev_tokens_minted": float(self.web3.fromWei(dev_minted, "ether")),
                "dao_tokens_minted": float(self.web3.fromWei(dao_minted, "ether")),
                "user_tokens_available": float(
                    self.web3.fromWei(available[0], "ether")
                ),
                "dev_tokens_available": float(self.web3.fromWei(available[1], "ether")),
                "max_supply": 1000000000.0,
            }

        except Exception as e:
            return {"error": str(e)}


# Global service instance
memory_token_service = MemoryTokenService()

# Flask Blueprint
token_bp = Blueprint("token", __name__)


@token_bp.route("/api/token/balance/<address>")
def get_token_balance(address):
    """Get user's token balance"""
    result = memory_token_service.get_balance(address)
    return jsonify(result)


@token_bp.route("/api/token/claim", methods=["POST"])
def claim_tokens():
    """Claim tokens for user activities"""
    data = request.get_json()

    user_address = data.get("user_address")
    activity_type = data.get("activity_type")

    if not user_address or not activity_type:
        return jsonify({"error": "Missing required parameters"}), 400

    if activity_type not in REWARDS:
        return jsonify({"error": "Invalid activity type"}), 400

    amount = REWARDS[activity_type]
    reason = f"Reward for {activity_type}"

    result = memory_token_service.reward_user(user_address, amount, reason)

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)


@token_bp.route("/api/token/buyback", methods=["POST"])
def execute_buyback():
    """Execute token buyback"""
    data = request.get_json()

    usdc_amount = data.get("usdc_amount")

    if not usdc_amount:
        return jsonify({"error": "USDC amount required"}), 400

    result = memory_token_service.execute_buyback(float(usdc_amount))

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)


@token_bp.route("/api/token/stats")
def get_token_stats():
    """Get contract statistics"""
    result = memory_token_service.get_contract_stats()
    return jsonify(result)


@token_bp.route("/api/token/rewards")
def get_reward_structure():
    """Get reward structure"""
    return jsonify(
        {
            "rewards": REWARDS,
            "description": {
                "reflection_saved": "For each saved reflection",
                "pattern_recognized": "When AI recognizes a pattern",
                "pattern_shared": "For sharing patterns anonymously",
                "milestone_10_reflections": "Bonus for 10 reflections",
                "milestone_50_reflections": "Bonus for 50 reflections",
                "milestone_100_reflections": "Bonus for 100 reflections",
            },
        }
    )


# Credit System Integration (for Stripe)
class CreditSystem:
    def __init__(self):
        self.credits_per_dollar = 10  # 10 credits per USD
        self.mem_per_credit = 0.1  # 0.1 $MEM per credit

    def process_payment(self, user_address: str, amount_usd: float) -> Dict:
        """Process credit purchase and distribute $MEM"""
        try:
            credits = amount_usd * self.credits_per_dollar
            mem_tokens = credits * self.mem_per_credit

            # Award $MEM tokens
            result = memory_token_service.reward_user(
                user_address, mem_tokens, f"Credit purchase: ${amount_usd}"
            )

            if "error" in result:
                return {"error": result["error"]}

            return {
                "success": True,
                "credits_purchased": credits,
                "mem_tokens_awarded": mem_tokens,
                "usd_amount": amount_usd,
                "tx_hash": result.get("tx_hash"),
            }

        except Exception as e:
            return {"error": str(e)}


credit_system = CreditSystem()


@token_bp.route("/api/credits/purchase", methods=["POST"])
def purchase_credits():
    """Purchase credits with USD and receive $MEM"""
    data = request.get_json()

    user_address = data.get("user_address")
    amount_usd = data.get("amount_usd")

    if not user_address or not amount_usd:
        return jsonify({"error": "Missing required parameters"}), 400

    result = credit_system.process_payment(user_address, float(amount_usd))

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)


if __name__ == "__main__":
    # Test the service
    print("Testing Memory Token Service...")

    # Test contract stats
    stats = memory_token_service.get_contract_stats()
    print("Contract Stats:", json.dumps(stats, indent=2))
