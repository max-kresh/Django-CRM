import factory
from factory.django import DjangoModelFactory
from common.models import User, Profile, Org, Address

class OrgFactory(DjangoModelFactory):
    class Meta:
        model = Org

    name = factory.Faker("company")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "testpass")


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    org = factory.SubFactory(OrgFactory)
    role = "USER"
    is_active = True


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    street = factory.Faker("street_address")
    city = factory.Faker("city")
    postcode = factory.Faker("postcode")
    country = "US" 

