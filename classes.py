
class Bus:
    def __init__(self, bus_number, source, destination,
                 total_seats, ticket_price):
        self.bus_number = bus_number
        self.source = source
        self.destination = destination
        self.total_seats = total_seats
        self.ticket_price = ticket_price
        self.seats = list(range(1, total_seats + 1))
        self.bookings = {}

    def available_seats(self):
        available = []
        for seat in self.seats:
            if seat not in self.bookings:
                available.append(seat)
        return available

    def book_ticket(self, seat, name, age, booking_id):
        if seat not in self.seats:
            return False, "Invalid seat number."

        if seat in self.bookings:
            return False, "This seat is already booked."

        self.bookings[seat] = {
            "Booking ID": booking_id,
            "Passenger Name": name,
            "Age": age,
            "Seat Number": seat,
            "Fare": self.ticket_price
        }
        return True, "Ticket booked successfully!"

    def cancel_ticket(self, booking_id):
        for seat in list(self.bookings.keys()):
            if self.bookings[seat]["Booking ID"] == booking_id:
                del self.bookings[seat]
                return True
        return False

    def total_price(self):
        price = 0
        for details in self.bookings.values():
            price += details["Fare"]
        return price
