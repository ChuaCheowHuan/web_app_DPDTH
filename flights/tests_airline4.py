from django.core.exceptions import ValidationError
from django.db.models import Max
from django.test import Client, TestCase

from .models import Airport, Flight, Passenger

# Create your tests here.
class FlightsTestCase(TestCase):

    def setUp(self):

        # Create airports.
        a1 = Airport.objects.create(code="AAA", city="City A")
        a2 = Airport.objects.create(code="BBB", city="City B")

    def test_departures_count(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")

        # Create 3 flights departing from a1.
        for i in range(1, 4):
            Flight.objects.create(origin=a1, destination=a2, duration=100)

        self.assertEqual(a1.departures.count(), 3)


    def test_arrivals_count(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")

        # Create a flight arriving at a1.
        Flight.objects.create(origin=a2, destination=a1, duration=100)
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.arrivals.count(), 1)


    def test_invalid_destination(self):
        a = Airport.objects.get(code="AAA")
        with self.assertRaises(ValidationError):
            Flight.objects.create(origin=a, destination=a, duration=200)


    def test_zero_duration(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        with self.assertRaises(ValidationError):
            Flight.objects.create(origin=a1, destination=a2, duration=0)


    def test_negative_duration(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        with self.assertRaises(ValidationError):
            Flight.objects.create(origin=a1, destination=a2, duration=-100)

    def test_index(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")

        Flight.objects.create(origin=a1, destination=a2, duration=100)
        Flight.objects.create(origin=a2, destination=a1, duration=100)

        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["flights"].count(), 2)

    def test_valid_flight_page(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.create(origin=a1, destination=a2, duration=100)

        c = Client()
        response = c.get(f"/{f.id}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_flight_page(self):
        max_id = Flight.objects.all().aggregate(Max("id"))["id__max"] or 0

        c = Client()
        response = c.get(f"/{max_id + 1}")
        self.assertEqual(response.status_code, 404)

    def test_flight_page_passengers(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.create(origin=a1, destination=a2, duration=100)
        p = Passenger.objects.create(first="Alice", last="Adams")
        f.passengers.add(p)

        c = Client()
        response = c.get(f"/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["passengers"].count(), 1)

    def test_flight_page_non_passengers(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.create(origin=a1, destination=a2, duration=100)
        p = Passenger.objects.create(first="Alice", last="Adams")

        c = Client()
        response = c.get(f"/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["non_passengers"].count(), 1)
