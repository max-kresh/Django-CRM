import factory
from factory.django import DjangoModelFactory
from common.tests.factories import AddressFactory, OrgFactory
from contacts.models import Contact

class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    primary_email = factory.Faker("email")

    mobile_number = factory.Faker("phone_number")

    secondary_number = ""

    address = factory.SubFactory(AddressFactory)
    org = factory.SubFactory(OrgFactory)

    is_active = True

    category = "Account" 