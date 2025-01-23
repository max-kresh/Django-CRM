from typing import Iterable
from accounts.models import Account
from leads.models import Lead
from opportunity.models import Opportunity
from contacts.models import Contact

def update_contacts_stage(contacts: Iterable[Contact]):
    for contact in contacts:
        update_contact_stage(contact)

def update_contact_stage(contact: Contact):
    contact.stage = None
    if Account.objects.filter(contacts__id=contact.id):
        contact.stage = "Account"
    elif Opportunity.objects.filter(contacts__id=contact.id):
        contact.stage = "Opportunity"
    elif Lead.objects.filter(contacts__id=contact.id):
        contact.stage = "Lead"
    contact.save()