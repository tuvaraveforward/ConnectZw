import os
import django
import sys
from unittest.mock import patch, MagicMock

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project1.settings')
django.setup()

from Project1.email_utils import (
    send_account_creation_email,
    send_purchase_confirmation_email,
    send_deposit_confirmation_email,
    send_redemption_confirmation_email
)

def test_emails():
    # Mocking Client and Transaction objects
    mock_client = MagicMock()
    mock_client.firstname = "Test"
    mock_client.lastname = "User"
    mock_client.username = "testuser"
    mock_client.email_address = "tuvaravef@gmail.com" # Use a valid format

    mock_transaction = MagicMock()
    mock_transaction.description = "Test Item"
    mock_transaction.category = "Test Category"
    mock_transaction.amount = 100.00

    transactions = [mock_transaction]

    with patch('Project1.email_utils.send_mail') as mocked_send_mail:
        print("Testing Account Creation Email...")
        send_account_creation_email(mock_client)
        assert mocked_send_mail.called
        print("✓ Account Creation Email call verified.")

        mocked_send_mail.reset_mock()
        print("Testing Purchase Confirmation Email...")
        send_purchase_confirmation_email(mock_client, transactions, 100.00, "COUPON123")
        assert mocked_send_mail.called
        print("✓ Purchase Confirmation Email call verified.")

        mocked_send_mail.reset_mock()
        print("Testing Deposit Confirmation Email...")
        send_deposit_confirmation_email(mock_client, 50.00, "Cash")
        assert mocked_send_mail.called
        print("✓ Deposit Confirmation Email call verified.")

        mocked_send_mail.reset_mock()
        print("Testing Redemption Confirmation Email...")
        send_redemption_confirmation_email(mock_client, "COUPON123", 1)
        assert mocked_send_mail.called
        print("✓ Redemption Confirmation Email call verified.")

    print("\nAll email utility tests passed!")

if __name__ == "__main__":
    try:
        test_emails()
    except Exception as e:
        import traceback
        with open('verify_emails.log', 'w') as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
        sys.exit(1)
