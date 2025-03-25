from django.db.models import Q

from typing import Iterable
from accounts.models import Account
from leads.models import Lead
from opportunity.models import Opportunity
from contacts.models import Contact

def update_contacts_category(contacts: Iterable[Contact]):
    for contact in contacts:
        update_contact_category(contact)

def update_contact_category(contact: Contact):
    contact.category = None
    if Account.objects.filter(contacts__id=contact.id).exists():
        contact.category = "Account"
    elif Opportunity.objects.filter(contacts__id=contact.id).exists():
        contact.category = "Opportunity"
    elif Lead.objects.filter(contacts__id=contact.id).exists():
        status = ""
        if Lead.objects.filter(contacts__id=contact.id, status__iexact="converted"):
            status = "Customer"
        if Lead.objects.filter(~Q(status__iexact="converted"), contacts__id=contact.id):
            status = "Customer/Lead" if status == "Customer" else "Lead"
        contact.category = status
    contact.save()