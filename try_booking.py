from busbidder.loading import load_companies, load_destinations, load_offers
from busbidder.booking import book_offer, seats_left, load_bookings, save_bookings
from busbidder.exceptions import BookingError

offers = {o.offer_id: o for o in load_offers(load_companies(), load_destinations())}
offer = offers[4]
bookings = load_bookings()

print("Seats before:", seats_left(offer, bookings))
b = book_offer(offer, 3, bookings)
save_bookings(bookings)
print("Booked:", b)
print("Seats after:", seats_left(offer, bookings))

try:
    book_offer(offer, 0, bookings)
except BookingError as e:
    print("Booking failed:", e)