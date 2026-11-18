"""
Synthetic customer profiles, fraud networks, and sample transactions.
All data is fictional and for educational demonstration only.
"""

CUSTOMER_PROFILES = {
    "CUST_789": {
        "name": "John Smith",
        "account_age_years": 3,
        "avg_transaction_usd": 320,
        "max_normal_transaction_usd": 1000,
        "normal_destinations": ["US domestic"],
        "transaction_frequency": "2-3 per week",
        "past_international_transfers": 0,
        "known_devices": ["iPhone 12 - San Francisco, CA"],
        "normal_hours": "09:00-22:00",
        "normal_location": "San Francisco, CA, USA",
        "risk_tier": "low",
        "recent_transactions": [
            {"amount": 285, "destination": "US domestic", "merchant": "Whole Foods", "date": "2024-11-14"},
            {"amount": 450, "destination": "US domestic", "merchant": "Amazon", "date": "2024-11-12"},
            {"amount": 175, "destination": "US domestic", "merchant": "Shell Gas Station", "date": "2024-11-10"},
            {"amount": 320, "destination": "US domestic", "merchant": "Costco", "date": "2024-11-08"},
        ],
    },
    "CUST_101": {
        "name": "Sarah Johnson",
        "account_age_years": 7,
        "avg_transaction_usd": 850,
        "max_normal_transaction_usd": 5000,
        "normal_destinations": ["US domestic", "UK", "Canada", "France"],
        "transaction_frequency": "daily",
        "past_international_transfers": 45,
        "known_devices": ["MacBook Pro - New York, NY", "iPhone 14 - New York, NY"],
        "normal_hours": "07:00-23:00",
        "normal_location": "New York, NY, USA",
        "risk_tier": "low",
        "recent_transactions": [
            {"amount": 650, "destination": "US domestic", "merchant": "Whole Foods NYC", "date": "2024-11-16"},
            {"amount": 1200, "destination": "UK", "merchant": "British Airways", "date": "2024-11-10"},
            {"amount": 450, "destination": "US domestic", "merchant": "Equinox Gym", "date": "2024-11-09"},
            {"amount": 2800, "destination": "France", "merchant": "Hotel Lutetia Paris", "date": "2024-11-01"},
        ],
    },
    "CUST_202": {
        "name": "Alex Chen",
        "account_age_years": 1,
        "avg_transaction_usd": 150,
        "max_normal_transaction_usd": 500,
        "normal_destinations": ["US domestic"],
        "transaction_frequency": "weekly",
        "past_international_transfers": 0,
        "known_devices": ["Samsung Galaxy S21 - Los Angeles, CA"],
        "normal_hours": "10:00-20:00",
        "normal_location": "Los Angeles, CA, USA",
        "risk_tier": "low",
        "recent_transactions": [
            {"amount": 120, "destination": "US domestic", "merchant": "Ralphs", "date": "2024-11-15"},
            {"amount": 85, "destination": "US domestic", "merchant": "ARCO Gas", "date": "2024-11-13"},
            {"amount": 200, "destination": "US domestic", "merchant": "Target", "date": "2024-11-07"},
            {"amount": 160, "destination": "US domestic", "merchant": "Netflix / Hulu", "date": "2024-11-01"},
        ],
    },
}

FRAUD_NETWORKS = {
    "RING_RU_001": {
        "name": "Russian Wire Fraud Ring",
        "members": ["CUST_456", "CUST_123", "CUST_789"],
        "pattern": "Account takeover via phishing → wire transfer to Russia via crypto",
        "total_fraud_amount_usd": 125000,
        "active_since": "2024-06-01",
        "confidence": 0.87,
        "recent_activity": [
            {"account": "CUST_456", "amount": 4500, "destination": "Russia", "date": "2024-11-01"},
            {"account": "CUST_123", "amount": 6000, "destination": "Russia", "date": "2024-11-05"},
        ],
    },
    "RING_MULE_002": {
        "name": "Money Mule Network",
        "members": ["CUST_555", "CUST_666", "CUST_777"],
        "pattern": "Receive large deposits → split and forward to offshore accounts",
        "total_fraud_amount_usd": 450000,
        "active_since": "2024-01-15",
        "confidence": 0.92,
        "recent_activity": [
            {"account": "CUST_555", "amount": 15000, "destination": "Cayman Islands", "date": "2024-11-10"},
            {"account": "CUST_666", "amount": 12000, "destination": "Cayman Islands", "date": "2024-11-12"},
        ],
    },
}

