
import json
import streamlit as st
from classes import Bus


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="BusGo - Bus Ticket Booking",
    page_icon="🚌",
    layout="wide"
)


# --------------------------------------------------
# LOAD BUS DATA
# --------------------------------------------------
def load_bus_configs():
    with open("data.json", "r") as file:
        data = json.load(file)

    return data["buses"]


# --------------------------------------------------
# INITIALIZE SESSION STATE
# --------------------------------------------------
if "buses" not in st.session_state:
    configs = load_bus_configs()

    st.session_state.buses = [
        Bus(
            config["bus_number"],
            config["source"],
            config["destination"],
            config["total_seats"],
            config["ticket_price"]
        )
        for config in configs
    ]

if "booking_counter" not in st.session_state:
    st.session_state.booking_counter = 1

if "last_booking" not in st.session_state:
    st.session_state.last_booking = None

buses = st.session_state.buses


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🚌 BusGo")
st.subheader("Your Journey, Your Seat, Your Adventure!")

st.write(
    "Welcome to BusGo! Book your bus tickets easily "
    "from Hyderabad to your favourite destinations."
)

st.divider()


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------
st.header("📊 Booking Dashboard")

total_routes = len(buses)

total_seats = sum(
    bus.total_seats for bus in buses
)

available_count = sum(
    len(bus.available_seats()) for bus in buses
)

booked_count = total_seats - available_count

