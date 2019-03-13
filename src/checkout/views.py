from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    publishKey = settings.STRIPE_PUBLISHABLE_KEY
    customer_id = request.user.userstripe.stripe_id

    # When the checkout form is submitted, the data is posted.
    if request.method == 'POST':
        # The value of the posted Stripe token is saved into a var called token.
        token = request.POST['stripeToken']

        customer = stripe.Customer.retrieve(customer_id)
        customer.sources.create(source=token)

        #Create a charge: this will charge the user's card
        charge = stripe.Charge.create(
            amount=500, # Amount in cents
            currency='usd',
            customer=customer,
            description='Example charge',
        )

    context = {'publishKey': publishKey}
    template = 'checkout/checkout.html'
    return render(request, template, context)

def confirmation(request):
        # Charge confirmation page
        template = 'checkout/charge.html'
        return render(request, template)