HIGH_RISK_COUNTRIES = [
    "Russia", "North Korea", "Iran", "Belarus", "Myanmar",
    "Syria", "Somalia", "Venezuela", "Cuba",
]

DEVICE_DATABASE = {
    "CUST_789": {
        "primary_device": "iPhone 12",
        "device_id": "IPHONE12_SF_ABC123",
        "last_seen_location": "San Francisco, CA, USA",
        "last_seen_time": "2024-11-17T00:00:00Z",
        "trusted": True,
    },
    "CUST_101": {
        "primary_device": "iPhone 14",
        "device_id": "IPHONE14_NY_DEF456",
        "last_seen_location": "New York, NY, USA",
        "last_seen_time": "2024-11-16T18:30:00Z",
        "trusted": True,
    },
    "CUST_202": {
        "primary_device": "Samsung Galaxy S21",
        "device_id": "SAMSUNG_LA_GHI789",
        "last_seen_location": "Los Angeles, CA, USA",
        "last_seen_time": "2024-11-15T14:00:00Z",
        "trusted": True,
    },
}

# Pre-built sample transactions for demonstration
SAMPLE_TRANSACTIONS = [
    {
        "id": "demo_1",
        "name": "FRAUD - Account Takeover + Russia Wire",
        "description": "Classic fraud scenario: impossible travel, device change, known fraud ring",
        "transaction": {
            "transaction_id": "TXN_12345",
            "customer_id": "CUST_789",
            "amount_usd": 5000,
            "currency": "USD",
            "destination_country": "Russia",
            "destination_account": "RU_BANK_ACC_9876",
            "payment_method": "cryptocurrency",
            "timestamp": "2024-11-17T02:00:00Z",
            "current_device": "Unknown Android",
            "current_device_id": "UNKNOWN_ANDROID_MOS_XYZ",
            "current_ip": "195.206.107.123",
            "current_location": "Moscow, Russia",
            "merchant_category": "international_wire",
        },
    },
    {
        "id": "demo_2",
        "name": "LEGITIMATE - Normal Purchase",
        "description": "Routine grocery purchase matching customer profile perfectly",
        "transaction": {
            "transaction_id": "TXN_67890",
            "customer_id": "CUST_101",
            "amount_usd": 650,
            "currency": "USD",
            "destination_country": "USA",
            "destination_account": "MERCHANT_WHOLE_FOODS_NYC",
            "payment_method": "debit_card",
            "timestamp": "2024-11-17T14:30:00Z",
            "current_device": "iPhone 14",
            "current_device_id": "IPHONE14_NY_DEF456",
            "current_ip": "72.23.145.67",
            "current_location": "New York, NY, USA",
            "merchant_category": "grocery",
        },
    },
    {
        "id": "demo_3",
        "name": "SUSPICIOUS - Unusual International Transfer",
        "description": "New account attempting first international transfer - edge case",
        "transaction": {
            "transaction_id": "TXN_11111",
            "customer_id": "CUST_202",
            "amount_usd": 800,
            "currency": "USD",
            "destination_country": "Mexico",
            "destination_account": "MX_BANK_ACC_5432",
            "payment_method": "bank_transfer",
            "timestamp": "2024-11-17T11:00:00Z",
            "current_device": "Samsung Galaxy S21",
            "current_device_id": "SAMSUNG_LA_GHI789",
            "current_ip": "104.32.89.201",
            "current_location": "Los Angeles, CA, USA",
            "merchant_category": "international_transfer",
        },
    },
]