total_price = sum(
    bus.total_price() for bus in buses
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🚌 Bus Routes", total_routes)

with col2:
    st.metric("💺 Available Seats", available_count)

with col3:
    st.metric("🎟️ Booked Seats", booked_count)

with col4:
    st.metric("💰 Total Amount", f"₹{total_price:,.0f}")

st.divider()


# --------------------------------------------------
# AVAILABLE BUS TABS
# --------------------------------------------------
st.header("🗺️ Available Buses")

st.write(
    "Select a destination tab to see bus information, "
    "seat availability, ticket fares, and booking options."
)

tab_names = [
    f"🚌 {bus.destination}" for bus in buses
]

tab_names.append("📊 Booking Summary")

tabs = st.tabs(tab_names)


# --------------------------------------------------
# INDIVIDUAL BUS INFORMATION
# --------------------------------------------------
for tab, bus in zip(tabs[:-1], buses):

    with tab:

        st.subheader(
            f"🚌 {bus.source} → {bus.destination}"
        )

        # Bus information
        info1, info2 = st.columns(2)

        with info1:
            st.info(f"**Bus Number:** {bus.bus_number}")
            st.info(f"**Starting Point:** {bus.source}")
            st.info(f"**Destination:** {bus.destination}")

        with info2:
            st.info(f"**Total Seats:** {bus.total_seats}")
            st.info(f"**Base Ticket Fare:** ₹{bus.ticket_price}")
            st.info("**Window Seats:** 5 and 10")

        # Seat availability
        available_seats = bus.available_seats()

        booked_seats = [
            seat for seat in bus.seats
            if seat in bus.bookings
        ]

        st.subheader("💺 Seat Availability")

        seat_col1, seat_col2, seat_col3 = st.columns(3)

        with seat_col1:
            st.metric("Total Seats", bus.total_seats)

        with seat_col2:
            st.metric("Available", len(available_seats))

        with seat_col3:
            st.metric("Booked", len(booked_seats))

        if bus.total_seats > 0:
            st.progress(
                len(booked_seats) / bus.total_seats,
                text="Seat Occupancy"
            )

        st.caption(
            "🟢 Available  |  🔴 Booked  |  🪟 Window Seat"
        )

        # Display seats in rows of five
        for row_start in range(1, bus.total_seats + 1, 5):

            seat_columns = st.columns(5)

            for index, seat in enumerate(
                range(
                    row_start,
                    min(row_start + 5, bus.total_seats + 1)
                )
            ):

                with seat_columns[index]:

                    if seat in booked_seats:
                        st.error(f"🔒 Seat {seat}")

                    elif seat in [5, 10]:
                        st.info(f"🪟 Seat {seat}")

                    else:
                        st.success(f"✅ Seat {seat}")

        st.divider()


        # --------------------------------------------------
        # BOOKING FORM
        # --------------------------------------------------
        st.subheader("🎫 Book Your Ticket")

        if available_seats:

            selected_seat = st.selectbox(
                "Choose Your Seat",
                options=available_seats,
                key=f"seat_select_{bus.bus_number}",
                format_func=lambda seat: (
                    f"Seat {seat} - Window Seat 🪟"
                    if seat in [5, 10]
                    else f"Seat {seat}"
                )
            )

            # Calculate ticket fare
            extra_charge = (
                250 if selected_seat in [5, 10] else 0
            )

            total_fare = bus.ticket_price + extra_charge

            fare_col1, fare_col2, fare_col3 = st.columns(3)

            with fare_col1:
                st.metric(
                    "Base Fare",
                    f"₹{bus.ticket_price:,.0f}"
                )

            with fare_col2:
                st.metric(
                    "Window Seat Charge",
                    f"₹{extra_charge:,.0f}"
                )

            with fare_col3:
                st.metric(
                    "Total Fare",
                    f"₹{total_fare:,.0f}"
                )

            with st.form(
                key=f"booking_form_{bus.bus_number}"
            ):

                passenger_name = st.text_input(
                    "Passenger Name",
                    placeholder="Enter passenger name"
                )

                passenger_age_text = st.text_input(
                    "Passenger Age",
                    placeholder="Enter age from 1 to 120"
                )

                confirm_booking = st.form_submit_button(
                    "🎟️ Confirm Booking",
                    use_container_width=True
                )

                if confirm_booking:

                    # ------------------------------------------
                    # VALIDATE PASSENGER NAME
                    # ------------------------------------------
                    name = passenger_name.strip()

                    if not name:

                        st.error(
                            "❌ Please enter the passenger name."
                        )

                    elif not all(
                        word.isalpha() for word in name.split()
                    ):

                        st.error(
                            "❌ Invalid passenger name! "
                            "Please enter alphabets only. "
                            "Numbers and special characters are not allowed."
                        )

                    # ------------------------------------------
                    # VALIDATE PASSENGER AGE
                    # ------------------------------------------
                    elif not passenger_age_text.strip():

                        st.error(
                            "❌ Please enter the passenger age."
                        )

                    elif not passenger_age_text.strip().isdigit():

                        st.error(
                            "❌ Invalid age! "
                            "Please enter numbers only. "
                            "Alphabets and special characters are not allowed."
                        )

                    else:

                        passenger_age = int(
                            passenger_age_text.strip()
                        )

                        # Age must be between 1 and 120
                        if passenger_age < 1 or passenger_age > 120:

                            st.error(
                                "❌ Booking failed! Passenger age "
                                "must be between 1 and 120 years."
                            )

                        else:

                            # ----------------------------------
                            # GENERATE BOOKING ID
                            # ----------------------------------
                            booking_id = (
                                f"BG{st.session_state.booking_counter:04d}"
                            )

                            # ----------------------------------
                            # BOOK TICKET
                            # ----------------------------------
                            success, message = bus.book_ticket(
                                selected_seat,
                                name,
                                passenger_age,
                                booking_id
                            )

                            if success:

                                # Save total fare
                                bus.bookings[selected_seat]["Fare"] = (
                                    total_fare
                                )

                                bus.bookings[selected_seat]["Extra Charge"] = (
                                    extra_charge
                                )

                                # Save last booking information
                                st.session_state.last_booking = {
                                    "Booking ID": booking_id,
                                    "Passenger Name": name,
                                    "Age": passenger_age,
                                    "Route": (
                                        f"{bus.source} → {bus.destination}"
                                    ),
                                    "Bus Number": bus.bus_number,
                                    "Seat Number": selected_seat,
                                    "Fare": total_fare
                                }

                                st.session_state.booking_counter += 1

                                st.success(message)
                                st.balloons()
                                st.rerun()

                            else:
                                st.error(message)

        else:

            st.warning(
                "😔 All seats on this bus have been booked."
            )


        # --------------------------------------------------
        # BOOKING DETAILS
        # --------------------------------------------------
        st.divider()
        st.subheader("📋 Passenger Booking Details")

        if bus.bookings:

            for seat, details in bus.bookings.items():

                with st.expander(
                    f"🎫 {details['Booking ID']} - "
                    f"{details['Passenger Name']} - Seat {seat}"
                ):

                    st.write(
                        f"**Booking ID:** {details['Booking ID']}"
                    )

                    st.write(
                        f"**Passenger Name:** "
                        f"{details['Passenger Name']}"
                    )

                    st.write(f"**Age:** {details['Age']}")

                    st.write(f"**Seat Number:** {seat}")

                    st.write(
                        f"**Window Seat Extra Charge:** "
                        f"₹{details.get('Extra Charge', 0):,.0f}"
                    )

                    st.write(
                        f"**Total Fare:** ₹{details['Fare']:,.0f}"
                    )

        else:

            st.info("No tickets booked for this bus yet.")


        # --------------------------------------------------
        # CANCEL TICKET
        # --------------------------------------------------
        st.divider()
        st.subheader("🔄 Cancel a Ticket")

        if bus.bookings:

            with st.form(
                key=f"cancel_form_{bus.bus_number}"
            ):

                booking_ids = [
                    details["Booking ID"]
                    for details in bus.bookings.values()
                ]

                selected_booking_id = st.selectbox(
                    "Select Booking ID",
                    options=booking_ids,
                    key=f"cancel_select_{bus.bus_number}"
                )

                cancel_button = st.form_submit_button(
                    "Cancel Booking",
                    use_container_width=True
                )

                if cancel_button:

                    cancelled = bus.cancel_ticket(
                        selected_booking_id
                    )

                    if cancelled:

                        st.success(
                            f"Booking {selected_booking_id} "
                            "cancelled successfully."
                        )

                        st.rerun()

                    else:

                        st.error("Booking ID not found.")

        else:

            st.caption("There are no tickets to cancel.")


# --------------------------------------------------
# OVERALL BOOKING SUMMARY
# --------------------------------------------------
with tabs[-1]:

    st.header("📊 Overall Booking Summary")

    summary_data = []

    for bus in buses:

        summary_data.append({
            "Route": f"{bus.source} → {bus.destination}",
            "Bus Number": bus.bus_number,
            "Total Seats": bus.total_seats,
            "Booked Seats": len(bus.bookings),
            "Available Seats": len(bus.available_seats()),
            "Total Amount (₹)": bus.total_price()
        })

    st.dataframe(
        summary_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("🎟️ All Passenger Bookings")

    all_bookings = []

    for bus in buses:

        for seat, details in bus.bookings.items():

            all_bookings.append({
                "Booking ID": details["Booking ID"],
                "Passenger Name": details["Passenger Name"],
                "Age": details["Age"],
                "Route": f"{bus.source} → {bus.destination}",
                "Bus Number": bus.bus_number,
                "Seat Number": seat,
                "Fare (₹)": details["Fare"]
            })

    if all_bookings:

        st.dataframe(
            all_bookings,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No bookings have been made yet.")

    st.divider()

    total_active_bookings = sum(
        len(bus.bookings) for bus in buses
    )

    final_amount = sum(
        bus.total_price() for bus in buses
    )

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        st.metric(
            "🎫 Active Bookings",
            total_active_bookings
        )

    with summary_col2:
        st.metric(
            "💰 Total Amount",
            f"₹{final_amount:,.0f}"
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "🚌 BusGo | Thank you for choosing us. "
    "Have a safe and happy journey!"
)
