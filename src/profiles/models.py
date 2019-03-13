from django.conf import settings
from django.db import models
from allauth.account.signals import user_logged_in, user_signed_up
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class profile(models.Model):
    name = models.CharField(max_length=120)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(default='description default text')

    def __str__(self):
        return self.name

# Below, to ensure each user has a Stripe ID associated with their account.

class userStripe(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        if self.stripe_id:
            return str(self.stripe_id)
        else:
            return self.user.username

#kwargs = key word arguments
def stripeCallback(sender, request, user, **kwargs):
    user_stripe_account, created = userStripe.objects.get_or_create(user=user)
    if created:
        print('Created for %s' %(user.username))
    
    # If the user does not have a Stripe ID or the ID exists and is an empty string,
    if user_stripe_account.stripe_id is None or user_stripe_account.stripe_id == '':
        # Create a new Stripe ID and set it equal to new_stripe_id
        new_stripe_id = stripe.Customer.create(email=user.email)

        # ['id'] is from Stripe JSON dictionary response
        user_stripe_account.stripe_id = new_stripe_id['id']
        user_stripe_account.save()

def profileCallback(sender, request, user, **kwargs):
    userProfile, is_created = profile.objects.get_or_create(user=user)
    if is_created:
        userProfile.name = user.username
        userProfile.save

# When a user logs in, stripeCallback will create a blank user ID.
user_logged_in.connect(stripeCallback)
user_signed_up.connect(profileCallback)
user_signed_up.connect(stripeCallback)