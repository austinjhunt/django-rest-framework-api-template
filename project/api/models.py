from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _



class Profile(models.Model):
    """
    Extension of the user model to store additional information about the user.

    Storing card data like the last four digits and the card type can improve
    the user experience on your site. For example, when a user is making a
    purchase, you can show them which card they have on file. This can give
    them confidence that they're using the correct card and allow them to easily
    switch cards if they have more than one on file.

    However, you should never store sensitive card information like the full
    card number or CVV code. This is against PCI compliance rules and can put your
    users' data at risk. Stripe handles all of this sensitive data for you.
    They provide you with a customer ID for each
    user, which you can use to create charges and manage subscriptions without
    handling sensitive card data directly.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    preferred_name = models.CharField(max_length=50, blank=True)
    stripe_customer_id = models.CharField(max_length=50, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=50, blank=True, null=True)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_exp_month = models.IntegerField(blank=True, null=True)
    card_exp_year = models.IntegerField(blank=True, null=True)

    class CardType(models.TextChoices):
        VISA = "Visa", "Visa"
        MASTERCARD = "MasterCard", "MasterCard"
        AMEX = "Amex", "American Express"
        DISCOVER = "Discover", "Discover"
        DINERS = "Diners", "Diners Club"
        JCB = "JCB", "JCB"

    card_type = models.CharField(
        max_length=15,
        choices=CardType.choices,
        default=CardType.VISA,
        blank=True,
        null=True,
    )

    # create text choices for plan type
    class PlanType(models.TextChoices):
        FREE = "FRE", _("Free")
        PREMIUM = "PRE", _("Premium")

    plan_type = models.CharField(
        max_length=3,
        choices=PlanType.choices,
        default=PlanType.FREE,
    )