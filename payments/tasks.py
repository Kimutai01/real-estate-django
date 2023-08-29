from .models import Payment
from python_daraja import payment as dj_payment


from django.db import transaction
from .models import Payment

def confirm_incomplete_transactions():
    payments = Payment.objects.filter(is_complete=False)
    for payment in payments:
        details = dj_payment.query_stk_push(checkout_request_id=payment.checkout_id)
        
        # Check Transaction status from json body of daraja response
        if details["Body"]["stkCallback"]["ResultCode"] == 0:
            # Transaction is complete
            payment.is_complete = True
            payment.save()
            generate_receipt(payment)
        else:
            # Transaction is incomplete
            pass
            

def generate_receipt(payment):
    # Implement your receipt/invoice generation logic here
    # You can use payment and associated data to create the receipt content
    
    receipt_content = f"Receipt for Payment ID: {payment.id}\n"
    receipt_content += f"Amount: {payment.amount}\n"
    receipt_content += "Thank you for your payment!\n"
    
    # Save the receipt content to a file or send it via email to the customer
    
    # Example: Saving receipt content to a file
    receipt_filename = f"receipt_{payment.id}.txt"
    with open(receipt_filename, "w") as receipt_file:
        receipt_file.write(receipt_content)
    
    # You can also implement logic to send the receipt content via email

# Assuming 'dj_payment' is your payment processing library/module
# Make sure to import and set up 'dj_payment' appropriately in your code

# Call the function to process incomplete transactions and generate receipts
confirm_incomplete_transactions()

        